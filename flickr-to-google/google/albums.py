import json
import asyncio
import os
from pathlib import Path

from .rest import post
from .authenticate import authenticate_user
from .constants import Endpoints, PhotoEntryKeys
from common.directory import (
    read_album_metadata,
    write_album_metadata,
    get_outputs_path,
)
from common.log import print_timestamped, print_separator

async def create_albums():
    """Attempts to create all remaining albums and updates the directory files accordingly, including
    the Photos album ID on success, then returns the proportion created as a tuple."""

    authenticate_user()

    requests = _get_requests()

    _print_init(requests)

    # Run this synchronously, as Google Photos disallows concurrent writes.
    responses = [await request for request in requests]

    _print_summary(responses, requests)

    return _get_proportion_created(responses, requests)

def _get_requests():
    """Returns a list of unfulfilled album creation requests."""

    requests = []

    outputs_path = get_outputs_path()
    _, directories, _ = next(os.walk(outputs_path))

    for directory in directories:
        if directory == 'photostream':
            continue

        album = read_album_metadata(directory)

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
    write_album_metadata(album)

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

def _print_init(requests):
    """Prints an upload initiation message."""

    print_timestamped(
        'Beginning to create {} remaining album(s).'.format(len(requests))
    )

def _print_summary(responses, requests):
    """Prints a final upload summary."""

    num_created, num_attempted = _get_proportion_created(responses, requests)

    print_separator()
    print_timestamped(
        f'Created {num_created} out of {num_attempted} remaining album(s).'
    )

def _get_proportion_created(responses, requests):
    """Returns a `(num_created, num_attempted)` tuple given `responses` and `requests`."""

    num_created = len([r for r in responses if r is not None])
    num_attempted = len(requests)

    return (num_created, num_attempted)

