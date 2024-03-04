import httpx
import json
import asyncio

from credentials import api_key
from oauth import generate_oauth_token

rest_url = 'https://www.flickr.com/services/rest/'

# TODO: modify per_page to decrease the number of queries.

# TODO: attempt to intialize this from a cache; move to a class object
oauth_token = generate_oauth_token()

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
