import argparse
import asyncio

from parse import parser, Methods

from flickr.oauth import authenticate_user as authenticate_flickr_user
from flickr.directory import create_directory

from google.authenticate import authenticate_user as authenticate_google_user
from google.albums import create_albums
from google.photo_upload import upload_photos

from common.config import Config, write_config

# TODO: Test directory on the production values, to ensure that it works without issues.
# TODO: add installation instructions (e.g. Python 3.11+)

async def exec():
    args = parser.parse_args()

    if args.method == Methods.SET_CONFIG:
        create_config(args)
    elif args.method == Methods.AUTHENTICATE:
        authenticate_flickr_user()
        authenticate_google_user()
    elif args.method == Methods.CREATE_DIRECTORY:
        await create_directory()
    else:
        await create_albums()
        await upload_photos()

def create_config(args):
    config = Config(
        args.flickr_user_id,
        args.google_secret,
        args.flickr_secret,
    )

    write_config(config)

if __name__ == '__main__':
    asyncio.run(exec())

