import os

current_directory = os.path.dirname(os.path.realpath(__file__))
demo_folder = os.path.join(current_directory, 'data', 'demographics')
if not os.path.isdir(demo_folder):
    os.mkdir(demo_folder)


def delete_existing_file(file):
    if os.path.isfile(file):
        print(f'\tremove existing {file}.')
        os.remove(file)


def create_folder(folder_path):
    if folder_path:
        if not os.path.isdir(folder_path):
            print(f"\t{folder_path} doesn't exist, creating {folder_path}.")
            os.mkdir(folder_path)
