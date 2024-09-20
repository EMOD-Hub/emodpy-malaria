# Run Snakemake Examples #
1) Create virtual environment in emodpy-malaria
```
PATH_TO_EMODPY_MALARIA\emodpy-malaria\python -m venv venv
```

2) Activate environment
```
PATH_TO_EMODPY_MALARIA\emodpy-malaria\venv\Scripts\activate.bat
```

3) pip
```
venv> pip install emodpy_malaria
```

4) Create profile for snakemake (see snakemake help)

On Windows:
In C:\ProgramData\snakemake\snakemake or C:\Users\USER_NAME\AppData\Local\snakemake\snakemake create a directory ```default``` and a file ```default.yaml``` (or ```config.yaml```, depending on machine's ask)
with the content: 
```
jobs: 1
```

5) Delete existing output files
```
venv> snakemake --profile=default --cores=2 clean
```

6) Run all snakemake rules in _snakefile_
```
venv> snakemake --profile=default --cores=2
```

To run only one rule from the set of rules in _snakefile_
```
venv> snakemake --profile=default --cores=2 snakemake_rule
```

