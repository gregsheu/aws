from operator import itemgetter
import base64
import sys
import boto3

def get_latest_ami():
    images = []
    ec2_c = boto3.client('ec2')
    resp = ec2_c.describe_images(Owners=['amazon'], Filters=[{'Name': 'owner-alias', 'Values': ['amazon']}, {'Name': 'name', 'Values': ['amzn2-ami-hvm*2020*gp2']}, {'Name': 'is-public', 'Values': ['true']}, {'Name': 'virtualization-type', 'Values': ['hvm']}, {'Name': 'architecture', 'Values': ['x86_64']}])
    for i in resp['Images']:
        images.append((i['ImageId'], i['CreationDate']))
    images2 = sorted(images, key=itemgetter(1), reverse=True)
    ami_id = images2[0][0]
    #print(images2[0][0], images2[0][1])
    #print(images2)
    return  ami_id

def lets_createlt(myawsvpc, ami_id, key_name, userdata):
    mysg_id = None
    mysubnets = []
    mysubnets_tags = {}
    myroutetables = []
    f = open(userdata, 'rb')
    base64string = base64.b64encode(f.read())
    base64string = base64string.decode('utf-8')
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
                    'UserData': base64string,
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
                #Userdata name is named in userdatagps.txt and userdatamap.txt, GPS & MAP
                LaunchTemplateName=v[0]['Value'] + 'LaunchTemplate' + userdata[-7:-4].upper(),
                VersionDescription=v[0]['Value'] + 'LaunchTemplateV2',
            )
            launch_template_id = resp['LaunchTemplate']['LaunchTemplateId']
            print(launch_template_id)

def main():
    myvpcid = sys.argv[1]
    ec2 = boto3.resource('ec2')
    ami_id = get_latest_ami()
    key_name = 'gregkey'
    myawsvpc = ec2.Vpc(myvpcid)
    userdata = './userdatagps.txt'
    lets_createlt(myawsvpc, ami_id, key_name, userdata)
    #userdata = './userdatamap.txt'
    #lets_createlt(myawsvpc, ami_id, key_name, userdata)

if __name__ == '__main__':
    main()
