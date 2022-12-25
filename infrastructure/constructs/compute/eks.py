from aws_cdk import (
    aws_eks as eks,
    aws_ec2 as ec2
)
from constructs import Construct
from ..networking.vpc import VPC


class EKS(Construct):
    def __init__(self, scope: Construct, id: str, *, vpc: VPC) -> None:
        super().__init__(scope, id)

        env_name = self.node.try_get_context("env")

        # Using spot instances and T2 micros to save on AWS costs
        # m5.large is probably suitable for real production workloads
        self.cluster = eks.Cluster(self, env_name,
                                   cluster_name=env_name,
                                   version=eks.KubernetesVersion.V1_24,
                                   vpc=vpc.vpc,
                                   default_capacity=0,
                                   default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
                                   default_capacity_instance=ec2.InstanceType.of(
                                       ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
                                   alb_controller=eks.AlbControllerOptions(
                                       version=eks.AlbControllerVersion.V2_4_1
                                   )
                                   )

        self.cluster.add_nodegroup_capacity("spot",
                                            instance_types=[
                                                ec2.InstanceType.of(ec2.InstanceClass.T2,
                                                                    ec2.InstanceSize.MICRO)
                                            ],
                                            min_size=2,
                                            max_size=2,
                                            desired_size=2
                                            )
