import pathlib

from emod_api.utils.distributions.exponential_distribution import ExponentialDistribution
from emod_api.utils.distributions.uniform_distribution import UniformDistribution
from emodpy.reporters.common import DemographicsReport
from emodpy_malaria.campaign.intervention_systems import CampaignType
from emodpy_malaria.utils.emod_enum import DiagnosticType, NonAdherenceOption
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from emodpy.emod_task import EMODTask as emod_task

import manifest

"""
    In this example we are adding a couple of drug campaigns - a scheduled and a triggered one

"""


def build_campaign(campaign):
    """
        Adding various test and treat drug campaigns
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    import emodpy_malaria.campaign.intervention_systems as isystems
    import emodpy_malaria.campaign.individual_intervention as ind_interventions
    import emodpy_malaria.campaign.common as campaign_common
    import emodpy_malaria.campaign.distributor as distribute
    import emodpy_malaria.campaign.waning_config as waning

    # must do this at the beginning of the campaign builder function to set the schema path for the
    # campaign object, this
    campaign.set_schema(manifest.schema_file)

    # create an outbreak intervention scheduled for day 10, with 21% coverage of the population to initiate disease dynamics
    distribute.add_intervention_scheduled(campaign,
                                          intervention_list=[ind_interventions.OutbreakIndividual(campaign)],
                                          start_day=10,
                                          target_demographics_config=campaign_common.TargetDemographicsConfig(demographic_coverage=0.21))
    campaign_type = CampaignType.MDA
    isystems.add_drug_campaign(campaign=campaign, campaign_type=campaign_type, drug="DHA_PQ", start_days=[60],
                                    receiving_drugs_event_name=f"{campaign_type}_EVENT", target_demographics_config=campaign_common.TargetDemographicsConfig(demographic_coverage=0.14, target_age_max=15))
    campaign_type = CampaignType.MSAT
    isystems.add_drug_campaign(campaign=campaign, campaign_type=campaign_type, drug="SPP", start_days=[100],
                                    target_demographics_config=campaign_common.TargetDemographicsConfig(demographic_coverage=0.35), duration=60,
                                    trigger_condition_list=["HappyBirthday"], treatment_delay=isystems.ExponentialDistribution(mean=2),
                                    receiving_drugs_event_name=f"{campaign_type}_EVENT", diagnostic_type=DiagnosticType.BLOOD_SMEAR_PARASITES, diagnostic_threshold=1)

    adherent_drug = ind_interventions.AdherentDrug(campaign, doses=[["Sulfadoxine", "Pyrimethamine", 'Amodiaquine'],
                                            ['Amodiaquine'],
                                            ['Amodiaquine'],
                                            ["Pyrimethamine"]],
                                     dose_interval=1,
                                     non_adherence_options=[NonAdherenceOption.NEXT_DOSAGE_TIME, NonAdherenceOption.STOP],
                                     non_adherence_distribution=[0.6, 0.4],
                                                   adherence_config=waning.Constant(0.95)
                                     )
    # give everyone adherent_drug
    isystems.add_drug_campaign(campaign=campaign, campaign_type="MTAT", drug=[adherent_drug], trigger_condition_list=["HappyBirthday"],
                               start_days=[150],
                               target_demographics_config=campaign_common.TargetDemographicsConfig(demographic_coverage=0.56),
                               receiving_drugs_event_name="AdherentDrug_EVENT", diagnostic_type=DiagnosticType.PCR_GAMETOCYTES,
                               diagnostic_threshold=3,
                               drug_ineligibility_duration=7)

    return campaign


def build_config(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["arabiensis"])
    config.parameters.Simulation_Duration = 200

    return config


def build_demographics():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog
    settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in
    emod-api as much as possible.

    """
    from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
    from emodpy_malaria.utils.distributions import UniformDistribution
    from emodpy_malaria.utils.emod_enum import BirthRateDependence

    demographics = MalariaDemographics.from_template_node(pop=1000)
    demographics.add_individual_property(property="DrugStatus", values=["None", "RecentDrug"], initial_distribution=[1, 0])
    demographics.set_age_distribution(UniformDistribution(0, 50))
    demographics.set_birth_rate(12, birth_rate_dependence=BirthRateDependence.POPULATION_DEP_RATE)


    return demographics

def add_reports(reporters):
    from emodpy_malaria.reporters.reporters import ReportEventCounter, ReportDrugStatus, ReportInfectionStatsMalaria
    reporters.add(ReportEventCounter(reporters, event_list=["HappyBirthday", "MDA_EVENT",
                                                                            "MSAT_EVENT", "AdherentDrug_EVENT"]))
    reporters.add(ReportDrugStatus(reporters))
    reporters.add(ReportInfectionStatsMalaria(reporters, reporting_interval=10))
    reporters.add(DemographicsReport(reporters))

    return reporters



def run_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    # sym_link=False: idmtools defaults to symlinks, but Windows requires Developer Mode
    # to create them. Using file copies instead works on all Windows configurations.
    platform = Platform(manifest.plat_name, job_directory=manifest.job_dir, docker_image=manifest.plat_image, sym_link=manifest.sym_link)

    experiment_name = "Drug Campaigns example"

    # create EMODTask
    print("Creating EMODTask (from files)...")
    task = emod_task.from_defaults(eradication_path=manifest.eradication_path,
                                   schema_path=manifest.schema_file,
                                   config_builder=build_config,
                                   campaign_builder=build_campaign,
                                   demographics_builder=build_demographics,
                                   report_builder=add_reports)

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
    run_sim()
