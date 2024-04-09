import asyncio
import json
from pathlib import Path

from .photos import query_photo_identifiers
from .photosets import query_photosets
from common.directory import write_album_metadata, write_photo_data
from common.log import print_timestamped, print_separator
from .api import init as init_flickr_api

async def create_directory():
    """Creates an unpopulated directory with `photosets` and `photo` identifiers."""

    init_flickr_api()
    _print_init()

    photo_identifiers = await query_photo_identifiers()
    photosets = await query_photosets()

    _validate_directory_queries(photo_identifiers, photosets)

    _write_photoset_directory_files(photosets)
    _write_photo_directory_files(photo_identifiers, photosets)

    _print_summary(photosets)

def _write_photoset_directory_files(photosets):
    """Writes directory files for `photosets`."""

    for photoset in photosets:
        write_album_metadata(photoset)

def _write_photo_directory_files(photo_identifiers, photosets):
    """Writes `{ id: photo_id }` directory skeleton files for `photos` given `photosets`."""

    photo_photosets = _get_photo_photosets(photosets)

    for photo_id in photo_identifiers:
        photoset_id = photo_photosets.get(photo_id, None)
        photo = { 'id': photo_id }
        _write_photo_directory_file(photo, photoset_id)

def _get_photo_photosets(photosets):
    """Returns a directory of `photo_id` to `photoset_id` for each photo in a photoset."""

    photo_photosets = {}

    for photoset in photosets:
        for photo_id in photoset['photo_ids']:
            photo_photosets[photo_id] = photoset['id']

    return photo_photosets

def _validate_directory_queries(photo_identifiers, photosets):
    """Verifies that the photos requested in photosets are present in photos."""

    photo_ids = set(photo_identifiers)

    for photoset in photosets:
        for photo_id in photoset['photo_ids']:
            assert photo_id in photo_ids

def _write_photo_directory_file(photo, photoset_id=None):
    """Writes a photo directory file for photo within the directory corresponding to `photoset_id`."""

    directory = 'photostream' if photoset_id is None else photoset_id
    write_photo_data(directory, photo)

def _print_init():
    """Prints a download initiation message."""

    print_timestamped('Beginning to create the directory.')

def _print_summary(photosets):
    """Prints a final download summary."""

    print_separator()
    print_timestamped(
        'Created the directory with {} album(s).'.format(len(photosets))
    )
