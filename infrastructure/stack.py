from constructs import Construct
import aws_cdk as cdk
from .constructs.networking.vpc import VPC
from .constructs.compute.eks import EKS
from .constructs.bastion import Bastion
from typing import Any


class Infrastructure(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        stack_id_: str,
        **kwargs: Any,
    ):
        super().__init__(scope, stack_id_, **kwargs)

        Vpc = VPC(self, "Vpc")

        dmz_subnets = self.get_dmz_subnets(Vpc)

        bastion = Bastion(self, "Bastion", Vpc=Vpc, dmz_subnets=dmz_subnets)

        bastion_security_group = bastion.bastion_security_group

        app_subnets = self.get_app_subnets(Vpc)

        EKS(
            self,
            "Eks",
            Vpc=Vpc,
            app_subnets=app_subnets,
            dmz_subnets=dmz_subnets,
            allow_security_group=bastion_security_group,
        )

    def get_app_subnets(self, Vpc: VPC):
        return cdk.aws_ec2.SubnetSelection(
            subnet_type=cdk.aws_ec2.SubnetType.PRIVATE_WITH_EGRESS
        )

    def get_dmz_subnets(self, Vpc: VPC):
        return cdk.aws_ec2.SubnetSelection(subnet_type=cdk.aws_ec2.SubnetType.PUBLIC)
