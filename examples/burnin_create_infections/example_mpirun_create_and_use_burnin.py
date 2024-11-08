#!/usr/bin/env python3

import os
import sys
from functools import partial
from typing import Any, Dict

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

from emodpy.emod_task import EMODTask
from idmtools.entities.simulation import Simulation

import manifest
from pathlib import Path

# Get the examples directory as a Path object
examples_directory = Path(__file__).resolve().parent.parent
utils_path = examples_directory / 'utils'
sys.path.insert(0, str(utils_path))
from burnin_utils import build_burnin_df


"""
This example shows how to remove infected vectors and/or infected humans from a serialized population.
"""

num_seeds = 10
sim_years = 5
serialize = False  # If True, we will use serialized files
burnin_exp_id = "df27b314-219e-ef11-aa19-b8830395dfc5"  # set this when serialize=True


def sweep_burnin_simulations(simulation, df, x: int):
    simulation.task.config.parameters.Serialized_Population_Path = os.path.join(df["outpath"][x], "output")
    simulation.task.config.parameters.Serialized_Population_Filenames = df["Serialized_Population_Filenames"][x]
    simulation.task.config.parameters["Num_Cores"] = int(df["Num_Cores"][x])
    simulation.task.config.parameters.Run_Number = int(df["Run_Number"][x])
    return {
        "Serialized_Population_Path": os.path.join(df["outpath"][x], "output"),
        "Serialized_Population_Filenames": df["Serialized_Population_Filenames"][x],
        "Num_Cores": int(df["Num_Cores"][x]),
        "Run_Number": int(df["Run_Number"][x])
    }


def set_param(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    """
    Set specific parameter value
    Args:
        simulation: idmtools Simulation
        param: parameter
        value: new value

    Returns:
        dict
    """
    return simulation.task.set_parameter(param, value)


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
    config.parameters.Simulation_Duration = sim_years * 365 + 1
    config.parameters.Serialization_Mask_Node_Write = 0
    config.parameters.Serialization_Precision = "REDUCED"
    if serialize:
        config.parameters.Serialization_Mask_Node_Read = 0
        config.parameters.Serialized_Population_Reading_Type = "READ"
        config.parameters.Serialized_Population_Writing_Type = "NONE"
    else:
        config.parameters.Serialization_Time_Steps = [sim_years * 365]
        config.parameters.Serialized_Population_Writing_Type = "TIMESTEP"

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
    if selected_platform.upper().startswith("COMPS"):
        platform = Platform("Calculon", node_group="idm_48cores", priority="Highest", num_cores=2)
        # set the singularity image to be used when running this experiment
        task.set_sif(manifest.sif_id)
    elif selected_platform.upper().startswith("SLURM_LOCAL"):
        # Slurm_Local is a platform configuration that allows job submissions to your SLURM cluster.
        # For the NU Quest SLURM cluster, 'b1139' is the guest partition for IDM users.
        # You may need to specify a different partition and account, depending on your SLURM setup.

        # ntasks=2 specifies that the job should use 2 cores (tasks) for parallel processing via mpirun in SLURM.
        # Make sure your SLURM job’s demographic data includes at least 2 nodes to support this;
        # otherwise, set ntasks=1 for a single core.

        # run_on_slurm=True indicates that all job setup and execution will occur on compute nodes.
        # If set to False, initial setup will occur on the login node, with the simulation itself running on compute nodes.
        platform = Platform(selected_platform, job_directory=manifest.job_directory, partition='b1139', time='10:00:00',
                            account='b1139', modules=['singularity', 'mpi/mpich-4.0.2-gcc-10.4.0'], ntasks=2,
                            run_on_slurm=False, max_running_jobs=10)

        # set the singularity image to be used when running this experiment
        # dtk_build_rocky_39.sif can be downloaded with command:
        # curl  https://packages.idmod.org:443/artifactory/idm-docker-public/idmtools/rocky_mpi/dtk_build_rocky_39.sif -o dtk_build_rocky_39.sif
        task.set_sif(manifest.sif_path_slurm, platform)

    builder = SimulationBuilder()

    if serialize:  # Use burnin simulations
        burnin_df = build_burnin_df(burnin_exp_id, platform, sim_years * 365)
        builder.add_sweep_definition(partial(sweep_burnin_simulations, df=burnin_df), burnin_df.index)
        experiment_name = f"Use_burnin_simulations {os.path.split(sys.argv[0])[1]}"

    else:  # Create burnin simulations
        builder.add_sweep_definition(partial(set_param, param='Run_Number'), range(num_seeds))
        experiment_name = f"Create_burnin_simulations {os.path.split(sys.argv[0])[1]}"

    experiment = Experiment.from_builder(builder, task, name=experiment_name)
    experiment.run(wait_until_done=True, platform=platform)

    #from idmtools.core import ItemType
    #experiment = platform.get_item("8dc522c9-0d9e-ef11-aa19-b8830395dfc5", ItemType.EXPERIMENT)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
        exit()
    else:
        print(f"Experiment {experiment.id} succeeded.")

    # Save experiment id to file
    with open("experiment_id", "w") as fd:
        fd.write(experiment.id)
    print()
    print(experiment.id)

    if not serialize:
        if selected_platform.upper().startswith("COMPS"):
            # important bit
            # WE ARE GOING TO USE SERIALIZATION FILES GENERATED IN burnin_create
            from idmtools_platform_comps.utils.download.download import DownloadWorkItem, CompressType
            dl_wi = DownloadWorkItem(
                related_experiments=[experiment.id],
                file_patterns=["output/*.dtk"],
                verbose=True,
                output_path="",
                delete_after_download=False,
                include_assets=True,
                compress_type=CompressType.deflate)

            dl_wi.run(wait_until_done=True, platform=platform)
            print("SHOULD BE DOWNLOADED")
        elif selected_platform.upper().startswith("SLURM_LOCAL"):
            for simulation in experiment.simulations:
                simulation_dir = platform._op_client.get_directory(simulation)
                if os.path.exists(os.path.join(simulation_dir, "output", "state-01825-001.dtk")):
                    print("dtk file path: ", os.path.join(simulation_dir, "output", "state-01825-001.dtk"))
                    assert True
                if os.path.exists(os.path.join(simulation_dir, "output", "state-01825-000.dtk")):
                    print("dtk file path: ", os.path.join(simulation_dir, "output", "state-01825-000.dtk"))
                    assert True
                else:
                    print("dtk file not exists!")
                    assert False


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    #selected_platform = "SLURM_LOCAL"
    selected_platform = "COMPS"
    general_sim(selected_platform)
