import httpx
from .config import read_config

from .exif import updated_data_with_exif

def download_photo_bytes(photo):
    """Downloads the photo content and returns the url and parsed bytes."""

    url, data = _download(photo)

    if data is None:
        return url, data, False

    data, did_update_exif = updated_data_with_exif(data, photo)

    return url, data, did_update_exif

def _download(photo):
    """Downloads the photo content and returns the url and raw bytes."""

    cookies = _get_request_cookies(photo)

    request_url = photo['url']

    try:
        response = httpx.get(
            request_url,
            follow_redirects=True,
            cookies=cookies
        )

        url = str(response.url)
        data = response.content

        print(len(data))

        if response.status_code != 200:
            return url, None

        return url, data
    except Exception:
        return request_url, None

def _get_request_cookies(photo):
    """Returns the cookies required to fetch `photo`."""

    if photo['media'] != 'video':
        return None

    config = read_config()

    return {
        'cookie_session': config.flickr_cookie_session,
        'cookie_epass': config.flickr_cookie_epass,
    }

