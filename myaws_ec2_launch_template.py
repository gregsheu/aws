from operator import itemgetter, attrgetter
import sys
import boto3

def get_latest_ami():
    images = []
    ec2_c = boto3.client('ec2')
    #resp = ec2_c.describe_images(Owners=['amazon'], Filters=[{'Name': 'owner-alias', 'Values': ['amazon']}, {'Name': 'name', 'Values': ['amzn2-ami-hvm*2020*gp2']}, {'Name': 'is-public', 'Values': ['true']}, {'Name': 'virtualization-type', 'Values': ['hvm']}, {'Name': 'architecture', 'Values': ['x86_64']}])
    resp = ec2_c.describe_images(Owners=['amazon'], Filters=[{'Name': 'owner-alias', 'Values': ['amazon']}, {'Name': 'name', 'Values': ['*ecs-hvm*']}, {'Name': 'is-public', 'Values': ['true']}, {'Name': 'virtualization-type', 'Values': ['hvm']}, {'Name': 'architecture', 'Values': ['x86_64']}])
    for i in resp['Images']:
        images.append((i['ImageId'], i['CreationDate']))
    images2 = sorted(images, key=itemgetter(1), reverse=True)
    ami_id = images2[0][0]
    #print(images2[0][0], images2[0][1])
    #print(images2)
    return  ami_id

def lets_createlt(myawsvpc, ami_id, key_name):
    mysg_id = None
    mysubnets = []
    mysubnets_tags = {}
    myroutetables = []
    ec2_c = boto3.client('ec2')
    for s in myawsvpc.security_groups.all():
        mysg_id = s.id
    for s in myawsvpc.subnets.all():
        mysubnets.append(s.id)
    for r in myawsvpc.route_tables.all():
        myroutetables.append(r.route_table_id)
    resp = ec2_c.describe_subnets(SubnetIds=mysubnets)
    for s in resp['Subnets']:
        mysubnets_tags.update({s['SubnetId']: s['Tags']})
    #print(mysubnets_tags[mysubnets[0]][0]['Value'])
    #for i in mysubnets:
    for k, v in mysubnets_tags.items():
        #print(k, v)
        if 'Pri' in v[0]['Value']:
            iam_profile = 'EC2BackEndProfile'
            subnetid = k
        else:
            iam_profile = 'EC2FrontEndProfile'
            subnetid = k
        resp = ec2_c.create_launch_template(
            LaunchTemplateData={
                'ImageId': ami_id,
                'InstanceType': 't3.large',
                'IamInstanceProfile': {
                    #'Arn':,
                    'Name': iam_profile
                    },
                #'SecurityGroupIds': [mysg_id],
                'KeyName': key_name,
                'Monitoring': {'Enabled': True},
                'NetworkInterfaces': [
                    {
                        'DeviceIndex': 0,
                        'Groups': [mysg_id],
                        'SubnetId': subnetid
                        }
                   ],
                'TagSpecifications': [
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'I-'+v[0]['Value'][8:len(v[0]['Value'])]
                                #'Value': 'Instance'+mysubnets_tags[i][0]['Value'][9:len(mysubnets_tags[i][0]['Value'])]
                                }
                            ]
                        }
                    ]
                },
            LaunchTemplateName='MyECS' + v[0]['Value'] + 'LaunchTemplate',
            VersionDescription='MyECS' + v[0]['Value'] + 'LaunchTemplateV1',
            #LaunchTemplateName=mysubnets_tags[i][0]['Value'] + 'LaunchTemplate',
            #VersionDescription=mysubnets_tags[i][0]['Value'] + 'LaunchTemplateV1',
        )
        launch_template_id = resp['LaunchTemplate']['LaunchTemplateId']
        print(launch_template_id)

def main():
    myvpcid = sys.argv[1]
    ec2 = boto3.resource('ec2')
    ami_id = get_latest_ami()
    print(ami_id)
    key_name = 'gregkey'
    myawsvpc = ec2.Vpc(myvpcid)
    lets_createlt(myawsvpc, ami_id, key_name)

if __name__ == '__main__':
    main()
