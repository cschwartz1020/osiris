from aws_cdk import aws_ec2 as ec2, CfnTag as tag
from constructs import Construct
from networking.vpc import VPC


class Bastion(Construct):
    def __init__(
        self, scope: Construct, id: str, *, Vpc: VPC, dmz_subnets: ec2.SubnetSelection
    ) -> None:
        super().__init__()

        env_name = self.node.try_get_context("env")

        key_pair = ec2.CfnKeyPair(
            self, f"bastion-{env_name}-keypair", key_name=f"bastion-{env_name}"
        )

        launch_template = ec2.CfnLaunchTemplate(
            self,
            f"bastion-{env_name}-lt",
            launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                instance_type="t2.micro",
                key_name=key_pair.key_name,
                tag_specifications=[
                    ec2.CfnLaunchTemplate.TagSpecificationProperty(
                        resource_type="instance",
                        tags=[tag(key="Name", value=f"bastion-{env_name}")],
                    )
                ],
            ),
            launch_template_name=f"bastion-{env_name}",
        )
