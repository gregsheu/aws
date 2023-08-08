import boto3
import pyotp 
import datetime

#Run this script after running myaws_iam.py
client = boto3.client('iam')
myuser = "greg"
#The VirtualMFADeviceName='WEARJ456LZS4O30DU510Q', just uses a random strings
resp = client.create_virtual_mfa_device(VirtualMFADeviceName='WEARJ456LZS4O30DU510Q')
#resp = client.list_virtual_mfa_devices(AssignmentStatus='Unassigned')
serial_number = resp['VirtualMFADevice']['SerialNumber']
print(serial_number)
string_seed = resp['VirtualMFADevice']['Base32StringSeed']
print(string_seed)
with open('%s.png' % myuser, 'wb') as f:
    f.write(resp['VirtualMFADevice']['QRCodePNG'])
totp = pyotp.TOTP(string_seed)
#first code
code1 = totp.generate_otp(totp.timecode(datetime.datetime.now() - datetime.timedelta(seconds=30)))
#the current code
code2 = totp.generate_otp(totp.timecode(datetime.datetime.now()))
resp = client.enable_mfa_device(UserName=myuser, SerialNumber=serial_number, AuthenticationCode1=code1, AuthenticationCode2=code2)

#it was working before
#resp = client.list_virtual_mfa_devices(AssignmentStatus='Unassigned')
#serial_number = resp['VirtualMFADevices'][0]['SerialNumber']
#print(serial_number)
#string_seed = resp['VirtualMFADevices'][0]['Base32StringSeed']
#print(string_seed)
