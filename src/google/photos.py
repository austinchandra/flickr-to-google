import httpx
import mimetypes
import asyncio
import os
import json
from pathlib import Path

from post import post

# TODO: upload all bytes asynchronously by making a list of tasks per file:
# https://developers.google.com/photos/library/guides/upload-media?authuser=1
#
# Create one batchCreate per album (per 50 items); do not use these in parallel; these will be fast,
# however, as the blobs are already uploaded; then, write to the files accordingly (on success);
# each attempt can simply read each file, identify the status, and act appropriately.
#
# Can test this at small-scale with a few hundred photos/videos, etc.

# TODO: Move with the others
endpoint = 'https://photoslibrary.googleapis.com/v1/uploads'
directory_path = 'outputs'
photo_upload_token_key = 'photos-upload-token'
album_id_key = 'photos_album_id'

async def upload_all_photo_bytes():
    """Attempts to upload all remaining photos and updates the directory files accordingly."""

    requests = get_photo_upload_requests()

    responses = await asyncio.gather(*requests)

    log_photo_bytes_uploaded(requests, responses)

    return responses

# TODO: Make a common util with albums
def log_photo_bytes_uploaded(requests, responses):
    """Prints a summary of the fraction of requests that succeeded."""

    succeeded = [response for response in responses if response is not None]

    print(
        "Upload bytes for {} out of {} remaining photos.".format(
            len(succeeded), len(requests)
        )
    )

def get_photo_upload_requests():
    """Returns a list of requests for photos which must be uploaded."""

    requests = []

    for dirpath, _, filenames in os.walk(directory_path):
        if dirpath == directory_path:
            continue

        album_id = read_photos_album_id(dirpath)

        if album_id is None:
            continue

        filepaths = get_photo_filepaths(dirpath, filenames)

        for filepath in filepaths:
            photo = read_json_file(filepath)

            if photo_upload_token_key in photo:
                continue

            request = upload_photo_bytes(
                filepath,
                photo,
                album_id,
            )

            requests.append(request)

    return requests

def get_photo_filepaths(dirpath, filenames):
    """Returns a list of paths for the photos at `dirpath` with filenames `filenames`."""

    photo_filenames = [
        filename for filename in filenames if 'metadata.json' not in filename
    ]

    return [os.path.join(dirpath, filename) for filename in photo_filenames]

def read_photos_album_id(album_path):
    """Reads and returns the Photos album ID corresponding to the album at `album_path`."""

    path = Path(f'{album_path}/metadata.json')
    metadata = read_json_file(path)

    return metadata.get(album_id_key, None)

# TODO: make this a common utility
def read_json_file(path):
    """Reads and returns the JSON object at path."""

    with open(path, 'r') as file:
        return json.load(file)

async def upload_photo_bytes(path, photo, album_id):
    """Uploads the bytes for `photo` and adds its upload token to the file on success."""

    content = download_photo_bytes(photo)
    headers = create_bytes_upload_headers(photo)

    response = await post(endpoint, content, **headers)

    upload_token = get_response_upload_token(response)

    if upload_token is not None:
        update_photo_data(path, photo, upload_token)

    return upload_token

def update_photo_data(path, photo, upload_token):
    """Updates the data file for the photo given the uploaded `token`."""

    photo[photo_upload_token_key] = upload_token

    # TODO: move to shared
    with open(path, 'w') as file:
        contents = json.dumps(photo)
        file.write(contents)

def download_photo_bytes(photo):
    """Downloads the photo content and returns the raw bytes."""

    return httpx.get(photo['url']).content

def create_bytes_upload_headers(photo):
    """Creates HTTP headers for uploading photo bytes."""

    headers = {
        'X-Goog-Upload-Protocol': 'raw',
        'Content-type': 'application/octet-stream',
    }

    media_type, _ = mimetypes.guess_type(photo['url'])

    if media_type is not None:
        headers['X-Goog-Upload-Content-Type'] = media_type

    return headers

def get_response_upload_token(response):
    """Returns the upload token within the response or `None` on failure."""

    if response.status_code == 200:
        return response.text

    return None

asyncio.run(upload_all_photo_bytes())
