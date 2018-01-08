require 'json'
require 'yaml'
require 'aws-sdk'
myawsvpc_id = ''
awsvpc_id = ''
myawsvpc_instances = ''
awsvpc_instances = ''
myawsvpc_security_group = ''
awsvpc_security_group = ''
myawsvpc_security_group = ''
awsvpc_security_group = ''
credreg = YAML.load(File.read('aws_key.yml'))
Aws.config[:region] = credreg['Region']
Aws.config[:credentials] = Aws::Credentials.new(credreg['AccessKeyId'], credreg['SecretAccessKey'])
ec2 = Aws::EC2::Client.new
resp = ec2.describe_vpcs
resp[:vpcs].each do |v|
    v[:tags].each do |vv|
        myawsvpc_id = v[:vpc_id] if vv[:value] =~ /myawsvpc/
        awsvpc_id = v[:vpc_id] if vv[:value] =~ /\bawsvpc\b/
    end
end
#resp = ec2.describe_instances
#resp.reservations.each do |r|
#    r.instances.each do |i|
#        puts 'Terminating ' + i.instance_id
#        ec2.terminate_instances(instance_ids: [i.instance_id])
#    end
#end
#resp = ec2.describe_addresses
#resp.addresses.each do |a|
#    puts 'Releasing ' + a.public_ip
#    ec2.release_address(allocation_id: a.allocation_id)
#    #ec2.disassociate_address(association_id: a.association_id)
#end
##cannot delete default by user
##resp = ec2.describe_security_groups
##resp.security_groups.each do |g|
##    puts 'Terminating ' + g.group_id
##    ec2.delete_security_group(group_id: g.group_id)
##end
myawsvpc = Aws::EC2::Vpc.new(myawsvpc_id)
awsvpc = Aws::EC2::Vpc.new(awsvpc_id)
vpcpeer = ec2.describe_vpc_peering_connections
#vpcpeer.vpc_peering_connections.each do |v|
#    ec2.delete_vpc_peering_connection(vpc_peering_connection_id: v.vpc_peering_connection_id)
#end
#myawsvpc.security_groups.each do |s|
#    ec2.delete_security_group(group_id: s.group_id)
#end
myawsvpc.internet_gateways.each do |i|
    myawsvpc.detach_internet_gateway(internet_gateway_id: i.internet_gateway_id)
    ec2.delete_internet_gateway(internet_gateway_id: i.internet_gateway_id)
end
myawsvpc.subnets.each do |s|
    ec2.delete_subnet(subnet_id: s.subnet_id)
end
myawsvpc.route_tables.each do |r|
    ec2.delete_route_table(route_table_id: r.route_table_id)
end
#awsvpc.security_groups.each do |s|
#    ec2.delete_security_group(group_id: s.group_id)
#end
awsvpc.internet_gateways.each do |i|
    awsvpc.detach_internet_gateway(internet_gateway_id: i.internet_gateway_id)
    ec2.delete_internet_gateway(internet_gateway_id: i.internet_gateway_id)
end
awsvpc.subnets.each do |s|
    ec2.delete_subnet(subnet_id: s.subnet_id)
end
awsvpc.route_tables.each do |r|
    ec2.delete_route_table(route_table_id: r.route_table_id)
end
myawsvpc.delete
awsvpc.delete
