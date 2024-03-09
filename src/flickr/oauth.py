from authlib.integrations.requests_client import OAuth1Session

from .constants import Endpoints
from common.files import read_json_file, write_json_file
from .config import write_oauth_token, read_api_secrets

def authenticate_user():
    """Generates an OAuth token and caches it to disk."""

    api_key, api_secret = read_api_secrets()

    client = OAuth1Session(
        api_key,
        api_secret,
        redirect_uri='oob'
    )

    request_token_endpoint = _create_oauth_request_url('request_token')
    client.fetch_request_token(request_token_endpoint)

    authorization_endpoint = _create_oauth_request_url('authorize')
    authorization_url = client.create_authorization_url(authorization_endpoint)
    verification_key = _verify_oauth_request(authorization_url)

    token = _create_verified_token(client.token, verification_key)
    write_oauth_token(token)

def _verify_oauth_request(authorization_url):
    """Prompts the user to perform a Flickr authorization and receives the verification key."""

    print('Please authenticate your Flickr account using the following url:')
    print(authorization_url)
    print('Then, enter the verification code:')

    return input()

def _create_verified_token(token, verification_key):
    """Combines OAuth token components into an authorized token."""

    token['oauth_verifier'] = verification_key

    return token

def _create_oauth_request_url(path):
    """Creates a url for the OAuth request at `path`."""

    return f'{Endpoints.OAUTH}/{path}'

