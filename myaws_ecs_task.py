import boto3

def describe_myecr(ecr_name):
    ecr_c = boto3.client('ecr')
    resp = ecr_c.describe_repositories(repositoryNames=[ecr_name])
    regi_id = resp['repositories'][0]['registryId']
    repo_name = resp['repositories'][0]['repositoryName']
    repo_uri = resp['repositories'][0]['repositoryUri']
    return (regi_id, repo_name, repo_uri)

def create_ecs_task_definition(repo_uri):
    print('Creating ECS Task Definition...')
    ecs_c = boto3.client('ecs')
    resp = ecs_c.register_task_definition( \
        #Use this two roles EC2ECSProfile, EC2ECSRole
        family='InitECSTask', \
        taskRoleArn='EC2ECSRole', \
        executionRoleArn='EC2ECSRole', \
        networkMode='bridge', \
        containerDefinitions=[ \
            { \
                'name': 'nginxrtmp', \
                'image': '%s:nginxrtmp' % repo_uri, \
                'memory': 800, \
                'memoryReservation': 600, \
                'portMappings': [ \
                    { \
                        'containerPort': 80, \
                        'hostPort': 0, \
                        'protocol': 'http' \
                    }, \
                ], \
                'essential': True, \
                #'command': [ \
                #    '/usr/local/nginx/sbin/nginx', \
                #    '-g', \
                #    'daemon off;' \
                #], \
                'mountPoints': [ \
                    { \
                        'sourceVolume': 'workdir', \
                        'containerPath': '/var/task', \
                        'readOnly': False \
                    }, \
                ], \
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
                'disableNetworking': False, \
                'privileged': False, \
                'readonlyRootFilesystem': False, \
                'interactive': False, \
                'pseudoTerminal': False, \
            }, \
            { \
                'name': 'gunicorn', \
                'image': '%s:gunicorn' % repo_uri, \
                'memory': 800, \
                'memoryReservation': 600, \
                'essential': True, \
                #'command': [ \
                #    '/usr/local/bin/gunicorn', \
                #    '4', \
                #    '--bind', \
                #    'unix:/var/task/gunicorn.sock', \
                #    'mysite.wsgi'
                #], \
                'mountPoints': [ \
                    { \
                        'sourceVolume': 'workdir', \
                        'containerPath': '/var/task', \
                        'readOnly': False \
                    }, \
                ], \
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
            } \
        ], \
        volumes=[ \
            { \
                'name': 'workdir', \
                'host': { \
                    'sourcePath': '/var/task' \
                } \
            } \
        ], \
        tags=[ \
            { \
                'key': 'Name', \
                'value': 'MyECSTaskNginxGunicorn' \
            } \
        ], \
        runtimePlatform={ \
            'cpuArchitecture': 'X86_64', \
            'operatingSystemFamily': 'LINUX' \
        } \
    )
    return resp['taskDefinition']['taskDefinitionArn']
def create_ecs_service(cluster_name, taskdefinition):
    print('Creating ECS Service...')
    cluster_name = 'MyECSCluster'
    ecs_c = boto3.client('ecs')
    #platformVersion only for Fargate, desiredCount is numbes of task to run
    ecs_c.create_service(cluster=cluster_name, serviceName='InitEcsService', taskDefinition=taskdefinition, loadBalancers=[{'targetGroupArn': 'arn:aws:elasticloadbalancing:us-east-2:141056581104:targetgroup/MyECSTargetGroup/833ec1b914298bd3', 'containerName': 'nginxrtmp', 'containerPort': 80}], desiredCount=1, capacityProviderStrategy=[{'capacityProvider': 'MyECSCapacity', 'weight': 10, 'base': 5}], deploymentController={'type': 'ECS'}, tags=[{'key': 'Name', 'value': 'InitEcsService'}], enableExecuteCommand=True)
    #networkConfiguration={'awsvpcConfiguration': {'subnets': ['subnet-06d1420e9c7c8bec1'], 'securityGroups': ['sg-0c4299eb63e51b56d'], 'assignPublicIp': 'DISABLED'}}

def main():
    regi_id, repo_name, repo_uri = describe_myecr('ksdevecr')
    print(repo_uri)
    taskdefinition = create_ecs_task_definition(repo_uri)
    ecs_name = 'IniEcsService'
    create_ecs_service(ecs_name, taskdefinition)

if __name__ == '__main__':
    main()
