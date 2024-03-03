import httpx
import json
import asyncio

from credentials import api_key
from oauth import generate_oauth_token

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

async def query_all_paginated(page_handler, **kwargs):
    """Queries all pages and applies `page_handler` to each one, returning a flattened list of the responses."""

    page_limit = await query_page_limit(**kwargs)

    # Repeat the original page query here, for simplicity.

    queries = [
        query(page=page, **kwargs) for page in range(1, page_limit + 1)
    ]

    results = await asyncio.gather(
        *[page_handler(query) for query in queries]
    )

    return flatten(results)

async def query(**kwargs):
    """Performs an API query and returns the JSON response."""

    payload = create_query_payload(**kwargs)

    async with httpx.AsyncClient() as client:
        response = await client.get(rest_url, params=payload)
        return unwrap_response_json(response.text)

def create_query_payload(**kwargs):
    """Creates a query payload with the given authorization and key-value pairs."""

    payload = {}

    # Set known arguments first to enable over-writing these.
    payload['api_key'] = api_key
    payload['format'] = 'json'

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

async def query_page_limit(**kwargs):
    """Queries the given request and returns the paginated page limit."""

    response = await query(**kwargs)
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

def flatten(l):
    """Flattens a list `l`."""

    return [subitem for item in l for subitem in item]

# TODO: attempt to intialize this from a cache; move to a class object
oauth_token = generate_oauth_token()
