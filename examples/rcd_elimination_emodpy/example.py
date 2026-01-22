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

from emod_api.interventions.common import BroadcastEventToOtherNodes, BroadcastEvent
from emodpy_malaria.interventions.outbreak import add_outbreak_individual
from emodpy_malaria.interventions.drug_campaign import add_drug_campaign
from emodpy_malaria.interventions.treatment_seeking import add_treatment_seeking
from emodpy_malaria.interventions.community_health_worker import add_community_health_worker

import manifest


# ****************************************************************
# This is an example template with the most basic functions
# which create config and demographics from pre-set defaults
# and adds one intervention to campaign file. Runs the simulation
# and writes experiment id into experiment_id
#
# ****************************************************************


def build_campaign(u5_hs_rate=0.02, days_between_followups=7, max_distance_to_other_nodes_km=0,
                   followup_sweep_coverage=1., delivery_method="MTAT", rdt_thresh=40,
                   ip_restrictions=None, target="Everyone",
                   nodeIDs=None):
    """
        Creating empty campaign. For adding interventions please find intervention name in the examples
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign

    # passing in manifest
    campaign.set_schema(manifest.schema_file)
    o5_hs_rate = u5_hs_rate * 0.5

    def create_target_list(u5_hs_rate, o5_hs_rate):
        return [{'trigger': 'NewClinicalCase',
                 'coverage': u5_hs_rate,
                 'agemin': 0,
                 'agemax': 5,
                 'rate': 0.3},
                {'trigger': 'NewClinicalCase',
                 'coverage': o5_hs_rate,
                 'agemin': 5,
                 'agemax': 100,
                 'rate': 0.3},
                {'trigger': 'NewSevereCase',
                 'rate': 0.5},
                {'trigger': 'NewSevereCase',
                 'coverage': 0.8,
                 'agemin': 5},
                {'trigger': 'HappyBirthday'}
        ]

    add_treatment_seeking(campaign=campaign,
                          node_ids=nodeIDs,
                          start_day=1,
                          targets=create_target_list(u5_hs_rate, o5_hs_rate),
                          drug=['Artemether', 'Lumefantrine'],
                          broadcast_event_name="Received_Treatment")

    request_msat_config = BroadcastEventToOtherNodes(
        camp=campaign,
        Event_Trigger="Diagnostic_Survey_0",
        Include_My_Node=True,
        Node_Selection_Type="DISTANCE_ONLY",  # already default
        Max_Distance_To_Other_Nodes_Km=max_distance_to_other_nodes_km)

    add_community_health_worker(campaign=campaign,
                                initial_amount=1,
                                amount_in_shipment=1,
                                days_between_shipments=days_between_followups,
                                max_stock=1,
                                max_distributed_per_day=1,
                                intervention_config=request_msat_config,
                                trigger_condition_list=["Received_Treatment"],
                                waiting_period=0)

    # response - no need to break them up, they are both triggered events, with AL drug code, the diagnostic-related
    # parameters will be either used or ignored based on the campaign_type
    add_drug_campaign(campaign=campaign, campaign_type=delivery_method, coverage=followup_sweep_coverage,
                      diagnostic_threshold=0, start_days=[1], drug_code="AL", diagnostic_type="BLOOD_SMEAR_PARASITES",
                      measurement_sensitivity=1. / rdt_thresh, trigger_condition_list=['Diagnostic_Survey_0'],
                      listening_duration=-1,  # already default
                      ind_property_restrictions=ip_restrictions, target_group=target, node_ids=nodeIDs)

    # recurring outbreak as importation
    outbreak_fraction = 0.01
    repetitions = -1
    tsteps_btwn = 365
    target = 'Everyone'  # by default
    strain = (0, 0)
    add_outbreak_individual(campaign=campaign, demographic_coverage=outbreak_fraction, repetitions=repetitions,
                            timesteps_between_repetitions=tsteps_btwn,
                            antigen=strain[0], genome=strain[1], broadcast_event="InfectionDropped")

    return campaign


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # You have to set simulation type explicitly before you set other parameters for the simulation
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
    import emod_api.demographics.Demographics as Demographics  # OK to call into emod-api

    demographics = Demographics.from_params(300, 5)
    demographics.SetBirthRate(0.001)
    return demographics


def general_sim(selected_platform):
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    experiment_name = "rcd_elimination_emodpy"

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
        task.set_sif(manifest.sif_path_slurm, platform)

    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment = Experiment.from_task(task=task, name=experiment_name)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
        exit()

    print(f"Experiment {experiment.id} succeeded.")

    # Save experiment id to file
    with open("experiment_id", "w") as fd:
        fd.write(experiment.id)


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    selected_platform = "COMPS"
    general_sim(selected_platform)
