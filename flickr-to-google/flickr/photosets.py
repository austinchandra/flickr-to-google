import asyncio

from .query import query_all_paginated, query, query_chunked
from .config import read_user_id
from common.log import print_timestamped
from .api import get_flickr_instance

async def query_photosets():
    """Queries for all photosets and returns a list of photoset objects."""

    user_id = read_user_id()
    flickr = get_flickr_instance()

    async def page_handler(query):
        response = await asyncio.create_task(query)
        photosets = response['photosets']['photoset']

        queries = [_query_photoset_data(photoset) for photoset in photosets]

        return await query_chunked(queries, _print_chunk_summary)

    return await query_all_paginated(
        flickr.photosets.getList,
        page_handler,
        user_id=user_id
    )

async def _query_photoset_data(photoset):
    """Queries for a particular photoset's information and returns a dictionary data object."""

    metadata = _parse_photoset_metadata(photoset)
    photo_ids = await _query_photoset_photos(photoset['id'])

    return _combine_photoset_fields(metadata, photo_ids)

def _parse_photoset_metadata(photoset):
    """Extracts the relevant metadata fields from a photoset response object."""

    metadata = {}

    metadata['id'] = photoset['id']
    metadata['title'] = photoset['title']['_content']
    metadata['created'] = photoset['date_create']

    return metadata

async def _query_photoset_photos(photoset_id):
    """Queries for the photos in the photoset and returns a list of the photo IDs."""

    user_id = read_user_id()
    flickr = get_flickr_instance()

    async def page_handler(query):
        response = await asyncio.create_task(query)
        photo_ids = [photo['id'] for photo in response['photoset']['photo']]

        return photo_ids

    return await query_all_paginated(
        flickr.photosets.getPhotos,
        page_handler,
        photoset_id=photoset_id,
        user_id=user_id
    )

def _combine_photoset_fields(metadata, photo_ids):
    """Combines photoset values separately retrieved into a single datum."""

    data = metadata
    data['photo_ids'] = photo_ids

    return data

def _print_chunk_summary(responses):
    """Prints a summary for each chunk of downloading."""

    print_timestamped(
        'Downloaded photoset data for {} album(s).'.format(len(responses))
    )
