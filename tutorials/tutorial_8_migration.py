"""
=== Tutorial 8 - Human and vector migration ===

In a spatial EMOD simulation, infections can only move between nodes if
infected people or mosquitoes physically move between them. A multi-node
simulation with no migration is effectively multiple independent simulations
that happen to run inside the same experiment. Migration connects the nodes.

This tutorial adds:
  - Human migration     gravity-model local migration with round trips
  - Vector migration    uniform migration rates between three nodes

The simulation has three nodes at different coordinates and population sizes.
Human migration rates are computed from a gravity model. Vector migration
uses explicit rates applied uniformly to all vectors.

For advanced migration features — age/gender-dependent rates, explicit human
rates, and genetics-based vector migration — see the how-to page:
  docs/emod/howto-migration-advanced.md

New in this tutorial (diff from tutorial_3_interventions.py):
  - build_demographics()  creates 3 nodes, adds human and vector migration
  - build_config()        adds a single vector species (gambiae)

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

sim_years = 5


def sweep_run_number(simulation, value):
    """Sets the random seed for a simulation."""
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def build_config(config):
    """Configures simulation with gambiae species."""
    import emodpy_malaria.malaria_config as malaria_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = sim_years * 365
    config.parameters.x_Base_Population = manifest.x_Base_Population_scale

    return config


def build_demographics():
    """Creates three nodes with gravity-model human migration and basic vector migration."""
    from emod_api.demographics.node import Node
    from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
    from emodpy_malaria.utils.distributions import UniformDistribution
    from emodpy_malaria.utils.emod_enum import BirthRateDependence
    from emodpy_malaria.migration import MigrationData, MigrationType, VectorMigrationData

    # --- Three nodes at different locations and population sizes ---
    nodes = [
        Node(lat=-2.0, lon=32.0, pop=5000, forced_id=1, name="Village_A"),
        Node(lat=-2.1, lon=32.2, pop=2000, forced_id=2, name="Village_B"),
        Node(lat=-2.3, lon=32.5, pop=500, forced_id=3, name="Village_C"),
    ]
    demog = MalariaDemographics(nodes=nodes, idref="tutorial_8")

    demog.set_birth_rate(40, birth_rate_dependence=BirthRateDependence.POPULATION_DEP_RATE)
    demog.set_age_distribution(UniformDistribution(0, 60))

    # ---------------------------------------------------------------
    # Human migration — gravity model with round trips
    # ---------------------------------------------------------------
    # rate = g0 * from_pop^g1 * to_pop^g2 * distance_km^g3
    gravity_params = [7.5e-06, 0.3, 0.6, -1.1]
    human_mig = MigrationData.from_gravity_model(demog, gravity_params)

    demog.add_migration(
        data=human_mig,
        migration_type=MigrationType.LOCAL,
        migration_pattern="SINGLE_ROUND_TRIPS",
        roundtrip_duration=3.0,
        roundtrip_probability=0.9,
        user_notes="Tutorial 8: gravity-model local migration"
    )

    # ---------------------------------------------------------------
    # Vector migration — uniform rates between all node pairs
    # ---------------------------------------------------------------
    vector_rates = {
        (1, 2): 0.01, (2, 1): 0.01,
        (1, 3): 0.005, (3, 1): 0.005,
        (2, 3): 0.008, (3, 2): 0.008,
    }
    vector_mig = VectorMigrationData.from_rates(rates=vector_rates)

    demog.add_vector_migration(
        data=vector_mig,
        species="gambiae",
        x_vector_migration=1.0,
        user_notes="Tutorial 8: basic vector migration"
    )

    return demog


def build_campaign(campaign):
    """Adds basic treatment-seeking at 50% coverage."""
    from emodpy_malaria.campaign.individual_intervention import AntimalarialDrug
    from emodpy_malaria.campaign.distributor import add_intervention_triggered
    from emodpy.campaign.common import TargetDemographicsConfig

    campaign.set_schema(manifest.schema_path)

    drug = AntimalarialDrug(campaign, drug_type="Artemether")
    add_intervention_triggered(
        campaign,
        intervention_list=[drug],
        triggers_list=["NewClinicalCase"],
        start_day=1,
        target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.5)
    )

    return campaign


def build_reports(reporters):
    """Adds InsetChart and MalariaSummaryReport."""
    from emodpy_malaria.reporters.reporters import InsetChart, MalariaSummaryReport
    from emodpy.reporters.base import ReportFilter

    reporters.add(InsetChart(reporters))

    reporters.add(MalariaSummaryReport(
        reporters,
        reporting_interval=30,
        age_bins=[0.25, 5, 115],
        max_number_reports=sim_years * 13,
        report_filter=ReportFilter(start_day=1, end_day=sim_years * 365,
                                   filename_suffix="monthly")
    ))

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
        "output/MalariaSummaryReport_monthly.json",
    ]
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

    manager = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager.add_item(experiment)
    manager.analyze()


def plot_results(output_path):
    """Plots InsetChart channels over time."""
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart

    plot_inset_chart(dir_name=output_path,
                     title="Tutorial 8 - Migration InsetChart",
                     output=output_path)


def handle_results(experiment, platform):
    """Checks experiment status, downloads results, and generates plots."""
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)

        output_path = "tutorial_8_results"
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
    builder.add_sweep_definition(sweep_run_number, [0])

    experiment = Experiment.from_builder(builder, task, name="tutorial_8_migration")
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print("\nTutorial 8 is done.")

    return experiment


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
