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


def build_demographics(birth_rate=0.004, total_population=300, rural_fraction=0.21):
    """
        Creates a demographics object that will be written to a demographics file to
        be used by the simulation.
    Args:
        birth_rate: Birth rate for all the nodes
        total_population: total population for all the nodes
        rural_fraction: fraction of the population that will live in all the nodes
            but the first (see below)

    Returns:
        Configured demographics object
    """

    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    import emod_api.demographics.DemographicsTemplates as demogTemplates

    #     Creates nodes with following logic: First node is the urban node, which contains
    #     tot_pop * (1-frac_rural) of the population, the rest of the nodes splip the left-over
    #     population with less and less people in each node.
    demographics = Demographics.from_params(tot_pop=total_population, num_nodes=5,
                                            frac_rural=rural_fraction, id_ref="from_params")

    demographics.raw['Defaults']['NodeAttributes'].update({
        "BirthRate": birth_rate})

    return demographics


def update_demographics_multiple_params(simulation, birth_rate, rural_fraction, total_population):
    """
        This callback function modifies several demographics parameters
    Args:
        simulation: simulation object that will be created in comps
        birth_rate: birth rate parameter which will be modified in the sweep
        rural_fraction: rural fraction parameter which will be modified in the sweep
        total_population: total population distributed between the nodes

    Returns:
        tag that will be used with the simulation
    """
    build_demog_partial = partial(build_demographics, birth_rate=birth_rate, rural_fraction=rural_fraction,
                                  total_population=total_population)
    simulation.task.create_demog_from_callback(build_demog_partial, from_sweep=True)
    return dict(birth_rate=birth_rate, rural_fraction=rural_fraction, total_population=total_population)


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
    
    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)
    
    # Create simulation sweep with builder
    # sweeping over start day AND killing effectiveness - this will be a cross product
    builder = SimulationBuilder()

    # this will sweep over the entire parameter space in a cross-product fashion
    # you will get 2x3x2 simulations
    builder.add_multiple_parameter_sweep_definition(
        update_demographics_multiple_params,
        dict(
            birth_rate=[0.000412, 0.000422],
            total_population=[1000, 700, 200],
            rural_fraction=[0.3, 0.5]
        )
    )
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
