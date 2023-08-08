
cdeploy_c.create_application(applicationName='nginxtest', computePlatform='Server', tags=[{'Key': 'Name', 'Value': 'MysiteCodeDeploymentApplication'}])
cdeploy_c.create_deployment_group(applicationName='nginxtest', deploymentGroupName='nginxtestdeploymentgroup',deploymentConfigName='CodeDeployDefault.OneAtATime', serviceRoleArn='arn:aws:iam::141056581104:role/KsDevCodeDeploy', ec2TagFilters=[{'Key': 'Name', 'Value': 'I-PublicTest', 'Type': 'KEY_AND_VALUE'}])

cdeploy_c.create_deployment(applicationName='nginxtest', deploymentGroupName='nginxtestdeploymentgroup', deploymentConfigName='CodeDeployDefault.OneAtATime', revision={'revisionType': 'S3', 's3Location': {'bucket': 'ksdevcodedeployeast2', 'key': 'nginxtest.tar.gz', 'bundleType': 'tgz'}})

autoscaling group deployment
cdeploy_c.create_application(applicationName='CodeDeployAutoScalingApplication', computePlatform='Server', tags=[{'Key': 'Name', 'Value': 'CodeDeployAutoScalingApplication'}])

cdeploy_c.create_deployment_group(applicationName='CodeDeployAutoScalingApplication', deploymentGroupName='CodeDeployAutoScalingDeploymentGroup', deploymentConfigName='CodeDeployDefault.OneAtATime', serviceRoleArn='arn:aws:iam::141056581104:role/KsDevCodeDeploy', autoScalingGroups=['CodeDeployHostAutoScalingGroup'])

cdeploy_c.create_deployment(applicationName='CodeDeployAutoScalingApplication', deploymentGroupName='CodeDeployAutoScalingDeploymentGroup', deploymentConfigName='CodeDeployDefault.OneAtATime', targetInstances={'autoScalingGroups': ['CodeDeployHostAutoScalingGroup']}, revision={'revisionType': 'S3', 's3Location': {'bucket': 'ksdevcodedeployeast2', 'key': 'nginxtest.tar.gz', 'bundleType': 'tgz'}})

cdeploy_c.create_application(applicationName='CodeDeployAutoScalingApplication', computePlatform='Server', tags=[{'Key': 'Name', 'Value': 'CodeDeployAutoScalingApplication'}])

with one targetgroup, this will blocktraffic in one instance and then allow traffic
cdeploy_c.create_deployment_group(applicationName='CodeDeployAutoScalingApplication', deploymentGroupName='CodeDeployLoadBalancerDeploymentGroup', deploymentConfigName='CodeDeployDefault.OneAtATime', serviceRoleArn='arn:aws:iam::141056581104:role/KsDevCodeDeploy', autoScalingGroups=['CodeDeployAutoScalingGroup'], deploymentStyle={'deploymentType': 'IN_PLACE', 'deploymentOption': 'WITH_TRAFFIC_CONTROL'}, loadBalancerInfo={'targetGroupInfoList': [{'name': 'CodeDeployTargetGroup1'}]})

cdeploy_c.create_deployment(applicationName='CodeDeployAutoScalingApplication', deploymentGroupName='CodeDeployLoadBalancerDeploymentGroup', deploymentConfigName='CodeDeployDefault.OneAtATime', targetInstances={'autoScalingGroups': ['CodeDeployAutoScalingGroup']}, revision={'revisionType': 'S3', 's3Location': {'bucket': 'ksdevcodedeployeast2', 'key': 'nginxtest.tar.gz', 'bundleType': 'tgz'}})

blue green deployment, needs this IAM
{ "Version": "2012-10-17", "Statement": [ { "Action": [ "iam:PassRole", "ec2:RunInstances", "ec2:CreateTags" ], "Effect": "Allow", "Resource": "*" } ]}
cdeploy_c.create_deployment_group(applicationName='CodeDeployAutoScalingApplication', deploymentGroupName='CodeDeployLoadBalancerDeploymentGroup', deploymentConfigName='CodeDeployDefault.OneAtATime', serviceRoleArn='arn:aws:iam::141056581104:role/KsDevCodeDeploy', autoScalingGroups=['CodeDeployAutoScalingGroup'], deploymentStyle={'deploymentType': 'BLUE_GREEN', 'deploymentOption': 'WITH_TRAFFIC_CONTROL'}, blueGreenDeploymentConfiguration={'terminateBlueInstancesOnDeploymentSuccess': {'action': 'TERMINATE', 'terminationWaitTimeInMinutes': 1}, 'deploymentReadyOption': {'actionOnTimeout': 'CONTINUE_DEPLOYMENT'}, 'greenFleetProvisioningOption': {'action': 'COPY_AUTO_SCALING_GROUP'}}, loadBalancerInfo={'targetGroupInfoList': [{'name': 'CodeDeployTargetGroup1'}]})

cdeploy_c.create_deployment(applicationName='CodeDeployAutoScalingApplication', deploymentGroupName='CodeDeployLoadBalancerDeploymentGroup', deploymentConfigName='CodeDeployDefault.OneAtATime', revision={'revisionType': 'S3', 's3Location': {'bucket': 'ksdevcodedeployeast2', 'key': 'nginxtest.tar.gz', 'bundleType': 'tgz'}})

autoscaling, load balancer, two target groups, two listeners , this is for ECS
ecs_service must have deploymentController CODE_DEPLOY
aws s3 ls s3://ksdevcodedeployeast2  appspec.yml

cdeploy_c.create_application(applicationName='CodeDeployECSApplication', computePlatform='ECS', tags=[{'Key': 'Name', 'Value': 'CodeDeployECS'}])

cdeploy_c.create_deployment_group(applicationName='CodeDeployECSApplication', deploymentGroupName='CodeDeployECSDeploymentGroup', deploymentConfigName='CodeDeployDefault.ECSAllAtOnce', serviceRoleArn='arn:aws:iam::141056581104:role/KsDevCodeDeploy', deploymentStyle={'deploymentType': 'BLUE_GREEN', 'deploymentOption': 'WITH_TRAFFIC_CONTROL'}, blueGreenDeploymentConfiguration={'terminateBlueInstancesOnDeploymentSuccess': {'action': 'TERMINATE', 'terminationWaitTimeInMinutes': 1}, 'deploymentReadyOption': {'actionOnTimeout': 'CONTINUE_DEPLOYMENT'}}, ecsServices=[{'serviceName':  'MyECSService', 'clusterName': 'MyECSCluster'}], loadBalancerInfo={'targetGroupPairInfoList': [{'targetGroups': [{'name': 'MyECSTargetGroup'}, {'name': 'MyECSTargetGroup1'}], 'prodTrafficRoute': {'listenerArns': ['arn:aws:elasticloadbalancing:us-east-2:141056581104:listener/app/MyECSLoadBalancer/df4c4c42cfb5d982/1d328867a9a37772']}, 'testTrafficRoute': {'listenerArns': ['arn:aws:elasticloadbalancing:us-east-2:141056581104:listener/app/MyECSLoadBalancer/df4c4c42cfb5d982/1a3bb635d991c98f']}}]}) 

cdeploy_c.create_deployment(applicationName='CodeDeployECSApplication', deploymentGroupName='CodeDeployECSDeploymentGroup', deploymentConfigName='CodeDeployDefault.ECSAllAtOnce', revision={'revisionType': 'S3', 's3Location': {'bucket': 'ksdevcodedeployeast2', 'key': 'appspec.yml', 'bundleType': 'yaml'}})
