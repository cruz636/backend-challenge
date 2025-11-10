// SQS queues 
import * as cdk from 'aws-cdk-lib';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';

export interface MessagingStackProps extends cdk.StackProps {
	queueName: string;
	dlqName: string;
}

export class MessagingStack extends cdk.Stack {
public readonly queue: sqs.Queue;
public readonly dlq: sqs.Queue;

constructor(scope: Construct, id: string, props: MessagingStackProps) {
	super(scope, id, props);

	// Dead Letter Queue
	this.dlq = new sqs.Queue(this, 'DeadLetterQueue', {
		queueName: props.dlqName,
		fifo: true,
		contentBasedDeduplication: true,
		retentionPeriod: cdk.Duration.days(14),
	});

	// Main FIFO queue
	this.queue = new sqs.Queue(this, 'MainQueue', {
		queueName: props.queueName,
		fifo: true,
		contentBasedDeduplication: true,
		retentionPeriod: cdk.Duration.days(4),
		deadLetterQueue: {
			maxReceiveCount: 3,
			queue: this.dlq,
		},
	});

	new cdk.CfnOutput(this, 'QueueURL', {value: this.queue.queueUrl});
	}
}
