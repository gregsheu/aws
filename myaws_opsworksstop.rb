#!/usr/bin/ruby
require "json"
require "yaml"
require "aws-sdk"
#credreg = JSON.load(File.read("aws_key.json"))
myowsk = "MyOwStack"
mys3bucket = "elasticbeanstalk-ruby"
mys3key = "ruby.zip"
myawsvpc_id = ""
myawssecurity_id = ""
myawssubnets = {}
awsvpc_id = "" 
awssecurity_id = "" 
awssubnets = {}
lb_layer_id = ""
rails_layer_id = ""
db_layer_id = ""
credreg = YAML.load(File.read("aws_key.yml"))
Aws.config[:region] = credreg["Region"]
Aws.config[:credentials] = Aws::Credentials.new(credreg["AccessKeyId"], credreg["SecretAccessKey"])
iam = Aws::IAM::Client.new
iam.delete_instance_profile(instance_profile_name: "OpsWorksInstanceProfile")
#myow = Aws::OpsWorks::Client.new
#resp = myow.describe_layers
#resp.each do |l|
#    myow.delete_layer(layer_id: l.layer_id)
#end
#myow.stop_instance(instance_id: "474b67a3-f394-434b-9b96-f3c8599a54d2")
#myow.delete_instance(instance_id: "474b67a3-f394-434b-9b96-f3c8599a54d2", delete_volumes: true)
#myow.stop_instance(instance_id: "cb93fdf3-7e5e-448e-a13f-70320417d5e2", delete_volumes: true)
