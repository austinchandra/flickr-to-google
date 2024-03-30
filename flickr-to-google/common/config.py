import os
from enum import StrEnum
from dataclasses import dataclass, asdict
from pathlib import Path

from .files import read_json_file, write_json_file

DIRECTORY_BASE_PATH = '.flickr-to-google'
CONFIG_FILENAME = 'config.json'

@dataclass
class Config:
    flickr_user_id: str

    # These are necessary to perform API requests.
    google_secret_path: str
    flickr_secret_path: str

    # These are necessary to retrieve full-quality videos on request.
    flickr_cookie_session: str
    flickr_cookie_epass: str

def read_config():
    """Returns the cached config."""

    path = get_config_path()
    contents = read_json_file(path)

    return Config(**contents)

def write_config(config):
    """Updates the cached config."""

    path = get_config_path()
    contents = asdict(config)

    write_json_file(path, contents)

def get_config_path():
    """Returns the path to the config file."""

    return create_path_from_base(CONFIG_FILENAME)

def create_path_from_base(subpath):
    """Creates a path from the base directory."""

    path = Path(os.path.join(Path.home(), DIRECTORY_BASE_PATH, subpath))
    path.parent.mkdir(parents=True, exist_ok=True)

    return path
