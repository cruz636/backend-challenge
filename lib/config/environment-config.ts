export interface EnvironmentConfig {
    // Environment identifier
    environment: 'local' | 'dev' | 'prod';

    // AWS Configuration
    region: string;
    account?: string;

    // SQS Configuration
    queueName: string;
    dlqName: string;

    // Lambda Configuration
    lambdaRuntime: string;
    apiHandlerTimeout: number;
    taskProcessorTimeout: number;

    // API Configuration
    apiStageName: string;

    // LocalStack specific
    localstackEndpoint?: string;
  }

  export function getConfig(): EnvironmentConfig {
    const env = process.env.ENVIRONMENT || 'aws';

    const baseConfig = {
      region: process.env.AWS_REGION || 'us-east-1',
      queueName: 'task-queue.fifo',
      dlqName: 'task-dlq.fifo',
      lambdaRuntime: 'python3.11',
      apiHandlerTimeout: 30,
      taskProcessorTimeout: 60,
      apiStageName: env === 'local' ? 'local' : 'prod',
    };

	// Using localstack configuration for local environment
    if (env === 'local') {
      return {
        ...baseConfig,
        environment: 'local',
        localstackEndpoint: 'http://localstack:4566',
        account: '000000000000',
      };
    }

	const awsAccount = process.env.CDK_DEFAULT_ACCOUNT;
    return {
      ...baseConfig,
      environment: 'dev',
      ...(awsAccount && { account: awsAccount, }),
    };
  }
