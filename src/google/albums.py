import json
import asyncio
import os
from pathlib import Path

from post import post
from authenticate import authenticate

# TODO: move to constants
endpoint = 'https://photoslibrary.googleapis.com/v1/albums'
# TODO: Enable this path to be set by the user; add unicode support
directory_path = 'outputs'
# TODO: Move to constants
album_id_key = 'photos_album_id'

async def create_all_albums():
    """Attempts to create all remaining albums and updates the directory files accordingly, including
    the Photos album ID on success, then returns a list of created album IDs."""

    authenticate()

    albums = get_albums_to_create()

    # Run this synchronously, as Google Photos disallows concurrent writes.
    responses = [
        await create_photos_album(album) for album in albums
    ]

    log_albums_created(albums, responses)

    return responses

def log_albums_created(albums, responses):
    """Prints a summary of the fraction of albums created."""

    created = [response for response in responses if response is not None]

    print(
        "Created {} out of {} remaining albums.".format(
            len(created), len(albums)
        )
    )

def get_albums_to_create():
    """Reads all albums within the directory and returns a list of uncreated albums."""

    albums = []

    _, directories, _ = next(os.walk(directory_path))

    for directory in directories:
        album = read_album_metadata(directory)

        if album_id_key in album:
            continue

        albums.append(album)

    return albums

def read_album_metadata(directory):
    """Reads an album at `directory` and returns a dictionary containing its information."""

    path = get_album_metadata_path(directory)

    with open(path, 'r') as file:
        return json.load(file)

async def create_photos_album(album):
    """Attempts to create `album` and updates its directory file."""

    payload = create_request_payload(album)
    response = await post(endpoint, data=payload)

    photo_album_id = get_created_album_id(response)

    if photo_album_id is not None:
        update_album_metadata(album, photo_album_id)

    return photo_album_id

def update_album_metadata(album, photo_album_id):
    """Updates the album's metadata file given the created `photo_album_id`."""

    album[album_id_key] = photo_album_id

    path = get_album_metadata_path(album['id'])

    with open(path, 'w') as file:
        contents = json.dumps(album)
        file.write(contents)

def get_album_metadata_path(directory):
    """Returns the path to the `metadata` file for `directory`."""

    return Path(f'{directory_path}/{directory}/metadata.json')

def create_request_payload(album):
    """Generates a request payload to create a new album `album`."""

    title = album['title']

    payload = {
        'album': {
            'title': title,
        }
    }

    return json.dumps(payload)

def get_created_album_id(response):
    """Returns the album ID or `None` on failure."""

    return response.json().get('id', None)

asyncio.run(create_all_albums())
