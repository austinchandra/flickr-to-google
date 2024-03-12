import flickrapi

from .config import read_api_keys

flickr = None

def init():
    """Initializes an authenticated Flickr instance."""

    api_key, api_secret = read_api_keys()

    global flickr
    flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')
    flickr.authenticate_via_browser(perms='read')

def get_flickr_instance():
    """Returns the Flickr instance."""

    return flickr
