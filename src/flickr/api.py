import flickrapi
from flickr_credentials import flickr_api_key, flickr_api_secret

flickr = flickrapi.FlickrAPI(
    flickr_api_key,
    flickr_api_secret,
    cache=True,
    format='parsed-json',
)
