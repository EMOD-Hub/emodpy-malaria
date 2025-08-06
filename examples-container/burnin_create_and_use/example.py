#!/usr/bin/env python3
import os
import sys
from functools import partial
from typing import Any, Dict
from pathlib import Path
from idmtools.builders import SimulationBuilder
# idmtools
from idmtools.core.platform_factory import Platform
# emodpy
from emodpy.emod_task import EMODTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation

from idmtools.entities.templated_simulation import TemplatedSimulations
import params
import manifest

# Get the examples directory as a Path object
examples_directory = Path(__file__).resolve().parent.parent.parent
utils_path = examples_directory / 'examples' / 'utils'
sys.path.insert(0, str(utils_path))
from burnin_utils import build_burnin_df

"""
In this example we create serialization files from a multicore simulation.
The important bits are in set_param_fn function and in Platform class call

"""


def set_param(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    return simulation.task.set_parameter(param, value)


def sweep_burnin_simulations(simulation, df, x: int):
    simulation.task.config.parameters.Serialized_Population_Path = os.path.join(df["outpath"][x], "output")
    simulation.task.config.parameters.Serialized_Population_Filenames = df["Serialized_Population_Filenames"][x]
    simulation.task.config.parameters["Num_Cores"] = int(df["Num_Cores"][x])
    simulation.task.config.parameters.Run_Number = int(df["Run_Number"][x])

    return {
        "Serialized_Population_Path": os.path.join(df["outpath"][x], "output"),
        "Serialized_Population_Filenames": df["Serialized_Population_Filenames"][x],
        "Num_Cores": int(df["Num_Cores"][x]),
        "Run_Number": int(df["Run_Number"][x])}


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
    if params.burnin_type == True:
        config.parameters.Simulation_Duration = 200
        config.parameters.Serialized_Population_Writing_Type = "TIMESTEP"
        config.parameters.Serialization_Mask_Node_Write = 0
        config.parameters.Serialization_Precision = "REDUCED"
    else:
        config.parameters.Simulation_Duration = 200
        config.parameters.Serialized_Population_Reading_Type = "READ"
        config.parameters.Serialization_Mask_Node_Read = 0
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

    # Set platform to Container Platform
    # ntasks=2 is triggering mpirun -n 2 for multiple process
    # make sure you have at least more than 2 nodes in your demographics
    platform = Platform("Container", job_directory="../example_jobs", ntasks=2)
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

    builder = SimulationBuilder()
    ts = TemplatedSimulations(base_task=task)
    if params.burnin_type:
        experiment_name = "burnin"
        run_count = 2
        builder.add_sweep_definition(partial(set_param, param='Run_Number'), range(run_count))
        builder.add_sweep_definition(partial(set_param, param='Serialization_Time_Steps'),
                                     [[100, 200]])
    else:
        experiment_name = "use_burnin"
        burnin_exp_id = "e5aa5423-b288-43b1-810c-cb3ebdb80747"  # this is experiment id from burnin run
        serialize_days = 200
        burnin_df = build_burnin_df(burnin_exp_id, platform, serialize_days)

        builder.add_sweep_definition(partial(sweep_burnin_simulations, df=burnin_df), burnin_df.index)
        run_count = 10
        builder.add_sweep_definition(partial(set_param, param='Run_Number'), range(run_count))
    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    ts.add_builder(builder)
    experiment = Experiment.from_template(ts, name=experiment_name)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True)

    # Check result
    print()
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
    else:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id.txt", "w") as fd:
            fd.write(experiment.id)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
