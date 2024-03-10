import asyncio

from .query import query_all_paginated, query
from .config import read_user_id

async def query_all_photos():
    """Queries for all media and returns a list of photo or video objects."""

    user_id = read_user_id()

    return await query_all_paginated(
        _query_photo_page,
        method='flickr.people.getPhotos',
        user_id=user_id
    )

async def _query_photo_page(page_query):
    """Queries a photo page and returns a list of photos for that page."""

    response = await asyncio.create_task(page_query)
    photos = response['photos']['photo']

    queries = [_query_photo_data(photo['id']) for photo in photos]

    return await asyncio.gather(*queries)

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

    response = await query(
        method='flickr.photos.getSizes',
        photo_id=photo_id
    )

    sizes = response['sizes']['size']
    assert len(sizes) > 0

    video_sizes = [size for size in sizes if size['media'] == 'video']

    if len(video_sizes) > 0:
        # Select the largest video, by width.
        original = sorted(video_sizes, key=lambda s: int(s['width']))[-1]
    else:
        original = sizes[-1]
        assert original['label'] == 'Original'

    return original['source']

async def _query_photo_metadata(photo_id):
    """Queries for a photo's metadata and returns the relevant fields."""

    response = await query(
        method='flickr.photos.getInfo',
        photo_id=photo_id
    )

    photo = response['photo']

    metadata = {}

    metadata['id'] = photo['id']
    metadata['title'] = photo['title']['_content']
    metadata['description'] = photo['description']['_content']
    metadata['posted'] = photo['dates']['posted']
    metadata['format'] = photo['originalformat']

    return metadata

def _combine_photo_fields(url, metadata):
    """Combines information fetched from separate photo queries into a single datum.""",

    data = metadata
    data['url'] = url

    return data
