import httpx
import mimetypes
import asyncio
import os
import json
from pathlib import Path

from post import post, create_headers
from authenticate import authenticate
from utils import read_json_file, write_json_file, get_photo_filepaths

# TODO: Can test this at small-scale with a few dozen photos/videos, etc.

# TODO: Move with the others
endpoint = 'https://photoslibrary.googleapis.com/v1/uploads'
directory_path = 'outputs'
photo_upload_token_key = 'photos-upload-token'
request_partition_size = 100

async def upload_all_photo_bytes():
    """Attempts to upload all remaining photo bytes and updates the directory files accordingly."""

    requests = get_photo_bytes_upload_requests()

    # Handle requests in chunks due to the size:
    responses = []
    start = 0

    while start < len(requests):
        authenticate()

        end = min(len(requests), start + request_partition_size)
        responses += await asyncio.gather(*requests[start:end])
        start += request_partition_size

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

def get_photo_bytes_upload_requests():
    """Returns a list of requests for photos that require their content to be uploaded."""

    requests = []

    for dirpath, _, filenames in os.walk(directory_path):
        if dirpath == directory_path:
            continue

        filepaths = get_photo_filepaths(dirpath, filenames)

        for filepath in filepaths:
            photo = read_json_file(filepath)

            if photo_upload_token_key in photo:
                continue

            request = upload_photo_bytes(
                filepath,
                photo,
            )

            requests.append(request)

    return requests

async def upload_photo_bytes(path, photo):
    """Uploads the bytes for `photo` and adds its upload token to the file on success."""

    headers = create_bytes_upload_headers(photo)
    content = download_photo_bytes(photo)

    response = await post(endpoint, headers, data=content)

    upload_token = get_response_upload_token(response)

    if upload_token is not None:
        update_photo_data(path, photo, upload_token)

    return upload_token

def update_photo_data(path, photo, upload_token):
    """Updates the data file for the photo given the uploaded `token`."""

    photo[photo_upload_token_key] = upload_token
    write_json_file(path, photo)

def download_photo_bytes(photo):
    """Downloads the photo content and returns the raw bytes."""

    return httpx.get(photo['url']).content

def create_bytes_upload_headers(photo):
    """Creates HTTP headers for uploading photo bytes."""

    args = {
        'X-Goog-Upload-Protocol': 'raw',
        'Content-type': 'application/octet-stream',
    }

    media_type, _ = mimetypes.guess_type(photo['url'])

    if media_type is not None:
        args['X-Goog-Upload-Content-Type'] = media_type

    return create_headers(**args)

def get_response_upload_token(response):
    """Returns the upload token within the response or `None` on failure."""

    if response.status_code == 200:
        return response.text

    return None

asyncio.run(upload_all_photo_bytes())
