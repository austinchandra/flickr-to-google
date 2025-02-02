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

    responses = []

    for i in range(0, len(requests), REQUESTS_BATCH_SIZE):
        batch = requests[i:i + REQUESTS_BATCH_SIZE]
        batch_responses = await asyncio.gather(*batch)
        _print_batch_summary(batch_responses)
        responses += batch_responses

    _print_summary(responses)

    return _get_downloaded_count(responses)

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

    url, data, did_update_exif = download_photo_bytes(photo)

    if data is None:
        return None

    filename = _get_download_filename(photo, url)
    path = _get_download_path(root_path, directory, filename)

    # Throw on failure, as further writes are likely to fail.
    write_buffer(path, data)
    _update_photo_entry(path, directory, photo, did_update_exif)

    return photo

def _get_download_path(root_path, directory, filename):
    """Returns the download file path for the photo given `root_path` and `directory`."""

    folder = _get_download_folder(directory)

    return Path(
        os.path.join(root_path, folder, filename)
    )

def _get_download_folder(directory):
    """Returns the name of the directory on the filesystem."""

    if _is_directory_photostream(directory):
        return 'Photostream'

    album = read_album_metadata(directory)

    # Use ID in case the title is poorly formatted.
    # TODO: Clean up excess calls to disk

    return album['id']

def _get_download_filename(photo, url):
    """Returns the photo filename, creating the extension from `url`."""

    # Use ID in case the title is poorly formatted.

    name = photo['id']
    extension = _parse_extension_from_url(url)

    return Path(f'{name}{extension}')

def _update_photo_entry(path, directory, photo, did_update_exif):
    """Updates the photo entry on a successful download."""

    photo[PhotoEntryKeys.DOWNLOAD_FILE_PATH] = str(path)

    if did_update_exif:
        photo[PhotoEntryKeys.DID_UPDATE_EXIF] = True

    write_photo_data(directory, photo)

def _is_media_video(photo):
    """Returns a boolean indicating whether the media item is a video."""

    return photo['media'] == 'video'

def _parse_extension_from_url(url):
    """Returns the extension (e.g. .jpg or .mov) from `url`, assuming that `url` is well-formed."""

    path = urlparse(url).path
    extension = os.path.splitext(path)[1]

    return extension

def _is_directory_photostream(directory):
    """Returns a boolean indicating whether `directory` is the photostream."""

    return directory == 'photostream'

def _get_downloaded_count(responses):
    """Returns a tuple with the number of photos downloaded and attempted."""

    num_downloaded = len([r for r in responses if r is not None])
    num_attempted = len(responses)

    return num_downloaded, num_attempted

def _print_init(requests):
    """Prints a download initiation message."""

    print_separator()
    print_timestamped(
        'Beginning download for {} remaining item(s).'.format(len(requests))
    )

def _print_batch_summary(responses):
    """Prints an intermediate download summary."""

    num_downloaded, num_attempted = _get_downloaded_count(responses)

    print_separator()
    print_timestamped(
        'Downloaded {} of {} item(s).'.format(num_downloaded, num_attempted)
    )

def _print_summary(responses):
    """Prints a final download summary."""

    num_downloaded, num_attempted = _get_downloaded_count(responses)

    print_separator()
    print_timestamped(
        'Downloaded {} of {} remaining item(s).'.format(num_downloaded, num_attempted)
    )
