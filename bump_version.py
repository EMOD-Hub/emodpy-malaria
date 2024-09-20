"""
Tool which bumps the version based on the following commandline args:
--dev
--patch
--minor
--major

For more information on the versioning scheme, please refer to: semver.org
"""
import argparse


def bump_version(version, bump_type):
    if "dev" in version:
        main_version, dev_str = version.split('.dev')
        dev = int(dev_str)
    else:
        main_version = version
        dev = None
        major, minor, patch = [int(x) for x in version.split('.', 2)] # gets "[patch].[dev]" for last str

    major, minor, patch = map(int, main_version.split('.'))

    if bump_type == 'dev':
        if dev is not None:
            dev = dev + 1
        else:
            dev = 0
    elif bump_type == 'patch':
        patch += 1
        dev = None
    elif bump_type == 'minor':
        minor += 1
        patch = 0
        dev = None
    elif bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
        dev = None

    new_version = f"{major}.{minor}.{patch}"
    if dev is not None:
        new_version += f".dev{dev}"

    print(f"Bumping a {bump_type} release from {version} to {new_version}")

    return new_version

def process_file(filename, bump_type):
    with open(filename, 'r') as f:
        lines = f.readlines()

    with open(filename, 'w') as f:
        for line in lines:
            if '__version__' in line or 'current_version' in line:
                version = line.split(' = ')[1].strip().strip("'")
                new_version = bump_version(version, bump_type)
                f.write(f"__version__ = '{new_version}'\n")
            elif 'current_version' in line:
                version = line.split(' = ')[1].strip()
                new_version = bump_version(version, bump_type)
                f.write("current_version = {new_version}\n")
           
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Bump version script.")
    parser.add_argument("--dev", action="store_true", help="Bump development version.")
    parser.add_argument("--patch", action="store_true", help="Bump patch version.")
    parser.add_argument("--minor", action="store_true", help="Bump minor version.")
    parser.add_argument("--major", action="store_true", help="Bump major version.")
    args = parser.parse_args()

    bump_type = None
    if args.dev:
        bump_type = 'dev'
    elif args.patch:
        bump_type = 'patch'
    elif args.minor:
        bump_type = 'minor'
    elif args.major:
        bump_type = 'major'

    if bump_type:
        # Example files to be processed
        files = [".bump_version.cfg", "version.py"]
        for file in files:
            process_file(file, bump_type)
    else:
        print("Error: Please specify a bump type. Use -h for help.")
