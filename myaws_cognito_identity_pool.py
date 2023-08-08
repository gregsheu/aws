import boto3

def create_authrole(role_name, identity_pool_id):
    print('Creating Role for Identity auth with S3 access...')
    auth_assume_role = '{ \
        "Version": "2012-10-17", \
            "Statement": [ \
                { \
                    "Effect": "Allow", \
                    "Principal": { \
                        "Federated": "cognito-identity.amazonaws.com" \
                    }, \
                    "Action": "sts:AssumeRoleWithWebIdentity", \
                    "Condition": { \
                        "StringEquals": { \
                            "cognito-identity.amazonaws.com:aud": "%s" \
                        }, \
                        "ForAnyValue:StringLike": { \
                            "cognito-identity.amazonaws.com:amr": "authenticated" \
                        } \
                    } \
                } \
            ] \
    }' % identity_pool_id
    iam_c = boto3.client('iam')
    resp = iam_c.create_role(RoleName=role_name, AssumeRolePolicyDocument=auth_assume_role)
    role_arn = resp['Role']['Arn']
    return role_arn

def create_unauthrole(role_name, identity_pool_id):
    print('Creating Role for Identity auth with S3 access...')
    unauth_assume_role = '{ \
        "Version": "2012-10-17", \
            "Statement": [ \
                { \
                    "Effect": "Allow", \
                    "Principal": { \
                        "Federated": "cognito-identity.amazonaws.com" \
                    }, \
                    "Action": "sts:AssumeRoleWithWebIdentity", \
                    "Condition": { \
                        "StringEquals": { \
                            "cognito-identity.amazonaws.com:aud": "%s" \
                        }, \
                        "ForAnyValue:StringLike": { \
                            "cognito-identity.amazonaws.com:amr": "unauthenticated" \
                        } \
                    } \
                } \
            ] \
    }' % identity_pool_id
    iam_c = boto3.client('iam')
    resp = iam_c.create_role(RoleName=role_name, AssumeRolePolicyDocument=unauth_assume_role)
    role_arn = resp['Role']['Arn']
    return role_arn

def create_authrolepolicy(policy_name):
    print('Creating Policy for Auth role...')
    role_policy = '{ \
            "Version": "2012-10-17", \
            "Statement": [{ \
            "Effect": "Allow", \
            "Action": [ \
            "mobileanalytics:PutEvents", \
            "cognito-sync:*", \
            "cognito-identity:*", \
            "s3:*" \
            ], \
            "Resource": [ "*" ] \
            }] \
            }'
    iam_c = boto3.client('iam')
    resp = iam_c.create_policy(PolicyName=policy_name, PolicyDocument=role_policy)
    policy_arn = resp['Policy']['Arn']
    return policy_arn

def create_unauthrolepolicy(policy_name):
    print('Creating Policy for Unauth role...')
    role_policy = '{ \
            "Version": "2012-10-17", \
            "Statement": [{ \
            "Effect": "Allow", \
            "Action": [ \
            "mobileanalytics:PutEvents", \
            "cognito-sync:*", \
            "s3:GetObject" \
            ], \
            "Resource": [ "*" ] \
            }] \
            }'
    iam_c = boto3.client('iam')
    resp = iam_c.create_policy(PolicyName=policy_name, PolicyDocument=role_policy)
    policy_arn = resp['Policy']['Arn']
    return policy_arn

def create_role_with_policy(role_name, policy_arn):
    print('Attaching %s policy to %s role...' % (policy_arn, role_name))
    iam_c = boto3.client('iam')
    iam_c.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

def create_pool(poolname):
    cog_i = boto3.client('cognito-identity')
    resp = cog_i.create_identity_pool(IdentityPoolName=poolname, AllowUnauthenticatedIdentities=True, AllowClassicFlow=True)
    identity_id = resp['IdentityPoolId']
    return identity_id

def attach_role(identity_id, auth_arn, unauth_arn):
    cog_i = boto3.client('cognito-identity')
    cog_i.set_identity_pool_roles(IdentityPoolId=identity_id, Roles={'authenticated': auth_arn, 'unauthenticated': unauth_arn})

def main():
    pool_id = create_pool('KsDevCognitoIdentityPool')
    auth_role_arn = create_authrole('KsDevAuthCognitoIdentity', pool_id)
    unauth_role_arn = create_unauthrole('KsDevUnauthCognitoIdentity', pool_id)
    auth_policy_arn = create_authrolepolicy('KsDevAuthCognitoIdentityPolicy') 
    unauth_policy_arn = create_unauthrolepolicy('KsDevUnauthCognitoIdentityPolicy') 
    create_role_with_policy('KsDevAuthCognitoIdentity', auth_policy_arn)
    create_role_with_policy('KsDevUnauthCognitoIdentity', unauth_policy_arn)
    attach_role(pool_id, auth_role_arn, unauth_role_arn)

if __name__ == '__main__':
    main()

