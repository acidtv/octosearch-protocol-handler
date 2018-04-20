import os
import sys
import argparse
import re
import base64

if sys.platform.startswith('darwin'):
    import macosx as platform
elif os.name == 'nt':
    import windows as platform
elif os.name == 'posix':
    import linux as platform
else:
    raise Exception('OS not supported: {}'.format(os.name))

PROTOCOL = 'octosearch'
VERSION = 'v1'


def parse_url(url):
    expr = PROTOCOL + r"://" + VERSION + "/open/(?P<encodedlocation>.+)"
    match = re.fullmatch(expr, url)

    if not match:
        raise Exception('That does not look like a url we can handle!')

    try:
        location = base64.b64decode(match.group('encodedlocation'))
    except Exception:
        raise Exception('It looks like the url provided does contain a valid base64 payload')

    return location.decode()


def executable_location():
    dirname = os.path.dirname(os.path.abspath(__file__))
    current_file = os.path.join(dirname, sys.argv[0])

    return current_file


def register_protocol_handler():
    platform.register()


def handle_open(url):
    filepath = parse_url(url)
    print('Opening {}...'.format(filepath))
    platform.open_file(filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Octosearch protocol handler')
    parser.add_argument('--register', dest='register', required=False, action='store_true', help='Register the protocol handler')
    parser.add_argument('url', nargs='?', help='Url to handle')
    args = parser.parse_args()

    if args.register:
        register_protocol_handler()
    else:
        handle_open(args.url)
