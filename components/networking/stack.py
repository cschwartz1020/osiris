from constructs import Construct
import aws_cdk as cdk
from .constructs.infrastructure import VPC
from typing import Any


class Networking(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        stack_id_: str,
        **kwargs: Any,
    ):
        super().__init__(scope, stack_id_, **kwargs)

        vpc = VPC(self, "Vpc")
