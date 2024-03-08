import json
import asyncio
import os
from pathlib import Path

from .rest import post
from .authenticate import refresh_authentication
from .constants import Endpoints, PhotoEntryKeys
from .utils import read_album_metadata, get_album_metadata_path, get_directory_path
from common.files import write_json_file, read_json_file

# TODO: Enable this path to be set by the user; add unicode support?
outputs_path = 'outputs'

async def create_all_albums():
    """Attempts to create all remaining albums and updates the directory files accordingly, including
    the Photos album ID on success, then returns a list of created album IDs."""

    refresh_authentication()

    requests = _get_requests()

    # Run this synchronously, as Google Photos disallows concurrent writes.
    responses = [await request for request in requests]

    _print_summary(responses, requests)

    return responses

def _print_summary(responses, requests):
    """Prints a summary of the proportion of albums created."""

    num_created = len([r for r in responses if r is not None])
    num_attempted = len(requests)

    print(f'Created {num_created} out of {num_attempted} remaining albums.')

def _get_requests():
    """Returns a list of pending requests."""

    requests = []

    for directory_path, _, filenames in os.walk(outputs_path):
        if directory_path == outputs_path:
            continue

        album = read_album_metadata(directory_path)

        if PhotoEntryKeys.GOOGLE_ALBUM_ID in album:
            continue

        requests.append(_create_album(album))

    return requests

async def _create_album(album):
    """Attempts to create `album` and updates its directory file."""

    payload = _create_request_payload(album)
    response = await post(Endpoints.ALBUMS, data=payload)

    photo_album_id = _parse_album_id(response)

    if photo_album_id is not None:
        _update_album_entry(album, photo_album_id)

    return photo_album_id

def _update_album_entry(album, photo_album_id):
    """Updates the album's metadata file given the created `photo_album_id`."""

    album[PhotoEntryKeys.GOOGLE_ALBUM_ID] = photo_album_id

    directory_path = get_directory_path(outputs_path, album['id'])
    path = get_album_metadata_path(directory_path)
    write_json_file(path, album)

def _create_request_payload(album):
    """Generates a request payload to create a new album `album`."""

    title = album['title']

    payload = {
        'album': {
            'title': title,
        }
    }

    return json.dumps(payload)

def _parse_album_id(response):
    """Returns the album ID or `None` on failure."""

    return response.json().get('id', None)
