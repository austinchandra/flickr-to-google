import asyncio

from oauth import generate_oauth_token
from query import query_all_paginated, query

# TODO: Test pagination in photos (within photoset).

async def query_photosets():
    """Queries for all photosets and returns a list of photoset objects."""

    return await query_all_paginated(
        query_photoset_page,
        token,
        method='flickr.photosets.getList',
        user_id=user_id
    )

async def query_photoset_page(page_query):
    """Queries a photoset page and returns a list of photosets for that page."""

    response = await asyncio.create_task(page_query)
    photosets = response['photosets']['photoset']

    queries = [query_photoset_data(photoset) for photoset in photosets]

    return await asyncio.gather(*queries)

async def query_photoset_data(photoset):
    """Queries for a particular photoset's information and returns a dictionary data object."""

    metadata = parse_photoset_metadata(photoset)
    photo_ids = await query_photoset_photos(photoset['id'])

    return combine_photoset_fields(metadata, photo_ids)

def parse_photoset_metadata(photoset):
    """Extracts the relevant metadata fields from a photoset response object."""

    metadata = {}

    metadata['id'] = photoset['id']
    metadata['title'] = photoset['title']['_content']
    metadata['created'] = photoset['date_create']

    return metadata

async def query_photoset_photos(photoset_id):
    """Queries for the photos in the photoset and returns a list of the photo IDs."""

    return await query_all_paginated(
        query_photoset_photos_page,
        token,
        method='flickr.photosets.getPhotos',
        photoset_id=photoset_id,
        user_id=user_id
    )

async def query_photoset_photos_page(page_query):
    """Queries a page of photos within a photoset and returns a list of the photo IDs."""

    response = await asyncio.create_task(page_query)
    photo_ids = [photo['id'] for photo in response['photoset']['photo']]

    return photo_ids

def combine_photoset_fields(metadata, photo_ids):
    """Combines photoset values separately retrieved into a single datum."""

    data = metadata
    data['photo_ids'] = photo_ids

    return data

token = generate_oauth_token()
user_id = '200072260@N02'

async def test():
    directory = await query_photosets()
    print(directory)

asyncio.run(test())
