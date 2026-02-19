# emodpy-malaria

Python module for use as user-space front-end for doing research easily with EMOD (MALARIA_SIM) via idmtools.

![mosquito](media/jorussell-mosquito.png)

![status](https://github.com/clorton/emodpy-malaria-singlebranch/workflows/Rebuild%20Malaria%20Docs/badge.svg) ![docs](https://readthedocs.org/projects/emodpy-malaria/badge/?version=latest) ![license](https://img.shields.io/badge/License-MIT-brightgreen.svg)

## Description

This package provides a Python scriptable interface for configuring EMOD for malaria modeling. This Python interface abstracts the process of creating JSON formatted files for parameter specification, demographics specification and intervention specification along as well as abstracting the process of creating binary climate and migration files.

## Getting started

Before installing `emodpy_malaria`, please see the [Getting Started page](getting_started.md).
It can guide you through trying EMOD before you try it on your own machine.

## Get `emodpy-malaria`

The `emodpy-malaria` package (and its supporting packages) is currently hosted on IDM's Python package repository.

```shell
python3 -m pip install emodpy-malaria --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

Note: you may need to only use `python` on Windows machines rather than `python3`.

## Documentation

Documentation available at https://docs.idmod.org/projects/emodpy-malaria/en/latest/.

To build the documentation locally, do the following:

1. Create and activate a venv.
2. Navigate to the root directory of the repo and enter the following:

    ```
    pip install -e . --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
    cd docs
    pip install -r requirements.txt
    make html
    ```
You may need to open a new command prompt before running `make html`. The HTML 
documentation will be output to the docs/_build/html directory. 

## FAQ

Frequently asked questions are answered in https://docs.idmod.org/projects/emodpy-malaria/en/latest/faq.html.

## Community

Have a question or a comment? Check out our [Discussions](https://github.com/EMOD-Hub/issues-and-discussions) space.


## Support and Contributions

The code in this repository was developed by IDM to support our research in disease
transmission and managing epidemics. We’ve made it publicly available under the MIT
License to provide others with a better understanding of our research and an opportunity
to build upon it for their own work. We make no representations that the code works as
intended or that we will provide support, address issues that are found, or accept pull
requests. You are welcome to create your own fork and modify the code to suit your own
modeling needs as contemplated under the MIT License.

If you have feature requests, issues, or new code, please see our
'CONTRIBUTING <https://github.com/InstituteforDiseaseModeling/emodpy-malaria/blob/main/CONTRIBUTING.rst>' page
for how to provide your feedback.

### Developer Installation
There are several options if you are modifying the code locally.

Option 1:
install in the `emodpy-malaria` directory:
```
pip install -e . --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

Option 2:
Each time you make a change you want to install 'build':
```
pip install build 
```
..and then run the following commands to build the package with latest code and install it:
```
python -m build --wheel
pip install dist\emodpy_malaria-XXX.whl 
```

# Disclaimer

The code in this repository was developed by IDM and other collaborators to support our joint research on flexible agent-based modeling.
 We've made it publicly available under the MIT License to provide others with a better understanding of our research and an opportunity to build upon it for 
 their own work. We make no representations that the code works as intended or that we will provide support, address issues that are found, or accept pull requests.
 You are welcome to create your own fork and modify the code to suit your own modeling needs as permitted under the MIT License.

