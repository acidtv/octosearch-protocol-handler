import subprocess
import os.path


def open_file(filepath):
    if not isinstance(filepath, str):
        raise Exception('filepath param must be str object')

    subprocess.call(('xdg-open', filepath))


def _register_protocol_handler():
    #[Desktop Entry]
    #Type=Application
    #Name=Octosearch Protocol Handler
    #Exec=/home/alex/code/octosearch-protocol-handler/protocolhandle.py url %u
    #StartupNotify=false
    #MimeType=x-scheme-handler/octosearch;

    # update-desktop-database ~/.local/share/applications/
    # xdg-mime default ssh-terminal.desktop x-scheme-handler/ssh
    pass


def install():
    pass


def settings_folder():
    return os.path.join(os.path.expanduser('~'), '.octosearch')


def popup(msg):
    """Display a popup"""
    subprocess.run(('zenity', '--title', 'Octosearch', '--notification', '--text', msg))
