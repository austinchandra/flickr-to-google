import httpx
import mimetypes
import asyncio
from pathlib import Path

from .rest import post, create_headers
from .constants import Endpoints, PhotoEntryKeys
from common.files import write_json_file, read_json_file

# TODO: Run a linter

async def upload_bytes_batch(batch):
    """Uploads photo bytes for a list of photos `batch`."""

    photos = await asyncio.gather(
        *[upload_bytes(photo) for photo in batch]
    )

    return [photo for photo in photos if photo is not None]

async def upload_bytes(photo):
    """Uploads the bytes for `photo` and returns an updated entry on success."""

    headers = _create_headers(photo)
    content = _download_content(photo)

    response = await post(Endpoints.BYTE_UPLOADS, headers, data=content)

    upload_token = _parse_upload_token(response)

    if upload_token is not None:
        photo[PhotoEntryKeys.GOOGLE_UPLOAD_TOKEN] = upload_token

        return photo

def _download_content(photo):
    """Downloads the photo content and returns the raw bytes."""

    return httpx.get(photo['url'], follow_redirects=True).content

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
