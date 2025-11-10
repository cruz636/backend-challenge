# Lambda Tests

Comprehensive test suite for the Lambda functions in this project.

## Overview

This test suite covers:
- **API Handler** (`lambda/api_handler/handler.py`): Tests for API token validation, SQS client configuration, and request handling
- **Task Processor** (`lambda/task_processor/task_handler.py`): Tests for task processing, priority routing, and error handling

## Test Coverage

### API Handler Tests (17 tests)
- Token validation (missing, invalid, valid tokens)
- Case-insensitive header handling
- SQS client configuration for different environments (local, staging, production)
- Request body parsing and defaults
- Message sending to SQS
- Authorization checks

### Task Handler Tests (18 tests)
- Priority-based task routing (high, normal, low)
- SQS event processing (single and multiple records)
- Default value handling
- Error handling (malformed JSON, missing fields)
- Logging and output verification

**Total: 35 tests**

## Running Tests

### Using Docker (Recommended)

Build and run tests in an isolated container:

```bash
cd lambda
docker build -t lambda-tests -f tests/Dockerfile .
docker run --rm lambda-tests
```

Or use the convenience script:

```bash
cd lambda/tests
./run-tests.sh
```

### Using Local Python Environment

If you prefer to run tests locally:

```bash
cd lambda/tests
pip install -r requirements-test.txt
pytest -v
```

## Test Structure

```
lambda/tests/
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini               # Pytest configuration
├── requirements-test.txt    # Test dependencies
├── test_api_handler.py     # API handler tests
├── test_task_handler.py    # Task processor tests
├── Dockerfile              # Docker setup for tests
├── docker-compose.test.yml # Docker Compose configuration
├── run-tests.sh            # Convenience script
└── README.md               # This file
```

## Test Dependencies

- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **boto3**: AWS SDK (same as production)
- **moto**: AWS service mocking (optional, for integration tests)

## Configuration

Tests use `conftest.py` for shared fixtures and configuration:
- Automatic environment variable cleanup between tests
- Pre-configured environment fixtures for local/production
- Sample event fixtures for API Gateway and SQS

## Notes

- Tests automatically reset environment variables after each test to prevent pollution
- All tests use mocks for AWS services (no real AWS calls)
- The test suite is portable and can be run in any environment with Docker
