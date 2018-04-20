import subprocess
import os.path


def open_file(filepath):
    if not isinstance(filepath, str):
        raise Exception('filepath param must be str object')

    subprocess.call(('open', filepath))


def install():
    pass


def settings_folder():
    return os.path.join(os.path.expanduser('~'), '.octosearch')


def popup(msg):
    """Display a popup"""
    print(msg)
