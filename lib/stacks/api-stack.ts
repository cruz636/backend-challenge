// API Gateway
import * as cdk from 'aws-cdk-lib';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export interface ApiStackProps extends cdk.StackProps {
	apiHandler: lambda.Function;
	stageName: string;
}

export class ApiStack extends cdk.Stack {
	public readonly api: apigateway.RestApi;
	
	constructor(scope: Construct, id: string, props: ApiStackProps) {
		super(scope, id, props);

		// API Gateway REST API 
		this.api = new apigateway.RestApi(
			this, 
			'ApiGateway', 
			{
				restApiName: 'Task API',
				description: 'API Gateway for task submission',
				deployOptions: {
					stageName: props.stageName,
					metricsEnabled: true,
				},
			}
		);

		// Task resource  
		const tasks = this.api.root.addResource('tasks');

		tasks.addMethod('POST', new apigateway.LambdaIntegration(props.apiHandler));

		// Output API URL
		new cdk.CfnOutput(this, 'ApiUrl', {
			value: this.api.url,
		});
	}
}
