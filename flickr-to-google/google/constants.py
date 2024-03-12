from enum import StrEnum

class Endpoints(StrEnum):
    BYTE_UPLOADS = 'https://photoslibrary.googleapis.com/v1/uploads'
    BATCH_CREATE = 'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate'
    ALBUMS = 'https://photoslibrary.googleapis.com/v1/albums'

class PhotoEntryKeys(StrEnum):
    GOOGLE_UPLOAD_TOKEN = 'google-upload-token'
    GOOGLE_ALBUM_ID = 'google-album-id'
    GOOGLE_MEDIA_ID = 'google-media-id'

REQUESTS_BATCH_SIZE = 10
CONTENT_BATCH_LIMIT = 50
