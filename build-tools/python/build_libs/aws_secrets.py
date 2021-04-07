import boto3
import json
import base64
import logging
from botocore.exceptions import ClientError


def get_secret(secret_names=None, region_name='eu-west=1'):
    secret_data = {}
    if not isinstance(secret_names, list):
        raise TypeError('secret_names must be provided as a list of names')

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    for secret_name in secret_names:
        secret_name_arr = secret_name.split('/')
        del secret_name_arr[0]
        key_name = "_".join(secret_name_arr)
        logging.info("Getting Values for secret: %s :: Key: %s", secret_name, key_name)
        if len(secret_name_arr) > 2:
            auth_id = "_".join([secret_name_arr[-2], secret_name_arr[-1]])
        else:
            auth_id = secret_name_arr[-1]

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
                secret = base64.b64decode(get_secret_value_response['SecretBinary'])

        secret_data[key_name] = json.loads(secret)
        try:
            secret_data[key_name]['auth_id']
        except KeyError:
            secret_data[key_name]['auth_id'] = auth_id
    return secret_data
