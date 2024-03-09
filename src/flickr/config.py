from common.config import (
    create_path_from_base,
    read_config,
)
from common.files import read_json_file, write_json_file

FLICKR_OAUTH_FILENAME = 'flickr_oauth.json'

def read_oauth_token():
    path = _get_token_path()
    return read_json_file(path)

def write_oauth_token(token):
    path = _get_token_path()
    write_json_file(path, token)

def read_user_id():
    config = read_config()
    return config.user_id

def read_api_secrets():
    config = read_config()
    path = config.flickr_secret_path

    contents = read_json_file(path)
    return (contents['api_key'], contents['api_secret'])

def _get_token_path():
    return create_path_from_base(FLICKR_OAUTH_FILENAME)
