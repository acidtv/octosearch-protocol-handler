#!/usr/bin/env python3

import os
import sys
import argparse
import re
import base64
import json
import configparser
import hmac

# import appropriate platform module
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

SAFE_EXTENSIONS = [
    # text and office files
    '.doc', '.docx', '.txt', '.md', '.rtf',
    '.odt', '.odp', '.ods', '.pdf', '.ppt', '.pptx',
    '.xls', '.xlsx', '.csv', '.log',

    # images
    '.gif', '.jpg', '.jpeg',
    '.tif', '.tiff', '.png',
    '.psd', '.svg', '.ai',
    '.webp', '.xcf', '.kra',

    # audio
    '.mp3', '.wav', '.ogg', '.flac',

    # video
    '.mpg', '.mpeg', '.mov', '.mkv', '.avi', '.wmv', '.vob',

    # archives
    '.zip', '.gz', '.xz',

    # misc
    '.html', '.htm', '.gpx', '.zip', '.ini', '.conf', '.nef',
    '.srt', '.yml',
]


def parse_url(url):
    """Parse an Octosearch url into usable parts"""
    expr = PROTOCOL + r"://" + VERSION + "/(?P<action>(open|register))/(?P<encodedpayload>[^/]+)(?:/(?P<hash>.*))?"
    match = re.fullmatch(expr, url)

    if not match:
        raise OctosearchException('That does not look like a url we can handle!')

    encoded_payload = match.group('encodedpayload')
    hash = match.group('hash')

    try:
        json_payload = base64.b64decode(encoded_payload)
        json_payload = json_payload.decode()
    except Exception:
        raise OctosearchException('It looks like the url provided does contain a valid base64 payload')

    payload = json.loads(json_payload)

    if not hash:
        hash = ''

    validated = validate_hmac(encoded_payload, hash)

    return (
        match.group('action'),
        payload,
        validated
    )


def executable_location():
    """Get the filesystem location of the current executable"""
    dirname = os.path.dirname(os.path.abspath(__file__))
    current_file = os.path.normpath(os.path.join(dirname, sys.argv[0]))

    return current_file


def validate_hmac(payload, hash):
    """Validate if hash is equal to payload hashed with our own secret"""
    secret = get_config('main', 'instance-secret').encode()

    if not secret:
        return None

    h = hmac.new(secret, payload.encode(), digestmod='sha256')

    return hmac.compare_digest(h.hexdigest(), hash)


def safe_extension(path):
    """Check if file has a safe extension"""
    __, ext = os.path.splitext(path)

    return ext.lower() in SAFE_EXTENSIONS


def handle_open(data, validated):
    """Open a local file"""

    if validated is None:
        platform.popup('Could not open file: you need to register this Octosearch instance before you can open files.')
        return
    elif validated is False:
        platform.popup('Could not open file: the hash does not match the registered Octosearch instance.')
        return

    filepath = data['url']

    if not safe_extension(filepath):
        platform.popup('The filetype of the file you\'re trying to open ({}) is not considered safe. If you insist on opening it, you will have to open it manually.'.format(filepath))
        return

    try:
        platform.open_file(filepath)
    except Exception as e:
        platform.popup('Could not open file: {}'.format(e))


def handle_register(data, validated):
    """Registers an Octosearch instance with this installation"""

    if get_config('main', 'instance-url'):
        platform.popup('There\'s already an Octosearch instance registered')
        return

    if ((not data.get('url')) or (not data.get('secret'))):
        platform.popup('Missing url or secret from register url')
        return

    put_config('main', 'instance-url', data['url'])
    put_config('main', 'instance-secret', data['secret'])

    platform.popup('New octosearch instance {} was successfully registered!'.format(data['url']))


def command_install(args):
    """Handles the cli command to register this program as a protocol handler"""
    platform.install()
    platform.popup('Installation succeeded!')


def command_url(args):
    """Handles the cli url command and delegates the handling to the appropriate handle_* function"""
    actions = {'open': handle_open, 'register': handle_register}
    url = args.url

    action, data, validated = parse_url(url)

    # call function to handle url action
    actions[action](data, validated)


def _config_file():
    """Returns the config file path"""
    folder = platform.settings_folder()

    try:
        os.makedirs(folder)
    except FileExistsError:
        pass

    return os.path.join(folder, 'octosearch.ini')


def _config():
    """Return a config object"""
    defaults = """
    [main]
    instance-url =
    instance-secret =
    """

    config = configparser.ConfigParser()
    config.read_string(defaults)

    try:
        config.read(_config_file())
    except FileNotFound:
        pass

    return config


def put_config(section, key, value):
    """Save a config var"""
    config = _config()
    config.set(section, key, value)

    with open(_config_file(), 'w') as configfile:
        config.write(configfile)


def get_config(section, key):
    """Get a config var"""
    try:
        return _config()[section][key]
    except KeyError:
        return None


class OctosearchException(Exception):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Octosearch protocol handler')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    parser_url = subparsers.add_parser('url', help='Handle a Octosearch url')
    parser_url.set_defaults(func=command_url)
    parser_url.add_argument('url', help='Url to handle')

    parser_register = subparsers.add_parser('install', help='Install the protocol handler')
    parser_register.set_defaults(func=command_install)

    args = parser.parse_args()

    try:
        args.func(args)
    except OctosearchException as e:
        platform.popup(str(e))
        #print('Error: {}'.format(e), file=sys.stderr)
        sys.exit(1)
