#Make sure use the most optimized ecs-hvm ami with ecs-agent installed default
#Steps to create ecs cluster.
#First is target group, load balancer and listener which needs load balancer arn and target group name
#Second is autoscaling group needs target group name
#Third is capacity provider, this needs autoscaling group arn or name
#Fourth is ecs cluster, this needs capacity provider
#Fifth is ecs task definiction, this doesn't seem to depend on any
#Sixth is ecs service name that needs cluster name, task definition, load balancer, target group, and capacity provider. If it uses autoscaling group, then capacity group needs to be created prior. 
import sys
import boto3

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

def get_security_ids(myvpcid):
    security_ids = []
    ec2_r = boto3.resource('ec2')
    myawsvpc = ec2_r.Vpc(myvpcid)
    for i in myawsvpc.security_groups.all():
        security_ids.append(i.id)
    return security_ids 

def get_template_id(template_name):
    #Use GPS or MAP
    template_id = None
    ec2_c = boto3.client('ec2')
    resp = ec2_c.describe_launch_templates()
    for i in resp['LaunchTemplates']:
        if template_name in i['LaunchTemplateName']:
            template_id = i['LaunchTemplateId']
    return template_id 

def describe_myecr(ecr_name):
    ecr_c = boto3.client('ecr')
    resp = ecr_c.describe_repositories(repositoryNames=[ecr_name])
    regi_id = resp['repositories'][0]['registryId']
    repo_name = resp['repositories'][0]['repositoryName']
    repo_uri = resp['repositories'][0]['repositoryUri']
    return (regi_id, repo_name, repo_uri)

def get_myecr_cred(regi_id):
    ecr_c = boto3.client('ecr')
    resp = ecr_c.get_authorization_token(registryIds=[regi_id])
    auths = base64.b64decode(resp['authorizationData'][0]['authorizationToken']).decode('utf-8').split(':')
    return auths

def create_ecs_target_group(myvpcid, target_group_name, protocol, port):
    print('Creating Target group...')
    elbv2_c = boto3.client('elbv2')
    if protocol == 'HTTP':
        protocol = 'HTTP'
        #resp = elbv2_c.create_target_group(Name=target_group_name, Protocol=protocol, Port=port, VpcId=myvpcid, HealthCheckProtocol=protocol, HealthCheckPort=str(port), HealthCheckEnabled=True, HealthCheckIntervalSeconds=10, HealthCheckTimeoutSeconds=5, HealthyThresholdCount=5, UnhealthyThresholdCount=5, Matcher={'HttpCode': '302'}, TargetType='instance')
        resp = elbv2_c.create_target_group(Name=target_group_name, Protocol=protocol, Port=port, VpcId=myvpcid, HealthCheckProtocol=protocol, HealthCheckPort='traffic-port', HealthCheckEnabled=True, HealthCheckIntervalSeconds=10, HealthCheckTimeoutSeconds=5, HealthyThresholdCount=5, UnhealthyThresholdCount=5, Matcher={'HttpCode': '302'}, TargetType='ip')
    else:
        resp = elbv2_c.create_target_group(Name=target_group_name, Protocol=protocol, Port=port, VpcId=myvpcid, HealthCheckProtocol='TCP', HealthCheckPort='22', HealthCheckEnabled=True, HealthCheckIntervalSeconds=10, HealthCheckTimeoutSeconds=10, HealthyThresholdCount=5, UnhealthyThresholdCount=5, Matcher={'HttpCode': '302'}, TargetType='instance')
    target_group_arn = resp['TargetGroups'][0]['TargetGroupArn']
    elbv2_c.modify_target_group_attributes(TargetGroupArn=target_group_arn, Attributes=[{'Key': 'stickiness.enabled', 'Value': 'true'}, {'Key': 'stickiness.type', 'Value': 'lb_cookie'}])
    #print(target_group_arn)
    return target_group_arn

def create_ecs_load_balancer(subnet_id, lb_name, type):
    print('Creating Load balancer...')
    if type == 'net':
        elbv2_c = boto3.client('elbv2')
        resp = elbv2_c.create_load_balancer(Name=lb_name, Subnets=[subnet_id], Tags=[{'Key': 'Name', 'Value': lb_name}], Type='network', IpAddressType='ipv4')
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
        print(dnsname)
    return lb_arn

def create_ecs_listener(lb_arn, target_group_arn, protocol, port):
    print('Creating Load balancer listener...')
    elbv2_c = boto3.client('elbv2')
    elbv2_c.create_listener(LoadBalancerArn=lb_arn, Protocol=protocol, Port=port, DefaultActions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn, 'ForwardConfig': {'TargetGroups': [{'TargetGroupArn': target_group_arn}]}}])
    #elbv2_c.create_listener(LoadBalancerArn=lb_arn, Protocol=protocol, Port=port, DefaultActions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn, 'ForwardConfig': {'TargetGroups': [{'TargetGroupArn': target_group_arn}], 'TargetGroupStickinessConfig': {'Enabled': True, 'DurationSeconds': 86400}}}])
    #create rule is only for listener
    #elbv2_c.create_rule

#def create_ecs_auto_scaling_group(subnet_id, target_group_arn, launch_template_id, group_name):
def create_ecs_auto_scaling_group(subnet_id, launch_template_id, group_name):
    print('Creating Autoscaling group...')
    as_c = boto3.client('autoscaling')
    #When use TargetGroupARNs, we don't need to use LoadBalancerNames=[lb_name].
    resp = as_c.create_auto_scaling_group( \
        AutoScalingGroupName=group_name, \
        LaunchTemplate={'LaunchTemplateId': launch_template_id, 'Version': '$Latest'}, \
        MinSize=1, \
        MaxSize=2, \
        #VPCZoneIdentifier=subnet_id, \
        #06292022 I commented the line below
        #TargetGroupARNs=[target_group_arn], \
        Tags=[
            {
                'Key': 'Name',
                'Value': group_name
                },
            ]
    )

def get_ecs_auto_scaling_group(group_name):
    print('Retrieving Autoscaling group...')
    as_c = boto3.client('autoscaling')
    #When use TargetGroupARNs, we don't need to use LoadBalancerNames=[lb_name].
    resp = as_c.describe_auto_scaling_groups(AutoScalingGroupNames=[group_name])
    print(resp)
    return resp['AutoScalingGroups'][0]['AutoScalingGroupARN']

def create_capacity_provider(ecsautoscalinggrouparn, cap_name):
    print('Creating ECS Capacity Provider...')
    ecs_c = boto3.client('ecs')
    resp = ecs_c.create_capacity_provider(name=cap_name, autoScalingGroupProvider={'autoScalingGroupArn': ecsautoscalinggrouparn, 'managedScaling': {'status': 'ENABLED', 'targetCapacity': 2, 'minimumScalingStepSize': 1, 'maximumScalingStepSize': 2}}, tags=[{'key': 'Name', 'value': 'MyECSCapacityProvider'}])
    #resp = ecs_c.create_capacity_provider(name=cap_name, autoScalingGroupProvider={'autoScalingGroupArn': ecsautoscalinggrouparn}, tags=[{'key': 'Name', 'value': 'MyECSCapacityProvider'}])

def get_capacity_provider(cap_name):
    print('Retrieving ECS Capacity Provider...')
    ecs_c = boto3.client('ecs')
    resp = ecs_c.describe_capacity_providers(capacityProviders=['MyECSCapacity'])
    cap_arn = resp['capacityProviders'][0]['capacityProviderArn'] 
    print(cap_arn)
    return cap_arn

def create_ecs_cluster(cluster_name):
    print('Creating ECS Cluster...')
    ecs_c = boto3.client('ecs')
    resp = ecs_c.create_cluster(clusterName=cluster_name, configuration={'executeCommandConfiguration': {'logging': 'OVERRIDE', 'logConfiguration': {'cloudWatchLogGroupName': 'MyECSCloudWatchLog', 'cloudWatchEncryptionEnabled': False, 's3BucketName': 'ksdevecseast2', 's3EncryptionEnabled': False}}}, capacityProviders=['FARGATE'])
    return resp['cluster']['clusterName']

def create_ecs_task_definition(repo_uri):
    print('Creating ECS Task Definition...')
    ecs_c = boto3.client('ecs')
    resp = ecs_c.register_task_definition( \
        #Use this two roles EC2ECSProfile, EC2ECSRole
        family='MyECSTask', \
        taskRoleArn='EC2ECSRole', \
        executionRoleArn='EC2ECSRole', \
        networkMode='awsvpc', \
        containerDefinitions=[ \
            { \
                'name': 'gunicorn', \
                'image': '%s:gunicornfargate' % repo_uri, \
                'memory': 800, \
                'memoryReservation': 600, \
                'essential': True, \
                'workingDirectory': '/var/task/mysite', \
                'logConfiguration': {  \
                    'logDriver': 'awslogs', \
                    'options': { \
                        'awslogs-group':  'ecstaskgroup', \
                        'awslogs-region': 'us-east-2', \
                        'awslogs-create-group': 'true', \
                        'awslogs-stream-prefix': 'ecstask' \
                    }
                 },
                'disableNetworking': False, \
                'privileged': False, \
                'readonlyRootFilesystem': False, \
                'interactive': False, \
                'pseudoTerminal': False, \
            }, \
            { \
                'name': 'nginxrtmp', \
                'image': '%s:nginxrtmpfargate' % repo_uri, \
                'memory': 800, \
                'memoryReservation': 600, \
                'portMappings': [ \
                    { \
                        'containerPort': 80, \
                        'hostPort': 80, \
                        'protocol': 'http' \
                    }, \
                ], \
                'essential': True, \
                'workingDirectory': '/var/task', \
                'logConfiguration': {  \
                    'logDriver': 'awslogs', \
                    'options': { \
                        'awslogs-group':  'ecstaskgroup', \
                        'awslogs-region': 'us-east-2', \
                        'awslogs-create-group': 'true', \
                        'awslogs-stream-prefix': 'ecstask' \
                    }
                 },
                'volumesFrom': [ \
                    { \
                        'sourceContainer': 'gunicorn', \
                        'readOnly': False \
                    }, \
                ], \
                'disableNetworking': False, \
                'privileged': False, \
                'readonlyRootFilesystem': False, \
                'interactive': False, \
                'pseudoTerminal': False, \
            } \
        ], \
        requiresCompatibilities=[ \
            'FARGATE'\
        ], \
        cpu='1024', \
        memory='4096', \
        tags=[ \
            { \
                'key': 'Name', \
                'value': 'MyECSTaskNginxGunicorn' \
            } \
        ] \
    )
    return resp['taskDefinition']['taskDefinitionArn']
   
def create_ecs_service(cluster_name, taskdefinition, target_group_arn, subnets, securitygroups):
    print('Creating ECS Service...')
    ecs_c = boto3.client('ecs')
    #platformVersion only for Fargate, desiredCount is numbes of task to run
    ecs_c.create_service(cluster=cluster_name, serviceName='MyECSService', taskDefinition=taskdefinition, loadBalancers=[{'targetGroupArn': target_group_arn, 'containerName': 'nginxrtmp', 'containerPort': 80}], desiredCount=2, launchType='FARGATE', networkConfiguration={'awsvpcConfiguration': {'subnets': subnets, 'securityGroups': securitygroups, 'assignPublicIp': 'DISABLED'}}, healthCheckGracePeriodSeconds=30, deploymentController={'type': 'CODE_DEPLOY'}, tags=[{'key': 'Name', 'value': 'MyECSService'}], enableExecuteCommand=True)
    #networkConfiguration={'awsvpcConfiguration': {'subnets': ['subnet-06d1420e9c7c8bec1'], 'securityGroups': ['sg-0c4299eb63e51b56d'], 'assignPublicIp': 'DISABLED'}}
   
def main():
    myvpcid = sys.argv[1]
    target_group_arn = create_ecs_target_group(myvpcid, 'MyECSAutoScalingTargetGroup', 'HTTP', 80)
    target_group_arn2 = create_ecs_target_group(myvpcid, 'MyECSAutoScalingTargetGroup1', 'HTTP', 80)
    subnet_id = get_pub_subnets(myvpcid)
    lb_arn = create_ecs_load_balancer(subnet_id, 'MyECSLoadBalancer', 'app')
    create_ecs_listener(lb_arn, target_group_arn, 'HTTP', 80)
    create_ecs_listener(lb_arn, target_group_arn2, 'HTTP', 8080)
    #Private launch template
    #launch_template_id = get_template_id('MyAWSVPC2PrivateSubnetALaunchTemplateECS')
    #print(launch_template_id)
    subnets = get_pri_subnets(myvpcid)
    securitygroups = get_security_ids(myvpcid)
    securitygroups = ['sg-0a0eade025d59923d']
    #create_ecs_auto_scaling_group(subnets, launch_template_id, 'MyECSAutoScalingGroup')
    #ecsautoscalingarn = get_ecs_auto_scaling_group('MyECSAutoScalingGroup')
    #print(ecsautoscalingarn)
    #create_capacity_provider(ecsautoscalingarn, 'MyECSCapacity')
    #cap_arn = get_capacity_provider('MyECSCapacity')
    ecs_name = create_ecs_cluster('MyECSCluster')
    regi_id, repo_name, repo_uri = describe_myecr('ksdevecr')
    print(repo_uri)
    taskdefinition = create_ecs_task_definition(repo_uri)
    ecs_name = 'MyECSCluster'
    create_ecs_service(ecs_name, taskdefinition, target_group_arn, subnets, securitygroups)

if __name__ == '__main__':
    main()
