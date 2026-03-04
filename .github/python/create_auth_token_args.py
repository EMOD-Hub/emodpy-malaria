import argparse
from COMPS import Client
from COMPS.CredentialPrompt import CredentialPrompt

__comps_client_version = 10


class StaticCredentialPrompt(CredentialPrompt):
    def __init__(self, comps_url, username, password):
        if (comps_url is None) or (username is None) or (password is None):
            print("Usage: python create_auth_token_args.py --comps_url url --username username --password pwd")
            print("\n")
            raise RuntimeError('Missing comps_url, or username or password')
        self._times_prompted = 0
        self.comps_url = comps_url
        self.username = username
        self.password = password
    
    def prompt(self):
        print("logging in with user/pw")
        self._times_prompted = self._times_prompted + 1
        if self._times_prompted > 3:
            raise RuntimeError('Failure authenticating')
        return {'Username': self.username, 'Password': self.password}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--comps_url', default='https://comps2.idmod.org', help='comps url')
    parser.add_argument('-u', '--username', help='enter username')
    parser.add_argument('-p', '--password', help='enter password')

    args = parser.parse_args()

    compshost = args.comps_url

    Client.login(compshost, StaticCredentialPrompt(comps_url=args.comps_url, username=args.username,
                                                   password=args.password))
