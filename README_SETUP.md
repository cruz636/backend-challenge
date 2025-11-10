# Task Management API System

A serverless task management API system built with AWS CDK, deployable to both AWS and LocalStack for local development.

## Architecture

- **API Gateway**: REST API with POST endpoint for task creation
- **Lambda Functions**:
  - API Handler (Python): Receives tasks and queues them
  - Task Processor (Python): Processes tasks from queue
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

```bash
# Load environment variables
source .env.local

# Bootstrap CDK (only needed once)
cdklocal bootstrap

# Synthesize CloudFormation templates
cdklocal synth

# Deploy all stacks
cdklocal deploy --all --require-approval never

# Get API endpoint
aws --endpoint-url=http://localhost:4566 apigateway get-rest-apis
```

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

## Testing the API

### Test with LocalStack

```bash
# Get the API endpoint
API_ID=$(aws --endpoint-url=http://localhost:4566 apigateway get-rest-apis --query 'items[0].id' --output text)
API_URL="http://localhost:4566/restapis/${API_ID}/local/_user_request_"

# Create a task
curl -X POST "${API_URL}/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "This is a test task",
    "priority": "high"
  }'
```

### Check SQS Queue

```bash
# List queues
aws --endpoint-url=http://localhost:4566 sqs list-queues

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

## Troubleshooting

### LocalStack not starting

- Ensure Docker is running
- Check Docker daemon socket permissions
- View logs: `docker-compose logs localstack`

### Lambda not executing

- Check Lambda logs in CloudWatch
- Verify Lambda has correct IAM permissions
- Ensure SQS event source mapping is configured

### API Gateway not responding

- Verify API is deployed: `cdklocal deploy`
- Check API Gateway endpoint URL
- Review API Gateway logs in CloudWatch

## Development

### Adding New Features

1. Create/modify stacks in `lib/stacks/`
2. Add Lambda code in `lambda/`
3. Test with LocalStack: `cdklocal deploy`
4. Validate for AWS: `cdk synth`

### Running Tests

```bash
# Run CDK tests
npm test

# Test Lambda functions locally
cd lambda/api-handler && python -m pytest
```

## Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [LocalStack Documentation](https://docs.localstack.cloud/)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
