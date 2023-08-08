import boto3

def verify_domain(domain_name):
    print('Verifying domain name %s...' % domain_name)
    ses_c = boto3.client('ses')
    resp = ses_c.verify_domain_dkim(Domain=domain_name)
    dkims = resp['DkimTokens']
    return dkims

def verify_email(email_address):
    print('Verifying email address %s...' % email_address)
    ses_c = boto3.client('ses')
    resp = ses_c.verify_email_address(EmailAddress=email_address)

def get_hosted_id(domain_name):
    r53_c = boto3.client('route53')
    resp = r53_c.list_hosted_zones_by_name(DNSName=domain_name)
    hostedzoneid = resp['HostedZones'][0]['Id'].split('/')[2]
    print(hostedzoneid)
    return hostedzoneid
    
def create_dkim_cname(dkims, hostedzoneid):
    print('Creating cname %s...' % dkims)
    r53_c = boto3.client('route53')
    for i in dkims:
        r53_c.change_resource_record_sets(HostedZoneId=hostedzoneid, ChangeBatch={'Comment': 'King Solarman IoT SES', 'Changes': [{'Action': 'CREATE', 'ResourceRecordSet': {'Name': i+'._domainkey.kingsolarmaniot.com', 'Type': 'CNAME', 'TTL': 300, 'ResourceRecords': [{'Value': i+'.dkim.amazonses.com'}]}}]})

def get_txt(domain_name):
    ses_c = boto3.client('ses')
    waiter = ses_c.get_waiter('identity_exists')
    waiter.wait(Identities=[domain_name], WaiterConfig={'Delay': 30, 'MaxAttempts': 3})
    resp = ses_c.get_identity_verification_attributes(Identities=[domain_name])
    txt_record = resp['VerificationAttributes'][domain_name]['VerificationToken']
    return txt_record

def create_txt_cname(txt_record, domain_name, hostedzoneid):
    print('Creating txt %s...' % txt_record)
    r53_c = boto3.client('route53')
    r53_c.change_resource_record_sets(HostedZoneId=hostedzoneid, ChangeBatch={'Comment': 'King Solarman IoT SES', 'Changes': [{'Action': 'CREATE', 'ResourceRecordSet': {'Name': txt_record+'_amazonses.'+domain_name, 'Type': 'TXT', 'TTL': 300, 'ResourceRecords': [{'Value': '\"'+txt_record+'\"'}]}}]})

def send_test_email(source_email):
    print('Sending test email from %s...' % source_email)
    toaddresses = ['kingsolarman88@gmail.com']
    ccaddresses = ['kingsolarman88@gmail.com', 'success@simulator.amazonses.com']
    bccaddresses = ['kingsolarman88@gmail.com']
    subject = 'Testing AWS SES'
    body = 'Testing a email from AWS SES'
    ses_c = boto3.client('ses')
    ses_c.send_email(Source=source_email, Destination={'ToAddresses': toaddresses, 'CcAddresses': ccaddresses, 'BccAddresses': bccaddresses}, Message={'Subject': {'Data': subject}, 'Body': {'Text': {'Data': body}, 'Html': {'Data': body}}}, ReplyToAddresses=[source_email])

def update_ses_account():
    print('Updating account to production enabled...')
    sesv2_c = boto3.client('sesv2')
    sesv2_c.put_account_details(MailType='TRANSACTIONAL', WebsiteURL='www.kingsolarmaniot.com', ContactLanguage='EN', UseCaseDescription='Sending emails through AWS SES', ProductionAccessEnabled=True)

def main():
    domain_name = 'kingsolarmaniot.com'
    email_address = 'greg@king-solarman.com'
    #hostedzoneid = get_hosted_id(domain_name)
    #dkims = verify_domain(domain_name)
    #create_dkim_cname(dkims, hostedzoneid)
    #txt_record = get_txt(domain_name)
    #create_txt_cname(txt_record, domain_name, hostedzoneid)
    #verify_email(email_address)
    send_test_email(email_address)
    #update_ses_account()

if __name__ == '__main__':
    main()
