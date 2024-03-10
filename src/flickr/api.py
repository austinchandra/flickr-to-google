import flickrapi

from .config import read_api_secrets

def get_flickr():
    # api_key, api_secret = read_api_secrets()
    api_key = u'55256e22b7cd1f302d2d2991e17ed570'
    api_secret = u'570ec2b4b241dbdd'

    flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')
    flickr.authenticate_via_browser(perms='read')

    return flickr
