import os
import os.path
import protocolhandle
import ctypes

try:
    import _winreg as wr
except ImportError:
    import winreg as wr

ACCESS_RIGHTS = (wr.KEY_WRITE | wr.KEY_READ
                | wr.KEY_QUERY_VALUE | wr.KEY_SET_VALUE
                | wr.KEY_CREATE_SUB_KEY | wr.KEY_ENUMERATE_SUB_KEYS)


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


def install():
    """Register this program as a protocol handler"""
    current_file = protocolhandle.executable_location()

    command = current_file + ' url ' + '"%1"'
    protocol = 'octosearch'
    description = 'Octosearch local file opener protocol handler'

    print('Attempting to register protocol handler')
    print('command = {}'.format(command))
    _register_protocol_handler(protocol, command, description)


def open_file(filepath):
    """Open a local file"""
    if not isinstance(filepath, str):
        raise protocolhandle.OctosearchException('filepath param must be str object')

    os.startfile(filepath)


def settings_folder():
    return os.path.join(os.getenv('APPDATA'), 'Octosearch')


def popup(msg):
    """Display a popup"""
    ctypes.windll.user32.MessageBoxW(0, msg, 'Octosearch', 1)
