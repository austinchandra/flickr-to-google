from authlib.integrations.requests_client import OAuth1Session

from credentials import api_key, api_secret

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

# Next: create interface to call/parse authenticated requests (including paginated queries);
# create directories with all photo information (including photosets); this requires using
# the photoset queries (and running them first), then querying for photos; perhaps all of
# these can use a new authenticated interface (as photosets will, too, be private); can
# likely replace flickrapi entirely.

# 1. https://www.flickr.com/services/api/flickr.people.getPhotos.html
# 2. https://www.flickr.com/services/api/flickr.photos.getInfo.html
# 3. https://www.flickr.com/services/api/misc.urls.html
# Separately:
# 4. https://www.flickr.com/services/api/flickr.photosets.getList.html
# 5. https://www.flickr.com/services/api/flickr.photosets.getInfo.html

# Link photosets to photos, having queried for both, to build a directory of all photosets -> photos and
# stream -> photos. Then, can use both of these to track the set of all images (in which all photos not
# assigned to a photoset can be grouped as loose pictures. Videos should be treated identically, with raw
# data assigned to the filetype in question. This should have a folders of information with each photo's
# content, including the URL and etc., such that at this point, the queries to Flickr are done.

# Can first query the photosets, then query the photos, and use information from the former to track
# all photos not in photosets (e.g. by querying a single file's contents, with a batch of photos); or,
# this can attempt to write to a file, and if the file exists, then it assumes a photo lives there (then,
# there can be a separate set of files that cover the photosets). Each of these files can also contain a
# boolean representing success on an upload; then, the transfer may operate on the same set of files each
# time (or, this may move the files to separate folders, to reduce the operational time). Each file would
# need to contain information necessary for a Google upload (including photo album IDs).
