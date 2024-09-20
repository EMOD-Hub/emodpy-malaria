#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files
from emodpy_malaria.vector_migration.vector_migration import from_demographics_and_gravity_params

import manifest


# ****************************************************************
# This is an example for Microsporidia-using sims.
# This shows how to set up microsporidia in vectors (with sweeps over the configuration parameters)
# The only way to introduce microsporidia is by the mosquito release intervention shown here
# Mircosporidia-related data can be found in ReportVectorStats which is also used
# The ReportVectorStats.csv is also converted to InsetChart-like time-step json so you can look at it in COMPS graphs
# using EP4/dtk_post_process.py
# ****************************************************************


def build_campaign(microsporidia=True):
    """
        The only way to introduce Microsporidia to the simulation is to release mosquitoes
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    campaign.set_schema(manifest.schema_file)
    from emodpy_malaria.interventions.mosquitorelease import add_scheduled_mosquito_release

    campaign.set_schema(manifest.schema_file)

    add_scheduled_mosquito_release(campaign, 50, released_number=1000, released_species="gambiae",
                                   released_microsporidia=True, released_genome=[['X', 'Y']])
    add_scheduled_mosquito_release(campaign, 50, released_number=1000, released_species="gambiae",
                                   released_microsporidia="Strain_B", released_genome=[['X', 'Y']])

    return campaign


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # You have to set simulation type explicitly before you set other parameters for the simulation
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "funestus"])
    config.parameters.Simulation_Duration = 100
    transmission_modification = {"Times": [0, 6], "Values": [1, 0.5]}
    malaria_config.add_microsporidia(config, manifest, species_name="gambiae",
                                     female_to_male_probability=0,
                                     male_to_female_probability=0, female_to_egg_probability=0,
                                     duration_to_disease_acquisition_modification=None,
                                     duration_to_disease_transmission_modification=transmission_modification,
                                     larval_growth_modifier=1,
                                     female_mortality_modifier=1, male_mortality_modifier=1)
    malaria_config.add_microsporidia(config, manifest, species_name="gambiae",
                                     strain_name="Strain_B",
                                     male_to_egg_probability=1,
                                     female_to_male_probability=0,
                                     male_to_female_probability=0, female_to_egg_probability=0,
                                     duration_to_disease_acquisition_modification=None,
                                     duration_to_disease_transmission_modification=transmission_modification,
                                     larval_growth_modifier=1,
                                     female_mortality_modifier=1, male_mortality_modifier=1)

    return config


def sweep_female_to_male_probability(simulation, value):
    simulation.task.config.parameters.Vector_Species_Params[
        0].Microsporidia[0].Female_To_Male_Transmission_Probability = value
    return {"female_to_male_probability": value}


def sweep_male_to_female_probability(simulation, value):
    simulation.task.config.parameters.Vector_Species_Params[
        0].Microsporidia[0].Male_To_Female_Transmission_Probability = value
    return {"male_to_female_probability": value}


def sweep_female_to_egg_probability(simulation, value):
    simulation.task.config.parameters.Vector_Species_Params[
        0].Microsporidia[0].Female_To_Egg_Transmission_Probability = value
    return {"female_to_egg_probability": value}


def sweep_male_to_egg_probability(simulation, value):
    simulation.task.config.parameters.Vector_Species_Params[
        0].Microsporidia[0].Male_To_Egg_Transmission_Probability = value
    return {"male_to_egg_probability": value}


def sweep_larval_growth_modifier(simulation, value):
    simulation.task.config.parametersVector_Species_Params[
        0].Microsporidia[0].Larval_Growth_Modifier = value
    return {"larval_growth_modifier": value}


def sweep_female_mortality_modifier(simulation, value):
    simulation.task.config.parameters.Vector_Species_Params[
        0].Microsporidia[0].Female_Mortality_Modifier = value
    return {"female_mortality_modifier": value}


def sweep_male_mortality_modifier(simulation, value):
    simulation.task.config.parameters.Vector_Species_Params[
        0].Microsporidia[0].Male_Mortality_Modifier = value
    return {"male_mortality_modifier": value}


def on_off_microsporidia(simulation, value):
    """
        This callback function updates the start day of the campaign.
        to use: Please un-comment builder.add_sweep_definition(update_campaign_start_day, etc)
    Args:
        simulation:
        value: value to which the start_day will be set

    Returns:
        tag that will be added to the simulation run
    """
    build_campaign_partial = partial(build_campaign, microsporidia=value)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"microsporidia": value}


def build_demographics():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog
    settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in
    emod-api as much as possible.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demographics = Demographics.from_params(tot_pop=10000, num_nodes=50, frac_rural=0.1)
    return demographics


def ep4_fn(task):
    task = emod_task.add_ep4_from_path(task, manifest.ep4_path)
    return task


def general_sim(selected_platform):
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """
    experiment_name = "Microsporidia_example"

    # create EMODTask
    print("Creating EMODTask (from files)...")
    task = emod_task.EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_campaign,
        schema_path=manifest.schema_file,
        ep4_custom_cb=ep4_fn,
        param_custom_cb=set_config_parameters,
        demog_builder=build_demographics
    )
    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    if selected_platform == "COMPS":
        platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")
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
        task.set_sif(manifest.SIF_PATH, platform)

    # set up sweeps
    builder = SimulationBuilder()

    builder.add_sweep_definition(on_off_microsporidia, [True, False])

    # builder.add_sweep_definition(sweep_male_to_egg_probability, [0, 0.5, 1])
    # builder.add_sweep_definition(sweep_female_to_male_probability, [0, 0.5, 1])
    # builder.add_sweep_definition(sweep_male_to_female_probability, [0,  0.5, 1])
    # builder.add_sweep_definition(sweep_larval_growth_modifier, [0, 0.5,  1,  5])
    # builder.add_sweep_definition(sweep_female_mortality_modifier, [0, 0.5, 1,  5])
    # builder.add_sweep_definition(sweep_male_mortality_modifier, [0, 0.5, 1, 5])

    # we need a demographics object to pass to
    demog = build_demographics()
    grav_parm = [1, 0.3, 0.01, -1.3]
    from_demographics_and_gravity_params(task, demographics_object=demog, gravity_params=grav_parm,
                                         migration_type="LOCAL_MIGRATION")

    from emodpy_malaria.reporters.builtin import add_report_vector_stats, add_report_microsporidia, add_report_vector_migration
    # ReportVectorStats
    add_report_vector_stats(task, manifest, species_list=["gambiae"], include_gestation=True,
                            include_microsporidia=True)
    add_report_vector_migration(task, manifest)

    # ReportMicrosporidia
    add_report_microsporidia(task, manifest)

    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    # experiment = Experiment.from_task(task=task, name=experiment_name)
    experiment = Experiment.from_builder(builder, task, name=experiment_name)
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
    selected_platform = "COMPS"
    general_sim(selected_platform)
