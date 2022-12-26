from aws_cdk import aws_eks as eks, aws_ec2 as ec2, aws_iam as iam, CfnTag as tag
from constructs import Construct
from ..networking.vpc import VPC


class EKS(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        Vpc: VPC,
        app_subnets: ec2.SubnetSelection,
        allow_security_group: ec2.SecurityGroup,
    ) -> None:
        super().__init__(scope, id)

        env_name = self.node.try_get_context("env")

        # Using spot instances and T2 micros to save on AWS costs
        # m5.large is probably suitable for real production workloads
        self.cluster = eks.Cluster(
            self,
            env_name,
            cluster_name=env_name,
            version=eks.KubernetesVersion.V1_23,
            vpc=Vpc.vpc,
            default_capacity=0,
            default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
            default_capacity_instance=ec2.InstanceType.of(
                ec2.InstanceClass.T2, ec2.InstanceSize.MICRO
            ),
            alb_controller=eks.AlbControllerOptions(
                version=eks.AlbControllerVersion.V2_4_1
            ),
        )

        key_pair = ec2.CfnKeyPair(
            self, f"k8s-{env_name}-keypair", key_name=f"k8s-{env_name}"
        )

        k8s_security_group = ec2.SecurityGroup(
            self,
            f"k8s-{env_name}-sg",
            vpc=Vpc.vpc,
            security_group_name=f"k8s-{env_name}-sg",
        )

        k8s_security_group.add_ingress_rule(
            ec2.Peer.security_group_id(allow_security_group.security_group_id),
            ec2.Port.tcp(22),
        )

        launch_template = ec2.CfnLaunchTemplate(
            self,
            f"k8s-{env_name}-lt",
            launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                instance_type="t2.micro",
                key_name=key_pair.key_name,
                security_group_ids=[k8s_security_group.security_group_id],
                tag_specifications=[
                    ec2.CfnLaunchTemplate.TagSpecificationProperty(
                        resource_type="instance",
                        tags=[tag(key="Name", value=f"k8s-{env_name}")],
                    )
                ],
            ),
            launch_template_name=f"k8s-{env_name}",
        )

        self.cluster.add_nodegroup_capacity(
            "spot",
            min_size=2,
            max_size=2,
            desired_size=2,
            nodegroup_name=f"spot-{env_name}",
            capacity_type=eks.CapacityType.SPOT,
            launch_template_spec=eks.LaunchTemplateSpec(
                id=launch_template.ref,
                version=launch_template.attr_latest_version_number,
            ),
            subnets=app_subnets,
        )
        admin_user = iam.User.from_user_name(self, "User", "adminUser")
        self.cluster.aws_auth.add_user_mapping(admin_user, groups=["system:masters"])
