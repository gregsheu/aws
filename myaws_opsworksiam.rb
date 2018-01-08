#!/usr/bin/ruby
require "json"
require "yaml"
require "aws-sdk"
#credreg = JSON.load(File.read("aws_key.json"))
credreg = YAML.load(File.read("aws_key.yml"))
Aws.config[:region] = credreg["Region"]
Aws.config[:credentials] = Aws::Credentials.new(credreg["AccessKeyId"], credreg["SecretAccessKey"])
opsworks_policy_name = ""
opsworks_policy_document = ""
opsworks_ow_arn = ""
opsworks_ec2_arn = ""
opsworks_version_id = ""
iam = Aws::IAM::Client.new
begin
    #iam.remove_role_from_instance_profile(instance_profile_name: "OpsWorksInstanceProfile", role_name: "OpsWorksRole")
    #iam.delete_instance_profile(instance_profile_name: "OpsWorksInstanceProfile")
    #iam.delete_role(role_name: "OpsWorksRole")
    resp = iam.list_policies(scope: "AWS", only_attached: false, path_prefix: "/", max_items: 200)
    resp.policies.each do |r|
        #opsworks_policy_name = r["policy_name"] if r["policy_name"] =~ /AWSOpsWorksFull/
        opsworks_ow_arn = r["arn"] if r["arn"] =~ /AWSOpsWorksFull/
        opsworks_ec2_arn = r["arn"] if r["arn"] =~ /AmazonEC2FullAccess/
    end
    resp = iam.list_policy_versions(policy_arn: opsworks_ow_arn)
    opsworks_version_id = resp.versions[0]["version_id"]
    resp = iam.get_policy_version(policy_arn: opsworks_ow_arn, version_id: opsworks_version_id)
    opsworks_policy_document = resp.policy_version.document
    opsworks_policy_ec2_document = '{
        "Version": "2008-10-17",
        "Statement": [{
        "Effect": "Allow",
        "Principal": {
        "Service": ["ec2.amazonaws.com"]
            },
        "Action": ["sts:AssumeRole"]
        }]
    }'
    opsworks_policy_document = '{
        "Version" : "2008-10-17",
        "Statement": [{
        "Effect": "Allow",
        "Principal": {
        "Service": ["opsworks.amazonaws.com"]
            },
        "Action": ["sts:AssumeRole"]
        }]
    }'
    puts "Creating OpsWorksEC2Role with policy #{opsworks_policy_ec2_document}"
    resp = iam.create_role(role_name: "OpsWorksEC2Role", assume_role_policy_document: opsworks_policy_ec2_document)
    puts "Creating OpsWorksRole with policy #{opsworks_policy_document}"
    resp = iam.create_role(role_name: "OpsWorksRole", assume_role_policy_document: opsworks_policy_document)
    puts "Attaching OpsWorksRole with policy #{opsworks_ow_arn}"
    resp = iam.attach_role_policy(role_name: "OpsWorksRole", policy_arn: opsworks_ow_arn)
    puts "Attaching OpsWorksRole with policy #{opsworks_ec2_arn}"
    resp = iam.attach_role_policy(role_name: "OpsWorksRole", policy_arn: opsworks_ec2_arn)
    puts "Creating OpsWorksInstanceProfile"
    resp = iam.create_instance_profile(instance_profile_name: "OpsWorksInstanceProfile")
    puts "Adding OpsWorksRole to OpsWorksInstanceProfile"
    resp = iam.add_role_to_instance_profile(instance_profile_name: "OpsWorksInstanceProfile", role_name: "OpsWorksEC2Role")
    p iam.list_instance_profiles

rescue Aws::IAM::Errors::ServiceError => errors_msg
    puts errors_msg
end
