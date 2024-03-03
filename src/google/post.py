import json
import httpx

# https://www.python-httpx.org/advanced/clients/

async def post(url, payload, **header_args):
    oauth_token = read_oauth_token()
    headers = create_headers(oauth_token, **header_args)

    return await send_request(
        'POST',
        url,
        headers,
        payload
    )

def read_oauth_token():
    # TODO: configure path
    with open('./token.json', 'r') as file:
        token = json.load(file)

    return token['token']

async def send_request(method, url, headers, payload):
    request = httpx.Request(
        method,
        url,
        headers=headers,
        data=payload,
    )

    async with httpx.AsyncClient() as client:
        return await client.send(request)

def create_headers(oauth_token, **header_args):
    headers = {
        'Authorization': f'Bearer {oauth_token}'
    }

    for _, (k, v) in enumerate(header_args.items()):
        headers[k] = v

    return headers
