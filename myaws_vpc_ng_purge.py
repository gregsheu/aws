import time
import sys
import boto3 

#09272020 is working
def get_nat_gateway_infos(myvpcid):
    ec2_c = boto3.client('ec2')
    resp = ec2_c.describe_nat_gateways(Filters=[{'Name': 'vpc-id', 'Values': [myvpcid]}])
    nat_gateway_id = resp['NatGateways'][0]['NatGatewayId']
    nat_gateway_allocationid = resp['NatGateways'][0]['NatGatewayAddresses'][0]['AllocationId']
    nat_gateway_publicip = resp['NatGateways'][0]['NatGatewayAddresses'][0]['PublicIp']
    return nat_gateway_id, nat_gateway_allocationid, nat_gateway_publicip

def remove_publicip(nat_gateway_allocationid, nat_gateway_publicip):
    ec2_c = boto3.client('ec2')
    #resp = ec2_c.describe_addresses(PublicIps=[nat_gateway_publicip], AllocationIds=[nat_gateway_allocationid])
    #nat_gateway_associationid = resp['Addresses'][0]['AssociationId']
    print('Releasing Elastic IP %s' % nat_gateway_publicip)
    ec2_c.release_address(AllocationId=nat_gateway_allocationid)

def remove_igw(myawsvpc, myvpcid):
    ec2_c = boto3.client('ec2')
    for i in myawsvpc.internet_gateways.all():
        myawsvpc.detach_internet_gateway(InternetGatewayId=i.internet_gateway_id, VpcId=myvpcid)
        ec2_c.delete_internet_gateway(InternetGatewayId=i.internet_gateway_id)

#The custom route will be gone after NAT deleted, so we need to run this before deleting NAT gateway
def get_custom_routes(myawsvpc):
    ec2_c = boto3.client('ec2')
    kv = {}
    main_route_table_id = None
    not_main_route_table_id = None
    for r in myawsvpc.route_tables.all():
        resp = ec2_c.describe_route_tables(RouteTableIds=[r.route_table_id], Filters=[{'Name': 'association.main', 'Values': ['false']}])
        #resp = ec2_c.describe_route_tables(RouteTableIds=[r.route_table_id])
        for a in resp['RouteTables'][0]['Associations']:
            if a['Main']:
                main_route_table_id = a['RouteTableId']
                kv.update({a['RouteTableId']: a['Main']})
        if not r.route_table_id in kv:
            not_main_route_table_id = r.route_table_id
            kv.update({a['RouteTableId']: 'False'})
    return main_route_table_id, not_main_route_table_id

def remove_custom_routes(myawsvpc, not_main_route_table_id, main_route_table_id):
    ec2_c = boto3.client('ec2')
    for s in myawsvpc.subnets.all():
        ec2_c.delete_subnet(SubnetId=s.subnet_id)
    ec2_c.delete_route(RouteTableId=main_route_table_id, DestinationCidrBlock='0.0.0.0/0')
    print('Removing custom route table %s' % not_main_route_table_id)
    ec2_c.delete_route_table(RouteTableId=not_main_route_table_id)
    print('Custom route table %s deleted' % not_main_route_table_id)

def remove_nat_gateway(nat_gateway_id):
    ec2_c = boto3.client('ec2')
    ec2_c.delete_nat_gateway(NatGatewayId=nat_gateway_id)
    print('Waiting for NAT gateway to be deleted')
    #Waiter is not working, so use sleep
    #waiter.wait(Filters=[{'Name': 'state', 'Values': ['deleting']}], WaiterConfig={'Delay': 30, 'MaxAttempts': 3})
    #waiter.wait(Filters=[{'Name': 'state', 'Values': ['deleted']}], WaiterConfig={'Delay': 30, 'MaxAttempts': 3})
    time.sleep(120)
    print('NAT gateway %s deleted' % nat_gateway_id)

def remove_vpc(myawsvpc,myvpcid):
    print('Deleting VPC %s' % myvpcid)
    myawsvpc.delete()
    print('Done')

def main():
    myvpcid = sys.argv[1]
    ec2 = boto3.resource('ec2')
    myawsvpc = ec2.Vpc(myvpcid)
    #If there is no NAT gateway, we don't need to run get_nat_gateway_infos, remove_nat_gateway and remove_publicip
    nat_gateway_id, nat_gateway_allocationid, nat_gateway_publicip = get_nat_gateway_infos(myvpcid)
    main_route_table_id, not_main_route_table_id = get_custom_routes(myawsvpc)
    remove_nat_gateway(nat_gateway_id) 
    remove_publicip(nat_gateway_allocationid, nat_gateway_publicip)
    remove_igw(myawsvpc, myvpcid)
    remove_custom_routes(myawsvpc, not_main_route_table_id, main_route_table_id)
    remove_vpc(myawsvpc, myvpcid)


if __name__ == '__main__':
    main()

