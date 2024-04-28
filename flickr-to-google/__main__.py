import argparse
import asyncio

from parse import parser, Methods

from flickr.api import init as init_flickr_api
from flickr.directory import create_directory
from flickr.photos import query_photo_data
from flickr.download import download_photos as flickr_download_photos

from google.authenticate import authenticate_user as authenticate_google_user
from google.albums import create_albums
from google.photo_upload import upload_photos as google_upload_photos

from common.config import Config, write_config
from common.log import print_separator, print_timestamped

OPERATION_RETRY_LIMIT = 10

async def run_cli():
    args = parser.parse_args()

    method = args.method

    if method == Methods.SET_CONFIG:
        create_config(args)
    elif method == Methods.AUTHENTICATE:
        authenticate()
    elif method == Methods.CREATE_DIRECTORY:
        await create_directory()
    elif method == Methods.POPULATE_DIRECTORY:
        await repeated(query_photo_data)
    elif method == Methods.DOWNLOAD_PHOTOS:
        await download_photos(args)
    elif method == Methods.CREATE_ALBUMS:
        await repeated(create_albums)
    else:
        await upload_photos(args)

def create_config(args):
    config = Config(
        args.flickr_user_id,
        args.google_keys_path,
        args.flickr_keys_path,
        args.flickr_cookie_session,
        args.flickr_cookie_epass,
    )

    write_config(config)

def authenticate():
    init_flickr_api()
    authenticate_google_user()

async def download_photos(args):
    await repeated(
        flickr_download_photos,
        args.path,
        args.download_all,
        args.videos_only,
    )

async def upload_photos(args):
    await repeated(
        google_upload_photos,
        args.videos_only,
        args.missing_exif_only,
        args.upload_all,
    )

async def repeated(method, *args, count=0):
    num_succeeded, num_attempted = await method(*args)

    if num_succeeded == num_attempted:
        return
    elif count == OPERATION_RETRY_LIMIT - 1:
        print_retry_failure()
        return
    else:
        await repeated(method, *args, count=count + 1)

def print_retry_failure():
    print_separator()
    print_timestamped(
        f'Did not complete after {OPERATION_RETRY_LIMIT} attempts.'
    )

if __name__ == '__main__':
    asyncio.run(run_cli())

