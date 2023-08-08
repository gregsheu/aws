import sys
import boto3
import base64

def create_target_group(myvpcid, target_group_name, protocol, port):
    print('Creating Target group...')
    elbv2_c = boto3.client('elbv2')
    if protocol == 'TCP':
        protocol = 'HTTP'
        resp = elbv2_c.create_target_group(Name=target_group_name, Protocol=protocol, Port=port, VpcId=myvpcid, HealthCheckProtocol=protocol, HealthCheckPort=str(port), HealthCheckEnabled=True, HealthCheckIntervalSeconds=10, HealthCheckTimeoutSeconds=5, HealthyThresholdCount=5, UnhealthyThresholdCount=5, TargetType='instance')
    else:
        resp = elbv2_c.create_target_group(Name=target_group_name, Protocol='TCP', Port=port, VpcId=myvpcid, HealthCheckProtocol='TCP', HealthCheckPort='111', HealthCheckEnabled=True, HealthCheckIntervalSeconds=30, HealthCheckTimeoutSeconds=10, HealthyThresholdCount=10, UnhealthyThresholdCount=10, TargetType='instance')
    target_group_arn = resp['TargetGroups'][0]['TargetGroupArn']
    #print(target_group_arn)
    return target_group_arn

def create_load_balancer(subnet_id, lb_name, type):
    print('Creating Load balancer...')
    if type == 'net':
        elbv2_c = boto3.client('elbv2')
        resp = elbv2_c.create_load_balancer(Name=lb_name, Subnets=subnet_id, Tags=[{'Key': 'Name', 'Value': lb_name}], Type='network', IpAddressType='ipv4')
        lb_arn = resp['LoadBalancers'][0]['LoadBalancerArn']
        dnsname = resp['LoadBalancers'][0]['DNSName']
        print('Waiting for Load Balancer to be active')
        waiter = elbv2_c.get_waiter('load_balancer_available')
        waiter.wait(LoadBalancerArns=[lb_arn], WaiterConfig={'Delay': 60, 'MaxAttempts': 10})
        #waiter.wait(Names=[lb_name], Marker='active', PageSize=1)
        print('Load Balancer is active')
    if type == 'app':
        elbv2_c = boto3.client('elbv2')
        resp = elbv2_c.create_load_balancer(Name=lb_name, Subnets=subnet_id, Tags=[{'Key': 'Name', 'Value': lb_name}], Type='application', IpAddressType='ipv4')
        lb_arn = resp['LoadBalancers'][0]['LoadBalancerArn']
        dnsname = resp['LoadBalancers'][0]['DNSName']
        print('Waiting for Load Balancer to be active')
        waiter = elbv2_c.get_waiter('load_balancer_available')
        waiter.wait(LoadBalancerArns=[lb_arn], WaiterConfig={'Delay': 60, 'MaxAttempts': 10})
        #waiter.wait(Names=[lb_name], Marker='active', PageSize=1)
        print('Load Balancer is active')
    return lb_arn

def create_listener(lb_arn, target_group_arn, protocol, port):
    print('Creating Load balancer listener...')
    elbv2_c = boto3.client('elbv2')
    elbv2_c.create_listener(LoadBalancerArn=lb_arn, Protocol=protocol, Port=port, DefaultActions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn, 'ForwardConfig': {'TargetGroups': [{'TargetGroupArn': target_group_arn}]}}])
    #create rule is only for listener
    #elbv2_c.create_rule

def create_autoscaling_group(subnet_id, target_group_arn, launch_template_id, group_name):
    print('Creating Autoscaling group...')
    as_c = boto3.client('autoscaling')
    #When use TargetGroupARNs, we don't need to use LoadBalancerNames=[lb_name].
    #When use launch template with subnet id, we don't need vpczoneidentifier
    resp = as_c.create_auto_scaling_group( \
        AutoScalingGroupName=group_name, \
        LaunchTemplate={'LaunchTemplateId': launch_template_id, 'Version': '$Latest'}, \
        MinSize=2, \
        MaxSize=4, \
        #VPCZoneIdentifier=subnet_id, \
        TargetGroupARNs=[target_group_arn], \
        Tags=[
            {
                'Key': 'Name',
                'Value': group_name
                },
            ]
    )

def get_pub_subnets(myvpcid):
    subnets = []
    mysubnets = []
    mysubnets_tags = {}
    ec2_c = boto3.client('ec2')
    ec2_r = boto3.resource('ec2')
    myawsvpc = ec2_r.Vpc(myvpcid)
    for s in myawsvpc.subnets.all():
        mysubnets.append(s.id)
    resp = ec2_c.describe_subnets(SubnetIds=mysubnets)
    for s in resp['Subnets']:
        mysubnets_tags.update({s['SubnetId']: s['Tags']})
    for k, v in mysubnets_tags.items():
        if 'Pub' in v[0]['Value']:
            subnets.append(k)
    return subnets

def get_pri_subnets(myvpcid):
    subnets = []
    mysubnets = []
    mysubnets_tags = {}
    ec2_c = boto3.client('ec2')
    ec2_r = boto3.resource('ec2')
    myawsvpc = ec2_r.Vpc(myvpcid)
    for s in myawsvpc.subnets.all():
        mysubnets.append(s.id)
    resp = ec2_c.describe_subnets(SubnetIds=mysubnets)
    for s in resp['Subnets']:
        mysubnets_tags.update({s['SubnetId']: s['Tags']})
    for k, v in mysubnets_tags.items():
        if 'Pri' in v[0]['Value']:
            subnets.append(k)
    return subnets

def get_template_id (image_id, security_group_id, subnet_id, key_name, userdata):
    f = open(userdata, 'rb')
    base64string = base64.b64encode(f.read())
    base64string = base64string.decode('utf-8')
    ec2_c = boto3.client('ec2')
    resp = ec2_c.create_launch_template(
        LaunchTemplateData={
            'ImageId': image_id,
            'InstanceType': 't2.small',
            'IamInstanceProfile': {
                'Name': 'EC2BackEndProfile'
            },
            'UserData': base64string,
            'NetworkInterfaces': [
                {
                    'DeviceIndex': 0,
                    'Groups': [security_group_id],
                    'SubnetId': subnet_id
                }
            ],
            #'SecurityGroupIds': [security_group_id],
            'KeyName': key_name,
            'Monitoring': {'Enabled': True},
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'CodeDeployHost',
                            },
                        ],
                    },
                ],
            },
        LaunchTemplateName='CodeDeployHost',
        VersionDescription='codedeploy_v1',
    )
    launch_template_id = resp['LaunchTemplate']['LaunchTemplateId']
    #launch_template_name = resp['LaunchTemplate']['LaunchTemplateName']
    return launch_template_id

def main():
    myvpcid = sys.argv[1]
    subnet_id = []
    as_subnet_id = []
    image_id = 'ami-0fa49cc9dc8d62c84'
    #Creating gps part 
    #target_group_arn = create_target_group(myvpcid, 'GpsAutoScalingTargetGroup', 'UDP', 10110)
    #Public subnet id
    #subnet_id = get_pub_subnets(myvpcid)
    #print(subnet_id) 
    #lb_arn = create_load_balancer(subnet_id, 'GpsLoadBalancer', 'net')
    #create_listener(lb_arn, target_group_arn, 'TCP', 10110)
    ##Private launch template
    #launch_template_id = get_template_id('GPS')
    #print(launch_template_id)
    #as_subnet_id = get_pri_subnets(myvpcid)
    #print(as_subnet_id)
    #create_autoscaling_group(as_subnet_id, target_group_arn, launch_template_id, 'GpsAutoScalingGroup')

    ##Creating map part 
    target_group_arn1 = create_target_group(myvpcid, 'CodeDeployTargetGroup1', 'TCP', 80)
    target_group_arn2 = create_target_group(myvpcid, 'CodeDeployTargetGroup2', 'TCP', 80)
    #Public subnet id
    subnet_id = get_pub_subnets(myvpcid)
    print(subnet_id) 
    lb_arn = create_load_balancer(subnet_id, 'CodeDeployLoadBalancer', 'app')
    create_listener(lb_arn, target_group_arn1, 'HTTP', 80)
    create_listener(lb_arn, target_group_arn2, 'HTTP', 8080)

    #Private launch template
    as_subnet_id = get_pri_subnets(myvpcid)
    key_name = 'gregkey'
    userdata = 'nginxtest/userdata.txt'
    security_group_id = 'sg-0a0eade025d59923d'
    launch_template_id = get_template_id(image_id, security_group_id, as_subnet_id[0], key_name, userdata)
    print(launch_template_id)
    print(as_subnet_id)
    create_autoscaling_group(as_subnet_id, target_group_arn1, launch_template_id, 'CodeDeployHostAutoScalingGroup')
 
if __name__ == '__main__':
    main()
