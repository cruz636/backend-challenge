// Lambda functions
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as LambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import { Construct } from 'constructs';


export interface ComputeStackProps extends cdk.StackProps {
	queue: sqs.Queue;
	environment: string;
	localstackEndpoint?: string;
}

export class ComputeStack extends cdk.Stack {
	public readonly apiHandler: lambda.Function;
	public readonly taskProcessor: lambda.Function;

	constructor(scope: Construct, id: string, props: ComputeStackProps) {
		super(scope, id, props);

		// API handler Lambda Function
		this.apiHandler = new lambda.Function(this, 'ApiHandlerFunction', {
			runtime: lambda.Runtime.PYTHON_3_11,
			handler: 'handler.main',
			code: lambda.Code.fromAsset('lambda/api_handler'),
			environment: {
				ENVIRONMENT: props.environment,
				QUEUE_URL: props.queue.queueUrl,
				LOCALSTACK_ENDPOINT: props.localstackEndpoint || '',
				API_TOKEN: process.env.API_TOKEN || 'default_token',
			},
			timeout: cdk.Duration.seconds(30),
		});

		// Task processor Lambda Function
		this.taskProcessor = new lambda.Function(this, 'TaskProcessorFunction', {
			runtime: lambda.Runtime.PYTHON_3_11,
			handler: 'processor.main',
			code: lambda.Code.fromAsset('lambda/task_processor'),
			environment: {
				ENVIRONMENT: props.environment,
				LOCALSTACK_ENDPOINT: props.localstackEndpoint || '',
			},
			timeout: cdk.Duration.seconds(60),
		});

		// Event source mapping
		new LambdaEventSources.SqsEventSource(props.queue, {
			batchSize: 1,
		}).bind(this.taskProcessor);

		// Grant permissions
        props.queue.grantSendMessages(this.apiHandler);
		props.queue.grantConsumeMessages(this.taskProcessor);
	


		}
}
