import asyncio

from flickr.oauth import generate_oauth_token
from flickr.directory import create_directory
# TODO: re-expose from google/base?
from google.albums import create_all_albums
from google.photo_upload import upload_all_photos

# TODO: add CLI patterns; user setup and authentication; configuration for output paths
# TODO: Likely need to intersperse uploading bytes/content, so that the upload tokens do not expire.

async def transfer():
    # TODO: Clear the previous directory
    await create_directory()
    await create_all_albums()
    await upload_all_photos()

asyncio.run(transfer())
