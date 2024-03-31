import sys
import argparse
from enum import StrEnum

class Methods(StrEnum):
    SET_CONFIG = 'set-config'
    AUTHENTICATE = 'authenticate'
    CREATE_DIRECTORY = 'create-directory'
    POPULATE_DIRECTORY = 'populate-directory'
    DOWNLOAD_PHOTOS = 'download-photos'
    CREATE_ALBUMS = 'create-albums'
    UPLOAD_PHOTOS = 'upload-photos'

parser = argparse.ArgumentParser(
    prog='Flickr-To-Google',
    description='Downloads images from Flickr and uploads them to Google Photos.',
)

parser.add_argument('method', choices=[method for method in Methods])

is_method_set_config = Methods.SET_CONFIG in sys.argv
parser.add_argument('-u', '--flickr-user-id', required=is_method_set_config)
parser.add_argument('--google-keys-path', required=is_method_set_config)
parser.add_argument('--flickr-keys-path', required=is_method_set_config)
parser.add_argument('--flickr-cookie-session', required=is_method_set_config)
parser.add_argument('--flickr-cookie-epass', required=is_method_set_config)

is_method_download_photos = Methods.DOWNLOAD_PHOTOS in sys.argv
parser.add_argument('-p', '--path', required=is_method_download_photos)
parser.add_argument('--download-all', action=argparse.BooleanOptionalAction)

parser.add_argument('-v', '--videos-only', action=argparse.BooleanOptionalAction)
