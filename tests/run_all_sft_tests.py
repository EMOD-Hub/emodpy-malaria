
import os
import subprocess
import sys


def walkdir(dirname):
    test_list = []
    for cur, _dirs, files in os.walk(dirname):
        for f in files:
            if f.startswith("test") and f.endswith(".py"):
                file_path = {cur: f}
                test_list.append(file_path)
    return test_list


if __name__ == '__main__':
    CURRENT_DIRECTORY = os.path.dirname(__file__)

    test_list = walkdir("dtk_sfts")
    cwd = os.getcwd()
    for dict_item in test_list:
        for key in dict_item:
            print(f"test file {dict_item[key]}")
            print(f"test dir {key}")
            p = subprocess.run(["pytest", "-x", "-v", "--junitxml", "test_results.xml"], cwd=key)
            if p.returncode != 0:
                sys.exit(p.returncode)
