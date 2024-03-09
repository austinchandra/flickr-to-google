import asyncio
import json
from pathlib import Path

from .photos import query_all_photos
from .photosets import query_photosets
from common.directory import write_album_metadata, write_photo_data
from common.log import print_timestamped, print_separator

# TODO: make this configurable. Clean up modules: use a single base module that can run separate
# commands, importing these from the child directories. Can set configurations in the filesystem, in
# ~/.<config file>; can export constants from the base module. At the same time, should make certain
# function definitions private (if they are not to be called). By convention, this uses the `__`
# prefix as a convention.
output_path = 'outputs'

async def create_directory():
    """Creates a directory of all photosets and photos in `outputs`."""

    _print_initiation()

    photos = await query_all_photos()
    photosets = await query_photosets()

    _validate_directory_queries(photos, photosets)

    _write_photoset_directory_files(photosets)
    _write_photo_directory_files(photos, photosets)

    _print_summary()

def _write_photoset_directory_files(photosets):
    """Writes directory files for `photosets`."""

    for photoset in photosets:
        _write_photoset_directory_file(photoset)

def _write_photo_directory_files(photos, photosets):
    """Writes directory files for `photos` given `photosets`."""

    photo_photosets = _get_photo_photosets(photosets)

    for photo in photos:
        photoset_id = photo_photosets.get(photo['id'], None)
        _write_photo_directory_file(photo, photoset_id)

def _get_photo_photosets(photosets):
    """Returns a directory of `photo_id` to `photoset_id` for each photo in a photoset."""

    photo_photosets = {}

    for photoset in photosets:
        for photo_id in photoset['photo_ids']:
            photo_photosets[photo_id] = photoset['id']

    return photo_photosets

def _validate_directory_queries(photos, photosets):
    """Verifies that the photos requested in photosets are present in photos."""

    photo_ids = set([photo['id'] for photo in photos])

    photoset_photo_ids = [
        photo_id for photoset in photosets for photo_id in photoset['photo_ids']
    ]

    for photo_id in photoset_photo_ids:
        assert photo_id in photo_ids

def _write_photoset_directory_file(photoset):
    """Writes a metadata file for `photoset` to `outputs`."""

    pruned_photoset = _get_pruned_photoset_metadata(photoset)
    write_album_metadata(pruned_photoset)

def _get_pruned_photoset_metadata(photoset):
    """Returns a pruned `photoset` object removing fields that are not needed."""

    pruned = photoset.copy()
    del pruned['photo_ids']

    return pruned

def _write_photo_directory_file(photo, photoset_id=None):
    """Writes a photo directory file for photo within the directory corresponding to `photoset_id`."""

    directory = 'photostream' if photoset_id is None else photoset_id
    write_photo_data(directory, photo)

def _print_initiation():
    """Prints a message on initiating `create_directory`."""

    print_timestamped('Beginning to create the directory.')

def _print_summary():
    """Prints a message on completion."""

    print_timestamped('Created the directory.')
