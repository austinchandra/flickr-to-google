from enum import StrEnum

class Endpoints(StrEnum):
    OAUTH = 'https://www.flickr.com/services/oauth'
    REST = 'https://www.flickr.com/services/rest/'

class PhotoEntryKeys(StrEnum):
    DOWNLOAD_FILE_PATH = 'image_path'
    DID_UPDATE_EXIF = 'did_update_exif'

QUERIES_PER_PAGE = 500
REQUESTS_BATCH_SIZE = 10
