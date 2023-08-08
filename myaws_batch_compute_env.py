from operator import itemgetter, attrgetter
import sys
import boto3
import botocore.waiter

def create_myrole(role_name):
    print('Creating Role for Batch...')
    assume_role = '{ \
        "Version": "2012-10-17", \
        "Statement": [{ \
            "Effect": "Allow", \
            "Principal": {"Service": "batch.amazonaws.com"}, \
            "Action": "sts:AssumeRole" \
            }] \
        }'
    iam_c = boto3.client('iam')
    resp = iam_c.create_role(RoleName=role_name, AssumeRolePolicyDocument=assume_role)
    role_arn = resp['Role']['Arn']
    return role_arn

def create_myrolepolicy(policy_name):
    print('Creating Policy for that role...')
    role_policy = '{ \
        "Version": "2012-10-17", \
        "Statement": [ \
            { \
                "Effect": "Allow", \
                "Action": [ \
                    "ec2:DescribeAccountAttributes", \
                    "ec2:DescribeInstances", \
                    "ec2:DescribeInstanceAttribute", \
                    "ec2:DescribeSubnets", \
                    "ec2:DescribeSecurityGroups", \
                    "ec2:DescribeKeyPairs", \
                    "ec2:DescribeImages", \
                    "ec2:DescribeImageAttribute", \
                    "ec2:DescribeSpotInstanceRequests", \
                    "ec2:DescribeSpotFleetInstances", \
                    "ec2:DescribeSpotFleetRequests", \
                    "ec2:DescribeSpotPriceHistory", \
                    "ec2:DescribeVpcClassicLink", \
                    "ec2:DescribeLaunchTemplateVersions", \
                    "ec2:CreateLaunchTemplate", \
                    "ec2:DeleteLaunchTemplate", \
                    "ec2:RequestSpotFleet", \
                    "ec2:CancelSpotFleetRequests", \
                    "ec2:ModifySpotFleetRequest", \
                    "ec2:TerminateInstances", \
                    "ec2:RunInstances", \
                    "autoscaling:DescribeAccountLimits", \
                    "autoscaling:DescribeAutoScalingGroups", \
                    "autoscaling:DescribeLaunchConfigurations", \
                    "autoscaling:DescribeAutoScalingInstances", \
                    "autoscaling:CreateLaunchConfiguration", \
                    "autoscaling:CreateAutoScalingGroup", \
                    "autoscaling:UpdateAutoScalingGroup", \
                    "autoscaling:SetDesiredCapacity", \
                    "autoscaling:DeleteLaunchConfiguration", \
                    "autoscaling:DeleteAutoScalingGroup", \
                    "autoscaling:CreateOrUpdateTags", \
                    "autoscaling:SuspendProcesses", \
                    "autoscaling:PutNotificationConfiguration", \
                    "autoscaling:TerminateInstanceInAutoScalingGroup", \
                    "ecs:DescribeClusters", \
                    "ecs:DescribeContainerInstances", \
                    "ecs:DescribeTaskDefinition", \
                    "ecs:DescribeTasks", \
                    "ecs:ListClusters", \
                    "ecs:ListContainerInstances", \
                    "ecs:ListTaskDefinitionFamilies", \
                    "ecs:ListTaskDefinitions", \
                    "ecs:ListTasks", \
                    "ecs:CreateCluster", \
                    "ecs:DeleteCluster", \
                    "ecs:RegisterTaskDefinition", \
                    "ecs:DeregisterTaskDefinition", \
                    "ecs:RunTask", \
                    "ecs:StartTask", \
                    "ecs:StopTask", \
                    "ecs:UpdateContainerAgent", \
                    "ecs:DeregisterContainerInstance", \
                    "logs:CreateLogGroup", \
                    "logs:CreateLogStream", \
                    "logs:PutLogEvents", \
                    "logs:DescribeLogGroups", \
                    "iam:GetInstanceProfile", \
                    "iam:GetRole" \
                ], \
                "Resource": "*" \
            }, \
            { \
                "Effect": "Allow", \
                "Action": "iam:PassRole", \
                "Resource": [ \
                    "*" \
                ], \
                "Condition": { \
                    "StringEquals": { \
                        "iam:PassedToService": [ \
                            "ec2.amazonaws.com", \
                            "ec2.amazonaws.com.cn", \
                            "ecs-tasks.amazonaws.com" \
                        ] \
                    } \
                } \
            }, \
            { \
                "Effect": "Allow", \
                "Action": "iam:CreateServiceLinkedRole", \
                "Resource": "*", \
                "Condition": { \
                    "StringEquals": { \
                        "iam:AWSServiceName": [ \
                            "spot.amazonaws.com", \
                            "spotfleet.amazonaws.com", \
                            "autoscaling.amazonaws.com", \
                            "ecs.amazonaws.com" \
                        ] \
                    } \
                } \
            }, \
            { \
                "Effect": "Allow", \
                "Action": [ \
                    "ec2:CreateTags" \
                ], \
                "Resource": [ \
                    "*" \
                ], \
                "Condition": { \
                    "StringEquals": { \
                        "ec2:CreateAction": "RunInstances" \
                    } \
                } \
            } \
        ] \
    }'
    iam_c = boto3.client('iam')
    resp = iam_c.create_policy(PolicyName=policy_name, PolicyDocument=role_policy)
    policy_arn = resp['Policy']['Arn']
    return policy_arn

def create_role_with_policy(role_name, policy_arn):
    print('Attaching policy to the role...')
    iam_c = boto3.client('iam')
    iam_c.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

def create_compute_env(env_name, subnet_ids, ami_id, security_ids, instance_role, service_role):
    print('Creating compute env %s' % env_name)
    bch_c = boto3.client('batch')
    bch_c.create_compute_environment(computeEnvironmentName=env_name, type='MANAGED', state='ENABLED', computeResources={'type': 'EC2', 'minvCpus': 2, 'maxvCpus': 8, 'instanceTypes': ['c4.large'], 'subnets': subnet_ids, 'imageId': ami_id, 'securityGroupIds': security_ids, 'ec2KeyPair': 'gregkey', 'instanceRole': instance_role, 'tags': {'Name': 'KsDevBatchComputeResource'}}, serviceRole=service_role, tags={'Name': 'KsDevBatchCompute'})

def create_compute_envtl(env_name, subnet_ids, launch_template_id, instance_role, service_role):
    print('Creating comoute env %s' % env_name)
    bch_c = boto3.client('batch')
    bch_c.create_compute_environment(computeEnvironmentName=env_name, type='MANAGED', state='ENABLED', computeResources={'type': 'EC2', 'minvCpus': 2, 'maxvCpus': 8, 'instanceTypes': ['c4.large'], 'subnets': subnet_ids, 'instanceRole': instance_role, 'tags': {'Name': 'KsDevBatchComputeResource'}, 'launchTemplate': {'launchTemplateId': launch_template_id}}, serviceRole=service_role, tags={'Name': 'KsDevBatchCompute'})

def create_myjobqueue(queue_name, compute_env):
    print('Creating job queue %s' % queue_name)
    bch_c = boto3.client('batch')
    bch_c.create_job_queue(jobQueueName=queue_name, state='ENABLED', priority=1, computeEnvironmentOrder=[{'order': 1, 'computeEnvironment': compute_env}], tags={'Name': 'KsDevBatchEnvQueue'})
    print('Job queue created...')

def create_myjobdef(job_name, image_name):
    print('Creating job definition...')
    bch_c = boto3.client('batch')
    #python3
    bch_c.register_job_definition(jobDefinitionName=job_name, type='container', parameters={'inputfile': ''}, containerProperties={'image': image_name, 'vcpus': 2, 'memory': 2000, 'command': ['Ref::inputfile'], 'jobRoleArn': 'arn:aws:iam::141056581104:role/EC2ECSRole', 'volumes': [{'host': {'sourcePath': '/home/ec2-user'}, 'name': 'vol_ec2_home'}], 'mountPoints': [{'containerPath': '/tmp', 'readOnly': False, 'sourceVolume': 'vol_ec2_home'}]})
    #python3v2
    #bch_c.register_job_definition(jobDefinitionName=job_name, type='container', parameters={'region': 'us-west-2'}, containerProperties={'image': image_name, 'vcpus': 2, 'memory': 2000, 'command': ['Ref::region'], 'jobRoleArn': 'arn:aws:iam::141056581104:role/EC2ECSRole', 'volumes': [{'host': {'sourcePath': '/home/ec2-user'}, 'name': 'vol_ec2_home'}], 'mountPoints': [{'containerPath': '/tmp', 'readOnly': False, 'sourceVolume': 'vol_ec2_home'}]})
    #python3v3
    bch_c.register_job_definition(jobDefinitionName=job_name, type='container', parameters={'bucket': '', 'object': '', 'region': ''}, containerProperties={'image': image_name, 'vcpus': 2, 'memory': 2000, 'command': ['Ref::bucket', 'Ref::object', 'Ref::region'], 'jobRoleArn': 'arn:aws:iam::141056581104:role/EC2ECSRole', 'volumes': [{'host': {'sourcePath': '/home/ec2-user'}, 'name': 'vol_ec2_home'}], 'mountPoints': [{'containerPath': '/tmp', 'readOnly': False, 'sourceVolume': 'vol_ec2_home'}]})
    print('Job definition created...')

def create_myjob(job_name, job_queue, job_def, parameter):
    print('Running job %s on %s queue...' % (job_name, job_queue))
    bch_c = boto3.client('batch')
    #job for image python3
    bch_c.submit_job(jobName=job_name, jobQueue=job_queue, jobDefinition=job_def, parameters={'inputfile': parameter})
    #job for image python3 
    #bch_c.submit_job(jobName='py_ffmpeg_snapshot', jobQueue='KsDevBatchEnvQueue', jobDefinition='python3', parameters={'inputfile': '/tmp/py_ffmpeg_snapshot.py'})
    #job for image python3v2
    bch_c.submit_job(jobName='py_ffmpeg_video', jobQueue='KsDevBatchEnvQueue', jobDefinition='python3v2', parameters={'region': 'us-west-2'}, containerOverrides={'environment':[{'name': 'S3BUCKET', 'value': 'ksdevbatchwest2'}, {'name': 'S3OBJECT', 'value': 'py_ffmpeg_video.py'}]})
    #job for image python3v3
    bch_c.submit_job(jobName='py_ffmpeg_video', jobQueue='KsDevBatchEnvQueue', jobDefinition='python3v3', parameters={'bucket': 'ksdevbatchwest2', 'object': 'py_ffmpeg_video.py', 'region': 'us-west-2', })

def dereg_myjobdef(jobdef_name):
    print('Deregister a job def %s ...' % jobdef_name)
    bch_c = boto3.client('batch')
    bch_c.deregister_job_definition(jobDefinition=jobdef_name+':1')

def get_waiter(types):
    bch_c = boto3.client('batch')
    if types == 'queue':
        waiter_id = 'JobQueueWaiter'
        operations = 'DescribeJobQueues'
        argument = 'jobQueues[].status'
    if types == 'env':
        waiter_id = 'ComputeEnvWaiter'
        operations = 'DescribeComputeEnvironments'
        argument = 'computeEnvironments[].status'
    model = botocore.waiter.WaiterModel({
        'version': 2,
        'waiters': {
            waiter_id: {
                'delay': 10,
                'operation': operations,
                'maxAttempts': 10,
                'acceptors': [
                    {
                        'expected': 'VALID',
                        'matcher': 'pathAll',
                        'state': 'success',
                        'argument': argument
                    },
                    {
                        'expected': [],
                        'matcher': 'path',
                        'state': 'success',
                        'argument': argument
                    },
                ]
            }
        }
    })
    waiter = botocore.waiter.create_waiter_with_client(waiter_id, model, bch_c)
    return waiter

def get_latest_ami():
    images = []
    ec2_c = boto3.client('ec2')
    #resp = ec2_c.describe_images(Owners=['amazon'], Filters=[{'Name': 'owner-alias', 'Values': ['amazon']}, {'Name': 'name', 'Values': ['*ecs-hvm*']}, {'Name': 'is-public', 'Values': ['true']}, {'Name': 'virtualization-type', 'Values': ['hvm']}, {'Name': 'architecture', 'Values': ['x86_64']}])
    resp = ec2_c.describe_images(Owners=['amazon'], Filters=[{'Name': 'owner-alias', 'Values': ['amazon']}, {'Name': 'name', 'Values': ['amzn2-ami-ecs*2020*']}, {'Name': 'is-public', 'Values': ['true']}, {'Name': 'virtualization-type', 'Values': ['hvm']}, {'Name': 'architecture', 'Values': ['x86_64']}])
    for i in resp['Images']:
        images.append((i['ImageId'], i['CreationDate']))
    images2 = sorted(images, key=itemgetter(1), reverse=True)
    ami_id = images2[0][0]
    #print(images2[0][0], images2[0][1])
    #print(images2)
    return  ami_id

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

def main():
    vpc_id = sys.argv[1]
    client = boto3.client('batch')
    queue_name = 'KsDevBatchEnvQueue'
    compute_env = 'KsDevBatchEnv'
    job_def = 'python3v3'
    image_name = '141056581104.dkr.ecr.us-west-2.amazonaws.com/ksdevecr:python3v3'
    securities = get_security_ids(vpc_id)
    subnets = get_pub_subnets(vpc_id)
    ami_id = get_latest_ami()
    print(ami_id)
    create_compute_env(compute_env, subnets, ami_id, securities, 'EC2FrontEndProfile', 'KsDevBatchRole')
    waiter = get_waiter('env')
    waiter.wait(computeEnvironments=[compute_env])
    print('Compute env %s valid' % compute_env)
    create_myjobqueue(queue_name, compute_env)
    #dereg_myjobdef(job_def)
    create_myjobdef(job_def, image_name)
    #create_myjob('py_log', queue_name, job_def, '/tmp/py_ffmpeg_snapshot.py')

if __name__ == '__main__':
    main()
