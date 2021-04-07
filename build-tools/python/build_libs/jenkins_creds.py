import urllib.parse
import requests
import os
import json
import logging


class Jenkins(object):
    def __init__(self, config=None):
        try:
            self.username = config['user_name']
            self.password = config['password']
            self.host = config['host']
            self.port = config['port']
        except KeyError:
            raise KeyError('''Configurations should be passed as a dict,
                              containing login_pass, login_user, host and port key/values''')
        if os.path.isfile(self.password):
            password_data = self.read_simple(config_file=self.password)
            self.password = password_data[0]
            logging.warning("Using Jenkins initialAdmin Password: (%s)", self.password)

        self.host_url = os.path.join('http://', '%s:%s' % (self.host, self.port))
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}
        self.good_status = [200, 201, 202, 203, 204, 205, 206]
        self.auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        parsed_url = urllib.parse.urlparse(self.host_url)
        self.crumb_issuer_url = urllib.parse.urlunparse((parsed_url.scheme,
                                                         parsed_url.netloc,
                                                         'crumbIssuer/api/json',
                                                         '', '', ''))

    def read_simple(self, config_file=None):
        values = []
        with open(config_file, "r") as config:
            for line in config:
                line = line.strip(' \n\t')
                values.append(line)
        return values

    def read_groovy(self, script=None, config_file=None):
        data = ""
        if config_file:
            data = ("def config_file = \"%s\"\n" % config_file)
        with open(script, 'r') as script_data:
            data += script_data.read()
        data = {'script': data}
        return data

    def init_auth(self):
        r = requests.get(self.crumb_issuer_url, auth=self.auth)
        if r.status_code in self.good_status:
            json_response = r.json()
            crumb = {json_response['crumbRequestField']: json_response['crumb']}
            self.headers.update(crumb)
        else:
            logging.warning("Response: %s", r.text)
            logging.warning("Auth Probably Not Setup :: Skipping Crumbs Header Addition")
            return None

    def generate_creds(self, data=None):
        cred_type = data['credentials_type']
        payload_data = {"": "0", 'credentials': {}}
        payload_data['credentials']['scope'] = 'GLOBAL'
        payload_data['credentials']['id'] = data['auth_id']
        payload_data['credentials']['description'] = data['auth_id'] + ' - Added by Post Installation Step'

        if cred_type == 'user':
            payload_data['credentials']['username'] = data['user']
            payload_data['credentials']['password'] = data['password']
            payload_data['credentials'][
                '$class'] = 'com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl'
        elif cred_type == 'string':
            payload_data['credentials']['fileName'] = data['auth_id']
            payload_data['credentials']['secret'] = data['secret']
            payload_data['credentials']['$class'] = 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl'
            payload_data['credentials']['description'] = data['auth_id']
        elif cred_type == 'ssh':
            try:
                passphrase = data['passphrase']
            except KeyError:
                passphrase = None
            payload_data['credentials']['username'] = data['user']
            payload_data['credentials']['passphrase'] = passphrase
            payload_data['credentials']['privateKeySource'] = {}
            payload_data['credentials']['privateKeySource'][
                'stapler-class'] = 'com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource'
            payload_data['credentials']['privateKeySource']['privateKey'] = data['ssh_key']
            payload_data['credentials'][
                'stapler-class'] = 'com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey'
        elif cred_type == 'ssh_file':
            try:
                passphrase = data['passphrase']
            except KeyError:
                passphrase = None
            payload_data['credentials']['username'] = data['user']
            payload_data['credentials']['passphrase'] = passphrase
            payload_data['credentials']['privateKeySource'] = {}
            payload_data['credentials']['privateKeySource'][
                'stapler-class'] = 'com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey'
            payload_data['credentials']['privateKeySource']['privateKeyFile'] = data['ssh_key_file']
            payload_data['credentials'][
                'stapler-class'] = 'com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey'
        payload = ("json=" + json.dumps(payload_data))
        return payload

    def post(self, query_url=None, payload=None):
        post_url = os.path.join(self.host_url, query_url)
        success_message = "Script Executed"
        fail_message = "Execute Script"
        print_response = True
        if "Credentials" in query_url:
            success_message = "Credentials Added"
            fail_message = "Add Credentials"
            print_response = False
        print("%s :: %s" % (post_url, self.headers))
        try:
            response = requests.post(post_url,
                                     headers=self.headers,
                                     auth=self.auth,
                                     data=payload)
        except Exception as err:
            logging.warning("Failed To Connect Using Auth :: Exception: %s", err)
            logging.info("Trying to Connect without authentication")
            try:
                response = requests.post(post_url,
                                         headers=self.headers,
                                         data=payload)
            except Exception as err:
                logging.error("Failed To Connect to Jenkins")
                raise ValueError("Error: %s", err)

        status = response.status_code
        if status in self.good_status:
            logging.info("%s Successfully", success_message)
            if print_response:
                logging.info("Response: %s", response.text)
            return response
        else:
            logging.error("Failed to %s", fail_message)
            logging.error("Response From Jenkins: %s", response.text)
        return None
