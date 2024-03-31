import os
import asyncio

from .query import query_all_paginated, query, query_chunked
from .config import read_user_id
from common.log import print_timestamped, print_separator
from common.directory import (
    get_outputs_path,
    get_directory_path,
    write_photo_data,
    read_photo_data,
)
from .api import get_flickr_instance, init as init_flickr_api

async def query_photo_identifiers():
    """Queries and returns a list of photo identifiers."""

    user_id = read_user_id()
    flickr = get_flickr_instance()

    async def page_handler(query):
        page_response = await asyncio.create_task(query)
        photos = page_response['photos']['photo']

        return [photo['id'] for photo in photos]

    return await query_all_paginated(
        flickr.people.getPhotos,
        page_handler,
        user_id=user_id,
    )

async def query_photo_data():
    """Queries all remaining photo fields and updates the directory."""

    init_flickr_api()

    requests = _get_requests()
    _print_init(requests)
    responses = await query_chunked(requests, _print_download_proportion)
    _print_summary(responses)

    return _get_proportion_downloaded(responses)

def _get_requests():
    """Returns a list of requests with photos to populate."""

    requests = []

    _, directories, _ = next(os.walk(get_outputs_path()))
    for directory in directories:

        _, _, filenames = next(os.walk(get_directory_path(directory)))
        for filename in filenames:
            if filename == 'metadata.json':
                continue

            photo = read_photo_data(directory, filename)

            if len(photo.keys()) > 1:
                continue

            requests.append(_query_photo_data(directory, photo['id']))

    return requests

async def _query_photo_data(directory, photo_id):
    """Queries a photo's data and updates its data entry."""

    try:
        [url, metadata] = await asyncio.gather(
            _query_photo_source(photo_id),
            _query_photo_metadata(photo_id),
        )

        photo = _combine_photo_fields(url, metadata)
        write_photo_data(directory, photo)

        return photo
    except Exception as err:
        print(err)
        return None

async def _query_photo_source(photo_id):
    """Queries for a photo's source and returns the URL of the original file."""

    # Query `getSizes` to find the original source:
    # - https://www.flickr.com/services/api/flickr.photos.getSizes.html
    # URLs cannot be constructed using the original IDs without a loss in quality:
    # - https://www.flickr.com/services/api/misc.urls.html

    flickr = get_flickr_instance()

    response = await query(
        flickr.photos.getSizes,
        photo_id=photo_id
    )

    sizes = response['sizes']['size']

    assert len(sizes) > 0

    # Filter video sizes for videos:
    video_sizes = [size for size in sizes if size['media'] == 'video']
    sizes = video_sizes if len(video_sizes) > 0 else sizes

    # Filter sizes with no width/height responses:
    sizes = [size for size in sizes if size['width'] is not None and size['height'] is not None]

    # Find the original size if it exists:
    original = None

    for size in sizes:
        if size['label'] == 'Original' or size['label'] == 'Video Original':
            original = size

    # Otherwise, select the value by largest resolution.
    if original is None:
        sorted_sizes = sorted(
            sizes,
            key=lambda size: int(size['width']) * int(size['height']),
            reverse=True
        )

        original = sorted_sizes[0]

    return original['source']

async def _query_photo_metadata(photo_id):
    """Queries for a photo's metadata and returns the relevant fields."""

    flickr = get_flickr_instance()

    response = await query(
        flickr.photos.getInfo,
        photo_id=photo_id
    )

    photo = response['photo']

    metadata = {}

    metadata['id'] = photo['id']
    metadata['title'] = photo['title']['_content']
    metadata['description'] = photo['description']['_content']
    metadata['posted'] = photo['dates']['posted']
    metadata['media'] = photo['media']

    return metadata

def _combine_photo_fields(url, metadata):
    """Combines information fetched from separate photo queries into a single datum.""",

    data = metadata
    data['url'] = url

    return data

def _print_init(requests):
    """Prints an initialization message with a timestamp."""

    print_timestamped(
        'Beginning to download metadata for {} photos.'.format(len(requests))
    )

def _get_proportion_downloaded(responses):
    """Returns a `(num_succeeded, num_attempted)` tuple of the proportion of photos downloaded."""

    num_succeeded = len([r for r in responses if r is not None])
    num_attempted = len(responses)

    return (num_succeeded, num_attempted)

def _print_download_proportion(responses):
    """Prints a download proportion for `responses`."""

    num_succeeded, num_attempted = _get_proportion_downloaded(responses)

    print_timestamped(
        f'Downloaded photo data for {num_succeeded} of {num_attempted} images.'
    )

def _print_summary(responses):
    """Prints a summary on download completion."""

    print_separator()
    _print_download_proportion(responses)
