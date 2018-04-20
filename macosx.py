import subprocess


def open_file(filepath):
    if not isinstance(filepath, str):
        raise Exception('filepath param must be str object')

    subprocess.call(('xdg-open', filepath))


def register():
    pass
