import boto3

ec2_c = boto3.client('ec2')
mysecurity_id = 'sg-044b584bd3b19477c'
ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpProtocol='tcp', FromPort=80, ToPort=80, CidrIp='0.0.0.0/0')
ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpPermissions=[{'FromPort':80, 'ToPort':80, 'IpProtocol': 'tcp', 'Ipv6Ranges':[{'CidrIpv6':'::/0'}]}])
ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpProtocol='udp', FromPort=10110, ToPort=10110, CidrIp='0.0.0.0/0')
ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpPermissions=[{'FromPort': 10110, 'ToPort': 10110, 'IpProtocol': 'udp', 'Ipv6Ranges':[{'CidrIpv6':'::/0'}]}])
ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpProtocol='-1', CidrIp='172.16.0.0/16')
