#!/usr/bin/env python3


# idmtools ...
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
from emodpy.bamboo import get_model_files

# importing all the reports functions, they all start with add_
from emodpy_malaria.reporters.builtin import *

import manifest

"""
    This is an example that shows how all the builtin custom reports are added to the simulations.
    Adding the reports creates custom_reports.json with the report parameters. 
    The reports need to be added after the emod_task.EMODTask is created as it needs to be passed
    to the reports so they can add themselves to the simulation. Please look in general_sim() for
    all the interesting bits. 

"""


def build_campaign():
    """
        Addind one intervention, so this template is easier to use when adding other interventions, replacing this one
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.ivermectin as ivermectin

    # passing in schema file to verify that everything is correct.
    campaign.set_schema(manifest.schema_file)
    # adding a scheduled ivermectin intervention
    ivermectin.add_scheduled_ivermectin(campaign=campaign, start_day=3)

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
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])
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
    global add_report_event_counter
    platform = Platform("Calculon", node_group="idm_48cores")

    experiment_name = "all reports example"

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
    
    """THIS IS WHERE WE ADD THE REPORTS"""
    add_event_recorder(task, event_list=["HappyBirthday", "Births"],
                       start_day=7, end_day=34, node_ids=[1], min_age_years=3,
                       max_age_years=21, must_have_ip_key_value="",
                       must_have_intervention="Ivermectin",
                       property_change_ip_to_record="")

    # ReportDrugStatus
    add_drug_status_report(task, manifest, start_day=5, end_day=43)

    # ReportHumanMigrationTracking
    add_human_migration_tracking(task, manifest)

    # ReportEventCounter
    add_report_event_counter(task, manifest, event_trigger_list=["HappyBirthday"])

    # MalariaImmunityReport
    add_malaria_immunity_report(task, manifest, end_day=10, reporting_interval=2, max_number_reports=2, node_ids=[],
                                age_bins=[24, 50, 115])

    # MalariaPatientJSONReport
    add_malaria_patient_json_report(task, manifest)

    # MalariaSummaryReport
    add_malaria_summary_report(task, manifest, start_day=56, end_day=66, reporting_interval=7,
                               age_bins=[3, 77, 115],
                               infectiousness_bins=[0.023, 0.1, 0.5], max_number_reports=3, parasitemia_bins=[12, 3423],
                               pretty_format=1)

    # ReportNodeDemographics
    add_report_node_demographics(task, manifest, age_bins=[5, 25, 100])

    # ReportVectorMigration
    add_report_vector_migration(task, manifest, start_day=56, end_day=64)

    # ReportVectorStats
    add_report_vector_stats(task, manifest, species_list=["arabiensis", "gambiae"], stratify_by_species=1)

    # ReportDrugStatus
    add_drug_status_report(task, manifest, start_day=25, end_day=37)

    # SpatialReportMalariaFiltered
    add_spatial_report_malaria_filtered(task, manifest)

    # VectorHabitatReport
    add_vector_habitat_report(task, manifest)

    # ReportIneterventionPopAvg
    add_report_intervention_pop_avg(task, manifest, start_day=70)

    # ReportNodeDemographicsMalaria
    add_report_node_demographics_malaria(task, manifest, age_bins=[3, 25, 50, 100])

    # MalariaSurveyJSONAnalyzer
    add_malaria_survey_analyzer(task, manifest, start_day=34, end_day=355, event_trigger_list=["HappyBirthday"],
                                max_number_reports=74,
                                reporting_interval=12,
                                node_ids=[1])

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
