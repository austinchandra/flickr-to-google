import argparse
import asyncio

from parse import parser, Methods

from flickr.api import init as init_flickr_api
from flickr.directory import create_directory
from flickr.photos import query_photo_data
from flickr.download import download_photos

from google.authenticate import authenticate_user as authenticate_google_user
from google.albums import create_albums
from google.photo_upload import upload_photos

from common.config import Config, write_config
from common.log import print_separator, print_timestamped

OPERATION_RETRY_LIMIT = 10

async def cli():
    args = parser.parse_args()

    method = args.method

    if method == Methods.SET_CONFIG:
        create_config(args)
    elif method == Methods.AUTHENTICATE:
        init_flickr_api()
        authenticate_google_user()
    elif method == Methods.CREATE_DIRECTORY:
        await create_directory()
    elif method == Methods.POPULATE_DIRECTORY:
        await run_with_retry(query_photo_data)
    elif method == Methods.DOWNLOAD_PHOTOS:
        path = args.path
        is_downloading_all = args.download_all
        await download_photos(path, is_downloading_all)
    elif method == Methods.CREATE_ALBUMS:
        await run_with_retry(create_albums)
    else:
        await run_with_retry(upload_photos)

def create_config(args):
    config = Config(
        args.flickr_user_id,
        args.google_keys_path,
        args.flickr_keys_path,
        args.flickr_cookie_session,
        args.flickr_cookie_epass,
    )

    write_config(config)

async def run_with_retry(method, count=0):
    """Runs `method` with proportionate success until completion up to a limit."""

    num_succeeded, num_attempted = await method()

    if num_succeeded == num_attempted:
        return
    elif count == OPERATION_RETRY_LIMIT - 1:
        print_separator()
        print_timestamped(
            f'Operation failed to complete after {OPERATION_RETRY_LIMIT} attempts.'
        )

        return
    else:
        await run_with_retry(method, count + 1)


if __name__ == '__main__':
    asyncio.run(cli())

