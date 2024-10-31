#!/usr/bin/env python3

# idmtools
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
from emodpy.emod_task import EMODTask
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files

import manifest

"""
In this example we create serialization files from a multicore simulation.
The important bits are in set_param_fn function and in Platform class call

"""



def set_param_fn(config):
    """
         This is a call-back function that sets parameters.
         Here we are getting "default" parameters for a MALARIA_SIM and
         explicitly adding Serialization_Parameters
    Args:
        config:

    Returns:
        completed configuration
    """

    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    config.parameters.Simulation_Duration = 210
    config.parameters.Serialization_Time_Steps = [20, 200]
    config.parameters.Serialized_Population_Writing_Type = "TIMESTEP"
    config.parameters.Serialization_Mask_Node_Write = 0
    config.parameters.Serialization_Precision = "REDUCED"
    return config


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as campaign
    from emodpy_malaria.interventions.bednet import add_itn_scheduled

    campaign.set_schema(manifest.schema_file)

    add_itn_scheduled(campaign,
                      start_day=100,
                      demographic_coverage=1.0,
                      killing_initial_effect=1.0,
                      blocking_initial_effect=1.0,
                      usage_initial_effect=1.0)
    return campaign


def build_demog():
    """
        Builds demographics
    Returns:
        final demographics object
    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demog = Demographics.from_params(tot_pop=100, num_nodes=4)
    return demog


def general_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", num_cores=2, node_group="idm_48cores", priority="Highest")
    experiment_name = "Create simulation from serialized files"
    
    # create EMODTask 
    print("Creating EMODTask (from files)...")

    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_camp,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_param_fn,  # THIS IS WHERE SERIALIZATION PARAMETERS ARE ADDED
        demog_builder=build_demog,
        plugin_report=None  # report
    )
    
    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)
    
    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment = Experiment.from_task(task=task, name=experiment_name)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
        exit()

    print(f"Experiment {experiment.id} succeeded.")

    # Save experiment id to file
    with open("experiment_id", "w") as fd:
        fd.write(experiment.id)
    print()
    print(experiment.id)
    
    # important bit
    # WE ARE GOING TO USE SERIALIZATION FILES GENERATED IN burnin_create
    from idmtools_platform_comps.utils.download.download import DownloadWorkItem, CompressType
    # navigating to the experiment.id file to retrieve experiment id
    # with open("../burnin_create/experiment.id") as f:
    #    experiment_id = f.readline()

    dl_wi = DownloadWorkItem(
                             related_experiments=[experiment.id],
                             file_patterns=["output/*.dtk"],
                             simulation_prefix_format_str='serialization_files',
                             verbose=True,
                             output_path="",
                             delete_after_download=False,
                             include_assets=True,
                             compress_type=CompressType.deflate)

    dl_wi.run(wait_on_done=True, platform=platform)
    print("SHOULD BE DOWNLOADED")


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
