#!/usr/bin/env python3

# idmtools
import os

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
from emodpy.emod_task import EMODTask

import manifest

"""
This example shows how to remove infected vectors and/or infected humans from a serialized population.
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
    malaria_config.add_species(config, manifest, "gambiae")
    # config.parameters.Vector_Sampling_Type = "TRACK_ALL_VECTORS"
    # config.parameters.Vector_Sampling_Type = "SAMPLE_IND_VECTORS" # default
    # config.parameters.Vector_Sampling_Type = "VECTOR_COMPARTMENTS_NUMBER"
    config.parameters.Simulation_Duration = 51
    config.parameters.Serialization_Time_Steps = [50]
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
    import emodpy_malaria.interventions.outbreak as outbreak

    campaign.set_schema(manifest.schema_file)
    outbreak.add_outbreak_individual(campaign, target_num_individuals=100)
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


def general_sim(selected_platform):
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """
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
    
    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    if selected_platform == "COMPS":
        #platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")
        platform = Platform("SLURMStage", num_retries=0)
        # set the singularity image to be used when running this experiment
        task.set_sif(manifest.sif_id)
    elif selected_platform.startswith("SLURM"):
        # This is for native slurm cluster
        # Quest slurm cluster. 'b1139' is guest partition for idm user. You may have different partition and acct
        platform = Platform(selected_platform, job_directory=manifest.job_directory, partition='b1139', time='10:00:00',
                            account='b1139', modules=['singularity'], max_running_jobs=10)
        # set the singularity image to be used when running this experiment
        # dtk_build_rocky_39.sif can be downloaded with command:
        # curl  https://packages.idmod.org:443/artifactory/idm-docker-public/idmtools/rocky_mpi/dtk_build_rocky_39.sif -o dtk_build_rocky_39.sif
        task.set_sif(manifest.sif_path_slurm, platform)
    
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
    if selected_platform == "COMPS":
        # important bit
        # WE ARE GOING TO USE SERIALIZATION FILES GENERATED IN burnin_create
        from idmtools_platform_comps.utils.download.download import DownloadWorkItem, CompressType
        dl_wi = DownloadWorkItem(
                                 related_experiments=[experiment.id],
                                 file_patterns=["output/*.dtk"],
                                 simulation_prefix_format_str='serialization_files',
                                 verbose=True,
                                 output_path="",
                                 delete_after_download=False,
                                 include_assets=True,
                                 compress_type=CompressType.deflate)

        dl_wi.run(wait_until_done=True, platform=platform)
        print("SHOULD BE DOWNLOADED")
    elif selected_platform.startswith("SLURM"):
        for simulation in experiment.simulations:
            simulation_dir = platform._op_client.get_directory(simulation)
            if os.path.exists(os.path.join(simulation_dir, "output", "state-00050.dtk")):
                print("dtk file path: ", os.path.join(simulation_dir, "output", "state-00050.dtk"))
                assert True
            else:
                print("dtk file not exists!")
                assert False

if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    selected_platform = "COMPS"
    general_sim(selected_platform)
