import boto3

ec2_c = boto3.client('ec2')
launch_template_id = 'lt-03ce61527ced7b891'
#resp = ec2_c.run_instances(ImageId='ami-0603cbe34fd08cb81', InstanceType='t2.xlarge', KeyName='gregkey', SubnetId='subnet-0457db0c26252a75a', SecurityGroupIds=['sg-0e1515c1659fe6b42'], MinCount=1, MaxCount=1, Monitoring={'Enabled': True}, TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': 'myawsvpc2_pri1_ffmpeg'}]}])
#print('Running on VPC ' + resp['Instances'][0]['VpcId'])
#print('The instance id ' + resp['Instances'][0]['InstanceId'])
#print('The private IP ' + resp['Instances'][0]['NetworkInterfaces'][0]['PrivateIpAddresses'][0]['PrivateIpAddress'])
ec2_c.run_instances(LaunchTemplate={'LaunchTemplateId': launch_template_id, 'Version': '$Latest'}, MinCount=1, MaxCount=1)
