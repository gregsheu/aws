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

def add_role_to_ec2profile(insprofile_name, role_name):
    iam_c = boto3.client('iam')
    iam_c.add_role_to_instance_profile(InstanceProfileName=insprofile_name, RoleName=role_name) 

def main():
    #profile_name = 'EC2FrontEndProfile'
    #role_name = 'EC2FrontEndRole'
    profile_name = 'EC2ECSProfile'
    role_name = 'EC2ECSRole'
    create_myec2_insprofile(profile_name)
    #create_myrole(role_name)
    ##policy_arn = create_myrolepolicy(policy_name)

    ##We'll just use AWS S3 full access policy arn
    #policy_arn = 'arn:aws:iam::aws:policy/AmazonS3FullAccess'
    #create_role_with_policy(role_name, policy_arn)
 
    ##We'll just use AWS EC2 full access policy arn
    #policy_arn = 'arn:aws:iam::aws:policy/AmazonEC2FullAccess'
    #create_role_with_policy(role_name, policy_arn)
 
    ##We'll just use AWS SSM full access policy arn
    #policy_arn = 'arn:aws:iam::aws:policy/AmazonSSMFullAccess'
    #create_role_with_policy(role_name, policy_arn)
 
    ##We'll just use AWS CloudTrail full access policy arn
    #policy_arn = 'arn:aws:iam::aws:policy/AWSCloudTrailFullAccess'
    #create_role_with_policy(role_name, policy_arn)

    #add_role_to_ec2profile(profile_name, role_name)

    #profile_name = 'EC2BackEndProfile'
    #role_name = 'EC2BackEndRole'
    #create_myec2_insprofile(profile_name)
    #create_myrole(role_name)
 
    ##We'll just use AWS S3 full access policy arn
    #policy_arn = 'arn:aws:iam::aws:policy/AmazonS3FullAccess'
    #create_role_with_policy(role_name, policy_arn)
 
    ##We'll just use AWS EC2 full access policy arn
    #policy_arn = 'arn:aws:iam::aws:policy/AmazonEC2FullAccess'
    #create_role_with_policy(role_name, policy_arn)
 
    ##We'll just use AWS SSM full access policy arn
    #policy_arn = 'arn:aws:iam::aws:policy/AmazonSSMFullAccess'
    #create_role_with_policy(role_name, policy_arn)
 
    ##We'll just use AWS CloudTrail full access policy arn
    #policy_arn = 'arn:aws:iam::aws:policy/AWSCloudTrailFullAccess'
    #create_role_with_policy(role_name, policy_arn)

    ##We'll just use AWS RDS full access policy arn
    #policy_arn = 'arn:aws:iam::aws:policy/AmazonRDSFullAccess'
    #create_role_with_policy(role_name, policy_arn)

    ##We'll just use AWS DynamoDB full access policy arn
    #policy_arn = 'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess'

    #create_role_with_policy(role_name, policy_arn)

    add_role_to_ec2profile(profile_name, role_name)

if __name__ == '__main__':
    main()
