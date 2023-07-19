import os

def get_app_root(file) -> str:
    return os.path.dirname(os.path.realpath(file))