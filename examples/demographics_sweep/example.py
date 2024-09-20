#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files

import manifest

"""
    We create an intervention that sweeps over demographics parameters
"""


def build_campaign(start_day=1, coverage=1.0, killing_effect=0):
    """
    Adds a SpaceSpraying intervention, using parameters passed in
    Args:
        start_day: the day the intervention goes in effect
        coverage: portion of each node covered by the intervention
        killing_effect: portion of vectors killed by the intervention

    Returns:
        campaign object
    """
    # adds a SpaceSpraying intervention
    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.spacespraying as spray

    campaign.set_schema(manifest.schema_file)

    # adding SpaceSpraying from emodpy_malaria.interventions.spacespraying
    spray.add_scheduled_space_spraying(campaign, start_day=start_day, spray_coverage=coverage,
                                       killing_initial_effect=killing_effect, killing_box_duration=73)
    return campaign


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config.parameters.Simulation_Type = "MALARIA_SIM"
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    config.parameters.Simulation_Duration = 80

    return config


def build_demographics(birth_rate=0.0004, total_population=300, rural_fraction=0.21):
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    import emod_api.demographics.DemographicsTemplates as demogTemplates

    # creates a demographic file with 5k total people (randomly?) spread between 5 nodes
    demographics = Demographics.from_params(tot_pop=total_population, num_nodes=5,
                                            frac_rural=rural_fraction, id_ref="from_params")

    # update birth rate directly, this access the demographics class/object as if it's a json file
    # this only has the defaults and not the information for individual nodes yet
    demographics.raw['Defaults']['NodeAttributes'].update({"BirthRate": birth_rate})
    # demographics.AddIndividualPropertyAndHINT("Mood", ["Happy", "Sad"], [0.73, 0.27])

    return demographics


def update_demographics_multiple_params(simulation, values):
    """
        This callback function modifies several demographics parameters
    Args:
        simulation:
        values: an array of values with which you want to update the paramters

    Returns:
        tag that will be used with the simulation
    """
    build_demog_partial = partial(build_demographics, birth_rate=values[0], rural_fraction=values[1],
                                  total_population=values[2])
    simulation.task.create_demog_from_callback(build_demog_partial, from_sweep=True)
    return {"birth_rate": values[0], "rural_fraction": values[1], "total_population": values[2]}


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
    experiment_name = "Demographics Sweep example"
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

    # Create simulation sweep with builder
    # sweeping over start day AND killing effectiveness - this will be a cross product
    builder = SimulationBuilder()

    # this sweeps over one parameter, calling several of these one-parameter sweeps in
    # this script will cause only the last parameter to be swept, but there will be a cross-product-of-the-sweeps
    # number of simulations created.
    # comment out the builder below when using this
    # builder.add_sweep_definition(update_campaign_start_day, [23, 3, 84, 1])

    # this is how you sweep over a multiple-parameters space:
    # itertools product creates a an array with all the combinations of parameters (cross-product)
    # so, 2x3x2 = 12 simulations
    import itertools
    # "birth_rate": values[0], "rural_fraction": values[1],"total_population": values[2]
    builder.add_sweep_definition(update_demographics_multiple_params,
                                 list(itertools.product([0.000412, 0.000422], [0.95, 0.87, 0.58], [300, 512])))

    # create experiment from builder
    experiment = Experiment.from_builder(builder, task, name=experiment_name)

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
    print()
    print(experiment.uid.hex)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
