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
from pprint import pprint

__version__ = "0.0.1"


def main():
    meta = aws_meta.Meta()
    document = meta.document()
    handler = file_handler.FileHandler()
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
    config['aws'].update(aws_data)

    config['aws_secret_path'] = []
    config['jenkins_credentials'] = []
    config['groovy_script_path'] = []

    for secret_path in config['aws_secrets']:
        config['aws_secret_path'].append(os.path.join(config['aws']['account_alias'], secret_path))
    config['aws_secrets'] = config['aws_secret_path']
    del config['aws_secret_path']

    for jenkins_cred in config['jenkins_master_credentials']:
        config['jenkins_credentials'].append(os.path.join(config['aws']['account_alias'], jenkins_cred))
    del config['jenkins_master_credentials']

    for groovy_script in config['groovy_scripts']:
        config['groovy_script_path'].append(os.path.join(config['temp_path'], groovy_script))
    config['groovy_scripts'] = config['groovy_script_path']
    del config['groovy_script_path']

    credentials_data = aws_secrets.get_secret(secret_names=config['jenkins_credentials'],
                                              region_name=config['aws']['aws_region'])
    for credentials in credentials_data:
        logging.info("Submitting Credentials: %s", credentials)

    for script in config['groovy_scripts']:
        logging.info("Executing Groovy Script: %s", script)

    for key, value in config['jenkins_master_settings'].items():
        print ("Printing KEY:")
        pprint(key)
        print ("Printing Value:")
        pprint(value)
        output_file = ("/tmp/groovy/%s.json" %(key))
        config_data = value['config']
        handler.write_json(output_file=output_file, data=config_data)




if __name__ == "__main__":
    name = "jenkins_master_post_configure"
    ''''initialise the command line checker -- add in all of the options'''
    cmd_opts = command_parser.Commands(name=name, version=__version__)
    cmd_opts.add_config()
    cmd_opts.add_debug()
    cmd_opts.add_logging()
    options, args, cmd_parser = cmd_opts.set_options()
    '''parse through the provided options make sure everything is set as required'''
    cmd_check = command_parser.CommandCheck(options=options, parser=cmd_parser)
    cmd_check.debug()
    cmd_check.config()
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
