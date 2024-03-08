import asyncio
import os
import json
import datetime
from pathlib import Path
from functools import reduce

from .rest import post
from .authenticate import refresh_authentication
from .constants import (
    PhotoEntryKeys,
    CONTENT_BATCH_LIMIT,
    REQUESTS_BATCH_SIZE,
)
from common.files import write_json_file, read_json_file
from .utils import get_photo_data_path, read_album_metadata
from .photo_content import upload_content_batch
from .photo_bytes import upload_bytes_batch

# TODO: pull from context
outputs_path = 'outputs'

async def upload_all_photos():
    """Uploads all photos and updates the entry files, printing output summaries throughout."""

    requests = _get_photo_upload_requests()

    responses = []
    # Handle requests in chunks due to the size:
    start, bound = 0, len(requests)

    while start < bound:
        refresh_authentication()

        end = min(start + REQUESTS_BATCH_SIZE, bound)
        # Batch item creations must be performed sequentially. Note that it is possible to run bytes upload
        # jobs while these are pending, but skip this optimization for simplicity.
        chunk_responses = [await request for request in requests[start:end]]
        start += REQUESTS_BATCH_SIZE

        _print_chunk_summary(chunk_responses)
        responses += chunk_responses

    _print_upload_summary(responses)

def _get_photo_upload_requests():
    """Returns a list of requests for photos to upload."""

    requests = []

    for directory_path, _, filenames in os.walk(outputs_path):
        if directory_path == outputs_path:
            continue

        album_id = _read_google_album_id(directory_path)

        if 'photostream' not in directory_path and album_id is None:
            continue

        filepaths = _get_photo_filepaths(directory_path, filenames)

        photo_batches = []
        batch = []

        for filepath in filepaths:
            photo = read_json_file(filepath)

            if PhotoEntryKeys.GOOGLE_MEDIA_ID in photo:
                continue

            if len(batch) >= CONTENT_BATCH_LIMIT:
                photo_batches.append(batch)
                batch = []

            batch.append(photo)

        if len(batch) > 0:
            photo_batches.append(batch)

        request = [
            _upload_photo_batch(
                directory_path,
                album_id,
                batch,
            ) for batch in photo_batches
        ]

        requests += request

    return requests

async def _upload_photo_batch(directory_path, album_id, batch):
    """Uploads photo bytes and bodies for `batch` then updates the corresponding data entries."""

    uploaded_batch = await upload_bytes_batch(batch)
    photos = await upload_content_batch(uploaded_batch, album_id)

    for photo in photos:
        _update_photo_data(directory_path, photo)

    return (len(photos), len(batch))

def _reduce_response_counts(responses):
    """Reduces a list of proportion tuples to a single cumulative value."""

    return reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), responses, (0, 0))

def _print_upload_summary(responses):
    """Prints a final upload summary."""

    succeeded_count, attempted_count = _reduce_response_counts(responses)
    timestamp = _compute_formatted_timestamp()

    print('--------')
    print(f'Uploaded {succeeded_count} out of {attempted_count} remaining photos at {timestamp}.')

def _print_chunk_summary(responses):
    """Prints an intermediate upload summary."""

    succeeded_count, attempted_count = _reduce_response_counts(responses)
    timestamp = _compute_formatted_timestamp()

    print(f'Uploaded {succeeded_count} out of {attempted_count} photos at {timestamp}.')

def _compute_formatted_timestamp():
    """Returns a formatted timestamp (e.g. 2024-03-09 09:28:05)."""

    return str(datetime.datetime.now()).split('.')[0]

def _get_photo_filepaths(directory_path, filenames):
    """Returns a list of paths for the photos at `directory_path` with filenames `filenames`."""

    photo_filenames = [
        filename for filename in filenames if 'metadata.json' not in filename
    ]

    return [os.path.join(directory_path, filename) for filename in photo_filenames]

def _read_google_album_id(album_path):
    """Returns the Google Photos album ID for the album at `album_path`."""

    metadata = read_album_metadata(album_path)
    return metadata.get(PhotoEntryKeys.GOOGLE_ALBUM_ID, None)

def _update_photo_data(directory_path, photo):
    """Updates the photo data for `photo` and `directory_path`."""

    path = get_photo_data_path(directory_path, photo)
    write_json_file(path, photo)

