import argparse
import asyncio

from parse import parser, Methods

from flickr.api import init as init_flickr_api
from flickr.directory import create_directory
from flickr.photos import query_photo_data

from google.authenticate import authenticate_user as authenticate_google_user
from google.albums import create_albums
from google.photo_upload import upload_photos

from common.config import Config, write_config

async def exec():
    args = parser.parse_args()

    if args.method == Methods.SET_CONFIG:
        create_config(args)
    elif args.method == Methods.AUTHENTICATE:
        init_flickr_api()
        authenticate_google_user()
    elif args.method == Methods.CREATE_DIRECTORY:
        await create_directory()
    elif args.method == Methods.POPULATE_DIRECTORY:
        await query_photo_data()
    elif args.method == Methods.UPLOAD_ALBUMS:
        await create_albums()
    else:
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

