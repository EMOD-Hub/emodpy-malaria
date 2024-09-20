#!/usr/bin/env python3
# coding=utf-8

from __future__ import print_function
import configparser
import platform
import os


def update_config(config_overrides, config_file=None, create=True):
    """Update a config (ini) file with specific override values then write out the config file with the updates. By
    default, create the file and populate it with only the overrides if it doesn't exist.

    Example:
        update_config({'global': { 'index-url': 'https://myrepo.com/staging' }}, '.\\pip.ini')

    Args:
        config_overrides (dict): nested dictionary of section keys to dictionaries of setting keys and values
        config_file (str): path to config_file to update or create, if not present defaults to ~/.pip/pip.conf on linux
            or %HOMEDIR%\pip\pip.ini on windows
        create (bool): whether to create the file if it doesn't exist

    Returns:
        str: config file path updated/created
    """
    config = configparser.ConfigParser()
    if not config_file:
        config_filename = 'pip.conf'
        config_dir = '.pip'
        if platform.system() == 'Linux':
            config_filename = 'pip.conf'
            config_dir = '.pip'
        if platform.system() == 'Windows':
            config_filename = 'pip.ini'
            config_dir = 'pip'

        virtual_env_dir = os.getenv('VIRTUAL_ENV')

        if virtual_env_dir and os.path.exists(virtual_env_dir):
            config_file = os.path.join(virtual_env_dir, config_filename)
        else:
            config_file = os.path.join(os.path.expanduser('~'), config_dir, config_filename)


        if platform.system() == 'Linux':
            config_file = os.path.join(os.path.expanduser('~'), '.pip', 'pip.conf')
        elif platform.system() == 'Windows':
            config_file = os.path.join(os.path.expanduser('~'), 'pip', 'pip.ini')
        else:
            raise NotImplementedError(f'Unknown platform {platform.system()} (neither linux nor windows).')

    if os.path.exists(config_file):
        with open(config_file, 'r') as config_reader:
            config.read_file(config_reader)
    else:
        if create:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
        else:
            raise FileNotFoundError(f"Config file {config_file} does not exist, and can't create.")

    for section in config_overrides.keys():
        if section != config.default_section and not config.has_section(section):
            config.add_section(section)
        for setting_key, setting_value in config_overrides[section].items():
            config.set(section, setting_key, setting_value)

    with open(config_file, 'w') as config_writer:
        config.write(config_writer)

    return config_file


def update_pip_conf():
    """Update default pip config file for user, add IDM artifactory index url.
    """
    update_config({'global': { 'index-url': 'https://packages.idmod.org/api/pypi/pypi-production/simple' }})


if __name__ == '__main__':
    """Run main function by default when run on cmdline (but not when imported as a library)
    """
    update_pip_conf()
