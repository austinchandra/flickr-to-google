import asyncio
import json
from pathlib import Path

from .photos import query_all_photos
from .photosets import query_photosets
from common.files import write_json_file

# TODO: make this configurable. Clean up modules: use a single base module that can run separate
# commands, importing these from the child directories. Can set configurations in the filesystem, in
# ~/.<config file>; can export constants from the base module. At the same time, should make certain
# function definitions private (if they are not to be called). By convention, this uses the `__`
# prefix as a convention.
output_path = 'outputs'

async def create_directory():
    """Creates a directory of all photosets and photos in `outputs`."""

    photos = await query_all_photos()
    photosets = await query_photosets()

    _validate_directory_queries(photos, photosets)

    _write_photoset_directory_files(photosets)
    _write_photo_directory_files(photos, photosets)

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
    path = _create_photoset_metadata_path(pruned_photoset)
    write_json_file(path, pruned_photoset)

def _get_pruned_photoset_metadata(photoset):
    """Returns a pruned `photoset` object removing fields that are not needed."""

    pruned = photoset.copy()
    del pruned['photo_ids']

    return pruned

def _write_photo_directory_file(photo, photoset_id=None):
    """Writes a photo directory file for photo within the directory corresponding to `photoset_id`."""

    if photoset_id is None:
        path = _create_photostream_photo_path(photo)
    else:
        path = _create_photoset_photo_path(photo, photoset_id)

    write_json_file(path, photo)

def _create_output_file_path(path_string):
    """Creates a path object within `outputs` at `path_string`."""

    path = Path(f'{output_path}/{path_string}')
    path.parent.mkdir(parents=True, exist_ok=True)

    return path

def _create_photostream_photo_path(photo):
    """Creates the photo path for `photo` within the photostream directory."""

    return _create_output_file_path('photostream/{}.json'.format(photo['id']))

def _create_photoset_photo_path(photo, photoset_id):
    """Creates the photo path for `photo` within the photoset directory for `photoset_id`."""

    return _create_output_file_path('{}/{}.json'.format(photoset_id, photo['id']))

def _create_photoset_metadata_path(photoset):
    """Creates the metadata path for `photoset`."""

    return _create_output_file_path('{}/metadata.json'.format(photoset['id']))
