import boto3

def get_launch_template_ids():
    template_ids = []
    ec2_c = boto3.client('ec2')
    resp = ec2_c.describe_launch_templates()
    for i in resp['LaunchTemplates']:
        #if 'MAP' in i['LaunchTemplateName'] or 'GPS' in i['LaunchTemplateName']:
        if 'GPS' in i['LaunchTemplateName']:
            template_ids.append(i['LaunchTemplateId'])
    return template_ids

def remove_launch_template(template_id):
    print('Deleting %s ...' % template_id)
    ec2_c = boto3.client('ec2')
    ec2_c.delete_launch_template(LaunchTemplateId=template_id)
    print('%s deleted.' % template_id)

def main():
    template_ids = get_launch_template_ids()
    for i in template_ids:
        remove_launch_template(i)

if __name__ == '__main__':
    main()
