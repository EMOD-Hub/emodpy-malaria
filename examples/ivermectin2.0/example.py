#!/usr/bin/env python3
import json
import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
from emodpy.emod_task import EMODTask
from emodpy_malaria.campaign.individual_intervention import (OutbreakIndividual, ControlledVaccine, BroadcastEvent,
                                                             Ivermectin)
from emodpy_malaria.campaign.distributor import add_intervention_scheduled, add_intervention_triggered
from emodpy_malaria.campaign.common import TargetDemographicsConfig as TDC, TargetGender
from emodpy_malaria.campaign.waning_config import MapPiecewise, BoxExponential
from emodpy_malaria.utils.distributions import ConstantDistribution, UniformDistribution
from emodpy_malaria.reporters.reporters import ReportVectorStats

import manifest

schema_json = json.loads(open(manifest.schema_file).read())


# ****************************************************************
# This is an example template with the most basic functions
# which create config and demographics from pre-set defaults
# and adds one intervention to campaign file. Runs the simulation
# and writes experiment id into experiment_id
#
# ****************************************************************


def build_campaign(campaign, coverage=1.0):
    """
    """
    ob = OutbreakIndividual(campaign)
    add_intervention_scheduled(campaign, intervention_list=[ob],
                               start_day=2,
                               target_demographics_config=TDC(0.05))
    new_iv_signal = BroadcastEvent(campaign, broadcast_event="Ivermectin_Distribution_Event")
    new_iv = Ivermectin(campaign,
                        insecticide="Example",
                        killing_waning_config=BoxExponential(initial_effect=0.7, box_duration=2,
                                                             decay_time_constant=30))
    add_intervention_triggered(campaign, intervention_list=[new_iv, new_iv_signal],
                               triggers_list=['NewInfectionEvent'],
                               target_demographics_config=TDC(target_gender=TargetGender.ALL,
                                                              demographic_coverage=coverage),
                               delay_distribution=UniformDistribution(0, 5),
                               start_day=20)
    return campaign


def update_campaign(simulation, coverage, run_number):
    """
        This callback function updates the coverage of the campaign.
    Args:
        simulation:
        coverage: value to which the coverage will be set

    Returns:
        tag that will be added to the simulation run
    """
    build_campaign_partial = partial(build_campaign, coverage=coverage)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    simulation.task.config.parameters.Run_Number = run_number
    return {"coverage": coverage, "run_number": run_number}


def build_config(config):
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
    config = malaria_config.set_team_defaults(config, schema_json)
    malaria_config.add_species(config, schema_json, ["gambiae", "arabiensis", "funestus"])
    malaria_config.add_genes_and_alleles(config,
                                         schema_json,
                                         species="funestus",
                                         alleles=[("a0", 0.5), ("a1", 0.35), ("a2", 0.15)])
    malaria_config.add_genes_and_alleles(config,
                                         schema_json,
                                         species="funestus",
                                         alleles=[("b0", 0.90), ("b1", 0.1)])
    malaria_config.add_genes_and_alleles(config,
                                         schema_json,
                                         species="arabiensis",
                                         alleles=[("c0", 0.66), ("c1", 0.1), ("c2", 0.24)])
    malaria_config.add_genes_and_alleles(config, schema_json, "gambiae", [("a", 0.5), ("b", 0.5), ("c", 0)])
    malaria_config.add_insecticide_resistance(config, schema_json, insecticide_name="Example",
                                              allele_combo=[["a", "a"]],
                                              species="gambiae", blocking=0.2, killing=0.3, repelling=0)
    linear_spline_habitat = malaria_config.configure_linear_spline(schema_json, max_larval_capacity=234000000,
                                                                   capacity_distribution_number_of_years=1,
                                                                   capacity_distribution_over_time={
                                                                       "Times": [0, 30, 60, 91, 122, 152, 182, 213, 243,
                                                                                 274, 304, 334, 365],
                                                                       "Values": [3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8,
                                                                                  6.5, 2.6, 2.1, 3]
                                                                   }
                                                                   )
    malaria_config.set_species_param(config, "gambiae", "Habitats", linear_spline_habitat)

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

    demographics = Demographics.from_template_node(lat=0, lon=0, pop=100, name=1, forced_id=1)
    return demographics


def add_reports(reporters):
    """
    To organize our logic, we will create a method that configures the reports we want EMOD to produce.
    EMOD is already generating the default InsetChart.json (by setting
    `config.parameters.Enable_Default_Reporting = 1`). We will add two more reports so you can see how
    it is done and get everyone's favorite `ReportHIVByAgeAndGender`.
    """

    reporters.add(ReportVectorStats(reporters_object=reporters,
                                    species_list=["gambiae"],
                                    include_death_state=True))

    return reporters


def general_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")

    experiment_name = "Ivermectin_2.0_Example"
    task = EMODTask.from_defaults(eradication_path=manifest.eradication_path,
                                  campaign_builder=build_campaign,
                                  demographics_builder=build_demographics,
                                  schema_path=manifest.schema_file,
                                  config_builder=build_config,
                                  report_builder=add_reports)
    task.set_sif(str(manifest.sif_path), platform=platform)  # set_sif() expects a string

    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition(update_campaign, coverage=[1], run_number=list(range(1)))

    # create experiment from builder
    experiment = Experiment.from_builder(builder, task, name=experiment_name)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
    else:
        print(f"Experiment {experiment.id} succeeded.")
        # create output file that snakemake will check for to see if the example succeeded
        with open("COMPS_ID", "w") as fd:
            fd.write(experiment.id)

    assert experiment.succeeded


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
