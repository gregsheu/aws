import sys
import re
import boto3

def create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, route_table_ids):
    ec2_c = boto3.client('ec2')
    #As 2022-06-19 same as terraform, interface endpoint doesn't need routetable id
    if ep_type == 'Interface':
        print('Creating Interface EP...')
        resp = ec2_c.create_vpc_endpoint(VpcEndpointType=ep_type, VpcId=myvpcid, ServiceName=service, SubnetIds=mysubnets, SecurityGroupIds=[mysg_id])
        ep_id = resp['VpcEndpoint']['VpcEndpointId']
        print('Interface EP %s created' % ep_id)
    #As 2022-06-19 same as terraform, gateway endpoint doesn't need security group and subnet
    if ep_type == 'Gateway':
        print('Creating Gateway EP...')
        resp = ec2_c.create_vpc_endpoint(VpcEndpointType=ep_type, VpcId=myvpcid, ServiceName=service, RouteTableIds=route_table_ids)
        ep_id = resp['VpcEndpoint']['VpcEndpointId']
        print('Gateway EP %s created' % ep_id)
    return ep_id

def main():
    myvpcid = sys.argv[1]
    mysg_id = None
    mysubnets = []
    myroutetables = []
    ec2_c = boto3.client('ec2')
    ec2 = boto3.resource('ec2')
    myawsvpc = ec2.Vpc(myvpcid)
    myvpcname = myawsvpc.tags[0]['Value']
    for s in myawsvpc.security_groups.all():
        mysg_id = s.id
    for s in myawsvpc.subnets.all():
        if re.search('Private', s.tags[0]['Value']):
            mysubnets.append(s.id)
    for r in myawsvpc.route_tables.all():
        myroutetables.append(r.route_table_id)
    ep_type = 'Interface'
    service = 'com.amazonaws.us-west-2.ec2'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'EC2EP'}])
    service = 'com.amazonaws.us-west-2.rds'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'RDSEP'}])
    service = 'com.amazonaws.us-west-2.ssm'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'SSMEP'}])
    service = 'com.amazonaws.us-west-2.ssmmessages'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'SSMMessagesEP'}])
    service = 'com.amazonaws.us-west-2.ec2messages'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'EC2MessagesEP'}])
    service = 'com.amazonaws.us-west-2.cloudtrail'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'CloudTrailEP'}])
    service = 'com.amazonaws.us-west-2.ecr.api'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'ECRApiEP'}])
    service = 'com.amazonaws.us-west-2.ecr.dkr'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'ECRDkrEP'}])
    service = 'com.amazonaws.us-west-2.secretsmanager'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'SecretsManagerEP'}])
    service = 'com.amazonaws.us-west-2.ecs'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'ECSEP'}])
    service = 'com.amazonaws.us-west-2.ecs-agent'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'ECSAgentEP'}])
    service = 'com.amazonaws.us-west-2.ecs-telemetry'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'ECSTelemetryEP'}])
    ep_type = 'Gateway'
    service = 'com.amazonaws.us-west-2.s3'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'S3EP'}])
    service = 'com.amazonaws.us-west-2.dynamodb'
    ep_id = create_myendpoint(myvpcid, ep_type, service, mysg_id, mysubnets, myroutetables)
    ec2_c.create_tags(Resources=[ep_id], Tags=[{'Key': 'Name', 'Value': myvpcname + 'DynamoDBEP'}])

if __name__ == '__main__':
    main()

