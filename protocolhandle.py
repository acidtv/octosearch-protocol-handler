import os.path
import argparse
import re
import base64

try:
    import _winreg as wr
except ImportError:
    import winreg as wr

ACCESS_RIGHTS = (wr.KEY_WRITE | wr.KEY_READ
                | wr.KEY_QUERY_VALUE | wr.KEY_SET_VALUE
                | wr.KEY_CREATE_SUB_KEY | wr.KEY_ENUMERATE_SUB_KEYS)


def register_octosearch_protocol_handler():
    current_file = os.path.abspath(__file__)
    command = 'python ' + current_file + ' ' + '"%1"'
    protocol = 'octosearch'
    description = 'Octosearch local file opener protocol handler'

    print('Attempting to register protocol handler')
    print('command = {}'.format(command))
    register_protocol_handler(protocol, command, description)


def register_protocol_handler(protocol, command, description):
    r"""
    HKEY_CLASSES_ROOT
        foo
            (Default) = "URL: Foo Protocol"
            URL Protocol = ""
            DefaultIcon
                (Default) = "foo.exe,1"
            shell
                open
                    command
                        (Default) = "C:\Program Files\example\foo.exe" "%1"
    """

    with wr.CreateKeyEx(wr.HKEY_CLASSES_ROOT, protocol, 0, ACCESS_RIGHTS) as key:
        wr.SetValueEx(key, "", 0, wr.REG_SZ, "URL: " + description)
        wr.SetValueEx(key, "URL Protocol", 0, wr.REG_SZ, "")

        shell_key = wr.CreateKeyEx(key, "shell", 0, ACCESS_RIGHTS)
        open_key = wr.CreateKeyEx(shell_key, "open", 0, ACCESS_RIGHTS)
        command_key = wr.CreateKeyEx(open_key, "command", 0, ACCESS_RIGHTS)

        wr.SetValueEx(command_key, "", 0, wr.REG_SZ, command)


def handle_open(url):
    location = parse_url(url)


def parse_url(url):
    expr = r"octosearch://v1/open/(?P<encodedlocation>[A-Z0-9]+)"
    match = re.fullmatch(expr, url)
    print(url)

    if not match:
        raise Exception('That does not look like a url we can handle!')

    decoded_location = base64.b64decode(match.group('encodedlocation'))

    return decoded_location


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Octosearch protocol handler')
    parser.add_argument('--register', dest='register', required=False, action='store_true', help='Register the protocol handler')
    parser.add_argument('url', nargs='?', help='Url to handle')
    args = parser.parse_args()

    if args.register:
        register_octosearch_protocol_handler()
    else:
        handle_open(args.url)
