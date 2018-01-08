#!/usr/bin/ruby
##Author: Greg Sheu, gregsheu@yahoo.com
##The automation of creating AWS VPC with one public subnet, two private subnets, and one NAT gateway in the public subnet. 
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
resp = ec2.create_vpc(:cidr_block => "172.34.0.0/16")
myvpc_id = resp[:vpc][:vpc_id]
myvpc_name = "development"
#ec2.create_tags(resources: [myvpc_id], tags: [key: "Name", value: "myawsvpc"])
ec2.create_tags(resources: [myvpc_id], tags: [key: "Name", value: myvpc_name])
(0..2).each do |i|
    resp = ec2.create_subnet(vpc_id: myvpc_id, cidr_block: "172.34.#{i}.0/24", availability_zone: "#{credreg["Region"]}a")
    mysubnets[i] = resp[:subnet][:subnet_id]
    if i == 0
        ec2.create_tags(resources: [mysubnets[i]], tags: [key: "Name", value: myvpc_name + "_public_subnet"])
    else
        ec2.create_tags(resources: [mysubnets[i]], tags: [key: "Name", value: myvpc_name + "_private_subnet#{i}"])
    end
end
(3..4).each do |i|
    resp = ec2.create_subnet(vpc_id: myvpc_id, cidr_block: "172.34.#{i}.0/24", availability_zone: "#{credreg["Region"]}c")
    mysubnets[i] = resp[:subnet][:subnet_id]
    ec2.create_tags(resources: [mysubnets[i]], tags: [key: "Name", value: myvpc_name + "_private_subnet#{i}"])
end
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
myip = RestClient.get("http://jsonip.com/") 
myip = JSON::parse(myip.to_s)["ip"]
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
(1..4).each do |i|
    ec2.associate_route_table(subnet_id: mysubnets[i], route_table_id: main_route_table_id)
end
resp = ec2.allocate_address(domain: "vpc")
nat_public_ip = resp[:public_ip]
nat_allocation_id = resp[:allocation_id]
resp = ec2.create_nat_gateway(subnet_id: mysubnets[0], allocation_id: nat_allocation_id)
#ec2.wait_until(:instance_status_ok, {instance_ids: [nat_instance_id], filters: [{name: "instance-state-name", values: ["running"]}]}) do |w|
puts "Waiting for NAT gateway to be running"
ec2.wait_until(:nat_gateway_available, {nat_gateway_ids: [resp[:nat_gateway][:nat_gateway_id]], filter: [{name: "state", values: ["available"]}]}) do |w|
    w.max_attempts = 60
    w.delay = 60
end
puts "Running now"
ec2.create_route(route_table_id: main_route_table_id, destination_cidr_block: "0.0.0.0/0", nat_gateway_id: resp[:nat_gateway][:nat_gateway_id])
rds_resp = Aws::RDS::Client.new
rds_resp.create_db_subnet_group({db_subnet_group_name: myvpc_name + "_db_subnet", db_subnet_group_description: "db sunet group from rds", subnet_ids: [mysubnets[2],mysubnets[4]], tags: [{key: "name", value: myvpc_name + "_db_subnet"}]})
