import json
import httpx

# https://www.python-httpx.org/advanced/clients/

async def post(url, headers=None, **kwargs):
    """Sends a POST request to `url` with the given parameters."""

    if headers is None:
        headers = create_headers()

    return await send_request(
        'POST',
        url,
        headers,
        **kwargs,
    )

def read_oauth_token():
    """Returns the cached OAuth token."""

    # TODO: configure path
    with open('./token.json', 'r') as file:
        token = json.load(file)

    return token['token']

async def send_request(method, url, headers, **kwargs):
    """Sends an authenticated request and returns the response."""

    request = httpx.Request(
        method,
        url,
        headers=headers,
        **kwargs
    )

    async with httpx.AsyncClient() as client:
        return await client.send(request)

def create_headers(**kwargs):
    """Returns authenticated HTTP headers populated with `header_args`."""

    oauth_token = read_oauth_token()

    headers = {
        'Authorization': f'Bearer {oauth_token}'
    }

    for _, (k, v) in enumerate(kwargs.items()):
        headers[k] = v

    return headers
