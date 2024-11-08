#!/usr/bin/env python3
import os
import sys

from functools import partial
from typing import Any, Dict
from pathlib import Path

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

from emodpy.emod_task import EMODTask
from idmtools.entities.simulation import Simulation
from emodpy_malaria.reporters.builtin import add_report_vector_genetics

import manifest

# Get the examples directory as a Path object
examples_directory = Path(__file__).resolve().parent.parent
utils_path = examples_directory / 'utils'
sys.path.insert(0, str(utils_path))
from burnin_utils import build_burnin_df

serialized_day = 50

serialize = False  # If True, we will use serialized files

burnin_exp_id = "ff075366-58d0-4080-90ca-739867859848"  # set this value to burnin experiment id when serialize=True
"""
This example shows how to remove infected vectors and/or infected humans from a serialized population.
"""
def sweep_burnin_simulations(simulation, df, x: int):
    simulation.task.config.parameters.Serialized_Population_Path = os.path.join(df["outpath"][x], "output")
    simulation.task.config.parameters.Serialized_Population_Filenames = df["Serialized_Population_Filenames"][x]
    simulation.task.config.parameters["Num_Cores"] = int(df["Num_Cores"][x])
    simulation.task.config.parameters.Run_Number = int(df["Run_Number"][x])
    simulation.task.config.parameters.x_Temporary_Larval_Habitat = float(df["x_Temporary_Larval_Habitat"][x])

    return {
        "Serialized_Population_Path": os.path.join(df["outpath"][x], "output"),
        "Serialized_Population_Filenames": df["Serialized_Population_Filenames"][x],
        "Num_Cores": int(df["Num_Cores"][x]),
        "Run_Number": int(df["Run_Number"][x]),
        "x_Temporary_Larval_Habitat": float(df["x_Temporary_Larval_Habitat"][x])
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
    if not serialize:  # burnin
        config.parameters.Simulation_Duration = serialized_day + 1
        config.parameters.Serialization_Time_Steps = [serialized_day]
        config.parameters.Serialized_Population_Writing_Type = "TIMESTEP"
        config.parameters.Serialization_Mask_Node_Write = 0
        config.parameters.Serialization_Precision = "REDUCED"
    else:
        config.parameters.Simulation_Duration = 365
        config.parameters.Serialized_Population_Reading_Type = "READ"
        config.parameters.Serialization_Mask_Node_Read = 0
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


def general_sim():
    """
        This example create 3 burnin simulations with sweeping on x_Temporary_Larval_Habitat = [0.1, 1, 10]
    Returns:
        Nothing
    """

    experiment_name = "Create burnin simulations"
    
    # create EMODTask 
    print("Creating EMODTask (from files)...")

    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_camp,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_param_fn,
        demog_builder=build_demog,
        plugin_report=None  # report
    )

    # Set platform
    platform = Platform("SLURM_LOCAL", job_directory=manifest.job_directory, partition='b1139', time='10:00:00',
                        account='b1139', modules=['singularity'], max_running_jobs=10)
    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path_slurm, platform)

    if serialize:
        add_report_vector_genetics(task, manifest, species="gambiae")
    builder = SimulationBuilder()

    if not serialize:  # Create new burnin simulations
        run_count = 1
        hab_vals = [0.1, 1, 10]
        builder.add_sweep_definition(partial(set_param, param='Run_Number'), range(run_count))
        builder.add_sweep_definition(partial(set_param, param='x_Temporary_Larval_Habitat'),
                                     [hab_val for hab_val in hab_vals])
        builder.add_sweep_definition(partial(set_param, param='Serialization_Time_Steps'),
                                     [[50]])
        experiment_name = f"Create_burnin_simulations_larval_habitat"
    else:  # Use serialized files
        burnin_df = build_burnin_df(burnin_exp_id, platform, serialized_day)
        builder.add_sweep_definition(partial(sweep_burnin_simulations, df=burnin_df), burnin_df.index)
        run_count = 10
        builder.add_sweep_definition(partial(set_param, param='Run_Number'), range(run_count))
        experiment_name = f"Use_burnin_simulations_larval_habitat"

    experiment = Experiment.from_builder(builder, task, name=experiment_name)
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


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
