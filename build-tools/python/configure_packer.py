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
from build_libs import aws_gather, command_parser, config_parser, custom_logger, file_handler, aws_meta
import os

__version__ = '0.0.1'


def main():
    meta = aws_meta.Meta()
    document = meta.document()
    handler = file_handler.FileHandler()
    aws_data = aws_gather.gather_data(config=config)
    if document:
        os.environ['AWS_DEFAULT_REGION'] = document['region']
        config['aws_meta'] = {}
        config['aws_meta'].update(document)
    try:
        if not isinstance(config['aws'], dict):
            config['aws'] = {}
    except KeyError:
        config['aws'] = {}
    try:
        if not isinstance(config['packer_variables'], dict):
            config['packer_variables'] = {}
    except KeyError:
        config['packer_variables'] = {}
    config['aws'].update(aws_data)
    account_alias = config['aws']['account_alias']
    var_path, var_file = os.path.split(options.packer_variable_file)
    var_file = ("%s_%s" % (account_alias, var_file))
    var_file = os.path.join(var_path, var_file)
    account_file = os.path.join(var_path, "account")

    try:
        packer_variables = handler.read_file(config_file=var_file, file_type='json')
    except Exception as err:
        logging.warning("Warning: Could not read variables from account specific variables file")
        logging.warning("Error Reason: %s", err)
        logging.warning("This is not a Failure :: Resorting to reading from base variables file")
        packer_variables = handler.read_file(config_file=options.packer_variable_file,
                                             file_type='json')

    packer_variables['packer_security_group_id'] = config['aws']['sg_id']
    packer_variables['packer_subnet_id'] = config['aws']['subnet_id']
    packer_variables['packer_vpc_id'] = config['aws']['vpc_id']
    packer_variables['account_id'] = config['aws']['account_id']
    packer_variables['account_alias'] = account_alias
    config['packer_variables'].update(packer_variables)

    handler.write_json(output_file=var_file, data=packer_variables)
    handler.write_file(output_file=account_file, data=account_alias)
    logging.info("All Done: Packer Variables have been updated")


if __name__ == "__main__":
    name = "configure_packer"
    ''''initialise the command line checker -- add in all of the options'''
    cmd_opts = command_parser.Commands(name=name, version=__version__)
    cmd_opts.add_config()
    cmd_opts.add_debug()
    cmd_opts.add_logging()
    cmd_opts.add_packer()
    options, args, cmd_parser = cmd_opts.set_options()
    '''parse through the provided options make sure everything is set as required'''
    cmd_check = command_parser.CommandCheck(options=options, parser=cmd_parser)
    cmd_check.debug()
    cmd_check.config()
    cmd_check.packer_variable_file()
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
