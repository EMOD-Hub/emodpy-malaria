import os
import shutil
from pathlib import Path
import time


def delete_existing_file(file):
    if os.path.isfile(file):
        os.remove(file)


def is_dir_path_empty(directory_path):
    path = Path(directory_path)
    if not path.is_dir():
        return False
    return not any(path.iterdir())


def delete_existing_folder(path, must_be_empty=False):
    if os.path.isdir(path):
        if not must_be_empty or (must_be_empty and is_dir_path_empty(path)):
            try:
                shutil.rmtree(path)
            except PermissionError:
                print(f"Failed to delete folder {path}.  It could be that the files are owned by root.")


def close_idmtools_logger(logger):
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)


def create_failed_tests_folder():
    import manifest
    if not os.path.exists(manifest.failed_tests):
        os.makedirs(manifest.failed_tests)
