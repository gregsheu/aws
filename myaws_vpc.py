import boto3
import json 
import requests

client = boto3.client('ec2')
mysubnets = []
custom_route_table_id = ''
mysecurity_id = ''
resp = client.create_vpc(CidrBlock='172.16.0.0/16')
myvpc_id = resp['Vpc']['VpcId']
myvpc_name = 'myawsvpc'
client.create_tags(Resources=[myvpc_id], Tags=[{'Key': 'Name', 'Value': myvpc_name}])
for i in range(0, 2):
    resp = client.create_subnet(VpcId=myvpc_id, CidrBlock='172.16.' + str(i) + '.0/24', AvailabilityZone='us-east-2b')
    mysubnets.append(resp['Subnet']['SubnetId'])
    if i == 0:
        client.create_tags(Resources=[mysubnets[i]], Tags=[{'Key': 'Name', 'Value': myvpc_name + '_public_subnet'}])
    else:
        client.create_tags(Resources=[mysubnets[i]], Tags=[{'Key': 'Name', 'Value': myvpc_name + '_private_subnet'}])
print(mysubnets)
vpc = boto3.resource('ec2').Vpc(myvpc_id)
for r in vpc.route_tables.all():
    custom_route_table_id = r.route_table_id

for s in vpc.security_groups.all():
    mysecurity_id = s.group_id
response = requests.get('http://jsonip.com/') 
myip = response.json()['ip']
client.authorize_security_group_ingress(GroupId=mysecurity_id, IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp=myip + '/32')

#We associate public subnet to default route table
client.create_tags(Resources=[custom_route_table_id], Tags=[{'Key': 'Name', 'Value': myvpc_name + '_custom_route'}])
client.associate_route_table(SubnetId=mysubnets[0], RouteTableId=custom_route_table_id)

#We need to have an internet gateway for our VPC
resp = client.create_internet_gateway()
igw_id = resp['InternetGateway']['InternetGatewayId']
client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=myvpc_id)
client.create_route(RouteTableId=custom_route_table_id, DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)

#We need to create second route table
resp = client.create_route_table(VpcId=myvpc_id)
main_route_table_id = resp['RouteTable']['RouteTableId']
client.create_tags(Resources=[main_route_table_id], Tags=[{'Key': 'Name', 'Value': myvpc_name + '_main_route'}])
client.associate_route_table(SubnetId=mysubnets[1], RouteTableId=main_route_table_id)

#Now we are getting the NAT id to create in public subnet
resp = client.describe_images(Owners=['amazon'], Filters=[{'Name': 'owner-alias', 'Values': ['amazon']}, {'Name': 'name', 'Values': ['amzn-ami-vpc-nat*']}, {'Name': 'is-public', 'Values': ['true']}, {'Name': 'virtualization-type', 'Values': ['hvm']}])
nat_image_id = resp['Images'][0]['ImageId']
print(nat_image_id)
 
resp = client.run_instances(ImageId=nat_image_id, InstanceType='t2.small', KeyName='greg', MinCount=1, MaxCount=1, SubnetId=mysubnets[0])
nat_instance_id = resp['Instances'][0]['InstanceId']
nat_interface_id = resp['Instances'][0]['NetworkInterfaces'][0]['NetworkInterfaceId']
resp = client.allocate_address(Domain='vpc')
nat_public_ip = resp['PublicIp']
nat_allocation_id = resp['AllocationId']
#We need waiter to wait for the NAT instance running. 
waiter = client.get_waiter('instance_status_ok')
waiter.wait(InstanceIds=[nat_instance_id], Filters=[{'Name': 'instance-state-name', 'Values': ['running']}], WaiterConfig={'Delay': 60, 'MaxAttempts': 60})
print('Waiting for NAT instance to be running')
client.create_tags(Resources=[nat_instance_id], Tags=[{'Key': 'Name', 'Value': 'myawsnat'}])
print('Running now')
client.modify_instance_attribute(InstanceId=nat_instance_id, SourceDestCheck={'Value': False})
client.associate_address(InstanceId=nat_instance_id, PublicIp=nat_public_ip)
client.create_route(RouteTableId=main_route_table_id, DestinationCidrBlock='0.0.0.0/0', InstanceId=nat_instance_id)
print('NAT public IP is %s' % nat_public_ip)
