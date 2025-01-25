"""An AWS Python Pulumi program"""

import json
import pulumi
import pulumi_aws as aws
import pulumi_aws_apigateway as apigateway

basic_dynamodb_table = aws.dynamodb.Table(
    "basic-dynamodb-table",
    name="URLS",
    billing_mode="PROVISIONED",
    read_capacity=5,
    write_capacity=5,
    stream_enabled=True,
    stream_view_type="NEW_IMAGE",
    hash_key="shortcode",
    attributes=[
        {
            "name": "shortcode",
            "type": "S",
        },
    ]
)

# An execution role to use for the Lambda function.
role = aws.iam.Role(
    "role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com",
                    },
                }
            ],
        }
    ),
    managed_policy_arns=[aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE, aws.iam.ManagedPolicy.AMAZON_DYNAMO_DB_FULL_ACCESS],
)

# A Lambda function to invoke.
handler = aws.lambda_.Function(
    "my-function",
    runtime="python3.13",
    handler="store.lambda_handler",
    role=role.arn,
    code=pulumi.FileArchive("./store.py.zip"),
)

# A REST API to route requests to the Lambda function.
api = apigateway.RestAPI(
    "api",
    apigateway.RestAPIArgs(
        api_key_source=apigateway.APIKeySource.HEADER,
        routes=[
            apigateway.RouteArgs(
                path="/",
                method=apigateway.Method.PUT,
                content_type="application/json",
                event_handler=handler,
                api_key_required=True,
            ),
            apigateway.RouteArgs(
                path="/",
                method=apigateway.Method.POST,
                content_type="application/json",
                event_handler=handler,
                api_key_required=True,
            ),
            apigateway.RouteArgs(
                path="/",
                method=apigateway.Method.OPTIONS,
                content_type="application/json",
                event_handler=handler,
                api_key_required=False,
            ),
        ]
    ),
    binary_media_types=""
)

key = aws.apigateway.ApiKey("key")

plan = aws.apigateway.UsagePlan("plan", aws.apigateway.UsagePlanArgs(
    api_stages=[
        aws.apigateway.UsagePlanApiStageArgs(
            api_id=api.api.id,
            stage=api.stage.stage_name,
        ),
    ],
))

plan_key = aws.apigateway.UsagePlanKey("plan-key", aws.apigateway.UsagePlanKeyArgs(
    key_id=key.id,
    key_type="API_KEY",
    usage_plan_id=plan.id,
))

# The URL at which the REST API will be served.
pulumi.export("url", api.url)

# The API key for the REST API.
pulumi.export("key", key.value)
