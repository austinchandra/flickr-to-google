import httpx
import json
import asyncio

from .constants import Endpoints, QUERIES_PER_PAGE, REQUESTS_BATCH_SIZE
from .config import read_oauth_token, read_api_secrets

async def query_all_paginated(page_handler, **kwargs):
    """Queries all pages and applies `page_handler` to each one, returning a flattened list of the responses."""

    page_limit = await _query_page_limit(per_page=QUERIES_PER_PAGE, **kwargs)

    # Repeat the original page query here, for simplicity.

    queries = [
        query(page=page, per_page=QUERIES_PER_PAGE, **kwargs) for page in range(1, page_limit + 1)
    ]

    # Use synchrony here, as each `page_handler` typically has requests of its own.
    results = [await page_handler(query) for query in queries]

    return _flatten(results)

async def query(**kwargs):
    """Performs an API query and returns the JSON response."""

    payload = _create_query_payload(**kwargs)

    async with httpx.AsyncClient() as client:
        response = await client.get(Endpoints.REST, params=payload, timeout=None)
        return _unwrap_response_json(response.text)

async def query_chunked(queries, chunk_handler):
    """Executes the queries in chunks to avoid creating excess requests."""

    responses = []

    # Technically, this should use a semaphore; but, use batches for timestamping.
    for i in range(0, len(queries), REQUESTS_BATCH_SIZE):
        chunk_responses = await asyncio.gather(*queries[i:i + REQUESTS_BATCH_SIZE])
        chunk_handler(len(chunk_responses))
        responses += chunk_responses

    return responses

def _create_query_payload(**kwargs):
    """Creates a query payload with the given authorization and key-value pairs."""

    oauth_token = read_oauth_token()
    api_key, _ = read_api_secrets()

    payload = {}

    # Set known arguments first to enable over-writing these.
    payload['api_key'] = api_key
    payload['format'] = 'json'

    for _, (k, v) in enumerate(oauth_token.items()):
        payload[k] = v

    for _, (k, v) in enumerate(kwargs.items()):
        payload[k] = v

    return payload

def _unwrap_response_json(contents):
    """Extracts the inner json from contents of form `jsonFlickrApi(<json>)`."""

    start = contents.find('{')
    # Find the last index of '}':
    end = contents[::-1].find('}') * -1

    return json.loads(contents[start:end])

async def _query_page_limit(**kwargs):
    """Queries the given request and returns the paginated page limit."""

    response = await query(**kwargs)
    return _parse_response_page_limit(response)

def _parse_response_page_limit(response):
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

def _flatten(l):
    """Flattens a list `l`."""

    return [subitem for item in l for subitem in item]

