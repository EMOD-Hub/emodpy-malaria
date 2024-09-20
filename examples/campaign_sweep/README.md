# Option #1 run example.py in comps:

    python3 example.py

# Option #2 run example_slurm.py in slurm: 
    python3 example_slurm.py -h
    -h, --help  show this help message and exit
    -l, --local select slurm_local


## Run example_slurm.py in slurm_bridged mode (inside singularity):
    python3 example_slurm.py

## Run example_slurm.py in slurm_local mode:
    python3 example_slurm.py -l
