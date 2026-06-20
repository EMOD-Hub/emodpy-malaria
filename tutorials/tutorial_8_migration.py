"""
=== Tutorial 8 - Human and vector migration ===

This tutorial adds spatial movement to a multi-node simulation:
  - Human migration     gravity-model local migration with round trips,
                        plus age- and gender-dependent regional migration
  - Vector migration    genetics-based migration (different rates per allele
                        combination, e.g. wild-type vs gene-drive mosquitoes)

The simulation has three nodes at different coordinates and population sizes.
Human migration rates are computed from a gravity model (local) and from
explicit rates with age/gender modifiers (regional). Vector migration rates
are defined per allele combination so that vectors carrying the drive allele
migrate faster than wild-type.

New in this tutorial (diff from tutorial_3_interventions.py):
  - build_demographics()  creates 3 nodes, adds human and vector migration
  - build_config()        adds gene alleles for the drive locus
  - build_reports()       adds ReportVectorMigration with genome data

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
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def build_config(config):
    import emodpy_malaria.malaria_config as malaria_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    # Add a gene locus with wild-type (a0) and drive (a1) alleles.
    # The drive allele starts at 5% frequency.
    malaria_config.add_genes_and_alleles(
        config, manifest,
        species="gambiae",
        alleles=[("a0", 0.95), ("a1", 0.05)]
    )

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = sim_years * 365
    config.parameters.x_Base_Population = manifest.x_Base_Population_scale

    return config


def build_demographics():
    from emod_api.demographics.node import Node
    from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
    from emodpy_malaria.utils.distributions import ExponentialDistribution
    from emodpy_malaria.migration import MigrationData, MigrationType, VectorMigrationData

    # --- Three nodes at different locations and population sizes ---
    nodes = [
        Node(lat=-2.0, lon=32.0, pop=5000, forced_id=1, name="Village_A"),
        Node(lat=-2.1, lon=32.2, pop=2000, forced_id=2, name="Village_B"),
        Node(lat=-2.3, lon=32.5, pop=500, forced_id=3, name="Village_C"),
    ]
    demog = MalariaDemographics(nodes=nodes, idref="tutorial_8")

    demog.set_birth_rate(40)
    demog.set_age_distribution(ExponentialDistribution(7300))

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
    # Human migration — age- and gender-dependent (regional)
    # ---------------------------------------------------------------
    # Method 1: apply_modifier — start from gravity rates, then scale
    # by age and gender via a callback function.
    regional_base = MigrationData.from_gravity_model(demog, [2e-06, 0.4, 0.5, -0.8])

    def age_gender_modifier(base_rate, age, gender):
        MALE = 0
        if age < 15:
            return base_rate * 0.2
        elif age < 65:
            if gender == MALE:
                return base_rate * 1.5
            return base_rate
        else:
            return base_rate * 0.3

    regional_mig = regional_base.apply_modifier(
        ages=[0, 15, 65],
        modifier_fn=age_gender_modifier
    )

    demog.add_migration(
        data=regional_mig,
        migration_type=MigrationType.REGIONAL,
        user_notes="Tutorial 8: age/gender regional migration"
    )

    # ---------------------------------------------------------------
    # Vector migration by allele combination
    # ---------------------------------------------------------------
    # Three rate layers:
    #   () = default (wild-type): low dispersal
    #   (("a1", "X"),) = one copy of drive allele: moderate dispersal
    #   (("a1", "a0"),) = heterozygous drive: high dispersal
    #
    # EMOD matches the most specific combo first. The empty tuple ()
    # is required as the fallback for any unmatched genotype.
    allele_rates = {
        # Wild-type / default fallback
        (): {
            (1, 2): 0.01, (2, 1): 0.01,
            (1, 3): 0.005, (3, 1): 0.005,
            (2, 3): 0.008, (3, 2): 0.008,
        },
        # One copy of a1 (drive heterozygote)
        (("a1", "X"),): {
            (1, 2): 0.05, (2, 1): 0.05,
            (1, 3): 0.02, (3, 1): 0.02,
            (2, 3): 0.03, (3, 2): 0.03,
        },
        # Homozygous drive (a1/a0 at this locus)
        (("a1", "a0"),): {
            (1, 2): 0.10, (2, 1): 0.10,
            (1, 3): 0.05, (3, 1): 0.05,
            (2, 3): 0.08, (3, 2): 0.08,
        },
    }

    vector_mig = VectorMigrationData.from_genetics(allele_rates, idref="tutorial_8")

    demog.add_vector_migration(
        data=vector_mig,
        species="gambiae",
        x_vector_migration=1.0,
        vector_migration_habitat_modifier=3.0,
        vector_migration_food_modifier=0.0,
        vector_migration_stay_put_modifier=0.5,
        user_notes="Tutorial 8: gene-drive allele-based vector migration"
    )

    return demog


def build_campaign(campaign):
    from emodpy_malaria.campaign.individual_intervention import AntimalarialDrug
    from emodpy_malaria.campaign.distributor import add_intervention_triggered
    from emodpy.campaign.common import TargetDemographicsConfig

    campaign.set_schema(manifest.schema_path)

    # Basic treatment-seeking care so infections resolve
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
    from emodpy_malaria.reporters.reporters import (
        InsetChart, ReportVectorMigration, MalariaSummaryReport
    )
    from emodpy.reporters.base import ReportFilter

    reporters.add(InsetChart(reporters))

    # Vector migration report with genome data to see allele-specific movement
    reporters.add(ReportVectorMigration(
        reporters,
        include_genome_data=True,
        species_list=["gambiae"],
        report_filter=ReportFilter(start_day=1, end_day=sim_years * 365)
    ))

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
    import shutil
    from idmtools.analysis.analyze_manager import AnalyzeManager
    from idmtools.analysis.download_analyzer import DownloadAnalyzer

    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    filenames = [
        "output/InsetChart.json",
        "output/MalariaSummaryReport_monthly.json",
        "output/ReportVectorMigration.csv",
    ]
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

    manager = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager.add_item(experiment)
    manager.analyze()


def plot_results(output_path):
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart

    plot_inset_chart(dir_name=output_path,
                     title="Tutorial 8 - Migration InsetChart",
                     output=output_path)


def handle_results(experiment, platform):
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)

        output_path = "tutorial_8_results"
        process_results(experiment, platform, output_path)
        print(f"Downloaded results for experiment {experiment.id}.")

        plot_results(output_path)
        print(f"\nLook in '{output_path}' for the plots.")
        print("ReportVectorMigration.csv shows per-timestep vector movement with genome data.")
    else:
        print(f"Experiment {experiment.id} failed.")


def run_experiment():
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
