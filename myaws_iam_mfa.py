import boto3

client = boto3.client('iam')
myuser = "greg"
resp = client.create_virtual_mfa_device(VirtualMFADeviceName='WEAAJ456LZS4A3QDU5FAQ')
serial_number = resp['VirtualMFADevice']['SerialNumber']
print(serial_number)
#print(base64.b32decode(resp['VirtualMFADevice']['Base32StringSeed']))
string_seed = resp['VirtualMFADevice']['Base32StringSeed']
print(string_seed)
with open('%s.png' % myuser, 'wb') as f:
    f.write(resp['VirtualMFADevice']['QRCodePNG'])
#resp = client.delete_virtual_mfa_device(SerialNumber=serial_number)
#print(resp)
resp = client.list_mfa_devices()
print(resp)
resp = client.list_virtual_mfa_devices()
print(resp)
