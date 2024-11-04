import unittest

from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.test_stream import TestStream
from apache_beam.testing.util import assert_that, equal_to

from app.kafka_to_dwh import ParseKafkaMessage
from app.models import CompanyEvent


class TestFullPipeline(unittest.TestCase):
    def test_parse_unknown_json_no_output(self):
        options = PipelineOptions()
        options.view_as(StandardOptions).streaming = True

        with TestPipeline(options=options) as p:
            EVENTS = [
                '{"ip": "138.201.212.70"}',
                "test",
                "",
            ]

            test_stream = (
                TestStream()
                .advance_watermark_to(0)
                .add_elements([EVENTS[0], EVENTS[1], EVENTS[2]])
                .advance_watermark_to_infinity()
            )

            output = p | test_stream | beam.ParDo(ParseKafkaMessage())

            EXPECTED_OUTPUT = []

            assert_that(output, equal_to(EXPECTED_OUTPUT))

    def test_parse_ok(self):
        options = PipelineOptions()
        options.view_as(StandardOptions).streaming = True

        with TestPipeline(options=options) as p:
            EVENTS = [
                (
                    None,
                    b'{"idempotency_key": "321", "id": "123", "name": "Test Company", "organization_id": "org123", "event": "created", "created_at": 1609459200, "updated_at": 1609459200, "changes": "{}"}',
                ),
            ]

            test_stream = (
                TestStream().advance_watermark_to(0).add_elements([EVENTS[0]]).advance_watermark_to_infinity()
            )

            output = p | test_stream | beam.ParDo(ParseKafkaMessage())

            EXPECTED_OUTPUT = [
                CompanyEvent(
                    idempotency_key="321",
                    event="created",
                    id="123",
                    organization_id="org123",
                    name="Test Company",
                    created_at=1609459200,
                    updated_at=1609459200,
                    changes={},
                )
            ]

            assert_that(output, equal_to(EXPECTED_OUTPUT))
