import boto3

def delete_scaling_group(auto_scaling_group_name):
    as_c = boto3.client('autoscaling')
    resp = as_c.delete_auto_scaling_group(AutoScalingGroupName=auto_scaling_group_name, ForceDelete=True)
    print('AutoScalingGroup %s deleted.' % auto_scaling_group_name) 

def delete_template_id():
    ec2_c = boto3.client('ec2')
    resp = ec2_c.describe_launch_templates()
    launch_template_id = resp['LaunchTemplates'][0]['LaunchTemplateId']
    ec2_c.delete_launch_template(LaunchTemplateId=launch_template_id)
    print('LaunchTemplate %s deleted' % launch_template_id)


def main():
    scaling_group_name = 'BastionHostAutoScalingGroup'
    delete_scaling_group(scaling_group_name)
    delete_template_id()
    print('Done')

if __name__ == '__main__':
    main()
