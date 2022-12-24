from aws_cdk import (
    aws_ec2 as ec2,
    aws_ssm as ssm
)
from constructs import Construct


class VPC(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        env_name = self.node.try_get_context("env")

        self.vpc = ec2.Vpc(self, env_name,
                           ip_addresses=ec2.IpAddresses.cidr(
                               '192.168.50.0/24'),
                           max_azs=2,
                           enable_dns_hostnames=True,
                           enable_dns_support=True,
                           subnet_configuration=[
                               ec2.SubnetConfiguration(
                                   name='Public-Subnet',
                                   subnet_type=ec2.SubnetType.PUBLIC,
                                   cidr_mask=26
                               ),
                               ec2.SubnetConfiguration(
                                   name='Private-Subnet',
                                   subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                                   cidr_mask=26
                               )
                           ],
                           nat_gateways=1,
                           )

        priv_subnets = [
            subnet.subnet_id for subnet in self.vpc.private_subnets]

        count = 1
        for psub in priv_subnets:
            ssm.StringParameter(self, 'private-subnet-' + str(count),
                                string_value=psub,
                                parameter_name='/'+env_name +
                                '/private-subnet-'+str(count)
                                )
            count += 1
