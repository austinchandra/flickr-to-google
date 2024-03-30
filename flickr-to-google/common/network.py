import httpx

from .config import read_config

def download_photo_bytes(photo):
    """Downloads the photo content and returns the content type and raw bytes."""

    config = read_config()

    cookies = {
        'cookie_session': config.flickr_cookie_session,
        'cookie_epass': config.flickr_cookie_epass,
    }

    response = httpx.get(photo['url'], follow_redirects=True, cookies=cookies)

    url = str(response.url)
    content_type = response.headers['content-type']
    data = response.content

    return url, content_type, data

