from authlib.integrations.requests_client import OAuth1Session

from credentials import api_key, api_secret

# TODO: Enable authentication to store a token.json, as with google (then, can run
# both authentications, one after another).

oauth_url = 'https://www.flickr.com/services/oauth'

def generate_oauth_token():
    """Generates an OAuth token to be used in authenticated queries."""

    client = OAuth1Session(
        api_key,
        api_secret,
        redirect_uri='oob'
    )

    client.fetch_request_token(f'{oauth_url}/request_token')
    authorization_url = client.create_authorization_url(f'{oauth_url}/authorize')
    verification_key = verify_oauth_request(authorization_url)

    return create_verified_token(client.token, verification_key)

def verify_oauth_request(authorization_url):
    """Prompts the user to perform a Flickr authorization and receives the verification key."""

    print('Please authenticate your Flickr account using the following url:')
    print(authorization_url)
    print('\n')
    print('Then, enter the verification code:')

    return input()

def create_verified_token(token, verification_key):
    """Combines OAuth token components into an authorized token."""

    token['oauth_verifier'] = verification_key

    return token
