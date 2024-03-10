import httpx
import json
import asyncio

from .constants import Endpoints, QUERIES_PER_PAGE, REQUESTS_BATCH_SIZE

async def query_all_paginated(method, page_handler, **kwargs):
    """Queries all pages and applies `page_handler` to each one, returning a flattened list of the responses."""

    page_limit = await _query_page_limit(
        method,
        per_page=QUERIES_PER_PAGE,
        **kwargs
    )

    # Repeat the original page query here, for simplicity.

    queries = [
        query(
            method,
            page=page,
            per_page=QUERIES_PER_PAGE,
            **kwargs
        ) for page in range(1, page_limit + 1)
    ]

    # Use synchrony here, as each `page_handler` typically has requests of its own.
    results = [await page_handler(query) for query in queries]

    return _flatten(results)

async def query(method, **kwargs):
    """Performs an API query and returns the JSON response."""

    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(None, lambda: method(**kwargs))

async def query_chunked(queries, chunk_handler):
    """Executes the queries in chunks to avoid creating excess requests."""

    responses = []

    # Technically, this should use a semaphore; but, use batches for timestamping.
    for i in range(0, len(queries), REQUESTS_BATCH_SIZE):
        chunk_responses = await asyncio.gather(*queries[i:i + REQUESTS_BATCH_SIZE])
        chunk_handler(len(chunk_responses))
        responses += chunk_responses

    return responses

async def _query_page_limit(method, **kwargs):
    """Queries the given request and returns the paginated page limit."""

    response = await query(method, **kwargs)

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

