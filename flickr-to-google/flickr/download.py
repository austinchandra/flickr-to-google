import asyncio
import os
from pathlib import Path
import mimetypes

from common.directory import (
    get_outputs_path,
    get_directory_path,
    read_album_metadata,
    write_photo_data,
    read_photo_data,
)
from .constants import REQUESTS_BATCH_SIZE, PhotoEntryKeys
from common.log import print_timestamped, print_separator
from common.network import download_photo_bytes
from common.files import write_buffer

async def download_photos(path, is_downloading_all=False):
    """Downloads all photos to `path` and updates the entry files, printing output summaries throughout."""

    requests = _get_requests(path, is_downloading_all)

    for i in range(0, len(requests), REQUESTS_BATCH_SIZE):
        await asyncio.gather(*requests[i:i + REQUESTS_BATCH_SIZE])

def _get_requests(root_path, is_downloading_all):
    """Returns a list of requests for all remaining photos."""

    requests = []

    _, directories, _ = next(os.walk(get_outputs_path()))

    for directory in directories:

        _, _, filenames = next(os.walk(get_directory_path(directory)))

        for filename in filenames:
            if filename == 'metadata.json':
                continue

            photo = read_photo_data(directory, filename)

            # Ignore photos that were not properly fetched:
            if len(photo.keys()) <= 1:
                continue

            if not is_downloading_all and PhotoEntryKeys.DOWNLOAD_FILE_PATH in photo:
                continue

            requests.append(_download_photo(root_path, directory, photo))

    return requests

def _get_download_path(root_path, directory, photo, content_type):
    """Returns the download file path for the photo given `root_path` and `directory`."""

    directory = _get_download_directory(directory)
    filename = _get_download_filename(photo, content_type)

    return Path(
        os.path.join(root_path, directory, filename)
    )

def _get_download_directory(directory):
    """Returns the name of the directory on the filesystem."""

    if directory == 'photostream':
        return 'Photostream'

    album = read_album_metadata(directory)
    return album['title']

def _get_download_filename(photo, content_type):

    filename = photo['title']
    extension = mimetypes.guess_extension(content_type)

    return Path(f'{filename}{extension}')

async def _download_photo(root_path, directory, photo):
    """Downloads the photo bytes for `photo` to the corresponding filepath."""

    content_type, data = download_photo_bytes(photo)
    path = _get_download_path(root_path, directory, photo, content_type)

    write_buffer(path, data)
    _update_photo_entry(path, directory, photo)

def _update_photo_entry(path, directory, photo):
    """Updates the photo entry on a successful download."""

    photo[PhotoEntryKeys.DOWNLOAD_FILE_PATH] = str(path)
    write_photo_data(directory, photo)
