import boto3

client = boto3.client('iam')
dak_resp = client.delete_access_key(UserName='root', AccessKeyId='AKIAITAQ3RV4IKNJW2DA')
