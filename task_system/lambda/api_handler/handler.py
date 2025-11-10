import json
import boto3
import os
import uuid
from datetime import datetime


def get_sqs_client():
    config = {}

    if os.environ.get("ENVIRONMENT") == "local":
        # Use LocalStack container hostname (from inside Docker network)
        localstack_endpoint = os.environ.get("LOCALSTACK_ENDPOINT", "http://localstack:4566")
        config['endpoint_url'] = localstack_endpoint
        print(f"DEBUG: Using LocalStack endpoint: {localstack_endpoint}")

    if os.environ.get("ENVIRONMENT") == "staging" or os.environ.get("ENVIRONMENT") == "production":
        config['endpoint_url'] = os.environ.get("AWS_SQS_ENDPOINT_URL")
        config['region_name'] = os.environ.get("AWS_REGION")
        config['aws_access_key_id'] = os.environ.get("AWS_ACCESS_KEY_ID")
        config['aws_secret_access_key'] = os.environ.get("AWS_SECRET_ACCESS_KEY")

    return boto3.client('sqs', **config)

def validate_api_token(headers) -> bool:
    expected_token = os.environ.get("API_TOKEN")

    if not expected_token:
        print("ERROR: API_TOKEN not configured")
        return False

    api_token_headers = (
        headers.get("x-api-key") or
        headers.get("X-Api-Key") or
        headers.get("X-API-KEY")
    )

    if not api_token_headers:
        print("ERROR: API token header missing")
        return False

    if api_token_headers != expected_token:
        print(f"ERROR: Invalid API token. Expected: {expected_token}, Got: {api_token_headers}")
        return False

    print("SUCCESS: Token validated")
    return True

def main(event, context):
    """
    Lambda function to process incoming events and send messages to SQS.
    
    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context in which the Lambda function is called.

    Returns:
        dict: A response object with status code and message.
    """

    # Validate API token
    headers = event.get("headers", {})

    if not validate_api_token(headers):
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "Unauthorized"})
        }

    # Parse body
    body = json.loads(event.get("body", "{}"))
    data = _get_data_from_body(body)

    # Send to SQS
    sqs_client = get_sqs_client()
    queue_url = os.environ.get("QUEUE_URL")
    task_id = str(uuid.uuid4())

   
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(data),
        MessageGroupId="tasks",
        MessageDeduplicationId=task_id,
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Message sent to SQS", "task_id": task_id})
    }



def _get_data_from_body(body: dict) -> dict:
    """
    Extracts data from the request body and sends it to SQS.

    Args:
        body (dict): The request body containing data.
    """

    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "payload": body.get("payload", {}),
        "description": body.get("description", ""),
        "priority": body.get("priority", "normal")
    }

    
