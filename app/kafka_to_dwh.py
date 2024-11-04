import json
import logging
import uuid

from psycopg2 import pool
from datetime import datetime, timezone
from apache_beam import Pipeline, ParDo, DoFn
from apache_beam.io.kafka import ReadFromKafka
from apache_beam.options.pipeline_options import PipelineOptions

from app.models import CompanyEvent
from app.options import KafkaToDwhOptions

LOGGER = logging.getLogger(__name__)


class ParseKafkaMessage(DoFn):
    """
    Parse the message value from Kafka to a CompanyEvent instance
    """

    def process(self, element):
        """
        We receive a tuple with the key and the message value from Kafka.
        Both are strings in bytes format. Parse the value to a valid model.
        :param element: Tuple with key and message value
        :return: CompanyEvent instance
        """
        try:
            data = json.loads(element[1].decode("utf-8"))

            # Parse the changes field from JSON string
            data["changes"] = json.loads(data["changes"])

            yield CompanyEvent(**data)
        except Exception:
            LOGGER.exception("Malformed event from Kafka", extra={"kafka_event": element})


class WriteToDwh(DoFn):
    """
    Write the CompanyEvent instance to the data warehouse in append mode.
    Add an ingestion timestamp to the record.
    """

    def __init__(self, db_config, *unused_args, **unused_kwargs):
        self.db_config = db_config
        self.connection_pool = None
        super().__init__(*unused_args, **unused_kwargs)

    def start_bundle(self):
        # Create a connection pool at the beginning of the bundle
        # create a pool of connections with psycopg2
        self.connection_pool = pool.SimpleConnectionPool(1, 20, **self.db_config)

    def process(self, event: CompanyEvent):
        """
        Write the CompanyEvent instance to the data warehouse.
        :param event: CompanyEvent instance
        """
        connection = self.connection_pool.getconn()
        try:
            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO public.companies_events (event_type, ingested_at, id, name, organization_id, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    event.event,
                    datetime.now(timezone.utc),
                    event.id,
                    event.name,
                    event.organization_id,
                    datetime.fromtimestamp(event.created_at, timezone.utc),
                    datetime.fromtimestamp(event.updated_at, timezone.utc),
                ),
            )

            connection.commit()
            cursor.close()
        except Exception:
            LOGGER.exception("Error writing event to DWH", extra={"event": event})
        finally:
            self.connection_pool.putconn(connection)

    def finish_bundle(self):
        # Close the connection pool when the bundle is done
        if self.connection_pool:
            self.connection_pool.closeall()


def run():
    """
    Run the pipeline to read from Kafka companies events and write to Postgres
    """
    pipeline_options = PipelineOptions()
    custom_options = pipeline_options.view_as(KafkaToDwhOptions)

    string_deserializer = "org.apache.kafka.common.serialization.StringDeserializer"

    db_config = {
        "dbname": custom_options.pg_db,
        "user": custom_options.pg_user,
        "password": custom_options.pg_password,
        "host": custom_options.pg_host,
        "port": custom_options.pg_port,
    }

    # Special options for the DirectRunner:
    # - max_num_records: limit the number of records read from Kafka to match the total number of events in the topic
    # - use a random group id to start from the beginning of the topic every time

    with Pipeline(options=pipeline_options) as p:
        (
            p
            | "ReadFromKafka"
            >> ReadFromKafka(
                consumer_config={
                    "bootstrap.servers": custom_options.broker,
                    "group.id": f"qonto-beam-{uuid.uuid4() if custom_options.dev else 'group'}",
                    "auto.offset.reset": "earliest",  # if no offset committed, start from the earliest we can
                    "key.deserializer": string_deserializer,
                    "value.deserializer": string_deserializer,
                },
                topics=[custom_options.topic],
                max_num_records=18 if custom_options.dev else None,
            )
            | "ParseKafkaMessage" >> ParDo(ParseKafkaMessage())
            | "WriteToDwh" >> ParDo(WriteToDwh(db_config))
        )
