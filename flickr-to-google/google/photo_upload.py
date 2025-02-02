import asyncio
import os
import json
from pathlib import Path
from functools import reduce

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

async def upload_photos(
    is_videos_only=False,
    is_missing_exif_only=False,
    is_uploading_all=False,
):
    """Uploads all photos and updates the entry files, printing output summaries throughout."""

    requests = _get_requests(
        is_videos_only,
        is_missing_exif_only,
        is_uploading_all,
    )

    _print_init(requests)

    responses = []

    # Handle requests in chunks due to the size of requests:

    for i in range(0, len(requests), REQUESTS_BATCH_SIZE):
        authenticate_user()

        # Batch item creations must be performed sequentially. Note that it is possible to run bytes upload
        # jobs while these are pending, but skip this optimization for simplicity.
        for request, _ in requests[i:i + REQUESTS_BATCH_SIZE]:
            batch_response = await request
            responses.append(batch_response)
            _print_batch_summary(batch_response, responses)

    _print_summary(responses)

    return _reduce_response_counts(responses)

def _get_requests(
    is_videos_only,
    is_missing_exif_only,
    is_uploading_all,
):
    """Returns a list of batch requests for all remaining photos."""

    requests = []

    _, directories, _ = next(os.walk(get_outputs_path()))

    for directory in directories:
        google_album_id = _read_google_album_id(directory)

        assert google_album_id is not None or directory == 'photostream'

        photos = _get_pending_photos(
            directory,
            is_videos_only,
            is_missing_exif_only,
            is_uploading_all,
        )

        for i in range(0, len(photos), CONTENT_BATCH_LIMIT):
            batch = photos[i: i + CONTENT_BATCH_LIMIT]
            request = _upload_photo_batch(
                directory,
                google_album_id,
                batch,
            )

            # Add the batch size for logging.
            requests.append((request, len(batch)))

    return requests

def _get_pending_photos(
    directory,
    is_videos_only,
    is_missing_exif_only,
    is_uploading_all,
):
    """Returns a list of photos to be uploaded within `directory`."""

    photos = []

    _, _, filenames = next(os.walk(get_directory_path(directory)))

    for filename in filenames:
        if filename == 'metadata.json':
            continue

        photo = read_photo_data(directory, filename)

        if PhotoEntryKeys.GOOGLE_MEDIA_ID in photo and not is_uploading_all:
            continue

        if is_videos_only and not _is_media_video(photo):
            continue

        if is_missing_exif_only and PhotoEntryKeys.DID_UPDATE_EXIF not in photo:
            continue

        # Ignore photos that were not properly fetched:
        if len(photo.keys()) <= 1:
            continue

        photos.append(photo)

    return photos

async def _upload_photo_batch(directory, album_id, batch):
    """Uploads photo bytes and bodies for `batch` then updates the corresponding data entries."""

    uploaded_batch = await upload_bytes_batch(batch)
    photos = await upload_content_batch(uploaded_batch, album_id)

    for photo in photos:
        write_photo_data(directory, photo)

    return (len(photos), len(batch))

def _is_media_video(photo):
    """Returns a boolean indicating whether the media item is a video."""

    return photo['media'] == 'video'

def _reduce_response_counts(responses):
    """Reduces a list of proportion tuples to a single cumulative value."""

    return reduce(lambda x, y: (x[0] + y[0], x[1] + y[1]), responses, (0, 0))

def _print_init(requests):
    """Prints an upload initiation message."""

    num_photos = _parse_num_photos(requests)

    print_separator()
    print_timestamped(
        'Beginning upload for {} remaining photo(s).'.format(num_photos)
    )

def _print_batch_summary(batch_response, responses):
    """Prints an intermediate upload summary."""

    batch_succeeded_count, batch_attempted_count = batch_response

    content = 'Uploaded {} out of {} photo(s).'.format(
        batch_succeeded_count,
        batch_attempted_count,
    )

    print_timestamped(content)

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

    if directory == 'photostream':
        return None

    metadata = read_album_metadata(directory)
    return metadata.get(PhotoEntryKeys.GOOGLE_ALBUM_ID, None)

