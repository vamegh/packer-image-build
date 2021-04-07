#
##
##########################################################################
#                                                                        #
#       gauth :: command_parser                                          #
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

from optparse import OptionParser
import os


class Commands(object):
    def __init__(self, name='', version='0.0.1', message=''):
        self.name = name
        self.version = version
        self.message = message
        self.parser = OptionParser(version=self.version,
                                   usage='\n'.join([
                                       self.name + ' [options]',
                                       'Version: ' + self.version,
                                   ]))

    def add_config(self):
        current_paths = os.path.dirname(os.path.realpath(__file__)).split('/')
        current_paths.pop()
        current_path = "/".join(current_paths)
        config_path = os.path.join(current_path, 'configs/config.yaml')

        self.parser.add_option('-c', '--config', action='store', default=config_path,
                               help=' '.join(['Provide a custom configuration file,',
                                              'defaults to <script_path>/configs/config.yaml if none provided']))

    def add_packer(self):
        current_path = os.getcwd()
        current_path = os.path.join(current_path, 'variables.json')

        self.parser.add_option('-p', '--packer_variable_file', action='store', default=current_path,
                               help=' '.join(['Provide a custom location for the packer variables file,',
                                              'defaults to <cwd>/variables.json if none provided']))

    def add_jenkins_output_file(self):
        self.parser.add_option('-o', '--jenkins_output_file', action='store', default='/etc/default/jenkins',
                               help=' '.join(['Provide a custom location for the output properties file',
                                              'To be feed into jenkins startup']))

    def add_debug(self):
        self.parser.add_option('-D', '--debug', action='store', type='int', default=None,
                               help=' '.join(['set debugging level: ',
                                              'an integer value between 1 to 5 (the higher the more',
                                              'debugging output that will be provided)']))

    def add_logging(self):
        self.parser.add_option('--log_file', action='store',
                               default=("/var/log/%s/%s.log" % (self.name, self.version)),
                               help=' '.join(['File to Log script run information',
                                              ', by default this is ',
                                              '/var/log/<name>/<name>_<version>_<date>.log (optional)']))

    def set_options(self):
        options, args = self.parser.parse_args()
        return options, args, self.parser


class CommandCheck(object):
    def __init__(self, options=None, parser=None):
        self.options = options
        self.parser = parser

    def debug(self):
        if self.options.debug:
            print("Setting log level to match debug level")

    def packer_variable_file(self):
        if not os.path.isfile(self.options.packer_variable_file):
            self.parser.print_help()
            raise ValueError("Error: variables file: %s :: Not Found... Please specify exact location" % (
                self.options.packer_variable_file))

    def config(self):
        if not os.path.isfile(self.options.config):
            self.parser.print_help()
            raise ValueError("Error: Config file: %s :: Not Found... Please specify exact location" % (
                self.options.config))

    def jenkins_output_file(self):
        if not os.path.isfile(self.options.jenkins_output_file):
            self.parser.print_help()
            raise ValueError("Error: Jenkins output file: %s :: Not Found... Please specify exact location" % (
                self.options.jenkins_output_file))
