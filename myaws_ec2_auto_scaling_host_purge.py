import boto3

def del_autoscaling(groupname):
    print('Deleting Auto scaling groups...')
    as_c = boto3.client('autoscaling')
    as_c.delete_auto_scaling_group(AutoScalingGroupName=groupname, ForceDelete=True)
    as_c.delete_auto_scaling_group(AutoScalingGroupName=groupname, ForceDelete=True)
    print('Auto scaling group deleted')

def del_load_balancer():
    print('Deleting Load balancers...')
    elbv2_c = boto3.client('elbv2')
    resp = elbv2_c.describe_load_balancers()
    #lb_arn = resp['LoadBalancers'][0]['LoadBalancerArn']
    for i in resp['LoadBalancers']:
        lb_arn = i['LoadBalancerArn']
        elbv2_c.delete_load_balancer(LoadBalancerArn=lb_arn)
        waiter = elbv2_c.get_waiter('load_balancers_deleted')
        print('Waiting for Load Balancer to be deleted')
        waiter.wait(LoadBalancerArns=[lb_arn], WaiterConfig={'Delay': 60, 'MaxAttempts': 10})
        print('Load balancer deleted')

def del_target_group():
    print('Deleting Target group...')
    elbv2_c = boto3.client('elbv2')
    resp = elbv2_c.describe_target_groups()
    #target_group_arn = resp['TargetGroups'][0]['TargetGroupArn']
    for i in resp['TargetGroups']:
        target_group_arn = i['TargetGroupArn']
        elbv2_c.delete_target_group(TargetGroupArn=target_group_arn)
    print('Target group deleted...')

def main():
    groupname = 'GpsAutoScalingGroup'
    del_autoscaling(groupname)
    groupname = 'MapAutoScalingGroup'
    del_autoscaling(groupname)
    del_load_balancer()
    del_target_group()

if __name__ == '__main__':
    main()
