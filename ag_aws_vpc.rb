#!/usr/bin/ruby
##Author: Greg Sheu, gregsheu@yahoo.com
##The automation of creating AWS VPC with one public subnet, two private subnets, and one NAT instance in the public subnet. 
##Resources needed in step by step
##Creating VPC
##Creating 3 subnets
##Creating two private routetables
##Creating one internet gateway
##Attach internet gateway to VPC
##Creating one route to internet gateway in public subnet
##Launching one NAT instance in public subnet
##Allocate public IP
##Associate public IP to NAT
##Modify source destination check on NAT
##Create one route to NAT in private routetables
##Associate private routetables to private subnets
require "rest-client"
require "json"
require "yaml"
require "aws-sdk"
#credreg = JSON.load(File.read("aws_key.json"))
credreg = YAML.load(File.read("aws_key.yml"))
Aws.config[:region] = credreg["Region"]
Aws.config[:credentials] = Aws::Credentials.new(credreg["AccessKeyId"], credreg["SecretAccessKey"])
mysubnets = []
custom_route_table_id = ""
nat_id = []
mysecurity_id = ""
ec2 = Aws::EC2::Client.new
resp = ec2.create_vpc(:cidr_block => "172.16.0.0/16")
myvpc_id = resp[:vpc][:vpc_id]
myvpc_name = "awsvpc"
#ec2.create_tags(resources: [myvpc_id], tags: [key: "Name", value: "myawsvpc"])
ec2.create_tags(resources: [myvpc_id], tags: [key: "Name", value: myvpc_name])
(32..33).each do |i|
    resp = ec2.create_subnet(vpc_id: myvpc_id, cidr_block: "172.16.#{i}.0/24", availability_zone: "us-east-1b")
    mysubnets[i] = resp[:subnet][:subnet_id]
    if i == 0
        ec2.create_tags(resources: [mysubnets[i]], tags: [key: "Name", value: myvpc_name + "_public_subnet"])
    else
        ec2.create_tags(resources: [mysubnets[i]], tags: [key: "Name", value: myvpc_name + "_private_subnet"])
    end
end
#ec2.delete_key_pair(:key_name => "gregkey2"
#mykey = ec2.create_key_pair(:key_name => "gregkey2"
#file = File.new("gregkey2.key" "wb"
#file.write(mykey[:key_material])
#file.chmod(0600)
#file.close
##We want the VPC we just create to get route table
#createdvpc = Aws::EC2::Vpc.new("vpc-e5b98880"
resp = Aws::EC2::Vpc.new(myvpc_id)
resp.route_tables.each do |rt|
    custom_route_table_id = rt.route_table_id
end
resp.security_groups.each do |sg|
    mysecurity_id = sg.group_id
end
##Get your own external IP address and add SSH to security group
myip = RestClient.get("http://jsonip.com/") {|s| JSON::parse(s.to_s)["ip"]}
ec2.authorize_security_group_ingress(group_id: mysecurity_id, ip_protocol: "tcp", from_port: 22, to_port: 22, cidr_ip: "#{myip}/32")
##We associate public subnet to default route table
ec2.create_tags(resources: [custom_route_table_id], tags: [key: "Name", value: myvpc_name + "_custom_route"])
ec2.associate_route_table(subnet_id: mysubnets[0], route_table_id: custom_route_table_id)
##We need to have an internet gateway for our VPC
resp = ec2.create_internet_gateway
igw_id = resp[:internet_gateway][:internet_gateway_id]
ec2.attach_internet_gateway(internet_gateway_id: igw_id, vpc_id: myvpc_id)
ec2.create_route(route_table_id: custom_route_table_id, destination_cidr_block: "0.0.0.0/0", gateway_id: igw_id)
##We need to create second route table
resp = ec2.create_route_table(vpc_id: myvpc_id)
main_route_table_id = resp[:route_table][:route_table_id]
ec2.create_tags(resources: [main_route_table_id], tags: [key: "Name", value: myvpc_name + "_main_route"])
ec2.associate_route_table(subnet_id: mysubnets[1], route_table_id: main_route_table_id)
##Now we are getting the NAT id to create in public subnet
resp = ec2.describe_images(owners: ["amazon"], filters: [{name: "owner-alias", values: ["amazon"]}, {name: "name", values: ["amzn-ami-vpc-nat*"]}, {name: "is-public", values: ["true"]}, {name:"virtualization-type", values: ["paravirtual"]}])
resp.sort.each do |i|
    i[:images].each do |j|
        #puts "Name " + j[:name]
        #puts "Owner " + j[:owner_id]
        #puts "Image ID " + j[:image_id]
        #puts "Hyper Visor " + j[:hypervisor]
        nat_id[0] = j[:image_id]
    end
end
#resp = ec2.run_instances(image_id: "ami-c02b04a8", key_name: "gregkey", min_count: 1, max_count: 1, subnet_id: mysubnets[0])
resp = ec2.run_instances(image_id: nat_id[0], key_name: "gregkey", min_count: 1, max_count: 1, subnet_id: mysubnets[0])
nat_instance_id = resp[:instances][0][:instance_id]
nat_interface_id = resp[:instances][0][:network_interfaces][0][:network_interface_id]
resp = ec2.allocate_address(domain: "vpc")
nat_public_ip = resp[:public_ip]
nat_allocation_id = resp[:allocation_id]
ec2.wait_until(:instance_status_ok, {instance_ids: [nat_instance_id], filters: [{name: "instance-state-name", values: ["running"]}]}) do |w|
    w.max_attempts = 60
    w.delay =  60
    puts "Waiting for NAT instance to be running"
end
ec2.create_tags(resources: [nat_instance_id], tags: [key: "Name", value: "awsnat"])
puts "Running now"
ec2.modify_instance_attribute(instance_id: nat_instance_id, source_dest_check: {value: false})
ec2.associate_address(instance_id: nat_instance_id, public_ip: nat_public_ip)
#ec2.create_route(route_table_id: main_route_table_id, destination_cidr_block: "0.0.0.0/0", network_interface_id: nat_interface_id)
ec2.create_route(route_table_id: main_route_table_id, destination_cidr_block: "0.0.0.0/0", instance_id: nat_instance_id)
puts "NAT public IP is #{nat_public_ip}"
