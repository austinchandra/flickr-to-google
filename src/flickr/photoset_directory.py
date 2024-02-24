from pathlib import Path
import json

from flickr import flickr
from photoset_query import query_photoset_list, query_photoset_photos

user_id = '200072260@N02'

output_path = 'outputs/'
metadata_path = 'metadata.txt'
photos_path = 'photos.txt'

# TODO:
# 1. Address Flickr OAuth needs
# 2. Pull photos without folders
# 3. Find out whether date information can be uploaded alongside files (if not, use folders)
# Basic threading can divide folders by name (up to the number of threads).
# TODO: Google Drive or Photos?
# TODO: Handle videos

# TODO: write successes, then compare the shortcomings between the directory and successes,
# to determine the contents of the next set.

def write_photoset_directory():
    photosets = query_photoset_list(user_id)

    for photoset in photosets:
        write_photoset_metadata(photoset)

        photo_ids = query_photoset_photos(user_id, photoset['id'])
        write_photoset_photos(photoset, photo_ids)

def write_photoset_metadata(photoset):
    path = create_path_for_photoset(photoset['id'], metadata_path)

    with open(path, 'w') as file:
        contents = json.dumps(photoset)
        file.write(contents)

def write_photoset_photos(photoset, photos):
    path = create_path_for_photoset(photoset['id'], photos_path)

    with open(path, 'w') as file:
        for photo in photos:
            contents = json.dumps(photo)
            file.write(contents)

# TODO: Clean this and improve exports
def create_path_for_photoset(photoset_id, file_path):
    directory_path = f'{output_path}/{photoset_id}'
    Path(directory_path).mkdir(parents=True, exist_ok=True)

    return f'{directory_path}/{file_path}'

    # Had difficulties with OAuth; perhaps Flickr's API is broken; tried a number
    # of libraries (the only thing remaining is to build the OAuth payload by
    # hand, which is possible, but much prefer to avoid this).

    # Presume these issues will not apply to OAuth on Google's side; next steps:
    # organize metadata and albums; be able to read these in accordingly; then,
    # connect this to Google's side, and handle failures (specified as a set of
    # photos per-album).

write_photoset_directory()
