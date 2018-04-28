import os
import os.path
import protocolhandle
import ctypes
import urllib.parse
from pathlib import PureWindowsPath

try:
    import _winreg as wr
except ImportError:
    import winreg as wr

ACCESS_RIGHTS = (wr.KEY_WRITE | wr.KEY_READ
                | wr.KEY_QUERY_VALUE | wr.KEY_SET_VALUE
                | wr.KEY_CREATE_SUB_KEY | wr.KEY_ENUMERATE_SUB_KEYS)

# Popup button options
BTN_OK = 0x0
BTN_YESNO = 0x4

# Popup button return codes
BTN_RESULT_OK = 1
BTN_RESULT_YES = 6
BTN_RESULT_NO = 7


def _register_protocol_handler(protocol, command, description):
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


def _translate_url(url):
    """Translate url into something Windows can understand.
    For now this translates smb:// urls into UNC paths"""

    if urllib.parse.urlparse(url).scheme == 'smb':
        parsed = urllib.parse.urlparse(url)
        winpath = PureWindowsPath(r'//' + parsed.netloc + parsed.path)

        return str(winpath)

    return url


def install():
    """Register this program as a protocol handler"""
    current_file = protocolhandle.executable_location()

    command = current_file + ' url ' + '"%1"'
    protocol = 'octosearch'
    description = 'Octosearch local file opener protocol handler'

    print('Attempting to register protocol handler')
    print('command = {}'.format(command))
    _register_protocol_handler(protocol, command, description)


def open_file(url):
    """Open a local file"""
    if not isinstance(url, str):
        raise protocolhandle.OctosearchException('url param must be str object')

    translated_url = _translate_url(url)

    print('Opening {}...'.format(translated_url))
    os.startfile(translated_url)


def settings_folder():
    return os.path.join(os.getenv('APPDATA'), 'Octosearch')


def popup(msg, button=None):
    """Display a popup"""
    if not button:
        button = BTN_OK

    return ctypes.windll.user32.MessageBoxW(0, msg, 'Octosearch', button)
