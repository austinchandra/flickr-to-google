import httpx
import mimetypes
import asyncio
import os
import json
from pathlib import Path
from functools import reduce

from post import post
from authenticate import authenticate
from utils import read_json_file, write_json_file, get_photo_filepaths

# TODO: Move with the others
endpoint = 'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate'
directory_path = 'outputs'
photo_upload_token_key = 'photos-upload-token'
album_id_key = 'photos_album_id'
photo_upload_media_id_key = 'photos-media-id'
upload_batch_limit = 50
request_partition_size = 100

async def upload_all_photos():
    """Attempts to upload all remaining photos and updates the directory files accordingly."""

    requests = get_photo_upload_requests()

    # Handle requests in chunks due to the size:
    # TODO: use common utility
    responses = []
    start = 0

    while start < len(requests):
        authenticate()

        end = min(len(requests), start + request_partition_size)
        # Batch item creations must be performed sequentially.
        responses = [await request for request in requests[start:end]]
        # TODO: Log responses periodically
        start += request_partition_size

    log_photos_uploaded(responses)

    return responses

def log_photos_uploaded(responses):
    """Prints a summary of the response succeeded/attempted totals."""

    response_proportions = [
        (len(photos), len(batch)) for (photos, batch) in responses
    ]

    num_succeeded, num_attempted = reduce(
        lambda x, y: (x[0] + y[0], x[1] + y[1]), response_proportions, (0, 0)
    )

    print(
        "Upload {} out of {} remaining photos.".format(
            num_succeeded, num_attempted
        )
    )

def get_photo_upload_requests():
    """Returns a list of requests for photos that require their content to be uploaded."""

    requests = []

    for dirpath, _, filenames in os.walk(directory_path):
        if dirpath == directory_path:
            continue

        album_id = read_photos_album_id(dirpath)

        if album_id is None:
            continue

        filepaths = get_photo_filepaths(dirpath, filenames)

        photo_batches = []
        batch = []

        for filepath in filepaths:
            photo = read_json_file(filepath)

            if photo_upload_token_key not in photo:
                continue

            if photo_upload_media_id_key in photo:
                continue

            if len(batch) >= upload_batch_limit:
                photo_batches.append(batch)
                batch = []

            batch.append(photo)

        if len(batch) > 0:
            photo_batches.append(batch)

        request = [
            upload_photo_batch(
                dirpath,
                album_id,
                batch,
            ) for batch in photo_batches
        ]

        requests += request

    return requests

def read_photos_album_id(album_path):
    """Reads and returns the Photos album ID corresponding to the album at `album_path`."""

    path = Path(f'{album_path}/metadata.json')
    metadata = read_json_file(path)

    return metadata.get(album_id_key, None)

async def upload_photo_batch(dirpath, album_id, batch):
    """Uploads the batch of photos adds the uploaded IDs to the file on success."""

    content = create_batch_request_payload(album_id, batch)
    response = await post(endpoint, json=content)

    photos = get_response_uploaded_photos(batch, response)

    for (photo, media_id) in photos:
        update_photo_data(dirpath, photo, media_id)

    return (photos, batch)

def create_batch_request_payload(album_id, batch):
    """Returns a payload constituting the body of the batch request."""

    media_items = [
        create_batch_media_item(photo) for photo in batch
    ]

    body = {
        'newMediaItems': media_items
    }

    if album_id is not None:
        body['albumId'] = album_id

    return body

def create_batch_media_item(photo):
    """Returns a batch media item for `photo`."""

    file_name = '{}/{}'.format(photo['title'], photo['format'])
    description = photo['description']
    upload_token = '{}'.format(photo[photo_upload_token_key])

    return {
        'description': description,
        'simpleMediaItem': {
            'fileName': file_name,
            'uploadToken': upload_token,
        }
    }

def update_photo_data(dirpath, photo, media_id):
    """Updates the data file for the photo given the uploaded `media_id`."""

    photo[photo_upload_media_id_key] = media_id

    path = Path('{}/{}.json'.format(dirpath, photo['id']))

    write_json_file(path, photo)

def get_response_uploaded_photos(photos, response):
    """Returns a list of (photo, media_id) tuples for photos for which uploads were successful."""

    if response.status_code != 200:
        return []

    results = response.json()['newMediaItemResults']
    # Tracks responses by upload token, since this is used as a unique identifier for each item.
    upload_media_ids = {}

    for result in results:
        if result['status']['message'] == 'Success':
            token = result['uploadToken']
            media_id = result['mediaItem']['id']

            upload_media_ids[token] = media_id

    uploaded_photos = []

    for photo in photos:
        upload_token = photo[photo_upload_token_key]

        if upload_token not in upload_media_ids:
            continue

        uploaded_photos.append((photo, upload_media_ids[upload_token]))

    return uploaded_photos

asyncio.run(upload_all_photos())
