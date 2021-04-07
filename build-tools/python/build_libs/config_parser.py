#
##
##########################################################################
#                                                                        #
#       gauth :: config_parser                                           #
#                                                                        #
#       (c) 2018 Vamegh Hedayati                                         #
#                                                                        #
#       Vamegh Hedayati <gh_vhedayati AT ev9 DOT io>                     #
#                                                                        #
#       Please see Copying for License Information                       #
#                             GNU/LGPL                                   #
##########################################################################
##
#
import file_handler
import getpass
import os
import pwd
import re
import sys


class Parse(object):
    def __init__(self, options=None, parser=None):
        self.options = options
        self.parser = parser
        self.handle = file_handler.FileHandler()
        self.config_data = None

    def read_config(self):
        if self.options.config:
            try:
                config_data = self.handle.read_file(config_file=self.options.config)
                self.config_data = config_data
            except (IOError, ValueError) as err:
                print("\nConfig File Issue: %s :: Error : %s\n" % (self.options.config, err))
                self.parser.print_help()
                sys.exit(1)

    def combine_config(self):
        try:
            color_map = self.config_data['color_map']
            if not os.path.isfile(color_map):
                current_paths = os.path.dirname(os.path.realpath(__file__)).split('/')
                current_paths.pop()
                current_path = "/".join(current_paths)
                color_map = os.path.join(current_path, color_map)
            color_data = self.handle.read_file(config_file=color_map)
            if color_data:
                self.config_data.update(color_data)
        except KeyError as err:
            print("color map not supplied :: Error: %s :: skipping" % err)

    def scan_config(self):
        if self.options.debug:
            debug = self.options.debug
            if debug == 1:
                debug_name = 'critical'
            elif debug == 2:
                debug_name = 'error'
            elif debug == 3:
                debug_name = 'warning'
            elif debug == 4:
                debug_name = 'info'
            elif debug == 5:
                debug_name = 'debug'
            else:
                print("Invalid debug level set, using default")
                debug_name = None
            if debug_name:
                self.config_data['logging_config']['log_level'] = debug_name

        ''' Add the user-id running this to config_data'''
        pam_user = os.getenv('PAM_USER')
        sys_user = getpass.getuser()
        check_is_uid = re.compile(r"^\d+")
        if not pam_user:
            self.config_data['user_name'] = sys_user
            pam_user = sys_user

        if check_is_uid.match(pam_user):
            self.config_data['user_name'] = pwd.getpwuid(pam_user)[0]

        '''add all of the command options to the config data as well'''
        self.config_data['options'] = self.options

    def return_config(self):
        return self.config_data
