from pathlib import Path

from common.files import read_json_file

def read_album_metadata(directory_path):
    """Returns the album metadata for the album at `directory_path`."""

    path = get_album_metadata_path(directory_path)
    return read_json_file(path)

def get_directory_path(outputs_path, directory):
    """Returns a `directory_path` by concatenating the components."""

    return Path(f'{outputs_path}/{directory}')

def get_album_metadata_path(directory_path):
    """Returns the path for an album's `metadata.json` file given `directory_path`."""

    return Path(f'{directory_path}/metadata.json')

def get_photo_data_path(directory_path, photo):
    """Returns the path for the photo entry `photo` at `directory_path`."""

    return Path('{}/{}.json'.format(directory_path, photo['id']))
