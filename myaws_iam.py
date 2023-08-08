import boto3

#Run this script to create user and add to the group accordingly and then run the myaws_iam_en_mfa.py
client = boto3.client('iam')
myuser = "sheu"
mygroup = "admin"
admin_group_policy_document = '{\
    "Version": "2012-10-17",\
    "Statement":[{\
    "Effect": "Allow",\
    "Action": "*",\
    "Resource": "*"\
    }]\
}'
resp = client.create_user(UserName=myuser)
resp = client.create_login_profile(UserName=myuser, Password="Az12345678!", PasswordResetRequired=True)
resp = client.create_access_key(UserName=myuser)
myaccess_key = resp['AccessKey']['AccessKeyId']
mysecret_access_key = resp['AccessKey']['SecretAccessKey']
#resp = client.create_group(GroupName=mygroup)
resp = client.add_user_to_group(GroupName=mygroup, UserName=myuser)
#resp = client.create_policy(PolicyName="admin_group_policy", PolicyDocument=admin_group_policy_document)
#mypolicy_arn = resp['Policy']['Arn']
#resp = client.attach_group_policy(GroupName=mygroup, PolicyArn=mypolicy_arn)
print('AccessKeyId: %s' % myaccess_key)
print('SecretAccessKey %s' % mysecret_access_key)
with open('ksgsheu.key', 'w') as key:
    key.write('AccessKeyId: %s' % myaccess_key)
    key.write('\n')
    key.write('SecretAccessKey: %s' % mysecret_access_key)
    key.write('\n')
resp = client.update_account_password_policy(MinimumPasswordLength=8, RequireSymbols=False, RequireNumbers=True, RequireUppercaseCharacters=True, RequireLowercaseCharacters=True, AllowUsersToChangePassword=True, MaxPasswordAge=90, PasswordReusePrevention=1, HardExpiry=True)
