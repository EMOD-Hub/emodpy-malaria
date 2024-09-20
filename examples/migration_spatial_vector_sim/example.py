#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files

# emod_api
import emod_api.migration as migration

from emodpy_malaria import vector_config
from emodpy_malaria import malaria_config as malaria_config
import manifest

"""
    In this example we create migration for a multi-node simulation and add spatial output.
    We are getting demographics files from a server, which is only reachable when you're on VPN
"""


def build_campaign():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as camp
    import emodpy_malaria.interventions.udbednet as udb

    # This isn't desirable. Need to think about right way to provide schema (once)
    camp.schema_path = manifest.schema_file

    # print( f"Telling emod-api to use {manifest.schema_file} as schema." )
    nodes = [1402941398, 1402941399, 1402941400, 1402941401, 1402941404, 1402941410, 1403072469, 1403072470, 1403072471,
             1403072472]
    camp.add(udb.UDBednet(camp, start_day=10, coverage=0.5, killing_eff=0.5, blocking_eff=0.5, node_ids=nodes))

    return camp


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # You have to set simulation type explicitly before you set other parameters for the simulation

    # sets "default" malaria parameters as determined by the malaria team
    config = vector_config.set_team_defaults(config, manifest)
    vector_config.add_species(config, manifest, ["funestus"])
    config.parameters.Enable_Migration_Heterogeneity = 0
    config.parameters.Enable_Vector_Species_Report = 1
    config.parameters.Custom_Individual_Events = ["Bednet_Got_New_One", "Bednet_Using", "Bednet_Discarded"]
    config.parameters.Enable_Spatial_Output = 1  # remove when emodpy-malaria #35 is closed
    config.parameters.Spatial_Output_Channels = [
        "Adult_Vectors", "New_Infections", "Infectious_Vectors"]

    config.parameters.Simulation_Duration = 80

    return config


def build_demographics():
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    # YOU NEED TO BE ON VPN (IDM internal network) to be able to access this server
    input_file = malaria_config.get_file_from_http(
        "http://ipadvweb02.linux.idm.ctr:8000/" + manifest.population_input_path)
    demographics = Demographics.from_pop_csv(input_file, site='burkina')

    migration_partial = partial(migration.from_demog_and_param_gravity,
                                gravity_params=[7.50395776e-06, 9.65648371e-01, 9.65648371e-01, -1.10305489e+00],
                                id_ref='burkina', migration_type=migration.Migration.REGIONAL)

    return demographics, migration_partial


def general_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores")

    experiment_name = "Migration and Spatial VECTOR_SIM example"

    # create EMODTask
    print("Creating EMODTask (from files)...")
    task = emod_task.EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_campaign,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_config_parameters,
        demog_builder=build_demographics
    )

    # need to add ReportHumanMigrationTracking.csv
    # need to add ReportEventRecorder.csv

    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment = Experiment.from_task(task=task, name=experiment_name)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        exit()

    print(f"Experiment {experiment.uid} succeeded.")

    # Save experiment id to file
    with open(manifest.experiment_id, "w") as fd:
        fd.write(experiment.uid.hex)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
