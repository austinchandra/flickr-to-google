import json

def read_json_file(path):
    """Reads and returns the JSON object at `path`."""

    with open(path, 'r') as file:
        return json.load(file)

def write_json_file(path, data):
    """Writes the JSON data to `path`."""

    with open(path, 'w') as file:
        contents = json.dumps(data)
        file.write(contents)

