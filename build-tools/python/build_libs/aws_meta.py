import requests
import os
import json
import logging


class Meta(object):
    def __init__(self):
        self.host_url = 'http://169.254.169.254'
        self.good_status = [200, 201, 202, 203, 204, 205, 206]

    def get(self, endpoint=None):
        url = os.path.join(self.host_url, endpoint)

        try:
            return requests.get(url, timeout=2)
        except Exception as err:
            logging.error("Requests failed: Skipping")
            logging.debug("Exception: %s", err)
            return None

    def document(self):
        r = self.get(endpoint='latest/dynamic/instance-identity/document')
        if not r:
            return None
        if r.status_code in self.good_status:
            return (r.json())

    def avail_zone(self):
        r = self.get(endpoint='latest/meta-data/placement/availability-zone')
        data = {}
        if not r:
            return None
        if r.status_code in self.good_status:
            data['availability_zone'] = r.text
            return (data)
