# Task Management API System

A serverless task management API system built with AWS CDK, deployable to both AWS and LocalStack for local development.

## Hello! 
This challenge was very interesting to work on. It is very interesting to see that it was allowed to use AI for help.
That is something very important, because almost every developer uses AI tools to help them with their daily tasks, so 
kudos for allowing it.

Some of the things that the AI helped me with were:
- Generating boilerplate code for CDK stacks:
  - I had experience with AWS Lambda before, but I have never used AWS CDK, so this was a great opportunity to learn it.
  - The AI helped me generate the initial code for the stacks, and then I modified it to fit the requirements.
- Integrating localstack with CDK:
  - I had some experience with LocalStack, but I was not sure how to integrate it with CDK.
  - The AI provided me with code snippets and explanations on how to do it.
- Writing some parts of the documentation.
- Troubleshooting some issues I encountered during development.
- Writing TS code, because I have more experience with Python, so the AI helped me with some TS syntax and best practices.

The way I use the AI is by asking specific questions and telling it to explain concepts to me, not to implement. In my 
opinion, the best way to learn is by doing and failing. I see many developers just asking the AI to implement everything for 
them, which could be faster but then the code is not really theirs. And when bugs appear, they don't know how to fix
them. Or when new features are requested, they don't know how to implement them. So I prefer to use the AI as a guide 
and a helper, not as a replacement for my own work.

The speed is important, but the quality and understanding of the code is more important. And I know it could be hard 
to see all the snippet there and click "Apply", but there is _no soul on that code_ . 

_"Failure is not the opposite of success; it's part of success."-Arianna Huffington_

## Notes:
- This project uses LocalStack because I used before for AWS services emulation. I haven't used it for sqs queues, but
it was a good opportunity to learn it.
- I used lambda functions before, which was in a very cool way:
  - We have a main app that when a User requested a heavy loaded operation, it would send the task to a Lambda Functions
    ( deployed in AWS ) that would process the tasks and post the result back to the main app through a webhook. With this, 
    the main app would have a status page where the user could see the status of their tasks.


## Architecture

- **API Gateway**: REST API with POST endpoint for task creation
- **Lambda Functions**:
  - API Handler (Python): Receives tasks and queues them
  - Task Processor (Python): Processes tasks from queue -> we can add more code here!
- **SQS FIFO Queue**: Ensures ordered task processing
- **CloudWatch**: Logging and monitoring

## Prerequisites

- Node.js 18+ and npm
- AWS CDK v2 (`npm install -g aws-cdk`)
- Docker and Docker Compose
- Python 3.11
- AWS CLI (optional, for AWS deployment)
- cdklocal (`npm install -g aws-cdk-local`) for LocalStack deployment

## LocalStack Setup

### 1. Start LocalStack

```bash
# Start LocalStack services
docker-compose up -d

# Check if LocalStack is healthy
docker-compose ps

# View LocalStack logs
docker-compose logs -f localstack
```

### 2. Verify LocalStack Health

```bash
curl http://localhost:4566/_localstack/health
```

You should see a JSON response with service statuses.

### 3. Install Dependencies

```bash
# Install CDK dependencies
npm install

# Install cdklocal (CDK wrapper for LocalStack)
npm install -g aws-cdk-local
```

## Deployment

### Deploy to LocalStack (Local Testing)

# update .env.local with your desired values. 

# Load environment variables
`source .env.local`

# Bootstrap CDK (only needed once)
`cdklocal bootstrap`

# Synthesize CloudFormation templates
`cdklocal synth`

# Deploy all stacks
`API_TOKEN=$API_TOKEN ENVIRONMENT=$ENVIRONMENT cdklocal deploy --all --require-approval never`

( setting the API_TOKEN and ENVIRONMENT variables is optional, but cdklocal might not read from .env.local sometimes )

# Check the URLS:
That command will output the API Gateway URL after deployment. I recommend you to store in a variable for easier testing, e.g.:
`export API_URL=https://ltfvqjux6x.execute-api.localhost.localstack.cloud:4566/local/`

# Send a testing request:
```bash
curl -X POST "${API_URL}/tasks" \
    -H "x-api-key: local-dev-token" \
    -H "Content-Type: application/json" \
    -d '{"title": "Test Task", "priority": "high"}' \
    --insecure
```

If you pass a wroing API key, you should get a 403 response.

# List the SQS queues to verify the queue was created:
`aws --endpoint-url=http://localhost:4566 --region us-east-1 sqs list-queues`


### Deploy to AWS (Production)

```bash
# Configure AWS credentials
aws configure

# Bootstrap CDK (only needed once per account/region)
cdk bootstrap

# Synthesize CloudFormation templates
cdk synth

# Deploy all stacks
cdk deploy --all
```


# Get queue attributes
QUEUE_URL=$(aws --endpoint-url=http://localhost:4566 sqs list-queues --query 'QueueUrls[0]' --output text)
aws --endpoint-url=http://localhost:4566 sqs get-queue-attributes --queue-url $QUEUE_URL --attribute-names All
```

### Check CloudWatch Logs

```bash
# List log groups
aws --endpoint-url=http://localhost:4566 logs describe-log-groups

# Get logs from Lambda function
aws --endpoint-url=http://localhost:4566 logs tail /aws/lambda/task-processor --follow
```

## Project Structure

```
task_system/
  ├── lib/                           # ← Infrastructure (TypeScript)
  │   ├── stacks/
  │   │   ├── messaging-stack.ts    # Creates SQS queues
  │   │   ├── compute-stack.ts      # Creates Lambda functions
  │   │   └── api-stack.ts          # Creates API Gateway
  │   └── config/
  │       └── environment-config.ts
  │
  ├── lambda/                        # ← Application code (Python)
  │   ├── api-handler/
  │   │   ├── handler.py            # Python code for API
  │   │   └── requirements.txt      # Python dependencies (boto3, etc.)
  │   └── task-processor/
  │       ├── handler.py            # Python code for processing
  │       └── requirements.txt
  │
  ├── bin/
  │   └── app.ts                    # CDK entry point
  ├── cdk.json
  ├── package.json                  # ← TypeScript/CDK dependencies
  └── tsconfig.json
```

## Helper Scripts

Create scripts in the `scripts/` directory:

- `deploy-local.sh`: Deploy to LocalStack
- `test-api.sh`: Test API endpoints
- `check-logs.sh`: View Lambda logs
- `cleanup.sh`: Remove all stacks

## Cleanup

### LocalStack

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (deletes persisted data)
docker-compose down -v

# Delete LocalStack data directory
rm -rf .localstack
```

### AWS

```bash
# Destroy all stacks
cdk destroy --all
```

## Environment Variables

LocalStack uses the following environment variables (see `.env.local`):

- `LOCALSTACK_ENDPOINT`: LocalStack endpoint URL
- `AWS_REGION`: AWS region for deployment
- `AWS_ACCOUNT_ID`: AWS account ID (000000000000 for LocalStack)
- `ENVIRONMENT`: Deployment environment (local/dev/prod)

### Running Tests
- Go to lambda/test and run 
```bash
./run_tests.sh
```
That script will spin up a docker container and run the tests inside it. I have also included a workflow action to run
the tests on every PR to main branch.

## Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [LocalStack Documentation](https://docs.localstack.cloud/)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
