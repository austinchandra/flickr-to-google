import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_authorize import creds

# Throws on error.
def create_folder(name):
    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    file = service.files().create(body=file_metadata, fields="id").execute()

    # TODO: get the folder ID when the folder has been created (e.g., can
    # write successes to the folder ID in question)
    return file.get('id')

def upload_to_folder(folder_id):
    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        file_metadata = {"name": "photo.jpg", "parents": [folder_id]}
        # TODO: download images from Flickr to disk; then, upload them
        # in this manner, to the correct folder; then, remove them from
        # disk, and write a note for success within the execution output.

        # On future executions, pull in the latest output (e.g. sorted
        # by timestamps) and add to these (ignoring all requests already
        # fulfilled), which can be pulled into memory per album; may be able
        # to assign albums per thread.

        # TODO: Check, to see if it is possible to adjust the date information
        # within the file's metadata.

        # TODO: Check to see if credentials.json should be private.
        media = MediaFileUpload(
            "download.jpeg", mimetype="image/jpeg", resumable=True
        )
        # pylint: disable=maybe-no-member
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f'File ID: "{file.get("id")}".')
        return file.get("id")

  except HttpError as error:
        print(f"An error occurred: {error}")
        return None
