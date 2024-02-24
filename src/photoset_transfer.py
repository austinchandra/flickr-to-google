import os
import json
import requests

from flickr import flickr
from photoset_directory import metadata_path, photos_path

# 1. given a folder path, parse through all folders;
# for each one, pull the metadata and write this to
# drive (alongside the folder); then, write these
# to successes; then, write each image; on each transfer,
# note down the success, e.g. by appending these
# to the file each time; the output folder can be
# titled with a timestamp, to avoid over-writes.

# https://developers.google.com/drive/api/quickstart/python
# https://developers.google.com/drive/api/guides/manage-uploads#resumable
# TODO: Add Rohit as test user (need Gmail account); verify Flickr only
# has public images, or that private images can be made public.

# https://developers.google.com/drive/api/reference/rest/v3/files
# - Unsure if possible to update file metadata (created time)
# https://developers.google.com/drive/api/guides/folder?hl=en#python
# https://github.com/googleapis/google-api-python-client/blob/main/docs/media.md

root_path = 'outputs/'

def upload_photosets_to_drive():
    for photoset in os.walk(root_path):
        path = photoset[0]

        if path == root_path:
            # Skip the first result, which is the root.
            continue

        upload_metadata_to_drive(path)
        upload_photos_to_drive(path)

def upload_photos_to_drive(directory_path):
    path = f'{directory_path}/{photos_path}'

    with open(path, 'r') as file:
        for line in file:
            photo = json.loads(line)
            url = fetch_image_url(photo['id'])
            data = fetch_image_data(url)

        # TODO: upload the image to drive, within
        # the requisite folder (which is assumed
        # to be uploaded).

def upload_metadata_to_drive(directory_path):
    path = f'{directory_path}/{metadata_path}'

    with open(path, 'r') as file:
        contents = file.read().rstrip()
        metadata = json.loads(contents)

    # TODO: write folder to drive

def fetch_image_url(photo_id):
    sizes = flickr.photos.getSizes(photo_id=photo_id)
    original = sizes['sizes']['size'][-1]

    assert original['label'] == 'Original'

    url = original['source']

    return url

def fetch_image_data(url):
    return requests.get(url).content

upload_photosets_to_drive()
