import unittest
from unittest.mock import patch
from app.kafka_to_dwh import ParseKafkaMessage, CompanyEvent


class TestParseKafkaMessage(unittest.TestCase):

    def test_process_valid_message(self):
        element = (
            b"key",
            b'{"idempotency_key": "321", "id": "123", "name": "Test Company", "organization_id": "org123", "event": "created", "created_at": 1609459200, "updated_at": 1609459200, "changes": "{}"}',
        )
        dofn = ParseKafkaMessage()
        result = list(dofn.process(element))
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], CompanyEvent)
        self.assertEqual(result[0].id, "123")
        self.assertEqual(result[0].name, "Test Company")
        self.assertEqual(result[0].organization_id, "org123")
        self.assertEqual(result[0].event, "created")

    @patch("app.kafka_to_dwh.LOGGER")
    def test_process_invalid_json(self, mock_logger):
        element = (b"key", b"invalid json")
        dofn = ParseKafkaMessage()
        result = list(dofn.process(element))
        self.assertEqual(len(result), 0)
        mock_logger.exception.assert_called_once_with("Malformed event from Kafka", extra={"kafka_event": element})

    @patch("app.kafka_to_dwh.LOGGER")
    def test_process_missing_fields(self, mock_logger):
        element = (b"key", b'{"id": "123", "name": "Test Company"}')
        dofn = ParseKafkaMessage()
        result = list(dofn.process(element))
        self.assertEqual(len(result), 0)
        mock_logger.exception.assert_called_once_with("Malformed event from Kafka", extra={"kafka_event": element})

    @patch("app.kafka_to_dwh.LOGGER")
    def test_process_invalid_changes_field(self, mock_logger):
        element = (
            b"key",
            b'{"id": "123", "name": "Test Company", "organization_id": "org123", "event": "created", "created_at": 1609459200, "updated_at": 1609459200, "changes": "invalid json"}',
        )
        dofn = ParseKafkaMessage()
        result = list(dofn.process(element))
        self.assertEqual(len(result), 0)
        mock_logger.exception.assert_called_once_with("Malformed event from Kafka", extra={"kafka_event": element})
