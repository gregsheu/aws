import boto3 
import requests
import json
import time
#09272020 is working
myvpc_id = 'vpc-0601ec24b1edccebd'
mynat_tag = 'myawsnat'
response = requests.get('http://jsonip.com/') 
myip = response.json()['ip']
ec2 = boto3.resource('ec2')
myawsvpc = ec2.Vpc(myvpc_id)
client = boto3.client('ec2')
resp = client.describe_instances(Filters=[{'Name': 'tag:name', 'Values': [mynat_tag], 'Name': 'vpc-id', 'Values': [myvpc_id]}])
nat_instance_id = resp['Reservations'][0]['Instances'][0]['InstanceId']
nat_instance_publicip = resp['Reservations'][0]['Instances'][0]['PublicIpAddress']
resp = client.describe_addresses(PublicIps=[nat_instance_publicip])
nat_instance_allocationid = resp['Addresses'][0]['AllocationId']
nat_instance_associationid = resp['Addresses'][0]['AssociationId']
#not_main_route_table_id = ''
for r in myawsvpc.route_tables.all():
    print(r.route_table_id)
    resp = client.describe_route_tables(RouteTableIds=[r.route_table_id], Filters=[{'Name': 'association.main', 'Values': ['false']}])
    if not resp['RouteTables'][0]['Associations'][0]['Main']:
        not_main_route_table_id = resp['RouteTables'][0]['RouteTableId']
print(nat_instance_associationid)
print(nat_instance_allocationid)
print(not_main_route_table_id)
print('Deleting NAT Instance')
client.terminate_instances(InstanceIds=[nat_instance_id])
print('Waiting for NAT instance to be deleted')
waiter = client.get_waiter('instance_terminated')
waiter.wait(InstanceIds=[nat_instance_id], Filters=[{'Name': 'instance-state-name', 'Values': ['terminated']}], WaiterConfig={'Delay': 30, 'MaxAttempts': 3})
print('Releasing Elastic IP %s' % nat_instance_publicip)
client.release_address(AllocationId=nat_instance_allocationid)
for i in myawsvpc.internet_gateways.all():
    myawsvpc.detach_internet_gateway(InternetGatewayId=i.internet_gateway_id, VpcId=myvpc_id)
    client.delete_internet_gateway(InternetGatewayId=i.internet_gateway_id)
#for s in myawsvpc.security_groups.all():
#    #client.revoke_security_group_ingress(GroupId=s.group_id, IpProtocol='-1', FromPort=-1, ToPort=-1, SourceSecurityGroupName='sg-0ec34cd6015f5e75f(default)')
#    client.revoke_security_group_ingress(GroupId=s.group_id, IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp=myip + '/32')
#    client.delete_security_group(GroupId=s.group_id)
for s in myawsvpc.subnets.all():
    client.delete_subnet(SubnetId=s.subnet_id)
for r in myawsvpc.route_tables.all():
    #resp = client.describe_route_tables(Filters=[{'Name': 'association.main', 'Values': ['false']}])
    #not_main_route_table_id = resp['RouteTables'][0]['Associations'][0]['RouteTableId']
    #resp = client.describe_route_tables(RouteTableIds=[r.route_table_id])
    #print(resp)
    #association_id = resp['RouteTables'][0]['Associations'][0]['RouteTableAssociationId']
    #print(association_id)
    #client.disassociate_route_table(AssociationId=association_id)
    client.delete_route(RouteTableId=r.route_table_id, DestinationCidrBlock='0.0.0.0/0')
    #if not_main_route_table_id:
        #client.delete_route_table(RouteTableId=r.route_table_id)
client.delete_route_table(RouteTableId=not_main_route_table_id)
myawsvpc.delete()
print('Done')
