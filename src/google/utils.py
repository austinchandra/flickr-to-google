import json
import os

def get_photo_filepaths(dirpath, filenames):
    """Returns a list of paths for the photos at `dirpath` with filenames `filenames`."""

    photo_filenames = [
        filename for filename in filenames if 'metadata.json' not in filename
    ]

    return [os.path.join(dirpath, filename) for filename in photo_filenames]

# TODO: make this a common utility
def read_json_file(path):
    """Reads and returns the JSON object at `path`."""

    with open(path, 'r') as file:
        return json.load(file)

def write_json_file(path, data):
    """Writes the JSON data to `path`."""

    with open(path, 'w') as file:
        contents = json.dumps(data)
        file.write(contents)
