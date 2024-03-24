import httpx

def download_photo_bytes(photo):
    """Downloads the photo content and returns the content type and raw bytes."""

    response = httpx.get(photo['url'], follow_redirects=True)

    data = response.content
    content_type = response.headers['content-type']

    # TODO: Should check sizing on videos (cannot get these at full resolution on my account). Would
    # need to integrate an authentication check, or similar, to replicate the effect on browser
    # (i.e., given the original link, can download the video when logged in, but only lower
    # resolution otherwise). I.e., include the login cookie on the request.

    return content_type, data

