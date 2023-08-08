import boto3

client = boto3.client('ec2')
resp = client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
for i in resp['Reservations']:
    print(i['Instances'][0]['InstanceId'])
    print(i['Instances'][0]['PrivateDnsName'])
    print(i['Instances'][0]['PrivateIpAddress'])
    print(i['Instances'][0]['PublicDnsName'])

#for i in resp['Reservations']:
#    for k, v in i['Instances'][0].items():
#        print(k, v)
