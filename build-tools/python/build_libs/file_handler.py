#
##
##########################################################################
#                                                                        #
#       gauth :: file_handler                                            #
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
import os
import sys

try:
    from ruamel import yaml
except:
    import yaml
import json
import logging


class FileHandler(object):
    def __init__(self):
        self.config_file = ''
        self.data = ''
        self.yaml_types = ["yaml", "yml", "yl"]
        self.json_types = ["json", "jsn", "js", "jn"]
        self.prop_types = ["bash", "properties", "property", "prop", "sh"]

    def make_dir(self, path=None):
        file_path, file_name = os.path.split(path)

        if file_path:
            if not os.path.exists(file_path):
                logging.info("Creating Directory: %s", file_path)
                os.makedirs(file_path)

    def read_yaml(self, file_type=None):
        if not file_type:
            try:
                file_type = self.config_file.split('.')[-1].lower()
            except (TypeError, AttributeError, IOError, KeyError) as err:
                logging.warning("Cannot properly determine file Extension: Error: %s", str(err))

        if file_type not in self.yaml_types:
            return False

        try:
            with open(self.config_file, "r") as config:
                yaml_data = yaml.safe_load(config)
            return yaml_data
        except (TypeError, IOError):
            print("Skipping Yaml Import for: {}".format(self.config_file))
            pass
        return False

    def read_json(self, file_type=None):
        if not file_type:
            try:
                file_type = self.config_file.split('.')[-1].lower()
            except (TypeError, AttributeError, IOError, KeyError) as err:
                logging.warning("Cannot properly determine file Extension: Error: %s", str(err))

        if file_type not in self.json_types:
            return False

        try:
            with open(self.config_file, "r") as config:
                json_data = json.load(config)
            return json_data
        except (TypeError, IOError):
            print("Skipping Json Import For: {}".format(self.config_file))
            pass
        return False

    def read_properties(self, file_type=None):
        if not file_type:
            try:
                file_type = self.config_file.split('.')[-1].lower()
            except (TypeError, AttributeError, IOError, KeyError) as err:
                logging.warning("Cannot properly determine file Extension: Error: %s", str(err))

        if file_type not in self.prop_types:
            return False

        data = {}
        try:
            with open(self.config_file, "r") as config:
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
                        print("I cannot parse line: {}, from file: {} :: Skipping it".format(line,
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
        except (TypeError, IOError):
            pass
        return False

    def read_simple(self, config_file=None):
        values = []
        with open(config_file, "r") as config:
            for line in config:
                values.append(line)
        return values

    def read_file(self, config_file=None, file_type=None):
        self.config_file = config_file
        if file_type:
            file_type = file_type.lower()
        config_data = self.read_yaml(file_type=file_type)
        if not config_data:
            config_data = self.read_json(file_type=file_type)
        if not config_data:
            config_data = self.read_properties(file_type=file_type)
        if not config_data:
            raise ValueError("Error Cannot Read Config File: %s ... Aborting" % config_file)
        return config_data

    def write_yaml(self, output_file=None, data=None):
        if not output_file or not data:
            logging.error("Error Data / Output File Not Provided")
            sys.exit(1)
        self.make_dir(path=output_file)
        with open(output_file, 'w') as output_file:
            output_file.write(yaml.safe_dump(data, default_flow_style=False,
                                             allow_unicode=True, encoding=None,
                                             explicit_start=True))

    def write_json(self, output_file=None, data=None):
        if not output_file or not data:
            logging.error("Error Data / Output File Not Provided")
            sys.exit(1)
        self.make_dir(path=output_file)
        with open(output_file, 'w') as output_file:
            json.dump(data, output_file, indent=4)

    def write_tf_properties(self, output_file=None, data=None):
        if not output_file or not data:
            logging.error("Error Data / Output File Not Provided")
            sys.exit(1)
        self.make_dir(path=output_file)
        with open(output_file, 'w') as output_file:
            for key, value in data.items():
                output_file.write("%s = \"%s\"\n" % (key, value))

    def write_properties(self, output_file=None, data=None, enable_quotes=False):
        if not output_file or not data:
            logging.error("Error Data / Output File Not Provided")
            sys.exit(1)
        self.make_dir(path=output_file)
        with open(output_file, 'w') as output_file:
            for key, value in data.items():
                if enable_quotes:
                    output_file.write("%s=\"%s\"\n" % (key, value))
                    continue
                output_file.write("%s=%s\n" % (key, value))

    def write_file(self, output_file=None, data=None, status=None, mode="w"):
        if not output_file or not data:
            logging.error("Error Data / Output File Not Provided")
            sys.exit(1)
        self.make_dir(path=output_file)
        with open(output_file, mode) as output_file:
            if isinstance(data, list):
                for value in data:
                    if status == "enable":
                        output_file.write("+%s\n" % value)
                    elif status == "disable":
                        output_file.write("-%s\n" % value)
                    else:
                        output_file.write("%s\n" % value)
            else:
                output_file.write("%s\n" % data)
