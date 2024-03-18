"""
This Lambda function retrieves model IDs from Amazon Bedrock, saves them to Amazon DynamoDB,
and sends a notification via Amazon SNS if new models are found.
"""
import json
from logging import getLogger
from typing import List, Dict, Any
import os
import boto3
from botocore.exceptions import ClientError

account_id = boto3.client("sts").get_caller_identity()["Account"]
bedrock = boto3.client('bedrock')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])
sns = boto3.client('sns')
topic_name = os.environ['TOPIC_NAME']
region = os.environ["AWS_REGION"]

logger = getLogger()

def fetch_model_ids() -> List[str]:
    """
    Retrieves a list of model IDs from Amazon Bedrock.

    Returns:
        List[str]: A list of retrieved model IDs.
    """
    try:
        response = bedrock.list_foundation_models()
        return [item['modelId'] for item in response['modelSummaries']]
    except ClientError as e:
        log_and_raise_error(e)

def fetch_previous_model_ids() -> List[str]:
    """
    Retrieves a list of model IDs previously fetched, from DynamoDB.

    Returns:
        List[str]: A list of model IDs. Returns an empty list if the item does not exist.
    """
    try:
        response = table.get_item(Key={'id': 'models_list'})
        if 'Item' in response:
            return response['Item']['models']
        else:
            return []
    except ClientError as e:
        log_and_raise_error(e)

def update_model_ids_in_dynamodb(model_ids: List[str]) -> None:
    """
    Saves the latest list of model IDs to DynamoDB.

    Args:
        model_ids (List[str]): The list of model IDs to be saved.
    """
    try:
        table.put_item(Item={'id': 'models_list', 'models': model_ids})
    except ClientError as e:
        log_and_raise_error(e)

def send_notification(new_models: List[str]) -> None:
    """
    Sends a notification via SNS if new models are found.

    Args:
        new_models (List[str]): A list of new model IDs.
    """
    message = {
        "version": "1.0",
        "source": "custom",
        "content": {
            "textType": "client-markdown",
            "title": f":tada: Amazon Bedrock に新しいモデルが追加されました!! Region: {region}",
            "description": '\n'.join(new_models),
            "nextSteps": [
                "宇宙最速を目指そう:rocket: ",
                f'''Go to <https://{region}.console.aws.amazon.com/bedrock/home?region={
                    region}#/modelaccess|*Model Access*>'''
            ]
        }
    }
    try:
        sns.publish(
            TopicArn=f"arn:aws:sns:{region}:{account_id}:{topic_name}",
            Message=json.dumps(message)
        )
    except ClientError as e:
        log_and_raise_error(e)

def log_and_raise_error(e):
    """
    Logs the error message and re-raises the error.

    Args:
        e (ClientError): The encountered client error.
    """
    error_message = e.response['Error']['Message']
    logger.error(error_message)
    raise

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    The entry point for the Lambda function. Retrieves new model IDs, saves them to DynamoDB,
    and sends a notification if necessary.

    Args:
        event (Dict[str, Any]): The event data passed to the Lambda function.
        context (Any): The execution context of the Lambda function.

    Returns:
        Dict[str, Any]: A dictionary containing the result of the operation.
    """
    logger.debug(event)
    model_ids = fetch_model_ids()
    previous_model_ids = fetch_previous_model_ids()
    new_models = list(set(model_ids) - set(previous_model_ids))

    if new_models:
        logger.info("New models found: %s", new_models)
        update_model_ids_in_dynamodb(model_ids)
        send_notification(new_models)

        return {
            'statusCode': 200,
            'body': json.dumps('New models found!')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('No additional models.')
    }
