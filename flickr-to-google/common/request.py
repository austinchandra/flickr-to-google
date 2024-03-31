import httpx

from PIL import Image, ExifTags
from io import BytesIO
import datetime

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
    data, did_update_exif = _get_exif_updated_data(response.content, photo)

    return url, content_type, did_update_exif, data

def _get_exif_updated_data(data, photo):
    """Inserts the upload date into the EXIF metadata if a date cannot be found."""

    did_update_exif = False

    if _is_media_video(photo):
        return data, did_update_exif

    image = _convert_bytes_to_image(data)

    if _does_image_have_date(image):
        return data, did_update_exif

    exif = _get_updated_exif(image, photo)

    did_update_exif = True

    return _convert_image_to_bytes(image, exif), did_update_exif

def _convert_bytes_to_image(data):
    stream = BytesIO(data)
    image = Image.open(stream)

    return image

def _convert_image_to_bytes(image, exif):
    buffer = BytesIO()
    image.save(buffer, image.format, exif=exif.tobytes())

    return buffer.getvalue()

def _is_media_video(photo):
    # TODO: Turn this into a util
    return photo['media'] == 'video'

def _does_image_have_date(image):
    exif = image.getexif()

    flags = [
        ExifTags.Base.DateTime,
        ExifTags.Base.DateTimeOriginal,
        ExifTags.Base.DateTimeDigitized,
    ]

    return any([flag in exif for flag in flags])

def _get_updated_exif(image, photo):
    exif = image.getexif()

    timestamp = int(photo['posted'])
    posted = str(datetime.datetime.fromtimestamp(timestamp))

    exif[ExifTags.Base.DateTime] = posted
    exif[ExifTags.Base.DateTimeOriginal] = posted
    exif[ExifTags.Base.DateTimeDigitized] = posted

    return exif
