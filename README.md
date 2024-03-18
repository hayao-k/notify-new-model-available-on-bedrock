# Notify New Model Available on Bedrock

This repository contains the AWS SAM (Serverless Application Model) template for deploying a serverless application designed to notify users when new models become available on Bedrock. The application uses AWS services such as Lambda, DynamoDB, EventBridge, and SNS to perform its operations.

## Overview
The application periodically checks for new models available on Bedrock and notifies subscribers through an SNS topic. It leverages DynamoDB for storing model information, Lambda for processing the data, EventBridge for scheduling checks, and SNS for sending notifications.

![](https://raw.githubusercontent.com/hayao-k/notify-new-model-available-on-bedrock/main/images/architecture.png)

It is assumed that the SNS Topic and AWS Chatbot for notification have already been created and configured.

## Prerequisites

Before deploying this application, ensure you have the following:

- SAM CLI installed
- SNS Topic for AWS Chatbot created & configured
- AWS Chatbot configured

## Deployment

To deploy this application:

   ```bash
   git clone https://github.com/hayao-k/notify-new-model-available-on-bedrock.git
   cd notify-new-model-available-on-bedrock
   sam deploy --guided 
   ```

Follow the prompts in the deployment process to set up the application.

## Parameters

The template accepts the following parameters:

- `pTopicName`: The name of the SNS topic for notifications. Default is "AWSChatbot-Topic".
- `pRateMinute`: Rate in minutes to set in the EventBridge scheduler for checking new models. Default is "5".

## Resources

The following resources are created by this template:

- **DynamoDB Table**: Stores information about the models.
- **Lambda Function**: Checks for new models and sends notifications.
- **EventBridge Schedule**: Triggers the Lambda function based on the specified schedule.
- **Log Group**: Captures logs from the Lambda function.
- **IAM Role**: Roles for Lambda execution and EventBridge Scheduler


## Cleanup

To delete the application and its resources:

1. Run the following command:

   ```bash
   sam delete
   ```

2. Follow the prompts to confirm deletion.
