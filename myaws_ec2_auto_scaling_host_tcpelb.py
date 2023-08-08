import sys
import boto3

def create_target_group(myvpcid, target_group_name, protocol, port):
    print('Creating Target group...')
    elbv2_c = boto3.client('elbv2')
    if protocol == 'TCP':
        protocol = 'HTTP'
        resp = elbv2_c.create_target_group(Name=target_group_name, Protocol=protocol, Port=port, VpcId=myvpcid, HealthCheckProtocol=protocol, HealthCheckPort=str(port), HealthCheckEnabled=True, HealthCheckIntervalSeconds=30, HealthCheckTimeoutSeconds=10, HealthyThresholdCount=5, UnhealthyThresholdCount=5, TargetType='instance')
    else:
        resp = elbv2_c.create_target_group(Name=target_group_name, Protocol='TCP', Port=port, VpcId=myvpcid, HealthCheckProtocol='TCP', HealthCheckPort='111', HealthCheckEnabled=True, HealthCheckIntervalSeconds=30, HealthCheckTimeoutSeconds=10, HealthyThresholdCount=5, UnhealthyThresholdCount=5, TargetType='instance')
        #resp = elbv2_c.create_target_group(Name=target_group_name, Protocol=protocol, Port=port, VpcId=myvpcid, TargetType='instance')
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

def get_template_id(template_name):
    #Use GPS or MAP
    template_id = None
    ec2_c = boto3.client('ec2')
    resp = ec2_c.describe_launch_templates()
    for i in resp['LaunchTemplates']:
        if template_name in i['LaunchTemplateName']:
            template_id = i['LaunchTemplateId']
    return template_id 

def main():
    myvpcid = sys.argv[1]
    subnet_id = []
    as_subnet_id = []
    #Creating gps part 
    target_group_arn = create_target_group(myvpcid, 'GpsAutoScalingTargetGroup2', 'UDP', 10110)
    #Public subnet id
    subnet_id = get_pub_subnets(myvpcid)
    print(subnet_id) 
    lb_arn = create_load_balancer(subnet_id, 'GpsLoadBalancer2', 'net')
    create_listener(lb_arn, target_group_arn, 'TCP', 10110)
    ##Private launch template
    launch_template_id = get_template_id('GPS')
    print(launch_template_id)
    as_subnet_id = get_pri_subnets(myvpcid)
    print(as_subnet_id)
    create_autoscaling_group(as_subnet_id, target_group_arn, launch_template_id, 'GpsAutoScalingGroup2')

    ##Creating map part 
    target_group_arn = create_target_group(myvpcid, 'MapAutoScalingTargetGroup2', 'TCP', 80)
    #Public subnet id
    subnet_id = get_pub_subnets(myvpcid)
    print(subnet_id) 
    lb_arn = create_load_balancer(subnet_id, 'MapLoadBalancer2', 'app')
    create_listener(lb_arn, target_group_arn, 'HTTP', 80)
    #Private launch template
    launch_template_id = get_template_id('MAP')
    print(launch_template_id)
    as_subnet_id = get_pri_subnets(myvpcid)
    print(as_subnet_id)
    create_autoscaling_group(as_subnet_id, target_group_arn, launch_template_id, 'MapAutoScalingGroup2')
 
if __name__ == '__main__':
    main()
