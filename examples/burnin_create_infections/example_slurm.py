#!/usr/bin/env python3
import argparse

from example import general_sim

import manifest

# Run command:
# "python3 example_slurm.py" -- to run with SLURM_BRIDGED mode inside singularity container
# "python3 example_slurm.py -l" -- to run in SLURM_LOCAL mode with virtual environment
if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local', action='store_true', help='select slurm_local')
    args = parser.parse_args()
    if args.local:
        selected_platform = "SLURM_LOCAL"
    else:
        selected_platform = "SLURM_BRIDGED"
    general_sim(selected_platform)
