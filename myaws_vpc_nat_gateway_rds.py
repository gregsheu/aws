import json
import requests
import time
import boto3

def create_myvpc(myvpcname, region, cidr):
    print('Creating VPC...')
    ec2_c = boto3.client('ec2')
    resp = ec2_c.create_vpc(CidrBlock=cidr)
    myvpcid = resp['Vpc']['VpcId']
    ec2_c.create_tags(Resources=[myvpcid], Tags=[{'Key': 'Name', 'Value': myvpcname}])
    #We need to enable dns support for endpoint
    ec2_c.modify_vpc_attribute(EnableDnsHostnames={'Value': True}, VpcId=myvpcid)
    ec2_c.modify_vpc_attribute(EnableDnsSupport={'Value': True}, VpcId=myvpcid)
    print('VPC %s created' % myvpcid)
    return myvpcid

def create_mysubnet(myvpcid, myvpcname):
    azs = []
    mysubnets = []
    ec2_c = boto3.client('ec2')
    resp = ec2_c.describe_availability_zones()
    for a in resp['AvailabilityZones']:
        azs.append(a['ZoneName'])
    #Creating public subnets
    for i in range(0, len(azs)):
        resp = ec2_c.create_subnet(VpcId=myvpcid, CidrBlock='172.16.4' + str(i) + '.0/24', AvailabilityZone=azs[i])
        mysubnets.append(resp['Subnet']['SubnetId'])
        time.sleep(1)
        ec2_c.create_tags(Resources=[mysubnets[i]], Tags=[{'Key': 'Name', 'Value': myvpcname + 'PublicSubnet' + azs[i][-1].upper()}])
        ec2_c.modify_subnet_attribute(SubnetId=mysubnets[i], MapPublicIpOnLaunch={'Value': True})
    #Creating private subnets
    for i in range(0, len(azs)):
        resp = ec2_c.create_subnet(VpcId=myvpcid, CidrBlock='172.16.4' + str(i+len(azs)) + '.0/24', AvailabilityZone=azs[i])
        mysubnets.append(resp['Subnet']['SubnetId'])
        time.sleep(1)
        ec2_c.create_tags(Resources=[mysubnets[i+len(azs)]], Tags=[{'Key': 'Name', 'Value': myvpcname + 'PrivateSubnet' + azs[i][-1].upper()}])
    return mysubnets

def create_myroute_tables(myvpcid, myvpcname, mysubnets):
    print('Creating 2nd Routetable...')
    ec2_c = boto3.client('ec2')
    vpc = boto3.resource('ec2').Vpc(myvpcid)
    for r in vpc.route_tables.all():
        main_route_table_id = r.route_table_id
    #We associate public subnet to default route table
    ec2_c.create_tags(Resources=[main_route_table_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'MainRoute'}])
    for i in range(0, int(len(mysubnets)/2)):
        ec2_c.associate_route_table(SubnetId=mysubnets[i], RouteTableId=main_route_table_id)
    #We need to create second route table
    resp = ec2_c.create_route_table(VpcId=myvpcid)
    custom_route_table_id = resp['RouteTable']['RouteTableId']
    ec2_c.create_tags(Resources=[custom_route_table_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'CustomRoute'}])
    for i in range(int(len(mysubnets)/2), len(mysubnets)):
        ec2_c.associate_route_table(SubnetId=mysubnets[i], RouteTableId=custom_route_table_id)
    return main_route_table_id, custom_route_table_id

def create_myigw(myvpcid, myvpcname, main_route_table_id):
    print('Creating Internet gateway...')
    #We need to have an internet gateway for our VPC
    ec2_c = boto3.client('ec2')
    resp = ec2_c.create_internet_gateway()
    igwid = resp['InternetGateway']['InternetGatewayId']
    ec2_c.create_tags(Resources=[igwid], Tags=[{'Key': 'Name', 'Value': myvpcname + 'IGW'}])
    ec2_c.attach_internet_gateway(InternetGatewayId=igwid, VpcId=myvpcid)
    ec2_c.create_route(RouteTableId=main_route_table_id, DestinationCidrBlock='0.0.0.0/0', GatewayId=igwid)

def create_nat_gateway(mysubnets, custom_route_table_id):
    print('Creating NAT gateway...')
    ec2_c = boto3.client('ec2')
    resp = ec2_c.allocate_address(Domain='vpc')
    nat_public_ip = resp['PublicIp']
    nat_allocation_id = resp['AllocationId']
    resp = ec2_c.create_nat_gateway(SubnetId=mysubnets[0], AllocationId=nat_allocation_id)
    nat_gateway_id = resp['NatGateway']['NatGatewayId']
    #We need waiter to wait for the NAT gateway running. 
    print('Waiting for NAT gateway to be running...')
    waiter = ec2_c.get_waiter('nat_gateway_available')
    waiter.wait(NatGatewayIds=[nat_gateway_id], Filters=[{'Name': 'state', 'Values': ['available']}], WaiterConfig={'Delay': 60, 'MaxAttempts': 5})
    print('NAT gateway Running now')
    ec2_c.create_route(RouteTableId=custom_route_table_id, DestinationCidrBlock='0.0.0.0/0', NatGatewayId=nat_gateway_id)
    
def update_security_groups(myvpcid, myvpcname):
    print('Updating Security groups...')
    ec2_c = boto3.client('ec2')
    vpc = boto3.resource('ec2').Vpc(myvpcid)
    for s in vpc.security_groups.all():
        mysecurity_id = s.group_id
    response = requests.get('http://jsonip.com/') 
    myip = response.json()['ip']
    ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp=myip + '/32')
    ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpProtocol='tcp', FromPort=80, ToPort=80, CidrIp='0.0.0.0/0')
    ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpPermissions=[{'FromPort':80, 'ToPort':80, 'IpProtocol': 'tcp', 'Ipv6Ranges':[{'CidrIpv6':'::/0'}]}])
    ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpProtocol='udp', FromPort=10110, ToPort=10110, CidrIp='0.0.0.0/0')
    ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpPermissions=[{'FromPort': 10110, 'ToPort': 10110, 'IpProtocol': 'udp', 'Ipv6Ranges':[{'CidrIpv6':'::/0'}]}])
    ec2_c.authorize_security_group_ingress(GroupId=mysecurity_id, IpProtocol='-1', CidrIp='172.16.0.0/16')
    ec2_c.create_tags(Resources=[mysecurity_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'SG'}])
    
def create_rds_subnets(myvpcname, mysubnets):
    print('Creating RDS subnetgroups...')
    rds_c = boto3.client('rds')
    #rds_c.create_db_subnet_group(DBSubnetGroupName=myvpcname + "RDSSubnet", DBSubnetGroupDescription="RDS Subnet Group", SubnetIds=[mysubnets[3],mysubnets[4],mysubnets[5]], Tags=[{'Key': "name", 'Value': myvpcname + "RDSSubnet"}])
    rds_c.create_db_subnet_group(DBSubnetGroupName=myvpcname + "RDSSubnet", DBSubnetGroupDescription="RDS Subnet Group", SubnetIds=[mysubnets[2],mysubnets[3]], Tags=[{'Key': "name", 'Value': myvpcname + "RDSSubnet"}])
        
def main():
    cidr = '172.16.0.0/16'
    region = 'us-west-1'
    myvpcname = 'KsDevVPC'
    myvpcid = create_myvpc(myvpcname, region, cidr)
    mysubnets = create_mysubnet(myvpcid, myvpcname)
    main_route_table_id, custom_route_table_id = create_myroute_tables(myvpcid, myvpcname, mysubnets)
    create_myigw(myvpcid, myvpcname, main_route_table_id)
    #We don't need to create NAT if we create VPC endpoints, such as S3 and S3 instance profile
    #create_nat_gateway(mysubnets, custom_route_table_id)
    create_rds_subnets(myvpcname, mysubnets)
    update_security_groups(myvpcid, myvpcname)

if __name__ == '__main__':
    main()

