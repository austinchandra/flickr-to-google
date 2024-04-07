import httpx
from .config import read_config

from .exif import updated_data_with_exif

def download_photo_bytes(photo):
    """Downloads the photo content and returns the url and parsed bytes."""

    url, raw_data = _download(photo)
    data = updated_data_with_exif(raw_data, photo)

    return url, data

def _download(photo):
    """Downloads the photo content and returns the url and raw bytes."""

    cookies = _get_request_cookies(photo)

    request_url = photo['url']

    response = httpx.get(
        request_url,
        follow_redirects=True,
        cookies=cookies
    )

    response_url = str(response.url)
    data = response.content

    return response_url, data

def _get_request_cookies(photo):
    """Returns the cookies required to fetch `photo`."""

    if photo['media'] != 'video':
        return None

    config = read_config()

    return {
        'cookie_session': config.flickr_cookie_session,
        'cookie_epass': config.flickr_cookie_epass,
    }

