# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

**emodpy-malaria** is a Python library that provides a scriptable interface for configuring the [EMOD](https://docs.idmod.org/projects/emod-malaria) malaria simulator. It abstracts the complexity of creating JSON configuration files, demographics, intervention definitions, and binary climate/migration files needed for running malaria simulations.

## Commands

### Install for development
```bash
pip install -e .
```

### Run all unit tests
```bash
cd tests && python -m pytest --dist loadfile -v --junitxml="test_results.xml"
```

### Run a single test file
```bash
cd tests && python -m pytest unittests/test_malaria_config.py -v
```

### Run a single test by name
```bash
cd tests && python -m pytest unittests/test_malaria_config.py::ClassName::test_method -v
```

### Lint
```bash
flake8 --ignore=E501,E261,W503 emodpy_malaria
```

### Build documentation locally
```bash
pip install -e"[docs]" .
python -m sphinx -T --keep-going -b html ./docs ./site
```

## Architecture

### How the Library Fits Together

The library is organized around the two concerns a user needs to configure before running a simulation:

1. **Simulation config** (`malaria_config.py`, `vector_config.py`) — sets parameters on the EMOD config object (disease progression, immunity, detection thresholds, vector biology, genetics). The entry point is `set_team_defaults()` in each module; individual functions like `add_species()` or `set_drug_param()` modify specific sections.

2. **Campaigns** (`interventions/`) — builds campaign events (JSON objects) representing interventions delivered to the population. Each intervention type (bednet, drug, vaccine, IRS, ivermectin, treatment-seeking, etc.) lives in its own module. `common.py` provides shared event-building utilities used by all other intervention modules.

Downstream concerns have their own subpackages:
- `demographics/` — generates population demographics files (initial prevalence, biting heterogeneity, larval habitat multipliers) via `MalariaDemographics`, which extends the base `Demographics` class from `emod_api`.
- `reporters/` (`builtin.py`) — configures which output reports EMOD writes during simulation.
- `weather/` — converts climate data between CSV, DataFrame, and EMOD binary formats; can also request data from an SSMT remote service.
- `migration/` — converts human/vector migration data to EMOD binary format.
- `serialization/` — handles checkpoint files (zeroing infections, swapping genomes).

### Key Design Patterns

**Schema-backed objects**: Configuration objects are generated from EMOD's JSON schema at runtime using `emod_api.schema_to_class`. The schema file is referenced via `tests/unittests/manifest.py` and `tests/unittests/schema_path_file.py` for tests.

**Intervention module pattern**: Every intervention module exposes one or more `add_*` functions that accept a `campaign` object and keyword parameters, build an intervention config using schema-backed classes, then call `common.add_campaign_event()` to attach it to the campaign.

**CSV-driven drug parameters**: Drug pharmacokinetics live in `emodpy_malaria/malaria_drug_params.csv`, not in Python. The `set_drug_param()` function reads this file to populate config values.

### Core Dependencies

| Package | Role |
|---------|------|
| `emod_api` | Base config/demographics/campaign objects and schema utilities |
| `emodpy ~=1.16` | IDM's core EMOD Python API (task creation, file handling) |
| `emod-malaria ~=2.34.0` | Malaria disease model binaries and schema |

### Test Layout

- `tests/unittests/` — standard pytest/unittest tests; run offline, no EMOD binary required
- `tests/doc_tests/` — validates documentation examples
- `examples-container/` — Snakemake-based integration tests that run actual EMOD simulations; Linux-only CI environment
