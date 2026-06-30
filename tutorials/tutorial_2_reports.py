"""
=== Tutorial 2 - Reports, downloading results, and plotting ===

EMOD can an InsetChart.json for any simulation. InsetChart is a handy
report because it gives you an overview of the simulation over time. It includes
human and vector populations, fraction of people infected, daily biting rate,
and many other statistics.

This tutorial adds two more reports, downloads the results using DownloadAnalyzer,
and then plots the output:
  - MalariaSummaryReport  age-stratified PfPR, clinical incidence, population
  - DemographicsSummary   population and vital dynamics over time
  - ReportVectorStats     vector population life-cycle data by species

New in this tutorial (diff from tutorial_1_intro.py):
  - build_reports()     adds MalariaSummaryReport and enables demographics reports
  - process_results()   downloads output files from each simulation using DownloadAnalyzer
  - plot_results()      plots InsetChart and DemographicsSummary from the downloaded files

=== INSTRUCTIONS ===
Select the correct platform in run_experiment() and update manifest.py if
using SLURM. See tutorial_1_intro.py for full platform details.
"""
import os
import pathlib

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from emodpy.emod_task import EMODTask

import manifest

sim_years = 3


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


def plot_results(output_path):
    """Plots InsetChart and DemographicsSummary from downloaded files."""
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart
    from emodpy_malaria.plotting.helpers import get_filenames

    plot_inset_chart(dir_name=output_path,
                     title="Tutorial 2 - InsetChart",
                     output=output_path)

    demog_files = get_filenames(dir_or_filename=output_path,
                                file_prefix="DemographicsSummary",
                                file_extension="json")
    if demog_files:
        plot_inset_chart(comparison1=demog_files[0],
                         title="Tutorial 2 - DemographicsSummary",
                         output=output_path)


def handle_results(experiment, platform):
    """Checks experiment status, downloads results, and generates plots."""
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)

        output_path = "tutorial_2_results"

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
        campaign_builder=None,
        demographics_builder=build_demographics,
        report_builder=build_reports
    )

    if platform.get_platform_type() == "COMPS":
        task.set_sif(manifest.comps_sif_path, platform)
    elif platform.get_platform_type() == "Slurm":
        task.set_sif(manifest.slurm_sif_path, platform)

    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, [0])

    experiment = Experiment.from_builder(builder, task, name="tutorial_2_reports")
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print("\nTutorial 2 is done.")

    return experiment


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
