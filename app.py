#!/usr/bin/env python3
import os
import aws_cdk as cdk
from components.networking.stack import Networking
import constants


app = cdk.App()
env_name = app.node.try_get_context("env")
if not env_name:
    raise Exception(
        "Environment not passed into context... Add -c env=<environment> to your CDK command")

Networking(
    app,
    f'{constants.APP_NAME}-{env_name}',
    env=cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    )
)

app.synth()
