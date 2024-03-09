import asyncio
import os
import json
from pathlib import Path
from functools import reduce

from .rest import post
from .authenticate import authenticate_user
from .constants import (
    PhotoEntryKeys,
    CONTENT_BATCH_LIMIT,
    REQUESTS_BATCH_SIZE,
)
from common.directory import (
    get_outputs_path,
    get_directory_path,
    read_album_metadata,
    write_photo_data,
    read_photo_data,
)
from common.log import print_timestamped, print_separator
from .photo_content import upload_content_batch
from .photo_bytes import upload_bytes_batch

async def upload_photos():
    """Uploads all photos and updates the entry files, printing output summaries throughout."""

    requests = _get_requests()

    _print_initiation(requests)

    responses = []
    # Handle requests in chunks due to the size:
    start, bound = 0, len(requests)

    while start < bound:
        authenticate_user()

        end = min(start + REQUESTS_BATCH_SIZE, bound)
        # Batch item creations must be performed sequentially. Note that it is possible to run bytes upload
        # jobs while these are pending, but skip this optimization for simplicity.
        chunk_responses = [await request for request, _ in requests[start:end]]
        start += REQUESTS_BATCH_SIZE

        _print_chunk_summary(chunk_responses)
        responses += chunk_responses

    _print_summary(responses)

def _get_requests():
    """Returns a list of requests for photos to upload."""

    requests = []

    outputs_path = get_outputs_path()
    _, directories, _ = next(os.walk(outputs_path))

    for directory in directories:
        _, _, filenames = next(os.walk(get_directory_path(directory)))

        album_id = _read_google_album_id(directory)

        if album_id is None and directory != 'photostream':
            continue

        batches = []
        next_batch = []

        for filename in filenames:
            if filename == 'metadata.json':
                continue

            photo = read_photo_data(directory, filename)

            if PhotoEntryKeys.GOOGLE_MEDIA_ID in photo:
                continue

            if len(next_batch) >= CONTENT_BATCH_LIMIT:
                batches.append(next_batch)
                next_batch = []

            next_batch.append(photo)

        if len(next_batch) > 0:
            batches.append(next_batch)

        batch_requests = [
            (_upload_photo_batch(directory, album_id, batch), len(batch)) for batch in batches
        ]

        requests += batch_requests

    return requests

async def _upload_photo_batch(directory, album_id, batch):
    """Uploads photo bytes and bodies for `batch` then updates the corresponding data entries."""

    uploaded_batch = await upload_bytes_batch(batch)
    photos = await upload_content_batch(uploaded_batch, album_id)

    for photo in photos:
        write_photo_data(directory, photo)

    return (len(photos), len(batch))

def _reduce_response_counts(responses):
    """Reduces a list of proportion tuples to a single cumulative value."""

    return reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), responses, (0, 0))

def _print_initiation(requests):
    """Prints an upload initiation message."""

    print_separator()

    num_photos = _parse_num_photos(requests)
    print_timestamped(
        'Beginning upload for {} remaining photos.'.format(num_photos)
    )

def _print_chunk_summary(responses):
    """Prints an intermediate upload summary."""

    succeeded_count, attempted_count = _reduce_response_counts(responses)

    print_timestamped(
        f'Uploaded {succeeded_count} out of {attempted_count} photo(s).'
    )

def _print_summary(responses):
    """Prints a final upload summary."""

    succeeded_count, attempted_count = _reduce_response_counts(responses)

    print_separator()
    print_timestamped(
        f'Uploaded {succeeded_count} out of {attempted_count} remaining photo(s).'
    )

def _parse_num_photos(requests):
    """Returns the number of photos in `requests` for logging."""

    return sum([batch_size for _, batch_size in requests])

def _read_google_album_id(directory):
    """Returns the Google Photos album ID for the album at `album_path`."""

    metadata = read_album_metadata(directory)
    return metadata.get(PhotoEntryKeys.GOOGLE_ALBUM_ID, None)

