#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

import pandas as pd

# idmtools ...
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files

import manifest


# ****************************************************************
# This is an example template with the most basic functions
# which create config and demographics from pre-set defaults
# and adds one intervention to campaign file. Runs the simulation
# and writes experiment id into experiment_id
#
# ****************************************************************


def build_campaign():
    """
       Adding ScaleLarvalHabitat intervention using various dataframe formats that are supported
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    from emodpy_malaria.interventions.scale_larval_habitats import add_scale_larval_habitats

    # passing in schema file to verify that everything is correct.
    campaign.schema_path = manifest.schema_file
    # # Scale TEMPORARY_RAINFALL by 3 - fold for all nodes, all species:
    # df = pd.DataFrame({'TEMPORARY_RAINFALL': [3]})
    # add_scale_larval_habitats(campaign, df=df, start_day=1)
    #
    # # Scale TEMPORARY_RAINFALL by 3 - fold for all nodes, arabiensis only:
    # df = pd.DataFrame({'TEMPORARY_RAINFALL.arabiensis': [3]})
    # add_scale_larval_habitats(campaign, df=df, start_day=2)

    # Scale differently by node ID::
    df = pd.DataFrame({'NodeID':                   [1, 2, 3, 4, 5],
                       'CONSTANT':                 [1, 0, 1, 1, 1],
                       'TEMPORARY_RAINFALL':       [1, 1, 0, 1, 0]
                       })
    # add_scale_larval_habitats(campaign, df=df, start_day=3)

    # Scale differently by both node ID and species:
    df = pd.DataFrame({'NodeID':                        [1, 2, 3, 4, 5],
                       'CONSTANT.arabiensis':           [1, 0, 1, 1, 1],
                       'TEMPORARY_RAINFALL.arabiensis': [1, 1, 0, 1, 0],
                       'CONSTANT.funestus':             [1, 0, 1, 1, 1]
                       })
    # add_scale_larval_habitats(campaign, df=df, start_day=4)

    # Scale some habitats by species and others same for all species:
    df = pd.DataFrame({'NodeID':                        [1, 2, 3, 4, 5],
                       'CONSTANT.arabiensis':           [1, 0, 1, 1, 1],
                       'TEMPORARY_RAINFALL.arabiensis': [1, 1, 0, 1, 0],
                       'CONSTANT.funestus':             [1, 0, 1, 1, 1],
                       'WATER_VEGETATION':              [1, 1, 0, 1, 0]
                       })
    add_scale_larval_habitats(campaign, df=df, start_day=5)

    # Scale nodes at different dates, start_day is ignored with this configuration:
    df = pd.DataFrame({'NodeID':             [1, 2, 3, 4, 5],
                       'CONSTANT':           [1, 0, 1, 1, 1],
                       'TEMPORARY_RAINFALL': [1, 1, 0, 1, 0],
                       'Start_Day':          [0, 30, 60, 65, 65]
                       })
    # add_scale_larval_habitats(campaign, df=df, start_day=6)

    return campaign


def set_config_parameters(config):
    """
        This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    Args:
        config:

    Returns:
        configuration settings
    """

    # You have to set simulation type explicitly before you set other parameters for the simulation
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])
    config.parameters.Simulation_Duration = 1
    import json
    with open('config_json.json', 'w') as f:
        json.dump(config.parameters, f)

    return config


def build_demographics():
    """
        Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog
    settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in
    emod-api as much as possible.
    Returns:
        demographics.. object???
    """

    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demographics = Demographics.from_params(23841, 5)

    return demographics


def general_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    platform = Platform("SLURMStage")  # to run on comps2.idmod.org for testing/dev work
    # platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")

    experiment_name = "ScaleLarvalHabitat_Example"

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
    with open("experiment_id", "w") as fd:
        fd.write(experiment.uid.hex)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
