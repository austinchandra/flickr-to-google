import asyncio
import json
from pathlib import Path

from media import query_all_media
from photosets import query_photosets

# TODO: authentication; test cases against a basic account, for all functions; this enables partial
# certainty against functionality, in which the production situation differs only with scale.

# TODO: make this configurable. Clean up modules: use a single base module that can run separate
# commands, importing these from the child directories. Can set configurations in the filesystem, in
# ~/.<config file>; can export constants from the base module. At the same time, should make certain
# function definitions private (if they are not to be called). By convention, this uses the `__`
# prefix as a convention.
output_path = 'outputs'

async def create_directory():
    """Creates a directory of all photosets and photos in `outputs`."""

    photos = await query_all_media()
    photosets = await query_photosets()

    validate_queries(photos, photosets)

    write_photoset_directory_files(photosets)
    write_photo_directory_files(photos, photosets)

def write_photoset_directory_files(photosets):
    """Writes directory files for `photosets`."""

    for photoset in photosets:
        write_photoset_directory_file(photoset)

def write_photo_directory_files(photos, photosets):
    """Writes directory files for `photos` given `photosets`."""

    photo_photosets = get_photo_photosets(photosets)

    for photo in photos:
        photoset_id = photo_photosets.get(photo['id'], None)
        write_photo_directory_file(photo, photoset_id)

def get_photo_photosets(photosets):
    """Returns a directory of `photo_id` to `photoset_id` for each photo in a photoset."""

    photo_photosets = {}

    for photoset in photosets:
        for photo_id in photoset['photo_ids']:
            photo_photosets[photo_id] = photoset['id']

    return photo_photosets

def validate_queries(photos, photosets):
    """Verifies that the photos requested in photosets are present in photos."""

    photo_ids = create_photo_ids_set(photos)

    photoset_photo_ids = [
        photo_id for photoset in photosets for photo_id in photoset['photo_ids']
    ]

    for photo_id in photoset_photo_ids:
        assert photo_id in photo_ids

def create_photo_ids_set(photos):
    """Returns a set consisting of `photo['id']` for set membership checks."""

    return set([photo['id'] for photo in photos])

def write_photoset_directory_file(photoset):
    """Writes a metadata file for `photoset` to `outputs`."""

    pruned_photoset = get_pruned_photoset_metadata(photoset)
    path = create_photoset_metadata_path(pruned_photoset)
    write_json_to_file(path, pruned_photoset)

def get_pruned_photoset_metadata(photoset):
    """Returns a pruned `photoset` object removing fields that are not needed."""

    pruned = photoset.copy()
    del pruned['photo_ids']

    return pruned

def write_photo_directory_file(photo, photoset_id=None):
    """Writes a photo directory file for photo within the directory corresponding to `photoset_id`."""

    if photoset_id is None:
        path = create_photostream_photo_path(photo)
    else:
        path = create_photoset_photo_path(photo, photoset_id)

    write_json_to_file(path, photo)

def write_json_to_file(path, json_contents):
    """Writes a JSON object `json_contents` to a file at `path`."""

    with open(path, 'w') as file:
        contents = json.dumps(json_contents)
        file.write(contents)

def create_output_file_path(path_string):
    """Creates a path object within `outputs` at `path_string`."""

    path = Path(f'{output_path}/{path_string}')
    path.parent.mkdir(parents=True, exist_ok=True)

    return path

def create_photostream_photo_path(photo):
    """Creates the photo path for `photo` within the photostream directory."""

    return create_output_file_path('photostream/{}.json'.format(photo['id']))

def create_photoset_photo_path(photo, photoset_id):
    """Creates the photo path for `photo` within the photoset directory for `photoset_id`."""

    return create_output_file_path('{}/{}.json'.format(photoset_id, photo['id']))

def create_photoset_metadata_path(photoset):
    """Creates the metadata path for `photoset`."""

    return create_output_file_path('{}/metadata.json'.format(photoset['id']))

asyncio.run(create_directory())

# TODO: create query class that exposes public methods, receives a token as input
# (or pulls it from a file); should have an authentication pathway, which takes
# place first, after which the token may be accessed from the query methods directly,
# and nothing else needs to know about it; should use a query class, which would
# be the most natural, although the token may be loaded in the file.

# TODO: test
