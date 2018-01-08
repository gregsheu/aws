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
myawssecurity = ""
myawssubnets = {}
awsvpc_id = "" 
awssecurity_id = "" 
awssubnets = {}
lb_layer_id = ""
rails_layer_id = ""
db_layer_id = ""
lb_security_groups = []
rails_security_groups = []
db_security_groups = []
credreg = YAML.load(File.read("aws_key.yml"))
Aws.config[:region] = credreg["Region"]
Aws.config[:credentials] = Aws::Credentials.new(credreg["AccessKeyId"], credreg["SecretAccessKey"])
ec2 = Aws::EC2::Client.new
resp = ec2.describe_vpcs
resp[:vpcs].each do |v|
    v[:tags].each {|vv| myawsvpc_id = v[:vpc_id] if vv[:value] =~ /myawsvpc/}
end
#myawsvpc_id = resp[:vpcs][0][:vpc_id]
resp = Aws::EC2::Vpc.new(myawsvpc_id)
resp.tags.each do |v|
    puts v[:value]
end
resp.subnets.each do |sn|
    sn.tags.each do |v|
        myawssubnets[v[:value]] = sn.subnet_id
    end
end
resp.security_groups.each do |sg|
    puts sg.group_name
    myawssecurity_id = sg.group_id if sg.group_name =~ /default/
    myawssecurity = sg if sg.group_name =~ /default/
end
puts myawsvpc_id
puts myawssecurity_id
puts myawssecurity.group_name
puts myawssecurity.vpc_id
puts myawssecurity.owner_id
myawssubnets.each {|k, v| puts k + " " + v}
opsworks_role = Aws::IAM::Role.new("OpsWorksRole")
opsworks_role_arn = opsworks_role.arn
instance_profile = Aws::IAM::InstanceProfile.new("OpsWorksInstanceProfile")
instance_profile_arn = instance_profile.arn
puts opsworks_role_arn 
puts instance_profile_arn
myow = Aws::OpsWorks::Client.new
resp = myow.create_stack(name: "MyAwsOpsWorks", region: credreg["Region"], vpc_id: myawsvpc_id, attributes: {"Color" => "rgb(100, 131, 57)"}, configuration_manager: {name: "Chef", version: "11.10"}, service_role_arn: opsworks_role_arn, default_instance_profile_arn: instance_profile_arn, default_availability_zone: "us-east-1b", default_os: "Amazon Linux 2015.03", default_subnet_id: myawssubnets["myawsvpc_private_subnet"], use_opsworks_security_groups: true, default_ssh_key_name: "gregkey") 
opsworks_id = resp.stack_id
#resp = myow.create_layer(stack_id: opsworks_id, type: "lb", name: "lb-layer", shortname: "lb-layer", volume_configurations: [{mount_point: "/dev/sdh", number_of_disks: 1, size: 8}])
resp = myow.create_layer(stack_id: opsworks_id, type: "lb", name: "lb-layer", shortname: "lb-layer", custom_security_group_ids: [myawssecurity_id])
lb_layer_id = resp.layer_id
#resp = myow.create_layer(stack_id: opsworks_id, type: "rails-app", name: "rails-app-layer", shortname: "rails-app-layer", volume_configurations: [{mount_point: "/dev/sdh", number_of_disks: 1, size: 8}])
resp = myow.create_layer(stack_id: opsworks_id, type: "rails-app", name: "rails-app-layer", shortname: "rails-app-layer", custom_security_group_ids: [myawssecurity_id])
rails_layer_id = resp.layer_id
#resp = myow.create_layer(stack_id: opsworks_id, type: "db-master", name: "db-master-layer", shortname: "db-master-layer", volume_configurations: [{mount_point: "/dev/sdh", number_of_disks: 1, size: 8}])
resp = myow.create_layer(stack_id: opsworks_id, type: "db-master", name: "db-master-layer", shortname: "db-master-layer", custom_security_group_ids: [myawssecurity_id])
db_layer_id = resp.layer_id

resp = myow.create_instance(stack_id: opsworks_id, layer_ids: [lb_layer_id], instance_type: "m1.small", auto_scaling_type: "load", ssh_key_name: "gregkey", availability_zone: "us-east-1b", subnet_id: myawssubnets["myawsvpc_public_subnet"], architecture: "x86_64", root_device_type: "instance-store", install_updates_on_boot: true, agent_version: "INHERIT")
puts "LB Layer Instance ID " + resp.instance_id 
myow.start_instance(instance_id: resp.instance_id)

resp = myow.create_instance(stack_id: opsworks_id, layer_ids: [rails_layer_id], instance_type: "m1.small", auto_scaling_type: "load", ssh_key_name: "gregkey", availability_zone: "us-east-1b", subnet_id: myawssubnets["myawsvpc_private_subnet"], architecture: "x86_64", root_device_type: "instance-store", install_updates_on_boot: true, agent_version: "INHERIT")
puts "Rails and DB Layer Instance ID " + resp.instance_id 
myow.start_instance(instance_id: resp.instance_id)

resp = myow.create_instance(stack_id: opsworks_id, layer_ids: [db_layer_id], instance_type: "m1.small", auto_scaling_type: "load", ssh_key_name: "gregkey", availability_zone: "us-east-1b", subnet_id: myawssubnets["myawsvpc_private_subnet"], architecture: "x86_64", root_device_type: "instance-store", install_updates_on_boot: true, agent_version: "INHERIT")
puts "Rails and DB Layer Instance ID " + resp.instance_id 
myow.start_instance(instance_id: resp.instance_id)
