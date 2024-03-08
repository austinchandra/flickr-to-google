from authlib.integrations.requests_client import OAuth1Session

from .credentials import api_key, api_secret
from .constants import Endpoints

# TODO: Enable authentication to store a token.json, as with google (then, can run
# both authentications, one after another).

def generate_oauth_token():
    """Generates an OAuth token to be used in authenticated queries."""

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

    return _create_verified_token(client.token, verification_key)

def _verify_oauth_request(authorization_url):
    """Prompts the user to perform a Flickr authorization and receives the verification key."""

    print('Please authenticate your Flickr account using the following url:')
    print(authorization_url)
    print('\n')
    print('Then, enter the verification code:')

    return input()

def _create_verified_token(token, verification_key):
    """Combines OAuth token components into an authorized token."""

    token['oauth_verifier'] = verification_key

    return token

def _create_oauth_request_url(path):
    """Creates a url for the OAuth request at `path`."""

    return f'{Endpoints.OAUTH}/{path}'
