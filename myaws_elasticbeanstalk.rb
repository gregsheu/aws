#!/usr/bin/ruby
##Author: Greg Sheu, gregsheu@yahoo.com
##The automation of creating AWS Elasticbeanstalk in my VPC
require 'json'
require 'yaml'
require 'aws-sdk'
myebapp = "MyEbPythonAppTest"
myebver = "v1.0"
myebenv = "MyEbDevTest"
mys3bucket = "elasticbeanstalk-python"
mys3key = "python.zip"
myvpc_id = ""
mysecurity_id = ""
mysubnets = {}
credreg = YAML.load(File.read('aws_key.yml'))
Aws.config[:region] = credreg['Region']
Aws.config[:credentials] = Aws::Credentials.new(credreg['AccessKeyId'], credreg['SecretAccessKey'])
ec2 = Aws::EC2::Client.new
resp = ec2.describe_vpcs
resp[:vpcs].each do |v|
    v[:tags].each {|vv| myvpc_id = v[:vpc_id] if vv[:value] =~ /myawsvpc/}
end
#myvpc_id = resp[:vpcs][0][:vpc_id]
resp = Aws::EC2::Vpc.new(myvpc_id)
resp.tags.each do |v|
    puts v[:value]
end
i = 0
resp.subnets.each do |sn|
    sn.tags.each do |v|
        mysubnets[v[:value]] = sn.subnet_id
        i = i + 1
    end
end
resp.security_groups.each do |sg|
    mysecurity_id = sg.group_id
end
puts myvpc_id
puts mysecurity_id
mysubnets.each {|k, v| puts k + " " + v}
myeb = Aws::ElasticBeanstalk::Client.new
myeb.create_application(application_name: myebapp, description: "My Eb Python App")
myeb.create_application_version(application_name: myebapp, version_label: myebver, source_bundle: {s3_bucket: mys3bucket, s3_key: mys3key})
s3 = Aws::S3::Client.new
#resp = s3.create_bucket(bucket: "elasticbeanstalk-python")
myfile_name = "python.zip"
myfile = File.new("/home/greg/python.zip")
resp = s3.create_multipart_upload(bucket: "elasticbeanstalk-python", key: myfile_name)
myupload_id = resp[:upload_id]
resp = s3.upload_part(bucket: "elasticbeanstalk-python", key: myfile_name, part_number: 1, upload_id: myupload_id, body: myfile)
myetag = resp[:etag]
resp = s3.complete_multipart_upload(bucket: "elasticbeanstalk-python", key: myfile_name, multipart_upload: {parts: [{etag: myetag, part_number: 1}]}, upload_id: myupload_id)
#resp = s3.delete_bucket(bucket: "/elasticbeanstalk-python")
myeb.create_environment(application_name: myebapp, environment_name: myebenv, solution_stack_name: "64bit Amazon Linux 2015.03 v1.3.1 running Python 3.4", option_settings: [{\
    namespace: "aws:autoscaling:launchconfiguration", \
    option_name: "EC2KeyName", \
    value: "gregkey" \
    }, {\
    namespace: "aws:ec2:vpc", \
    option_name: "VPCID", \
    value: myvpc_id \
    }, {\
    namespace: "aws:ec2:vpc", \
    option_name: "Subnets", \
    value: mysubnets["private_subnet"] \
    }, {\
    namespace: "aws:ec2:vpc", \
    option_name: "ELBSubnets", \
    value: mysubnets["public_subnet"] \
    }, {\
    namespace: "aws:autoscaling:launchconfiguration", \
    option_name: "InstanceType", \
    value: "m1.small" \
    }, {\
    namespace: "aws:autoscaling:launchconfiguration", \
    option_name: "SecurityGroups", \
    value: mysecurity_id \
    }])
