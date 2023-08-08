import boto3

def create_myrole(role_name):
    print('Creating Role for EC2 with full S3 access...')
    assume_role = '{ \
        "Version": "2012-10-17", \
        "Statement": { \
            "Effect": "Allow", \
            "Principal": {"Service": "ec2.amazonaws.com"}, \
            "Action": "sts:AssumeRole" \
        } \
    }'
    iam_c = boto3.client('iam')
    resp = iam_c.create_role(RoleName=role_name, AssumeRolePolicyDocument=assume_role)
    role_arn = resp['Role']['Arn']
    return role_arn

def create_myrolepolicy(policy_name):
    print('Creating Policy for that role...')
    role_policy = '{ \
        "Version": "2012-10-17", \
        "Statement": { \
            "Effect": "Allow", \
            "Action": "s3:*", \
            "Resource": "*" \
        } \
    }'
    iam_c = boto3.client('iam')
    resp = iam_c.create_policy(PolicyName=policy_name, PolicyDocument=role_policy)
    policy_arn = resp['Policy']['Arn']
    return policy_arn

def create_role_with_policy(role_name, policy_arn):
    print('Attaching policy to the role...')
    iam_c = boto3.client('iam')
    iam_c.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

def create_myec2_insprofile(insprofile_name):
    iam_c = boto3.client('iam')
    iam_c.create_instance_profile(InstanceProfileName=insprofile_name)

def add_myec2_s3role(insprofile_name, role_name):
    iam_c = boto3.client('iam')
    iam_c.add_role_to_instance_profile(InstanceProfileName=insprofile_name, RoleName=role_name) 

def main():
    role_name = 'EC2S3Role'
    policy_name = 'EC2S3Policy'
    profile_name = 'EC2S3Profile'
    create_myrole(role_name)
    policy_arn = create_myrolepolicy(policy_name)
    #We'll just use AWS S3 full access policy arn
    policy_arn = 'arn:aws:iam::aws:policy/AmazonS3FullAccess'
    create_role_with_policy(role_name, policy_arn)
    create_myec2_insprofile(profile_name)
    add_myec2_s3role(profile_name, role_name)

if __name__ == '__main__':
    main()
