from common.config import (
    create_path_from_base,
    read_config,
)
from common.files import read_json_file, write_json_file

FLICKR_OAUTH_FILENAME = 'flickr_oauth.json'

def read_user_id():
    """Returns the Flickr NSID."""

    config = read_config()
    return config.flickr_user_id

def read_api_keys():
    """Returns the API keys."""

    config = read_config()
    path = config.flickr_secret_path

    contents = read_json_file(path)
    return (contents['api_key'], contents['api_secret'])
