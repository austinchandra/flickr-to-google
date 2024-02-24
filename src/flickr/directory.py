import asyncio

from oauth import generate_oauth_token
from query import query_all_paginated, query

# Perform all queries and validate the responses; extract information into text contents
# to be written to disk; write these to disk, one by one. Set up handling albums such
# that photos queried through getPhotos can be linked to their respective albums.

# The downloader can run through the incomplete files linked here; pull image contents
# to a temp folder, transfer them, then erase on completion.

# TODO: find out whether the destination is Google Drive or Photos.

# TODO: Testing and error handling: test videos, pagination.
# TODO: Query for albums or photosets.

async def query_all_media():
    """Queries for all photos and returns a list of media objects."""

    queries = await query_all_paginated(token, 'flickr.people.getPhotos', user_id=user_id)

    media = await asyncio.gather(
        *[query_media_page(query) for query in queries]
    )

    return flatten(media)

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

    response = await query(token, 'flickr.photos.getSizes', photo_id=photo_id)
    sizes = response['sizes']['size']

    assert len(sizes) > 0
    original = sizes[-1]
    assert original['label'] == 'Original'

    return original['source']

async def query_media_metadata(photo_id):
    """Queries for a media's metadata and returns the relevant fields."""

    response = await query(token, 'flickr.photos.getInfo', photo_id=photo_id)
    media = response['photo']

    metadata = {}

    metadata['title'] = media['title']['_content']
    metadata['posted'] = media['dates']['posted']
    metadata['format'] = media['originalformat']

    return metadata

def combine_media_fields(url, metadata):
    """Combines information fetched from separate media queries into a single datum.""",

    data = metadata
    data['url'] = url

    return data

def flatten(l):
    """Flattens a list `l`."""

    return [subitem for item in l for subitem in item]

token = generate_oauth_token()
user_id = '200072260@N02'

async def test():
    directory = await query_all_media()
    print(directory)

asyncio.run(test())
