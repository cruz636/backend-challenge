import json
import pytest
from unittest.mock import patch, MagicMock, call
import os
import sys

# Add the lambda directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api_handler'))

from handler import main, validate_api_token, get_sqs_client, _get_data_from_body


class TestValidateApiToken:
    """Tests for the validate_api_token function"""

    def test_raise_error_if_token_is_not_present(self):
        """Test that validation fails when API token header is missing"""
        with patch.dict(os.environ, {"API_TOKEN": "test-token"}):
            headers = {}
            assert validate_api_token(headers) is False

    def test_raise_error_if_token_is_invalid(self):
        """Test that validation fails when API token is incorrect"""
        with patch.dict(os.environ, {"API_TOKEN": "correct-token"}):
            headers = {"X-Api-Key": "wrong-token"}
            assert validate_api_token(headers) is False

    def test_successful_validation_with_valid_token(self):
        """Test that validation succeeds with correct token"""
        with patch.dict(os.environ, {"API_TOKEN": "valid-token"}):
            headers = {"X-Api-Key": "valid-token"}
            assert validate_api_token(headers) is True

    def test_token_validation_case_insensitive_header(self):
        """Test that different case variations of the header key work"""
        with patch.dict(os.environ, {"API_TOKEN": "valid-token"}):
            # Test lowercase
            assert validate_api_token({"x-api-key": "valid-token"}) is True
            # Test mixed case
            assert validate_api_token({"X-API-KEY": "valid-token"}) is True

    def test_validation_fails_when_api_token_not_configured(self):
        """Test that validation fails when API_TOKEN env var is not set"""
        with patch.dict(os.environ, {}, clear=True):
            headers = {"X-Api-Key": "some-token"}
            assert validate_api_token(headers) is False


class TestGetSqsClient:
    """Tests for the get_sqs_client function"""

    @patch('handler.boto3.client')
    def test_local_environment_uses_localstack_endpoint(self, mock_boto_client):
        """Test that local environment configures LocalStack endpoint"""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "local",
            "LOCALSTACK_ENDPOINT": "http://localstack:4566"
        }):
            get_sqs_client()
            mock_boto_client.assert_called_once_with(
                'sqs',
                endpoint_url='http://localstack:4566'
            )

    @patch('handler.boto3.client')
    def test_staging_environment_uses_aws_config(self, mock_boto_client):
        """Test that staging environment uses AWS credentials"""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "staging",
            "AWS_SQS_ENDPOINT_URL": "https://sqs.us-east-1.amazonaws.com",
            "AWS_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret"
        }):
            get_sqs_client()
            mock_boto_client.assert_called_once_with(
                'sqs',
                endpoint_url='https://sqs.us-east-1.amazonaws.com',
                region_name='us-east-1',
                aws_access_key_id='test-key',
                aws_secret_access_key='test-secret'
            )

    @patch('handler.boto3.client')
    def test_production_environment_uses_aws_config(self, mock_boto_client):
        """Test that production environment uses AWS credentials"""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "AWS_SQS_ENDPOINT_URL": "https://sqs.us-west-2.amazonaws.com",
            "AWS_REGION": "us-west-2",
            "AWS_ACCESS_KEY_ID": "prod-key",
            "AWS_SECRET_ACCESS_KEY": "prod-secret"
        }):
            get_sqs_client()
            mock_boto_client.assert_called_once_with(
                'sqs',
                endpoint_url='https://sqs.us-west-2.amazonaws.com',
                region_name='us-west-2',
                aws_access_key_id='prod-key',
                aws_secret_access_key='prod-secret'
            )


class TestGetDataFromBody:
    """Tests for the _get_data_from_body function"""

    def test_extracts_payload_correctly(self):
        """Test that payload is extracted from body"""
        body = {"payload": {"key": "value"}, "description": "test", "priority": "high"}
        result = _get_data_from_body(body)
        assert result["payload"] == {"key": "value"}

    def test_uses_default_priority_when_missing(self):
        """Test that default priority is 'normal' when not provided"""
        body = {"payload": {}, "description": "test"}
        result = _get_data_from_body(body)
        assert result["priority"] == "normal"

    def test_uses_empty_string_for_missing_description(self):
        """Test that description defaults to empty string"""
        body = {"payload": {}, "priority": "high"}
        result = _get_data_from_body(body)
        assert result["description"] == ""

    def test_generates_unique_id_and_timestamp(self):
        """Test that id and timestamp are generated"""
        body = {"payload": {}}
        result = _get_data_from_body(body)
        assert "id" in result
        assert "timestamp" in result
        assert len(result["id"]) > 0
        assert len(result["timestamp"]) > 0


class TestMainHandler:
    """Tests for the main Lambda handler function"""

    @patch('handler.get_sqs_client')
    def test_unauthorized_when_token_missing(self, mock_get_sqs):
        """Test that 401 is returned when API token is missing"""
        with patch.dict(os.environ, {"API_TOKEN": "valid-token"}):
            event = {
                "headers": {},
                "body": json.dumps({"title": "Test Task", "priority": "high"})
            }
            result = main(event, None)

            assert result["statusCode"] == 401
            assert "Unauthorized" in result["body"]
            mock_get_sqs.assert_not_called()

    @patch('handler.get_sqs_client')
    def test_unauthorized_when_token_invalid(self, mock_get_sqs):
        """Test that 401 is returned when API token is invalid"""
        with patch.dict(os.environ, {"API_TOKEN": "valid-token"}):
            event = {
                "headers": {"X-Api-Key": "wrong-token"},
                "body": json.dumps({"title": "Test Task", "priority": "high"})
            }
            result = main(event, None)

            assert result["statusCode"] == 401
            assert "Unauthorized" in result["body"]
            mock_get_sqs.assert_not_called()

    @patch('handler.get_sqs_client')
    def test_successful_execution_with_valid_token(self, mock_get_sqs):
        """Test successful message sending with valid token"""
        mock_sqs = MagicMock()
        mock_get_sqs.return_value = mock_sqs

        with patch.dict(os.environ, {
            "API_TOKEN": "valid-token",
            "QUEUE_URL": "http://localhost:4566/000000000000/test-queue.fifo"
        }):
            event = {
                "headers": {"X-Api-Key": "valid-token"},
                "body": json.dumps({
                    "title": "Test Task",
                    "priority": "high",
                    "description": "Test description"
                })
            }
            result = main(event, None)

            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert "Message sent to SQS" in body["message"]
            assert "task_id" in body

            # Verify SQS send_message was called
            mock_sqs.send_message.assert_called_once()
            call_args = mock_sqs.send_message.call_args

            assert call_args[1]["QueueUrl"] == "http://localhost:4566/000000000000/test-queue.fifo"
            assert call_args[1]["MessageGroupId"] == "tasks"
            assert "MessageDeduplicationId" in call_args[1]

    @patch('handler.get_sqs_client')
    def test_body_with_all_fields(self, mock_get_sqs):
        """Test that all body fields are properly processed"""
        mock_sqs = MagicMock()
        mock_get_sqs.return_value = mock_sqs

        with patch.dict(os.environ, {
            "API_TOKEN": "valid-token",
            "QUEUE_URL": "http://localhost:4566/000000000000/test-queue.fifo"
        }):
            event = {
                "headers": {"X-Api-Key": "valid-token"},
                "body": json.dumps({
                    "payload": {"data": "test"},
                    "priority": "low",
                    "description": "Full test"
                })
            }
            result = main(event, None)

            assert result["statusCode"] == 200

            # Verify message body structure
            call_args = mock_sqs.send_message.call_args
            message_body = json.loads(call_args[1]["MessageBody"])

            assert message_body["priority"] == "low"
            assert message_body["description"] == "Full test"
            assert message_body["payload"] == {"data": "test"}
            assert "id" in message_body
            assert "timestamp" in message_body

    @patch('handler.get_sqs_client')
    def test_empty_body_uses_defaults(self, mock_get_sqs):
        """Test that empty body still works with default values"""
        mock_sqs = MagicMock()
        mock_get_sqs.return_value = mock_sqs

        with patch.dict(os.environ, {
            "API_TOKEN": "valid-token",
            "QUEUE_URL": "http://localhost:4566/000000000000/test-queue.fifo"
        }):
            event = {
                "headers": {"X-Api-Key": "valid-token"},
                "body": json.dumps({})
            }
            result = main(event, None)

            assert result["statusCode"] == 200

            # Verify defaults are used
            call_args = mock_sqs.send_message.call_args
            message_body = json.loads(call_args[1]["MessageBody"])

            assert message_body["priority"] == "normal"
            assert message_body["description"] == ""
            assert message_body["payload"] == {}
