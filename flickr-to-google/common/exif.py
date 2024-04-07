import datetime

from PIL import Image, ExifTags
from io import BytesIO

def updated_data_with_exif(data, photo):
    """Inserts the upload date into the EXIF metadata if a date cannot be found."""

    if _is_media_video(photo):
        return data

    image = _bytes_to_image(data)

    if _image_has_date(image):
        return data

    exif = _get_exif(image, photo)

    return _image_to_bytes(image, exif)

def _bytes_to_image(data):
    """Converts bytes to a PIL image object."""

    stream = BytesIO(data)
    image = Image.open(stream)

    return image

def _image_to_bytes(image, exif):
    """Converts a PIL image and an EXIF dictionary to bytes."""

    buffer = BytesIO()
    image.save(buffer, image.format, exif=exif.tobytes())

    return buffer.getvalue()

def _is_media_video(photo):
    return photo['media'] == 'video'

def _image_has_date(image):
    """Returns a boolean indicating whether the image has any date information in its EXIF."""

    exif = image.getexif()

    flags = [
        ExifTags.Base.DateTime,
        ExifTags.Base.DateTimeOriginal,
        ExifTags.Base.DateTimeDigitized,
    ]

    return any([flag in exif for flag in flags])

def _get_exif(image, photo):
    """Returns an updated EXIF dictionary with date fields."""

    exif = image.getexif()

    timestamp = int(photo['posted'])
    posted = str(datetime.datetime.fromtimestamp(timestamp))

    exif[ExifTags.Base.DateTime] = posted
    exif[ExifTags.Base.DateTimeOriginal] = posted
    exif[ExifTags.Base.DateTimeDigitized] = posted

    return exif
