#!/usr/bin/env python3

from pathlib import Path
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

import manifest
import sys

from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files

sys.path.append('../../emodpy_malaria/serialization')
import zero_infections

"""
This example downloads serialized files from the burnin/example
The important bits are in set_param_fn function and general_sim function
"""
def set_param_fn(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, "gambiae")
    config.parameters.Simulation_Duration = 1   # Just to check if saved dtk file can be loaded
    config.parameters.Serialized_Population_Reading_Type = "READ"
    config.parameters.Serialization_Mask_Node_Read = 0
    config.parameters.Serialized_Population_Path = manifest.assets_input_dir # <--we uploaded files to here
    config.parameters.Serialized_Population_Filenames = [manifest.destination]

    return config

def build_demog():
    """
        Builds demographics
    Returns:
        final demographics object
    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    return Demographics.from_params() # dummy, loading serialized population

def general_sim():
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", num_cores=1, node_group="idm_48cores", priority="Highest")
    experiment_name = "Create simulation from serialized files"

    # important bit
    # WE ARE GOING TO USE SERIALIZATION FILES GENERATED IN burnin_create
    from idmtools_platform_comps.utils.download.download import DownloadWorkItem, CompressType
    # navigating to the experiment.id file to retrieve experiment id
    with open("../burnin_create_infections/experiment_id") as f:
        experiment_id = f.readline()

    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=None,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        ep4_custom_cb=None,
        demog_builder=build_demog,
        plugin_report=None  # report
    )
    
    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)
    
    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment = Experiment.from_task(task=task, name=experiment_name)

    print("Adding asset dir...")
    task.common_assets.add_directory(assets_directory=manifest.ser_out_path)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        exit()

    print(f"Experiment {experiment.uid} succeeded.")

    # Save experiment id to file
    with open("experiment_id", "w") as fd:
        fd.write(experiment.uid.hex)
    print()
    print(experiment.uid.hex)


def run_example():
    # 2) remove infection
    source_dtk = Path(manifest.ser_path, manifest.source)
    destination_dtk = Path(manifest.ser_out_path, manifest.destination)
    zero_infections.zero_infections(source_dtk, destination_dtk, [], [])
    
    # 3) Check if generated dtk file can be loaded
    general_sim()


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(Path(manifest.eradication_path).parent)
    run_example()

