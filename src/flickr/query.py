import httpx
import json

from credentials import api_key

rest_url = 'https://www.flickr.com/services/rest/'

# TODO: modify per_page to decrease the number of queries.

# Query in a callback (on separate thread); return a handle on the thread to be joined.
# This seems the typical solution to handle concurrency; async/await is another option,
# using asyncio; can then use a thread pool (or process pool, for writing to disk, but
# this is unlikely to be necessary):

# https://docs.python.org/3/library/asyncio.html
# - https://docs.python.org/3/library/asyncio-task.html
# - https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor

# Will need a mutex to handle shared memory:
# - https://docs.python.org/3/library/asyncio-sync.html#asyncio.Lock

# Asyncio is not thread-safe, meaning these values cannot be accessed across threads
# (but within a single thread, i.e. the calling thread, these can be treated using standard
# parallelism).

# To run multiple requests (and await the result), akin to a thread spawn/join on all:
# https://docs.python.org/3/library/asyncio-task.html#asyncio.gather
# The paginated query can await the first query; then, create a set of async queries to
# be performed (can duplicate the first query here, to keep the interface clean); return
# these as a list, in which they may be wrapped and gathered accordingly.

# Can take advantage of WebSockets with built-in async (and remove overhead from multi-threading).

# https://stackoverflow.com/questions/27435284/multiprocessing-vs-multithreading-vs-asyncio
# https://github.com/encode/httpx

async def query_all_paginated(oauth_token, method, **kwargs):
    """Returns a list of all paginated queries."""

    page_limit = await query_page_limit(oauth_token, method, **kwargs)

    # Repeat the original page query here, for simplicity.

    return [
        query(oauth_token, method, page=page, **kwargs) for page in range(1, page_limit + 1)
    ]

async def query(oauth_token, method, **kwargs):
    """Performs an API query and returns the JSON response."""

    payload = create_query_payload(oauth_token, method, **kwargs)

    async with httpx.AsyncClient() as client:
        response = await client.get(rest_url, params=payload)
        return unwrap_response_json(response.text)

def create_query_payload(oauth_token, method, **kwargs):
    """Creates a query payload with the given authorization, method, and key-value pairs."""

    payload = {}

    # Set known arguments first to enable over-writing these.
    payload['api_key'] = api_key
    payload['format'] = 'json'
    payload['method'] = method

    for _, (k, v) in enumerate(oauth_token.items()):
        # TODO: validation?
        payload[k] = v

    for _, (k, v) in enumerate(kwargs.items()):
        payload[k] = v

    return payload

def unwrap_response_json(contents):
    """Extracts the inner json from contents of form `jsonFlickrApi(<json>)`."""

    start = contents.find('{')
    # Find the last index of '}':
    end = contents[::-1].find('}') * -1

    return json.loads(contents[start:end])

async def query_page_limit(oauth_token, method, **kwargs):
    """Queries the given request and returns the paginated page limit."""

    response = await query(oauth_token, method, **kwargs)
    return parse_response_page_limit(response)

def parse_response_page_limit(response):
    """Returns the total number of pages in a paginated query."""

    # Find the first member that is a dictionary with key `pages`, then return the value:
    key = 'pages'

    for member in response.values():
        if type(member) is not dict:
            continue

        if key not in member:
            continue

        return member[key]

    raise Exception('Page limit requested for non-paginated request')

