require 'json'
require 'yaml'
require 'aws-sdk'
myawsvpc_id = ''
myawsvpc_route_table_id = ''
myawssecurity_id = ''
myawsvpc_cidr = ''
awsvpc_id = ''
awsvpc_route_table_id = ''
awssecurity_id = ''
awsvpc_cidr = ''
credreg = YAML.load(File.read('aws_key.yml'))
Aws.config[:region] = credreg['Region']
Aws.config[:credentials] = Aws::Credentials.new(credreg['AccessKeyId'], credreg['SecretAccessKey'])
ec2 = Aws::EC2::Client.new
resp = ec2.describe_vpcs
#For vpc with tags
resp[:vpcs].each do |v|
    v[:tags].each do |vv|
        myawsvpc_id = v[:vpc_id] if vv[:value] =~ /myawsvpc/
        awsvpc_id = v[:vpc_id] if vv[:value] =~ /\bawsvpc\b/
    end
end
#For an existing vpc peering connection
#vpcpeeringconnection_id = ec2.describe_vpc_peering_connections.vpc_peering_connections[0].vpc_peering_connection_id
resp = ec2.create_vpc_peering_connection({vpc_id: myawsvpc_id, peer_vpc_id: awsvpc_id})
vpcpeeringconnection_id = resp.vpc_peering_connection.vpc_peering_connection_id
resp = ec2.accept_vpc_peering_connection({vpc_peering_connection_id: vpcpeeringconnection_id})

myawsvpc_resp = Aws::EC2::Vpc.new(myawsvpc_id)
myawsvpc_cidr = myawsvpc_resp.cidr_block
awsvpc_resp = Aws::EC2::Vpc.new(awsvpc_id)
awsvpc_cidr = awsvpc_resp.cidr_block
puts "We are adding routes from VPC #{myawsvpc_resp} #{myawsvpc_id} to VPC #{awsvpc_resp} #{awsvpc_id} and vice versa."

myawsvpc_resp.route_tables.each do |r|
    puts "Adding route to #{awsvpc_cidr} in route #{myawsvpc_route_table_id} through #{vpcpeeringconnection_id}"
    myawsvpc_route_table_id = r.route_table_id
    ec2.create_route(route_table_id: myawsvpc_route_table_id, destination_cidr_block: awsvpc_cidr , vpc_peering_connection_id: vpcpeeringconnection_id)
end
myawsvpc_resp.security_groups.each do |s|
    myawssecurity_id = s.group_id
end
awsvpc_resp.route_tables.each do |r|
    puts "Adding route to #{myawsvpc_cidr} in route #{awsvpc_route_table_id} through #{vpcpeeringconnection_id}"
    awsvpc_route_table_id = r.route_table_id
    ec2.create_route(route_table_id: awsvpc_route_table_id, destination_cidr_block: myawsvpc_cidr, vpc_peering_connection_id: vpcpeeringconnection_id)
end
awsvpc_resp.security_groups.each do |s|
    awssecurity_id = s.group_id
end
puts "Adding permission of security group #{myawssecurity_id} to allow all tcp, udp and icmp from #{awssecurity_id}" 
ec2.authorize_security_group_ingress(group_id: myawssecurity_id, ip_protocol: '-1', from_port: -1, to_port: -1, cidr_ip: awsvpc_cidr)
puts "Adding permission of security group #{awssecurity_id} to allow all tcp, udp and icmp from #{myawssecurity_id}" 
ec2.authorize_security_group_ingress(group_id: awssecurity_id, ip_protocol: '-1', from_port: -1, to_port: -1, cidr_ip: myawsvpc_cidr)
