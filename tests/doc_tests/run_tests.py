# this code was modified from https://github.com/boxed/pytest-readme
import os
import re
import pytest
from pathlib import Path


folders = [Path(__file__).parents[2].joinpath('emodpy_malaria/weather')]

def setup():
    tests = []
    for f in folders:
        subfolder = str(f.parts[-1])
        subfolder = re.sub('[^A-Za-z0-9]+', '', subfolder)
        test_name = f.joinpath(f'test_readme_{subfolder}.py')
        with open(test_name, 'w') as out, open(f.joinpath('README.md')) as readme:
            mode = None
            output = []
            import_statement = []
            for i, line in enumerate(readme.readlines()):
                output.append('\n')
                if mode is None and line.strip() == '```python':
                    mode = 'first_line'
                    output[i] = 'def test_line_%s():\n' % i
                    continue
                elif line.strip() == '```':
                    if mode == 'doctest':
                        output[i] = '    """\n'
                    mode = None
                    continue
                elif mode == 'first_line':
                    if line.strip() == '':
                        mode = None
                        output[i - 1] = '\n'
                        continue
                    if line.strip().startswith('>>>'):
                        mode = 'doctest'
                        output[i - 2] = output[i - 1][:-1] + '  ' + output[i - 2]  # move the def line one line up
                        output[i - 1] = '    """\n'
                    else:
                        mode = 'test'
                if mode in ('doctest', 'test'):
                    if 'import *' in line.strip():
                        import_statement.append(line.strip() + '\n')
                        continue
                    else:
                        output[i] = '    ' + line
                else:
                    output[i] = '# %s' % line
            output = list(set(import_statement)) + output
            out.writelines(output)
            tests.append(test_name)
    # append test names to pytest.ini
            with open(f.joinpath('pytest.ini'), 'w') as ini:
                ini.writelines("[pytest]\naddopts = --doctest-modules\n")

if __name__ == "__main__":
    setup()
    # change directory to root folder
    os.chdir(Path(__file__).parents[2])
    for f in folders:
        pytest.main([f'{f}',
                     f'--junitxml={Path(__file__).parent.joinpath(f.parts[len(f.parts)-1])}_readme_test.xml'])