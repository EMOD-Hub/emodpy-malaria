import argparse

import emodpy.bamboo_api_utils as bamboo_api

"""
    Run this script to login to bamboo and cache credentials. Usage:

    "python bamboo_login_with_arguments.py -u youremail@idmod.org -p password"

"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', '--username', help='enter bamboo username')
    parser.add_argument('-p', '--password', help='enter bamboo password')

    args = parser.parse_args()
    print("Login to bamboo and cache the credentials.")

    succeed = bamboo_api.bamboo_connection().login(username=args.username, password=args.password)
    print(f'login status: {succeed}')

    if succeed:
        bamboo_api.save_credentials(username=args.username, password=args.password)
