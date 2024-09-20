#!/usr/bin/env python3
# coding=utf-8

from __future__ import print_function
import os
import glob
import argparse
from sys import exit
from subprocess import check_output


def get_argparser(parser=None):
    """Return default argparser object for command-line args for this script.

    Args:
            parser (argparser.ArgumentParser): the ArgumentParser object to add arguments to (useful for testing)

        Returns:
            argparser.ArgumentParser: ArgumentParser object w/ added arguments and config
    """
    if not parser:
        parser = argparse.ArgumentParser(description='')

    parser.add_argument('--package-file', default='setup.py', help='Package setup filename.')
    parser.add_argument('--set-gh-actions-var', type=str, help='Set github actions variable via stdout.')

    return parser


def get_wheel_filename(package_file: str):
    """Get wheel filename from a python setup package filename

    Args:
        package_file (str): relative path to the package file

    Returns:
        str: path to the appropriate wheel file corresponding to the package (if it exists), or None if it doesn't exist
    """
    if not os.path.isfile(package_file):
        raise FileNotFoundError(f"Package file not found at '{package_file}'")

    pkg_name = check_output(['python', '-W', 'ignore', package_file, '--name']).decode('utf-8').strip().replace('-', '_')
    dist_path = os.path.join(os.path.dirname(package_file), 'dist')

    files = glob.glob(os.path.join(dist_path, f'{pkg_name}*.whl'))
    if len(files) > 0:
        return files[0]
    return None


def set_gh_actions_var(name: str, value: str):
    """Set a github actions variable by using specially formatted stdout messages.

    Args:
        name (str): name of the variable
        value (str): value of the variable
    """
    print(f'::set-output name={name}::{value}')


def main(args):
    """Main script function.

    Args:
        args: argparser parser.parse_args() object containing cmdline argument values as properties

    Returns:
        bool: success
    """
    wheel_file = get_wheel_filename(args.package_file)

    if not wheel_file:
        raise FileNotFoundError(f"Wheel file not found for package '{args.package_file}'.")

    if args.set_gh_actions_var:
        set_gh_actions_var(args.set_gh_actions_var, wheel_file)
    else:
        print(wheel_file)

    return True


if __name__ == '__main__':
    """Run main function by default when run on cmdline (but not when imported as a library)  
    """
    parser = get_argparser()
    arguments = parser.parse_args()

    if not main(arguments):
        exit(1)
