import asyncio

from .query import query_all_paginated, query, query_chunked
from .config import read_user_id
from common.log import print_timestamped
from .api import get_flickr

async def query_all_photos():
    """Queries for all media and returns a list of photo or video objects."""

    flickr = get_flickr()
    user_id = read_user_id()

    return await query_all_paginated(
        flickr.people.getPhotos,
        _query_photo_page,
        user_id=user_id,
    )

async def _query_photo_page(page_query):
    """Queries a photo page and returns a list of photos for that page."""

    page_response = await asyncio.create_task(page_query)
    photos = page_response['photos']['photo']

    queries = [_query_photo_data(photo['id']) for photo in photos]

    return await query_chunked(queries, _print_chunk_summary)

async def _query_photo_data(photo_id):
    """Performs a set of queries for the given photo object and returns a dictionary data object."""

    [url, metadata] = await asyncio.gather(
        _query_photo_source(photo_id),
        _query_photo_metadata(photo_id),
    )

    return _combine_photo_fields(url, metadata)

async def _query_photo_source(photo_id):
    """Queries for a photo's source and returns the URL of the original file."""

    # Query `getSizes` to find the original source:
    # - https://www.flickr.com/services/api/flickr.photos.getSizes.html
    # URLs cannot be constructed using the original IDs without a loss in quality:
    # - https://www.flickr.com/services/api/misc.urls.html

    flickr = get_flickr()

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

    # Select the value by largest combined resolution.
    sorted_sizes = sorted(
        sizes,
        key=lambda size: int(size['width']) * int(size['height']),
        reverse=True
    )

    original = sorted_sizes[0]

    return original['source']

async def _query_photo_metadata(photo_id):
    """Queries for a photo's metadata and returns the relevant fields."""

    flickr = get_flickr()

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

    return metadata

def _combine_photo_fields(url, metadata):
    """Combines information fetched from separate photo queries into a single datum.""",

    data = metadata
    data['url'] = url

    return data

def _print_chunk_summary(count):
    """Prints a summary for each chunk of downloading."""

    print_timestamped(
        'Downloaded photo data for {} images.'.format(count)
    )
