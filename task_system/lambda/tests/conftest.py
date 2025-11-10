"""
Pytest configuration and shared fixtures for Lambda tests
"""
import pytest
import os
import sys

# Add lambda directories to Python path
lambda_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(lambda_root, 'api_handler'))
sys.path.insert(0, os.path.join(lambda_root, 'task_processor'))


@pytest.fixture(autouse=True)
def reset_env_vars():
    """
    Fixture to reset environment variables after each test
    This prevents test pollution
    """
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_env_local():
    """Fixture providing local environment variables"""
    return {
        "ENVIRONMENT": "local",
        "LOCALSTACK_ENDPOINT": "http://localstack:4566",
        "API_TOKEN": "test-token",
        "QUEUE_URL": "http://localhost:4566/000000000000/test-queue.fifo"
    }


@pytest.fixture
def mock_env_production():
    """Fixture providing production environment variables"""
    return {
        "ENVIRONMENT": "production",
        "AWS_SQS_ENDPOINT_URL": "https://sqs.us-east-1.amazonaws.com",
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "prod-key",
        "AWS_SECRET_ACCESS_KEY": "prod-secret",
        "API_TOKEN": "prod-token",
        "QUEUE_URL": "https://sqs.us-east-1.amazonaws.com/123456789012/prod-queue.fifo"
    }


@pytest.fixture
def sample_api_event():
    """Fixture providing a sample API Gateway event"""
    return {
        "headers": {
            "X-Api-Key": "test-token",
            "Content-Type": "application/json"
        },
        "body": '{"title": "Test Task", "priority": "high", "description": "Test description"}'
    }


@pytest.fixture
def sample_sqs_event():
    """Fixture providing a sample SQS event"""
    return {
        "Records": [
            {
                "messageId": "test-message-id",
                "receiptHandle": "test-receipt-handle",
                "body": '{"task_id": "test-123", "task_type": "email", "description": "Test task", "priority": "high", "created_at": "2025-11-09T10:00:00"}',
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1699520000000",
                    "SenderId": "AIDAIT2UOQQY3AUEKVGXU",
                    "ApproximateFirstReceiveTimestamp": "1699520000000"
                },
                "messageAttributes": {},
                "md5OfBody": "test-md5",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:000000000000:test-queue.fifo",
                "awsRegion": "us-east-1"
            }
        ]
    }
