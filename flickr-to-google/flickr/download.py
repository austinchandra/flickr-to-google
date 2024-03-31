import asyncio
import os
from pathlib import Path
from urllib.parse import urlparse
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
from common.request import download_photo_bytes
from common.files import write_buffer

async def download_photos(path, is_downloading_all=False, is_videos_only=False):
    """Downloads all photos to `path` and updates the entry files, printing output summaries throughout."""

    requests = _get_requests(path, is_downloading_all, is_videos_only)

    _print_init(requests)

    for i in range(0, len(requests), REQUESTS_BATCH_SIZE):
        batch = requests[i:i + REQUESTS_BATCH_SIZE]
        await asyncio.gather(*batch)
        _print_batch_summary(batch)

    _print_summary(requests)

def _get_requests(root_path, is_downloading_all, is_videos_only):
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

            if is_videos_only and not _is_media_video(photo):
                continue

            requests.append(_download_photo(root_path, directory, photo))

    return requests

async def _download_photo(root_path, directory, photo):
    """Downloads the photo bytes for `photo` to the corresponding filepath."""

    url, content_type, did_update_exif, data = download_photo_bytes(photo)

    filename = _get_download_filename(photo, content_type, url)
    path = _get_download_path(root_path, directory, filename)

    write_buffer(path, data)
    _update_photo_entry(path, directory, did_update_exif, photo)

def _get_download_path(root_path, directory, filename):
    """Returns the download file path for the photo given `root_path` and `directory`."""

    folder = _get_download_folder(directory)

    return Path(
        os.path.join(root_path, folder, filename)
    )

def _get_download_folder(directory):
    """Returns the name of the directory on the filesystem."""

    if directory == 'photostream':
        return 'Photostream'

    album = read_album_metadata(directory)

    return album['title']

def _get_download_filename(photo, content_type, url):
    """Returns the photo filename, creating the extension from `content_type` or `url`."""

    name = photo['title']
    extension = mimetypes.guess_extension(content_type)

    if extension is None:
        path = urlparse(url).path
        extension = os.path.splitext(path)[1]

    return Path(f'{name}{extension}')

def _update_photo_entry(path, directory, did_update_exif, photo):
    """Updates the photo entry on a successful download."""

    photo[PhotoEntryKeys.DOWNLOAD_FILE_PATH] = str(path)

    if did_update_exif:
        photo[PhotoEntryKeys.DID_UPDATE_EXIF] = did_update_exif

    write_photo_data(directory, photo)

def _is_media_video(photo):
    """Returns a boolean indicating whether the media item is a video."""

    return photo['media'] == 'video'

def _print_init(requests):
    """Prints a download initiation message."""

    print_timestamped(
        'Beginning download for {} remaining item(s).'.format(len(requests))
    )

def _print_batch_summary(batch):
    """Prints an intermediate download summary."""

    print_separator()
    print_timestamped(
        'Downloaded {} item(s).'.format(len(batch))
    )

def _print_summary(requests):
    """Prints a final download summary."""

    print_separator()
    print_timestamped(
        'Downloaded {} remaining item(s).'.format(len(requests))
    )
