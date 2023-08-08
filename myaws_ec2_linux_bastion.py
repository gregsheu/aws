import boto3
import base64

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

def create_scaling_group(launch_template_id, subnet_id, auto_scaling_group_name):
    as_c = boto3.client('autoscaling')
    as_c.create_auto_scaling_group(
        AutoScalingGroupName=auto_scaling_group_name,
        LaunchTemplate={'LaunchTemplateId': launch_template_id, 'Version': '$Latest'},
        MinSize=1,
        MaxSize=4,
        VPCZoneIdentifier=subnet_id,
        Tags=[
            {
                'Key': 'Name',
                'Value': 'CodeDeployHostAutoScalingGroup'
                },
            ]
    )
#resp = as_c.describe_auto_scaling_groups(AutoScalingGroupNames=['BastionHostAutoScalingGroup'])
#target_instance_ids = []
#for i in resp['AutoScalingGroups'][0]['Instances']:
#    target_instance_ids.append(i['InstanceId'])
#print(target_instance_ids)
def main():
    #subnet_id = 'subnet-4c47d700'
    subnet_id = 'subnet-0d090745add7c4bf1'
    #image_id = 'ami-0603cbe34fd08cb81'
    image_id = 'ami-0fa49cc9dc8d62c84'
    #security_group_id = 'sg-c8e0d0ae'
    security_group_id = 'sg-0a0eade025d59923d'
    key_name = 'gregkey'
    userdata = 'nginxtest/userdata.txt'
    template_id = get_template_id(image_id, security_group_id, subnet_id, key_name, userdata)
    print('Launch Template %s created.' % template_id)
    auto_scaling_group_name = 'CodeDeployHostAutoScalingGroup'
    create_scaling_group(template_id, subnet_id, auto_scaling_group_name)
    print('AutoScalingGroup %s created.' % auto_scaling_group_name)
    print('Done')

if __name__ == '__main__':
    main()
