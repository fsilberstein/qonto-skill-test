from apache_beam.options.pipeline_options import PipelineOptions


class KafkaToDwhOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument("--broker", default="kafka:9092", help="The Kafka broker to read events from.")
        parser.add_argument("--topic", default="companies", help="The input topic from Kafka to read events from.")
        parser.add_argument(
            "--dev",
            default=False,
            help="Dev mode or not. Needed locally due to DirectRunner limitations.",
        )
        parser.add_argument(
            "--pg-host",
            default="localhost",
            help="Host to use to connect to Postgres.",
        )
        parser.add_argument(
            "--pg-port",
            default=5432,
            help="Port to use to connect to Postgres.",
        )
        parser.add_argument(
            "--pg-user",
            default="postgres",
            help="User to use to connect to Postgres.",
        )
        parser.add_argument(
            "--pg-password",
            default="postgres",
            help="Password to use to connect to Postgres.",
        )
        parser.add_argument(
            "--pg-db",
            default="postgres",
            help="Database to use to connect to Postgres.",
        )
