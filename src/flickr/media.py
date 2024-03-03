import asyncio

from query import query_all_paginated, query

# Perform all queries and validate the responses; extract information into text contents
# to be written to disk; write these to disk, one by one. Set up handling albums such
# that photos queried through getPhotos can be linked to their respective albums.

# The downloader can run through the incomplete files linked here; pull image contents
# to a temp folder, transfer them, then erase on completion.

# TODO: find out whether the destination is Google Drive or Photos. (Photos)
# TODO: Add CLI paths to verify, store the OAuth code on a separate file for re-use.
# TODO: use streaming implementation; use photosets to build a directory (for photo albums).
# TODO: create directories; create authentication paths for each side; create the transfer code.

# TODO: Testing and error handling: test videos, pagination (e.g. on the actual dataset).
# TODO: Query for albums or photosets.

# TODO: build the directory: can run through each photoset, create the resulting directory
# files; for each, pull the relevant photo information from the list of photos, then remove
# these (after transferred); build the photostream directory from the remaining photos.

async def query_all_media():
    """Queries for all photos and returns a list of media objects."""

    return await query_all_paginated(
        query_media_page,
        method='flickr.people.getPhotos',
        user_id=user_id
    )

async def query_media_page(page_query):
    """Queries a media page and returns a list of media for that page."""

    response = await asyncio.create_task(page_query)
    photos = response['photos']['photo']

    queries = [query_media_data(photo['id']) for photo in photos]

    return await asyncio.gather(*queries)

async def query_media_data(photo_id):
    """Performs a set of queries for the given media object and returns a dictionary data object."""

    [url, metadata] = await asyncio.gather(
        query_media_source(photo_id),
        query_media_metadata(photo_id),
    )

    return combine_media_fields(url, metadata)

async def query_media_source(photo_id):
    """Queries for a media's source and returns the URL of the original file."""

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
    original = sizes[-1]
    assert original['label'] == 'Original'

    return original['source']

async def query_media_metadata(photo_id):
    """Queries for a media's metadata and returns the relevant fields."""

    response = await query(
        method='flickr.photos.getInfo',
        photo_id=photo_id
    )

    media = response['photo']

    metadata = {}

    metadata['id'] = media['id']
    metadata['title'] = media['title']['_content']
    metadata['posted'] = media['dates']['posted']
    metadata['format'] = media['originalformat']

    return metadata

def combine_media_fields(url, metadata):
    """Combines information fetched from separate media queries into a single datum.""",

    data = metadata
    data['url'] = url

    return data

user_id = '200072260@N02'
