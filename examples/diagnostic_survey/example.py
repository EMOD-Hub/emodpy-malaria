#!/usr/bin/env python3

# idmtools ...
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files

import manifest

"""
    This is an example the creates a diagnostic survey intervention, triggered and scheduled, 
    and broadcasts events on positive and negative results. 
    Adding ReportEventCounter so you can see the events.

"""


def build_campaign():
    """
        Creating two interventions, one scheduled, one triggered.
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.diag_survey as diagnostic_survey
    import emod_api.interventions.common  # this is where BroadcastEvent comes from

    # adding schema file, so it can be looked up when creating the campaigns
    campaign.set_schema(manifest.schema_file)

    # creating events to broadcast with positive and negative results
    fever_detected = emod_api.interventions.common.BroadcastEvent(campaign, Event_Trigger="FEVER")
    no_fever = emod_api.interventions.common.BroadcastEvent(campaign, Event_Trigger="NO_FEVER")
    broadcast_ivermectin = emod_api.interventions.common.BroadcastEvent(campaign, Event_Trigger="Ivermectin")
    all_good = emod_api.interventions.common.BroadcastEvent(campaign, Event_Trigger="All_Good")

    # diagnostic survey scheduled for every 7 days, for 10 runs, checks on 89% of population if they have fever
    # sends out a "FEVER" event which can be used as a trigger for another intervention
    diagnostic_survey.add_diagnostic_survey(campaign=campaign, start_day=13, diagnostic_type="FEVER",
                                            diagnostic_threshold=37,
                                            repetitions=10, tsteps_btwn_repetitions=7, coverage=0.89, event_name="Test",
                                            positive_diagnosis_configs=[fever_detected],
                                            negative_diagnosis_configs=[no_fever])

    # diagnostic survey that is triggered on the person when it is their birthday,
    # it is checking for TRUE_PARASITE_DENSITY with a threshold of 20
    # send out "Ivermectin" event which can be used as a trigger for another intervention
    diagnostic_survey.add_diagnostic_survey(campaign=campaign, start_day=9, diagnostic_type="TRUE_PARASITE_DENSITY",
                                            diagnostic_threshold=20,
                                            trigger_condition_list=["HappyBirthday"],
                                            positive_diagnosis_configs=[broadcast_ivermectin],
                                            negative_diagnosis_configs=[all_good])

    return campaign


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # You have to set simulation type explicitly before you set other parameters for the simulation
    config.parameters.Simulation_Type = "MALARIA_SIM"
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    config.parameters.Simulation_Duration = 80

    return config


def build_demographics():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog
    settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in
    emod-api as much as possible.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demographics = Demographics.from_template_node(lat=0, lon=0, pop=10000, name=1, forced_id=1)
    return demographics


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

    experiment_name = "Diagnostic Survey Example"

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

    # Adding ReportEventCounter so you can see the events.
    from emodpy_malaria.reporters.builtin import ReportEventCounter

    def fmr_config_builder(params):
        params.Event_Trigger_List = ["HappyBirthday", "FEVER", "Ivermectin", "NO_FEVER", "All_Good", "Received_Test",
                                     "TestedPositive", "TestedNegative"]
        return params

    report = ReportEventCounter()
    report.config(fmr_config_builder, manifest)
    task.reporters.add_reporter(report)

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
