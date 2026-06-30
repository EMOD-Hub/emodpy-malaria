"""
=== Tutorial 3 - Interventions ===

This tutorial adds two interventions that represent a standard malaria control
package:
  - Treatment           case management: people seek and receive antimalarial
                        treatment when they develop clinical symptoms
  - ITN distribution    insecticide-treated nets distributed annually to half
                        the population

Adding interventions requires a build_campaign(campaign) function that constructs the
campaign file. EMODTask accepts this via campaign_builder= (previously None).

The new class-based API uses:
  - AntimalarialDrug for treatment, distributed via
    add_intervention_triggered() on "NewClinicalCase" / "NewSevereCase"
  - SimpleBednet for ITNs, distributed via add_intervention_scheduled()

New in this tutorial (diff from tutorial_2_reports.py):
  - build_campaign(campaign)   builds the campaign with treatment and ITN
  - campaign_builder           changed from None to build_campaign

Toggle deploy_treatment and deploy_itn at the top of this file to run with
each intervention separately, then with both together.

=== INSTRUCTIONS ===
Select the correct platform in run_experiment() and update manifest.py if
using SLURM. See tutorial_1_intro.py for full platform details.
"""
import os
import pathlib

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

from emodpy.campaign.common import TargetDemographicsConfig, RepetitionConfig
from emodpy.emod_task import EMODTask

import manifest
from emodpy_malaria.reporters.reporters import InsetChart

sim_years = 3

deploy_treatment = True
deploy_itn = True


def get_run_suffix():
    """Returns a suffix string based on which interventions are enabled."""
    if deploy_treatment and deploy_itn:
        return "_both"
    if deploy_treatment:
        return "_ts"
    if deploy_itn:
        return "_itn"
    return "_no_interventions"


def sweep_run_number(simulation, value):
    """Sets the random seed for a simulation."""
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def build_config(config):
    """Configures simulation parameters with team defaults and three vector species."""
    import emodpy_malaria.malaria_config as malaria_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = sim_years * 365
    config.parameters.x_Base_Population = manifest.x_Base_Population_scale

    return config


def build_demographics():
    """Creates a single-node population with birth rate and age distribution."""
    from emodpy_malaria.demographics import MalariaDemographics as Demographics
    from emodpy_malaria.utils.distributions import UniformDistribution
    from emodpy_malaria.utils.emod_enum import BirthRateDependence

    demog = Demographics.from_template_node(lat=-3.2, lon=37.9, pop=1000,
                                            name="Tutorial_Site")
    demog.set_birth_rate(40, birth_rate_dependence=BirthRateDependence.POPULATION_DEP_RATE)
    demog.set_age_distribution(UniformDistribution(0, 60))
    demog.set_prevalence_distribution(UniformDistribution(0, 0.2))
    return demog


def build_campaign(campaign):
    """Adds treatment (clinical and severe) and ITN interventions."""
    from emodpy_malaria.campaign.individual_intervention import (
        AntimalarialDrug, SimpleBednet
    )
    from emodpy_malaria.campaign.distributor import (
        add_intervention_scheduled, add_intervention_triggered
    )
    import emodpy_malaria.campaign.waning_config as waning

    campaign.set_schema(manifest.schema_path)

    if deploy_treatment:
        # Clinical case management: treat with artemether
        # NewClinicalCase at 70% coverage
        clinical_drug = AntimalarialDrug(campaign, drug_type="Artemether")
        add_intervention_triggered(
            campaign,
            intervention_list=[clinical_drug],
            triggers_list=["NewClinicalCase"],
            start_day=60,
            target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.7)
        )

        # Severe case management at 90% coverage for those 40 years and younger
        severe_drug = [AntimalarialDrug(campaign, drug_type="Chloroquine"),
                       AntimalarialDrug(campaign, drug_type="Lumefantrine")]
        add_intervention_triggered(
            campaign,
            intervention_list=severe_drug,
            triggers_list=["NewSevereCase"],
            start_day=40,
            target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.9, target_age_max=40)
        )

    if deploy_itn:
        # ITN distribution: 50% coverage, single distribution on day 365.

        bednet = SimpleBednet(
            campaign,
            repelling_config=waning.Exponential(initial_effect=0.3, decay_time_constant=400),
            blocking_config=waning.Exponential(initial_effect=0.9,  decay_time_constant=200),
            killing_config=waning.Exponential(initial_effect=0.1,  decay_time_constant=300),
        )

        add_intervention_scheduled(
            campaign,
            intervention_list=[bednet],
            start_day=5,
            repetition_config=RepetitionConfig(infinite_repetitions=True, timesteps_between_repetitions=361),
            target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.5)
        )

    return campaign


def build_reports(reporters):
    """Adds MalariaSummaryReport, InsetChart, DemographicsReport, and ReportVectorStats."""
    from emodpy_malaria.reporters.reporters import (MalariaSummaryReport, DemographicsReport,
                                                     ReportVectorStats)
    from emodpy.reporters.base import ReportFilter

    reporters.add(MalariaSummaryReport(
        reporters,
        reporting_interval=30,
        age_bins=[0.25, 5, 115],
        max_number_reports=sim_years * 13,
        report_filter=ReportFilter(start_day=1, end_day=sim_years * 365, filename_suffix="monthly")
    ))
    reporters.add(InsetChart(reporters))
    reporters.add(DemographicsReport(reporters))
    reporters.add(ReportVectorStats(reporters, species_list=["gambiae", "arabiensis", "funestus"],
                                    stratify_by_species=True))

    return reporters


def process_results(experiment, platform, output_path):
    """Downloads report output files from completed simulations."""
    import shutil
    from idmtools.analysis.analyze_manager import AnalyzeManager
    from idmtools.analysis.download_analyzer import DownloadAnalyzer

    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    filenames = [
        "output/InsetChart.json",
        "output/DemographicsSummary.json",
        "output/MalariaSummaryReport_monthly.json",
        "output/ReportVectorStats.csv"
    ]
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

    manager = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager.add_item(experiment)
    manager.analyze()


def plot_results(output_path):
    """Plots InsetChart and DemographicsSummary, using tutorial 2 as reference."""
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart
    from emodpy_malaria.plotting.helpers import get_filenames

    reference = None
    t2_path = "tutorial_2_results"
    if os.path.exists(t2_path):
        t2_files = get_filenames(dir_or_filename=t2_path,
                                 file_prefix="InsetChart",
                                 file_extension="json")
        if t2_files:
            reference = t2_files[0]

    plot_inset_chart(dir_name=output_path,
                     reference=reference,
                     title="Tutorial 3 - InsetChart",
                     output=output_path)

    demog_files = get_filenames(dir_or_filename=output_path,
                                file_prefix="DemographicsSummary",
                                file_extension="json")
    if demog_files:
        plot_inset_chart(comparison1=demog_files[0],
                         title="Tutorial 3 - DemographicsSummary",
                         output=output_path)


def handle_results(experiment, platform, suffix):
    """Checks experiment status, downloads results, and generates plots."""
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)

        output_path = f"tutorial_3_results{suffix}"

        process_results(experiment, platform, output_path)
        print(f"Downloaded results for experiment {experiment.id}.")

        plot_results(output_path)
        print(f"\nLook in '{output_path}' for the plots.")
    else:
        print(f"Experiment {experiment.id} failed.")


def run_experiment():
    """Sets up the platform, task, and experiment, then runs it."""
    # ============================================================
    # UPDATE - Select the correct platform for your environment
    # ============================================================
    # sym_link=False: idmtools defaults to symlinks, but Windows requires Developer Mode
    # to create them. Using file copies instead works on all Windows configurations.
    platform = Platform("Container", job_directory=manifest.job_dir,
                        docker_image=manifest.plat_image,
                        sym_link=False, max_job=4)

    # platform = Platform("Calculon", node_group="idm_48cores", priority="Normal")

    # platform = Platform("SLURM_LOCAL",
    #                     job_directory=manifest.job_dir,
    #                     time="02:00:00",
    #                     partition="cpu_short",
    #                     mail_user="you@example.org",   # UPDATE
    #                     mail_type="ALL",
    #                     max_running_jobs=1000000,
    #                     array_batch_size=1000000)

    task = EMODTask.from_defaults(
        eradication_path=manifest.eradication_path,
        schema_path=manifest.schema_path,
        config_builder=build_config,
        campaign_builder=build_campaign,
        demographics_builder=build_demographics,
        report_builder=build_reports
    )

    if platform.get_platform_type() == "COMPS":
        task.set_sif(manifest.comps_sif_path, platform)
    elif platform.get_platform_type() == "Slurm":
        task.set_sif(manifest.slurm_sif_path, platform)

    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, [0])

    suffix = get_run_suffix()
    exp_name = f"tutorial_3_interventions{suffix}"
    experiment = Experiment.from_builder(builder, task, name=exp_name)
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform, suffix)

    print("\nTutorial 3 is done.")

    return experiment


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
