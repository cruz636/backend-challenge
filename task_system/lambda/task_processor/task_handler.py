import json
import boto3
import os
from datetime import datetime, timedelta


def process(event, context):
    """
    Lamda handler for SQS messages.

    Args:
        event (dict): The event data from SQS.
        context (object): The runtime information of the Lambda function.

    Returns:
        dict: A response indicating success or failure.
    """

    print("Received event:", json.dumps(event, indent=2))

    for record in event["Records"]:
        try:
            message_body = json.loads(record["body"])

            # Task details
            task_id = message_body["task_id"]
            task_type = message_body["task_type"]
            description = message_body.get("description", "No description provided")
            priority = message_body.get("priority", "normal")
            created_at = message_body.get("created_at", datetime.utcnow().isoformat())

            print(f"Processing task {task_id}:")

            process_task(task_id, task_type, description, priority, created_at)

            print(f"Task {task_id} processed successfully.")

        except Exception as e:
            print(f"Error processing task due to: {str(e)}")
            raise

    return {"statusCode": 200, "body": json.dumps("Tasks processed successfully")}


def process_task(task_id, task_type, description, priority, created_at):
    """
    Process individual task based on its type.

    Args:
        task_id (str): The unique identifier for the task.
        task_type (str): The type of the task.
        description (str): Description of the task.
        priority (str): Priority level of the task.
        created_at (str): Timestamp when the task was created.
    """

    priority_function_map = {
        "high": handle_high_priority_task,
        "normal": handle_normal_priority_task,
        "low": handle_low_priority_task,
    }

    try:
        function_to_call = priority_function_map.get(priority)

    except KeyError:
        print(f"Unknown priority level: {priority}. Defaulting to normal.")
        function_to_call = handle_normal_priority_task

    function_to_call(task_id, task_type, description, created_at)


def handle_high_priority_task(task_id, task_type, description, created_at):
    print(
        f"[HIGH PRIORITY] Handling task {task_id} of type {task_type} created at {created_at}. Description: {description}"
    )


def handle_normal_priority_task(task_id, task_type, description, created_at):
    print(
        f"[NORMAL PRIORITY] Handling task {task_id} of type {task_type} created at {created_at}. Description: {description}"
    )


def handle_low_priority_task(task_id, task_type, description, created_at):
    print(
        f"[LOW PRIORITY] Handling task {task_id} of type {task_type} created at {created_at}. Description: {description}"
    )
