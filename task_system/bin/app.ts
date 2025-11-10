#!/usr/bin/env node

import * as cdk from 'aws-cdk-lib';
import { MessagingStack } from '../lib/stacks/messaging-stack.js';
import { ComputeStack } from '../lib/stacks/compute-stack.js';
import { ApiStack } from '../lib/stacks/api-stack.js';
import { getConfig } from '../lib/config/environment-config.js';


const app = new cdk.App();
const config = getConfig();

const messagingStack = new MessagingStack(app, 'MessagingStack', {
	queueName: config.queueName,
	dlqName: config.dlqName,
});

const computeStack = new ComputeStack(app, 'ComputeStack', {
	queue: messagingStack.queue,
	environment: config.environment,
	...(config.localstackEndpoint && { localstackEndpoint: config.localstackEndpoint, }),
});

const apiStack = new ApiStack(app, 'ApiStack', {
	apiHandler: computeStack.apiHandler,
	stageName: config.apiStageName,
});

computeStack.addDependency(messagingStack);
apiStack.addDependency(computeStack);

app.synth();


