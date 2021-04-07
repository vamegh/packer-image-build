#!/usr/bin/env python3
#
##
##########################################################################
#                                                                        #
#       configure-packer                                                 #
#                                                                        #
#       (c) 2019 Vamegh Hedayati                                         #
#                                                                        #
#       Vamegh Hedayati <gh_vhedayati AT ev9 DOT io>                     #
#                                                                        #
#       Please see Copying for License Information                       #
#                             GNU/LGPL                                   #
##########################################################################
##
#
from build_libs import aws_gather, command_parser, config_parser, custom_logger, file_handler, aws_secrets, \
    jenkins_creds, aws_meta
import os
import socket

__version__ = "0.0.1"


def main():
    meta = aws_meta.Meta()
    document = meta.document()
    handler = file_handler.FileHandler()
    output_file = config['options'].jenkins_output_file
    host_name = socket.gethostname()
    config['auth_creds'] = {}
    config['secret_data'] = {}
    try:
        if not isinstance(config['aws'], dict):
            config['aws'] = {}
    except KeyError:
        config['aws'] = {}

    if document:
        os.environ['AWS_DEFAULT_REGION'] = document['region']
        config['aws_meta'] = {}
        config['aws_meta'].update(document)

    aws_data = aws_gather.gather_data(config=config)
    r53_zones = aws_gather.get_route53_zones(config=config)
    config['aws'].update(aws_data)
    try:
        aws_region = config['aws']['aws_region']
    except KeyError:
        aws_region = document['region']

    config['aws_secret_path'] = []
    config['jenkins_credentials'] = []

    for secret_path in config['aws_secrets']:
        config['aws_secret_path'].append(os.path.join(config['aws']['account_alias'], secret_path))
    config['aws_secrets'] = config['aws_secret_path']
    del config['aws_secret_path']

    for jenkins_cred in config['jenkins_agent_credentials']:
        config['jenkins_credentials'].append(os.path.join(config['aws']['account_alias'], jenkins_cred))
    del config['jenkins_agent_credentials']

    config['auth_creds'] = aws_secrets.get_secret(secret_names=config['jenkins_credentials'],
                                                  region_name=aws_region)
    config['secret_data'] = aws_secrets.get_secret(secret_names=config['aws_secrets'],
                                                   region_name=aws_region)

    dns_domain = config['secret_data']['dns']['domain']
    agent_config = config['secret_data']['jenkins_agent']
    auth_creds = config['auth_creds']['credentials_github_swarm_autobot']
    data = handler.read_file(config_file=output_file, file_type='properties')
    data['JAVA_OPTS'] = agent_config['java_opts']
    data['JENKINS_USERNAME'] = auth_creds['user']
    data['JENKINS_PASSWORD'] = auth_creds['password']
    data['JENKINS_URL'] = "https://jenkins.dev.local"
    data['JENKINS_NAME'] = "_".join([agent_config['name'], host_name])
    data['JENKINS_EXECUTORS'] = agent_config['executors']
    data['JENKINS_HOME'] = agent_config['jenkins_home']
    data['JENKINS_UC'] = agent_config['jenkins_uc']
    handler.write_properties(output_file=output_file, data=data, enable_quotes=True)
    logging.info("All Done: Jenkins Agent Default File should be fully configured")


if __name__ == "__main__":
    name = "jenkins_agent_configure"
    ''''initialise the command line checker -- add in all of the options'''
    cmd_opts = command_parser.Commands(name=name, version=__version__)
    cmd_opts.add_config()
    cmd_opts.add_jenkins_output_file()
    cmd_opts.add_debug()
    cmd_opts.add_logging()
    options, args, cmd_parser = cmd_opts.set_options()
    '''parse through the provided options make sure everything is set as required'''
    cmd_check = command_parser.CommandCheck(options=options, parser=cmd_parser)
    cmd_check.debug()
    cmd_check.config()
    cmd_check.jenkins_output_file()
    ''' inject cli options modifications into config data '''
    config_parser = config_parser.Parse(options=options, parser=cmd_parser)
    config_parser.read_config()
    config_parser.combine_config()
    config_parser.scan_config()
    config = config_parser.return_config()
    ''' set up the logging '''
    logging = custom_logger.colourLog(name=name, config=config)

    config['logging'] = logging
    main()
