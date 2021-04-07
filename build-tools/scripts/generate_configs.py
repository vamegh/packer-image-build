import boto3
import json
import base64
import sys
import os
from botocore.exceptions import ClientError
import pwd
import grp
import logging
#from botocore.credentials import InstanceMetadataProvider, InstanceMetadataFetcher

from libs import aws_gather

def make_dir(path=None):
    file_path, file_name = os.path.split(path)
    if file_path:
        if not os.path.exists(file_path):
            print("Creating Directory: {}".format(file_path))
            os.makedirs(file_path)


def get_route53_zone(platform=None, domain=None):
    r53 = boto3.client('route53')
    hosted_zones = r53.list_hosted_zones()

    for zone in hosted_zones['HostedZones']:
        zone_name = zone['Name']
        zone_env = zone['Name'].split('.')[1]
        if zone_name.endswith('.'):
            zone_name = zone_name[:-1]
        if domain in zone_name:
            if platform in zone_name:
                print("Found Zone: {0} :: This must be the {1} account".format(zone_name, zone_env))
                return zone_name, zone_env
    return None, None


def set_perms(path=None, sys_user=None, sys_group=None):
    file_path, file_name = os.path.split(path)
    if "root" in path:
        sys_user = "root"
        sys_group = "root"
    uid = pwd.getpwnam(sys_user).pw_uid
    gid = grp.getgrnam(sys_group).gr_gid
    os.chmod(file_path, 0o700)
    os.chown(file_path, uid, gid)
    os.chmod(path, 0o600)
    os.chown(path, uid, gid)


def read_config(config_file=None, mode="r+"):
    data = {}
    values = []
    try:
        with open(config_file, mode) as config:
            for line in config:
                if line.startswith('#'):
                    continue
                if len(line.strip()) == 0:
                    continue
                if line.startswith('export'):
                    line = line.split(' ', 1)[1]
                line = line.split('#', 1)[0]
                line = line.rstrip()
                values = line.split("=")
                if len(values) > 2:
                    key = values.pop(0)
                    value = '='.join(values)
                elif len(values) == 2:
                    key, value = line.split("=")
                else:
                    print("I cannot parse the following line: {}, from file: {} :: Skipping it".format(line,
                                                                                                       self.config_file))
                    continue
                if key.startswith('\'') and key.endswith('\''):
                    key = key[1:]
                    key = key[:-1]
                if key.startswith('\"') and key.endswith('\"'):
                    key = key[1:]
                    key = key[:-1]
                if value.startswith('\'') and value.endswith('\''):
                    value = value[1:]
                    value = value[:-1]
                if value.startswith('\"') and value.endswith('\"'):
                    value = value[1:]
                    value = value[:-1]
                data[key] = value
        return data
    except (TypeError, IOError) as err:
        pass
    return False


def write_properties(output_file=None, data=None):
    if not output_file or not data:
        logging.error("Error Data / Output File Not Provided")
        print("Error Data / Output File Not Provided")
        sys.exit(1)
    make_dir(path=output_file)
    with open(output_file, 'w') as output_file:
        for key, value in data.items():
            output_file.write("%s=\"%s\"\n" % (key, value))


def get_secret():
    aws_data = aws_gather.gather_data()
    aws_env = aws_data['aws_account_profile']
    secret_names = [ aws_env + "/github/user"]
    #secret_name = "staging/jenkins/agent"
    region_name = "eu-west-1"
    secret_data = {}

    # Create a Secrets Manager client
    #aws_access_key_id=access_key,
    #aws_secret_access_key=secret_key,
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    for secret_name in secret_names:
        secret_name_arr = secret_name.split('/')
        key_name = "_".join(secret_name_arr)

        secret_data[key_name] = {}
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            raise e
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

        secret_data[key_name] = json.loads(secret)
    return secret_data


def process_data(secret_data=None, config_file=None):
    if not secret_data:
        print("Error No Secret Data Provided")
        sys.exit(1)

    if not config_file:
        print("Error No Config File Provided")
        sys.exit(1)

    config_data = read_config(config_file=config_file, mode="r")
    r53_domain, r53_env = get_route53_zone(platform=secret_data['platform'], domain=secret_data['domain'])

    if not r53_domain:
        print("Error Cannot reliably determine Account Domain Exiting")
        sys.exit(1)

    try:
        config_data['JENKINS_USERNAME'] = secret_data['user']
    except KeyError as err:
        print("Required Key Error :: {}".format(err))
        raise err

    try:
        config_data['JENKINS_PASSWORD'] = secret_data['pass']
    except KeyError as err:
        print("Error :: Jenkins Password Not Found: {}".format(err))
        return None

    try:
        master_host = secret_data['master_host']
        config_data['JENKINS_URL'] = '.'.join([master_host, r53_domain])
    except KeyError as err:
        print("Required Key Error :: {}".format(err))
        return None

    try:
        config_data['JENKINS_NAME'] = secret_data['name']
    except KeyError as err:
        print("Required Key Error :: {}".format(err))
        return None

    try:
        config_data['JENKINS_EXECUTORS'] = secret_data['executors']
    except KeyError as err:
        print("Required Key Error :: {}".format(err))
        return None

    write_properties(output_file=config_file, data=config_data)
    print("All Done")


if __name__ == '__main__':
    #provider = InstanceMetadataProvider(iam_role_fetcher=InstanceMetadataFetcher(timeout=1000, num_attempts=2))
    #creds = provider.load()
    #access_key = creds.access_key
    #secret_key = creds.secret_key

    process_data(secret_data=get_secret(), config_file=sys.argv[1])
