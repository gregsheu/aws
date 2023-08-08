import boto3

efs_c = boto3.client('efs')
resp = efs_c.create_file_system(PerformanceMode='generalPurpose', ThroughputMode='provisioned', ProvisionedThroughputInMibps=128, AvailabilityZoneName='us-east-2a', Tags=[{'Key': 'Name', 'Value': 'Dev1EfsEcsEast2'}])
print(resp)
