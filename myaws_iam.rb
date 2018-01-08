#!/usr/bin/ruby
require 'json'
require 'yaml'
require 'aws-sdk'
#credreg = JSON.load(File.read('aws_key.json'))
credreg = YAML.load(File.read('aws_key.yml'))
Aws.config[:region] = credreg['Region']
Aws.config[:credentials] = Aws::Credentials.new(credreg['AccessKeyId'], credreg['SecretAccessKey'])
myuser = "gsheu"
mygroup = "admins"
admins_group_policy_document = '{
    "Version": "2012-10-17",
    "Statement":[{ 
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
    }]
}'
iam = Aws::IAM::Client.new
begin
resp = iam.create_user(user_name: myuser)
resp = iam.create_login_profile(user_name: myuser, password: "A12345678Z", password_reset_required: true)
resp = iam.create_access_key(user_name: myuser)
myaccess_key = resp[:access_key][:access_key_id]
mysecret_access_key = resp[:access_key][:secret_access_key]
resp = iam.create_group(group_name: mygroup)
resp = iam.add_user_to_group(group_name: mygroup, user_name: myuser)
resp = iam.create_policy(policy_name: "admins_group_policy", policy_document: admins_group_policy_document)
mypolicy_arn = resp[:policy][:arn]
resp = iam.attach_group_policy(group_name: mygroup, policy_arn: mypolicy_arn)
puts "AccessKeyId: #{myaccess_key}"
puts "SecretAccessKey: #{mysecret_access_key}"
rescue Aws::IAM::Errors::ServiceError => errors_msg
    puts errors_msg
end
mykey_file = File.new("myaws.yml", "wb")
mykey_file.write("AccessKeyId: #{myaccess_key}")
mykey_file.write("SecretAccessKey: #{mysecret_access_key}")
mykey_file.chmod(0600)
mykey_file.close
resp = iam.update_account_policy(minimum_password_length: 8, require_symbols: true, require_numbers: true, require_uppercase_characters: true, require_lowercase_characters: true, allow_users_to_change_password: true, max_password_age: 90, password_reuse_prevention: 1, hard_expiry: true)
#begin
#  do stuff
#rescue Aws::EC2::Errors::ServiceError
#  rescues all errors returned by Amazon Elastic Compute Cloud
#end
