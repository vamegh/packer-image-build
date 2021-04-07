import boto3
import logging


def get_route53_zones(config=None):
    dns_zones = {}
    if config:
        config['dns_zones'] = {}

    r53 = boto3.client('route53')
    hosted_zones = r53.list_hosted_zones()

    for zone in hosted_zones['HostedZones']:
        zone_name = zone['Name']
        zone_id = zone['Id']
        if "/" in zone_id:
            zone_id = zone_id.split('/')[-1]
        if zone_name.endswith('.'):
            zone_name = zone_name[:-1]
        dns_zones[zone_name] = zone_id
        if config:
            config['dns_zones'][zone_name] = zone_id
    return dns_zones


def get_jenkins_master(region=None):
    ec2 = boto3.resource('ec2', region)
    master_info = {}
    private_ip = ""
    running_instances = ec2.instances.filter(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ])
    for instance in running_instances:
        for tag in instance.tags:
            if "Name" == tag['Key']:
                if "jenkins_master" in tag['Value'].lower():
                    private_ip = instance.private_ip_address
                    master_info[instance.id] = {
                        'Name': tag['Value'],
                        'ip': instance.private_ip_address
                    }
    return private_ip, master_info


def gather_data(config=None):
    sts = boto3.client('sts')
    iam = boto3.client('iam')
    ec2 = boto3.client('ec2')
    session = boto3.session.Session()
    region = session.region_name
    account_id = sts.get_caller_identity().get('Account')
    account_alias_full = iam.list_account_aliases().get('AccountAliases')[0]
    account_alias = iam.list_account_aliases().get('AccountAliases')[0]
    user_id_raw = sts.get_caller_identity().get('UserId')
    user_id = user_id_raw.split(':')[-1]

    try:
        filter_name = config['aws']['filter_key']
        filter_values = config['aws']['filter_values']
    except KeyError as err:
        logging.error("Could Not Find Filter Variables, from config, using defaults")
        filter_name = 'tag:Name'
        filter_values = ['*packer*']

    ec2_filter = [{'Name': filter_name, 'Values': filter_values}]
    ec2_vpcs = ec2.describe_vpcs(Filters=ec2_filter)
    ec2_subnets = ec2.describe_subnets(Filters=ec2_filter)
    ec2_security_groups = ec2.describe_security_groups(Filters=ec2_filter)

    vpc_id = ec2_vpcs['Vpcs'][0]['VpcId']
    subnet_id = ec2_subnets['Subnets'][0]['SubnetId']
    security_group_id = ec2_security_groups['SecurityGroups'][0]['GroupId']
    if not region:
        region = "eu-west-1"

    if "dataplatform-" in account_alias:
        account_alias = account_alias.split('dataplatform-')[-1]

    if "default-" in user_id:
        user_id = user_id.split('default-')[-1]

    if "-sts" in user_id:
        user_id = user_id.split('-sts')[0]

    logging.info("Account ID: %s", account_id)
    logging.info("Full Account Alias: %s", account_alias_full)
    logging.info("Account Alias: %s", account_alias)
    logging.info("Region: %s", region)
    logging.info("Full User ID: %s", user_id_raw)
    logging.info("User ID: %s", user_id)
    logging.info("VPC ID: %s", vpc_id)
    logging.info("Subnet ID: %s", subnet_id)
    logging.info("Security Group ID: %s", security_group_id)

    data = {}
    data['stack'] = 'test'
    data['aws_account_profile'] = user_id
    data['account_id'] = account_id
    data['account_alias_full'] = account_alias_full
    data['account_alias'] = account_alias
    data['user_id_full'] = user_id_raw
    data['user_id'] = user_id
    data['aws_region'] = region
    data['keys_path'] = "{{ packer_files }}/public_keys"
    data['vpc_id'] = vpc_id
    data['subnet_id'] = subnet_id
    data['sg_id'] = security_group_id
    return data
