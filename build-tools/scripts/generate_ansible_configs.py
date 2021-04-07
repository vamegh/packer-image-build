#!/usr/bin/env python3
###
# This is an incredibly hacky script ive put in place temporarily just to boot-strap ansible
# I will revisit this and clean it up later / when I have a chance.
###
import boto3
import yaml
import yaml.representer
import os
import sys
from botocore.exceptions import ClientError
import logging


def make_dir(path=None):
    file_path, file_name = os.path.split(path)

    if file_path:
        if not os.path.exists(file_path):
            logging.info("Creating Directory: %s", file_path)
            os.makedirs(file_path)

#def literal_presenter(dumper, data):
#  if isinstance(data, str) and "\n" in data:
#      return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
#  return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

def write_yaml(output_file=None, data=None):
    if not output_file or not data:
        logging.error("Error Data / Output File Not Provided")
        sys.exit(1)
    make_dir(path=output_file)
    #yaml.add_representer(str, literal_presenter)
    with open(output_file, 'w') as output_file:
        output_file.write(yaml.safe_dump(data, default_flow_style=False,
                                    allow_unicode=True, encoding=None,
                                    explicit_start=True))
    print("Generated the group_vars configuration.yaml file for ansible")

def write_hosts(output_file=None, mode="w"):
    data = "[local]\nlocalhost ansible_connection=local"
    if not output_file or not data:
        logging.error("Error Data / Output File Not Provided")
        sys.exit(1)
    make_dir(path=output_file)
    with open(output_file, mode) as output_file:
        output_file.write("%s\n" % (data))
    print("Generated the hosts.ini for ansible")

def gather_data(packer_path=None):
    sts = boto3.client('sts')
    iam = boto3.client('iam')
    session = boto3.session.Session()
    region = session.region_name
    account_id = sts.get_caller_identity().get('Account')
    account_alias = iam.list_account_aliases().get('AccountAliases')[0]
    user_id_raw = sts.get_caller_identity().get('UserId')
    user_id = user_id_raw.split(':')[-1]

    if not region:
        region = "eu-west-1"

    if "default-" in user_id:
        user_id = user_id.split('default-')[-1]

    if "-sts" in user_id:
        user_id = user_id.split('-sts')[0]

    print("Account ID: {}".format(account_id))
    print("Account Alias: {}".format(account_alias))
    print("Region: {}".format(region))
    print("User ID: {}".format(user_id))
    logging.info("Account ID: %s", account_id)
    logging.info("Account Alias: %s", account_alias)
    logging.info("Region: %s", region)
    logging.info("User ID: %s", user_id)

    data = {}
    data['stack'] = 'test'
    data['aws_account_profile'] = user_id
    data['mel_account_id'] = account_id
    data['aws_region'] = region
    data['packer_files'] = packer_path
    data['keys_path'] = "{{ packer_files }}/public_keys"
    return data


if __name__ == '__main__':
    data = gather_data(packer_path=sys.argv[1])
    write_yaml(output_file="generated/group_vars/all/configuration.yml", data=data)
    write_hosts(output_file="generated/group_vars/hosts.ini", mode="w")
    print("All Done")

