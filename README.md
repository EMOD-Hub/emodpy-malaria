# emodpy-malaria

The Python interface for running EMOD malaria simulations.

![mosquito](docs/figures/jorussell-mosquito.png)

![license](https://img.shields.io/badge/License-MIT-brightgreen.svg)

## Description

emodpy-malaria is the primary way to work with EMOD for malaria research. Use it to set up
transmission settings, define populations, and evaluate the impact of interventions such as
insecticide-treated nets, indoor residual spraying, treatment seeking, and vaccines — then
run simulations and analyze the results.

## Project status

EMOD-Hub projects are provided as open source software under the MIT License for
community use, research, and development.

**Unless otherwise noted, these projects are no longer actively maintained or supported
by IDM or the Gates Foundation.**

Community contributions are welcome, and trusted collaborators may review and
merge pull requests, but no guarantees are made regarding support, pull request
review, security response, maintenance, or release timelines.

## Try it now

No installation required. Open the repository in
[GitHub Codespaces](https://github.com/codespaces/new?repo=EMOD-Hub/emodpy-malaria),
wait for the environment to build, then run:

```
cd tutorials
python tutorial_1_intro.py
```

See the [tutorial setup page](https://emod.idmod.org/emodpy-malaria/tutorials/setup/) for
Codespaces and local installation instructions, and
[Tutorial 1](https://emod.idmod.org/emodpy-malaria/tutorials/tutorial-1/) for a walkthrough
of what the script does.

## Installation

```shell
pip install emodpy-malaria
```

For complete installation instructions, including Codespaces, container-based workflows,
and local environment setup, see:

https://emod.idmod.org/emodpy-malaria/installation/

For developers, see the [developer installation](developer_installation.md) instructions.

## Upgrading from 5.x

**Version 6.0 is a major overhaul** of emodpy-malaria. Import paths,
API patterns, and the dependency stack have all changed significantly.
Projects using emodpy-malaria 5.x or earlier will require substantial
restructuring to work with 6.x.

- **[Migration guide](https://emod.idmod.org/emodpy-malaria/migration-guide-6x/)** — step-by-step upgrade instructions with before/after code examples
- **[Changelog](https://emod.idmod.org/emodpy-malaria/changes-5x-to-6x/)** — complete inventory of every file, module, and API change

## Documentation

Full documentation: https://emod.idmod.org/emodpy-malaria

**Releases and changelog:** https://github.com/EMOD-Hub/emodpy-malaria/releases

## Community

Have a question or a comment? Check out our
[Discussions](https://github.com/orgs/EMOD-Hub/discussions) space.

## Contributing

If you have feature requests, issues, or new code, please see our
[CONTRIBUTING](https://github.com/EMOD-Hub/.github/blob/main/CONTRIBUTING.md)
 page for how to provide your feedback.