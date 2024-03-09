import datetime

def print_timestamped(contents):
    """Prints a timestamp-prefixed text string."""

    timestamp = _get_formatted_timestamp()
    print(f'{timestamp}:\t{contents}')

def print_separator():
    """Prints a separator line."""

    print('{}'.format('-' * 64))

def _get_formatted_timestamp():
    """Returns a formatted timestamp in YYYY-MM-DD HH-MM-SS."""

    return str(datetime.datetime.now()).split('.')[0]
