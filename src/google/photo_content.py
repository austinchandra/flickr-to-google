import httpx
import asyncio

from .rest import post
from .constants import (
    Endpoints,
    PhotoEntryKeys,
)

async def upload_content_batch(batch, album_id):
    """Uploads a batch of photos `batch` and returns a list of uploaded photos, updated in-place."""

    content = _create_request_payload(album_id, batch)
    response = await post(Endpoints.BATCH_CREATE, json=content)

    photos = _get_uploaded_photos(batch, response)

    return photos

def _create_request_payload(album_id, batch):
    """Returns a payload to serve as the body of the batch request."""

    media_items = [
        _create_media_item(photo) for photo in batch
    ]

    body = {
        'newMediaItems': media_items
    }

    if album_id is not None:
        body['albumId'] = album_id

    return body

def _create_media_item(photo):
    """Returns a batch media item for `photo`."""

    file_name = '{}/{}'.format(photo['title'], photo['format'])
    description = photo['description']
    upload_token = photo[PhotoEntryKeys.GOOGLE_UPLOAD_TOKEN]

    return {
        'description': description,
        'simpleMediaItem': {
            'fileName': file_name,
            'uploadToken': upload_token,
        }
    }

def _get_uploaded_photos(batch, response):
    """Returns a list of uploaded photos, each updated in-place."""

    results = _parse_results(response)
    media_ids = _parse_media_ids(results)

    photos = []

    for photo in batch:
        upload_token = photo[PhotoEntryKeys.GOOGLE_UPLOAD_TOKEN]
        media_id = media_ids.get(upload_token, None)

        if media_id is None:
            continue

        photo[PhotoEntryKeys.GOOGLE_MEDIA_ID] = media_id
        photos.append(photo)

    return photos

def _parse_results(response):
    """Returns the results for `response` or None on failure."""

    if response.status_code != 200:
        return []

    return response.json()['newMediaItemResults']

def _parse_media_ids(results):
    """Returns a dictionary of `upload_token` to `media_id` for uploaded media."""

    # Tracks responses by upload token, since this is used as a unique identifier for each item.
    media_ids = {}

    for result in results:
        if result['status']['message'] == 'Success':
            token = result['uploadToken']
            media_id = result['mediaItem']['id']

            media_ids[token] = media_id

    return media_ids
