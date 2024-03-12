from common.config import (
    create_path_from_base,
    read_config,
)
from common.files import read_json_file, write_json_file

GOOGLE_AUTH_FILENAME = 'google_token.json'

def read_oauth_token():
    path = get_oauth_token_path()
    return read_json_file(path)

def get_oauth_token_path():
    return create_path_from_base(GOOGLE_AUTH_FILENAME)

def get_credentials_path():
    config = read_config()
    return config.google_secret_path
