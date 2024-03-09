import os
from enum import StrEnum
from dataclasses import dataclass, asdict
from pathlib import Path

from .files import read_json_file, write_json_file

DIRECTORY_BASE_PATH = 'flickr-to-google'
CONFIG_FILENAME = 'config.json'

@dataclass
class Config:
    user_id: str # 200072260@N02
    google_secret_path: str
    flickr_secret_path: str

def read_config():
    path = get_config_path()
    contents = read_json_file(path)

    return Config(**contents)

def write_config(config):
    path = get_config_path()
    contents = asdict(config)

    write_json_file(path, contents)

def get_config_path():
    return create_path_from_base(CONFIG_FILENAME)

def create_path_from_base(subpath):
    path = Path(os.path.join(Path.home(), DIRECTORY_BASE_PATH, subpath))
    path.parent.mkdir(parents=True, exist_ok=True)

    return path
