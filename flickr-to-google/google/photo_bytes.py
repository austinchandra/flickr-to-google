import httpx
import mimetypes
import asyncio
from pathlib import Path

from .rest import post, create_headers
from .constants import Endpoints, PhotoEntryKeys
from common.files import write_json_file, read_json_file
from common.request import download_photo_bytes

# TODO: Run a linter

async def upload_bytes_batch(batch):
    """Uploads photo bytes for a list of photos `batch`."""

    photos = await asyncio.gather(
        *[upload_bytes(photo) for photo in batch]
    )

    print('Batch photos with uploaded bytes:')
    print(photos)

    return [photo for photo in photos if photo is not None]

async def upload_bytes(photo):
    """Uploads the bytes for `photo` and returns an updated entry on success."""

    headers = _create_headers(photo)
    _, content, _ = download_photo_bytes(photo)

    if content is None:
        return None

    response = await post(Endpoints.BYTE_UPLOADS, headers, data=content)

    print('Uploading bytes, response:')
    print(response)

    if response is None:
        return None

    upload_token = _parse_upload_token(response)

    if upload_token is not None:
        photo[PhotoEntryKeys.GOOGLE_UPLOAD_TOKEN] = upload_token

        return photo

def _create_headers(photo):
    """Creates HTTP headers for uploading photo bytes."""

    args = {
        'X-Goog-Upload-Protocol': 'raw',
        'Content-type': 'application/octet-stream',
    }

    media_type, _ = mimetypes.guess_type(photo['url'])

    if media_type is not None:
        args['X-Goog-Upload-Content-Type'] = media_type

    return create_headers(**args)

def _parse_upload_token(response):
    """Returns the upload token within the response or `None` on failure."""

    if response.status_code == 200:
        return response.text

    return None
