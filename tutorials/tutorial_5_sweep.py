"""
=== Tutorial 5 - Parameter Sweeps ===

A parameter sweep runs the same scenario across a range of input values so you
can study how outcomes change with each parameter. This tutorial sweeps over
treatment-seeking coverage to show how different levels of case management
affect malaria burden in a seasonal setting.

SimulationBuilder manages the sweep. Adding two sweep definitions produces a
cross-product: every combination of treatment_coverage and Run_Number gets its own
simulation. With 3 coverage values and 3 random seeds that is 9 simulations.

New in this tutorial (diff from tutorial_4_seasonality.py):
  - build_campaign(campaign, treatment_coverage)
                              coverage is now a parameter, not a constant
  - update_campaign()         sweep callback that rebuilds the campaign per
                              simulation using functools.partial
  - two sweep definitions     treatment_coverage x Run_Number cross-product
  - Run_Number sweep widened  [0] -> [0, 1, 2] for stochastic variation

=== INSTRUCTIONS ===
Select the correct platform in run_experiment() and update manifest.py if
using SLURM. See tutorial_1_intro.py for full platform details.
"""
import os
import pathlib
from functools import partial

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from emodpy.campaign.common import RepetitionConfig
from emodpy.emod_task import EMODTask

import manifest

sim_years = 3


def sweep_run_number(simulation, value):
    """Sets the random seed for a simulation."""
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def update_campaign(simulation, treatment_coverage):
    """Sweep callback that rebuilds the campaign with a specific treatment coverage."""
    build_campaign_partial = partial(build_campaign, treatment_coverage=treatment_coverage)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"treatment_coverage": treatment_coverage}


def build_config(config):
    """Configures simulation with seasonal habitat for all species."""
    import emodpy_malaria.malaria_config as malaria_config
    from emodpy_malaria.utils.emod_enum import HabitatType

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = sim_years * 365

    seasonal_habitat = malaria_config.VectorHabitat(
        habitat_type=HabitatType.LINEAR_SPLINE,
        max_larval_capacity=1e8,
        capacity_distribution_number_of_years=1,
        capacity_distribution_over_time={
            "Times":  [0,   30,  60,   91,  122, 152, 182, 213,  243, 274, 304, 334, 365],
            "Values": [3.0, 0.8, 1.25, 0.1, 2.7, 8.0, 4.0, 25.0, 6.8, 6.5, 2.6, 2.1, 3.0]
        }
    )

    for species in ["gambiae", "arabiensis", "funestus"]:
        malaria_config.set_species_param(config, species, "Habitats",
                                         seasonal_habitat, overwrite=True)

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


def build_campaign(campaign, treatment_coverage=0.8):
    """Adds treatment-seeking at swept coverage and ITNs at fixed 50% coverage."""
    from emodpy_malaria.campaign.individual_intervention import (
        AntimalarialDrug, SimpleBednet
    )
    from emodpy_malaria.campaign.distributor import (
        add_intervention_scheduled, add_intervention_triggered
    )
    import emodpy_malaria.campaign.waning_config as waning
    from emodpy_malaria.campaign.common import TargetDemographicsConfig

    campaign.set_schema(manifest.schema_path)

    # Treatment seeking: clinical cases at swept coverage
    clinical_drug = AntimalarialDrug(campaign, drug_type="Artemether")
    add_intervention_triggered(
        campaign,
        intervention_list=[clinical_drug],
        triggers_list=["NewClinicalCase"],
        start_day=60,
        target_demographics_config=TargetDemographicsConfig(demographic_coverage=treatment_coverage)
    )

    # Treatment seeking: severe cases at coverage + 0.2, capped at 1.0
    severe_drug = [AntimalarialDrug(campaign, drug_type="Chloroquine"),
                   AntimalarialDrug(campaign, drug_type="Lumefantrine")]
    add_intervention_triggered(
        campaign,
        intervention_list=severe_drug,
        triggers_list=["NewSevereCase"],
        start_day=40,
        target_demographics_config=TargetDemographicsConfig(
            demographic_coverage=min(treatment_coverage + 0.2, 1.0),
            target_age_max=40)
    )

    # ITN distribution: fixed at 50%
    bednet = SimpleBednet(
        campaign,
        repelling_config=waning.Exponential(initial_effect=0.3, decay_time_constant=400),
        blocking_config=waning.Exponential(initial_effect=0.9, decay_time_constant=200),
        killing_config=waning.Exponential(initial_effect=0.1, decay_time_constant=300),
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
                                                     InsetChart, ReportVectorStats)
    from emodpy.reporters.base import ReportFilter

    reporters.add(MalariaSummaryReport(
        reporters,
        reporting_interval=30,
        age_bins=[0.25, 5, 115],
        max_number_reports=sim_years * 13,
        pretty_format=True,
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


def group_by_coverage(experiment, output_path):
    """Reorganizes downloaded results into subdirectories by treatment coverage."""
    import shutil
    coverage_dirs = {}
    for sim in experiment.simulations:
        coverage = sim.tags.get("treatment_coverage")
        if coverage is None:
            continue
        sim_dir = os.path.join(output_path, str(sim.id))
        if not os.path.exists(sim_dir):
            continue
        label = f"treatment_coverage_{coverage}"
        target_dir = os.path.join(output_path, label)
        os.makedirs(target_dir, exist_ok=True)
        shutil.move(sim_dir, os.path.join(target_dir, str(sim.id)))
        coverage_dirs[float(coverage)] = target_dir
    return [coverage_dirs[k] for k in sorted(coverage_dirs)]


def plot_results(output_path, dirs):
    """Plots mean InsetChart comparison across three coverage levels."""
    from emodpy_malaria.plotting.plot_inset_chart_mean_compare import plot_mean

    plot_mean(dir1=dirs[0],
              dir2=dirs[1],
              dir3=dirs[2],
              title="Tutorial 5 - InsetChart",
              show_raw_data=True,
              output=output_path)


def handle_results(experiment, platform):
    """Checks experiment status, downloads and groups results, and generates plots."""
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)

        output_path = "tutorial_5_results"

        process_results(experiment, platform, output_path)
        print(f"Downloaded results for experiment {experiment.id}.")

        dirs = group_by_coverage(experiment, output_path)
        plot_results(output_path, dirs)
        print(f"\nLook in '{output_path}' for the plots.")
    else:
        print(f"Experiment {experiment.id} failed.")


def run_experiment():
    """Sets up the platform with a coverage x Run_Number sweep, then runs it."""
    # ============================================================
    # UPDATE - Select the correct platform for your environment
    # ============================================================
    platform = Platform("Container", job_directory=manifest.job_dir,
                        docker_image=manifest.plat_image,
                        max_job=4)

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
    builder.add_sweep_definition(update_campaign, [0.3, 0.6, 0.9])
    builder.add_sweep_definition(sweep_run_number, [0, 1, 2])

    experiment = Experiment.from_builder(builder, task, name="tutorial_5_sweep")
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print("\nTutorial 5 is done.")

    return experiment


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
