import sys
import argparse
from enum import StrEnum

class Methods(StrEnum):
    SET_CONFIG = 'set-config'
    AUTHENTICATE = 'authenticate'
    CREATE_DIRECTORY = 'create-directory'
    UPLOAD_PHOTOS = 'upload-photos'

parser = argparse.ArgumentParser(
    prog='Flickr-To-Google',
    description='Downloads images from Flickr and uploads them to Google Photos.',
)

parser.add_argument('method', choices=[method for method in Methods])

is_set_config = Methods.SET_CONFIG in sys.argv
parser.add_argument('-u', '--flickr-user-id', required=is_set_config)
parser.add_argument('-g', '--google-secret', required=is_set_config)
parser.add_argument('-f', '--flickr-secret', required=is_set_config)
