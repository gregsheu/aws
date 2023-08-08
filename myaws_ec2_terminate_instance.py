import boto3

client = boto3.client('ec2')
resp = client.terminate_instances(InstanceIds=['i-056cce99729d8cf8a'])
print(resp)
