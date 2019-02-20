import subprocess
import os.path
from protocolhandle import executable_location


def open_file(filepath):
    if not isinstance(filepath, str):
        raise Exception('filepath param must be str object')

    subprocess.call(('xdg-open', filepath))


def _register_protocol_handler(protocol, command, description):
    desktopfiles_dir = os.path.expanduser('~/.local/share/applications/')
    desktopfile_name = protocol + '.desktop'
    desktopfile_path = os.path.join(desktopfiles_dir, desktopfile_name)

    if os.path.isfile(desktopfile_path):
        popup('The desktop file is already installed.\nTrying to re-register {}'.format(desktopfile_path))
    else:
        contents = "[Desktop Entry]\n"
        contents += "Type=Application\n"
        contents += "Name={}\n".format(description)
        contents += "Exec={} url %u\n".format(command)
        contents += "StartupNotify=false\n"
        contents += "MimeType=x-scheme-handler/{};\n".format(protocol)

        with open(desktopfile_path, 'w') as f:
            f.write(contents)

    subprocess.check_call(('update-desktop-database', desktopfiles_dir))
    subprocess.check_call(('xdg-mime', 'default', desktopfile_name, 'x-scheme-handler/' + protocol))


def install():
    command = executable_location()
    _register_protocol_handler('octosearch', command, 'Octosearch Protocol Handler')


def settings_folder():
    return os.path.join(os.path.expanduser('~'), '.octosearch')


def popup(msg):
    """Display a popup"""
    subprocess.call(('zenity', '--title', 'Octosearch', '--notification', '--text', msg))
