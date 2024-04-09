import json
import httpx

from .config import read_oauth_token

# TODO: Nice-looking download progress bars:
# https://www.python-httpx.org/advanced/clients/

async def post(url, headers=None, **kwargs):
    """Sends a POST request to `url` with the given parameters."""

    if headers is None:
        headers = create_headers()

    return await _send_request(
        'POST',
        url,
        headers,
        **kwargs,
    )

def create_headers(**kwargs):
    """Returns authenticated HTTP headers populated with `header_args`."""

    oauth_token = _read_oauth_token()

    headers = {
        'Authorization': f'Bearer {oauth_token}'
    }

    for _, (k, v) in enumerate(kwargs.items()):
        headers[k] = v

    return headers

def _read_oauth_token():
    """Returns the cached OAuth token."""

    token = read_oauth_token()
    return token['token']

async def _send_request(method, url, headers, **kwargs):
    """Sends an authenticated request and returns the response."""

    request = httpx.Request(
        method,
        url,
        headers=headers,
        **kwargs
    )

    try:
        async with httpx.AsyncClient() as client:
            return await client.send(request)
    except Exception:
        return None
