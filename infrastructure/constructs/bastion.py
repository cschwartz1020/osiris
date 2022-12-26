from aws_cdk import aws_ec2 as ec2, CfnTag as tag, aws_autoscaling as autoscaling
from constructs import Construct
from .networking.vpc import VPC


class Bastion(Construct):
    def __init__(
        self, scope: Construct, id: str, *, Vpc: VPC, dmz_subnets: ec2.SubnetSelection
    ) -> None:
        super().__init__(scope, id)

        env_name = self.node.try_get_context("env")
        allow_ip = self.node.try_get_context("ip")

        key_pair = ec2.CfnKeyPair(
            self, f"bastion-{env_name}-keypair", key_name=f"bastion-{env_name}"
        )

        self.bastion_security_group = ec2.SecurityGroup(
            self,
            f"bastion-{env_name}-sg",
            vpc=Vpc.vpc,
            security_group_name=f"bastion-{env_name}-sg",
        )

        self.bastion_security_group.add_ingress_rule(
            ec2.Peer.ipv4(f"{allow_ip}/32"), ec2.Port.tcp(22)
        )

        bastion_launch_template = ec2.CfnLaunchTemplate(
            self,
            f"bastion-{env_name}-lt",
            launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                instance_type="t2.micro",
                key_name=key_pair.key_name,
                security_group_ids=[self.bastion_security_group.security_group_id],
                instance_market_options=ec2.CfnLaunchTemplate.InstanceMarketOptionsProperty(
                    market_type="spot"
                ),
                image_id=ec2.MachineImage.latest_amazon_linux()
                .get_image(self)
                .image_id,
                tag_specifications=[
                    ec2.CfnLaunchTemplate.TagSpecificationProperty(
                        resource_type="instance",
                        tags=[tag(key="Name", value=f"bastion-{env_name}")],
                    )
                ],
            ),
            launch_template_name=f"bastion-{env_name}",
        )

        bastion_launch_template_asg_specification_property = (
            autoscaling.CfnAutoScalingGroup.LaunchTemplateSpecificationProperty(
                launch_template_id=bastion_launch_template.ref,
                version=bastion_launch_template.attr_latest_version_number,
            )
        )

        autoscaling.CfnAutoScalingGroup(
            self,
            f"bastion-{env_name}-asg",
            auto_scaling_group_name="bastion-{env_name}-asg",
            launch_template=bastion_launch_template_asg_specification_property,
            vpc_zone_identifier=dmz_subnets.subnets,
            desired_capacity="1",
            max_size="1",
            min_size="1",
            availability_zones=dmz_subnets.availability_zones,
        )
