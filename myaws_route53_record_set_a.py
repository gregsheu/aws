import boto3

route53_c = boto3.client('route53')
route53_c.change_resource_record_sets(HostedZoneId=hostedzoneid, ChangeBatch={'Comment': 'testing', 'Changes': [{'Action': 'CREATE', 'ResourceRecordSet': {'Name': 'map.kingsolarmaniot.com', 'Type': 'A', 'TTL': 300, 'ResourceRecords': [{'Value': '71.84.71.18'}]}}]})

#update a record set
route53_c.change_resource_record_sets(HostedZoneId=hostedzoneid, ChangeBatch={'Comment': 'testing', 'Changes': [{'Action': 'UPSERT', 'ResourceRecordSet': {'Name': 'map.kingsolarmaniot.com', 'Type': 'A', 'TTL': 300, 'ResourceRecords': [{'Value': '71.84.71.92'}]}}]})


route53_c.change_resource_record_sets(HostedZoneId=hostedzoneid, ChangeBatch={'Comment': 'testing', 'Changes': [{'Action': 'DELETE', 'ResourceRecordSet': {'Name': 'map.kingsolarmaniot.com', 'Type': 'A', 'TTL': 300, 'ResourceRecords': [{'Value': '71.84.71.92'}]}}]})
