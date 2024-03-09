from pathlib import Path

from .files import read_json_file, write_json_file

def get_outputs_path():
    # TODO: fix
    return 'outputs'

def read_album_metadata(directory):
    """Returns the album metadata for the album at `directory`."""

    path = get_album_metadata_path(directory)
    return read_json_file(path)

def write_album_metadata(album):
    """Writes an album metadata to the appropriate path."""

    path = get_album_metadata_path(album['id'])
    path.parent.mkdir(parents=True, exist_ok=True)

    write_json_file(path, album)

def get_album_metadata_path(directory):
    """Returns a path to the album metadata.json."""

    directory_path = get_directory_path(directory)
    return Path(f'{directory_path}/metadata.json')

def read_photo_data(directory, filename):
    """Returns a photo data object from `directory/filename`."""

    path = get_photo_data_path(directory, filename)
    return read_json_file(path)

def write_photo_data(directory, photo):
    """Writes a photo data entry within `directory`."""

    filename = get_photo_filename(photo)
    path = get_photo_data_path(directory, filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    write_json_file(path, photo)

def get_photo_data_path(directory, filename):
    """Returns a path to the photo data entry."""

    directory_path = get_directory_path(directory)
    return Path(f'{directory_path}/{filename}')

def get_directory_path(directory):
    """Returns a `directory_path` by concatenating the components."""

    outputs_path = get_outputs_path()
    return Path(f'{outputs_path}/{directory}')

def get_photo_filename(photo):
    """Returns the filename corresponding to `photo`."""

    return '{}.json'.format(photo['id'])
