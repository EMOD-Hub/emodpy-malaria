"""
=== Tutorial 7 - Serialization Part 2: Pickup ===

This script reads the serialized population states produced by
tutorial_7_burnin.py and starts new simulations from those saved states,
adding treatment-seeking care and ITNs — the same interventions from
Tutorial 3, now evaluated against a population with a realistic history
of infections and immunity.

Starting from a serialized state instead of time zero means:
  - Each simulation begins in year 51 of the population's history with
    a realistic age structure, pre-existing immunity, and ongoing
    transmission — not a cold-start artifact
  - Running multiple burnin runs as starting points captures the
    natural stochastic spread of outcomes under the same intervention
  - Only the pickup portion (sim_years) needs to be re-run when changing
    intervention parameters — the 50-year burnin is reused as-is

=== INSTRUCTIONS ===
1. Run tutorial_7_burnin.py first.
2. Paste the printed experiment ID into BURNIN_EXP_ID below.
3. Set CALIBRATED_LOG10_X_LARVAL_HABITAT to the same value used in the burnin.
4. Select the correct platform in run_experiment().
"""
import os
import pathlib
from functools import partial

from idmtools.core.platform_factory import Platform
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment
from emodpy.campaign.common import RepetitionConfig
from emodpy.emod_task import EMODTask

from emodpy_malaria.utils.serialization import (
    configure_serialization_read,
    get_burnin_sim_outpaths,
)

import manifest

# ============================================================
# UPDATE - Paste the log10 value from Tutorial 6.
# ============================================================
CALIBRATED_LOG10_X_LARVAL_HABITAT = -1.61

# ================================================================
# UPDATE - Paste the experiment ID printed by tutorial_7_burnin.py
# ================================================================
BURNIN_EXP_ID = "c3105282-f249-4dfd-bf84-9be455aa7291"

serialize_years      = manifest.burnin_serialize_years
sim_years            = 3
N_SIMS_PER_PICKUP    = 3


def sweep_run_number(simulation, value):
    """Sets the random seed for a simulation."""
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def build_config(config):
    """Configures a pickup simulation with calibrated larval habitat."""
    import emodpy_malaria.malaria_config as malaria_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = sim_years * 365
    config.parameters.x_Temporary_Larval_Habitat = 10 ** CALIBRATED_LOG10_X_LARVAL_HABITAT

    from emodpy_malaria.utils.emod_enum import HabitatType

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

    # Serialization reading is configured per-simulation in update_serialize_parameters()
    # because the path differs for each burnin run.

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
    """Adds treatment-seeking and ITN interventions for the pickup period."""
    from emodpy_malaria.campaign.individual_intervention import (
        AntimalarialDrug, SimpleBednet
    )
    from emodpy_malaria.campaign.distributor import (
        add_intervention_scheduled, add_intervention_triggered
    )
    import emodpy_malaria.campaign.waning_config as waning
    from emodpy_malaria.campaign.common import TargetDemographicsConfig

    campaign.set_schema(manifest.schema_path)

    # Clinical case management at 70% coverage
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

    # ITN distribution
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
    """Adds MalariaSummaryReport and InsetChart."""
    from emodpy_malaria.reporters.reporters import MalariaSummaryReport, InsetChart
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

    return reporters


def update_serialize_parameters(simulation, burnin_index, df):
    """Points a simulation to read its initial population from a burnin output."""
    sim_path = df["outpath"][burnin_index]
    filename = f"state-{serialize_years * 365:05d}.dtk"
    configure_serialization_read(
        simulation.task.config,
        path=sim_path,
        filenames=[filename],
    )
    return {
        "Run_Number":                 int(df["Run_Number"][burnin_index]),
        "Serialized_Population_Path": sim_path,
    }


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
    """Plots InsetChart and monthly PfPR from pickup simulations."""
    import glob
    import json
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart

    plot_inset_chart(dir_name=output_path,
                     title="Tutorial 7 - Pickup InsetChart",
                     output=output_path)

    summary_files = sorted(glob.glob(
        os.path.join(output_path, "**", "MalariaSummaryReport_monthly.json"),
        recursive=True
    ))
    if not summary_files:
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    for f in summary_files:
        with open(f) as fh:
            report = json.load(fh)
        pfpr_by_time = report["DataByTimeAndAgeBins"]["PfPR by Age Bin"]
        monthly_pfpr = [step[1] for step in pfpr_by_time]
        ax.plot(range(len(monthly_pfpr)), monthly_pfpr, alpha=0.7, linewidth=1.2)

    ax.axvline(x=12, color="red", linestyle="--", linewidth=1.5,
               label="Interventions start (month 12)")
    ax.set_xlabel("Month")
    ax.set_ylabel("PfPR (under 5)")
    ax.set_title("Tutorial 7 - Monthly PfPR Under-5 (Pickup Period)")
    ax.legend()
    fig.tight_layout()
    out_path = os.path.join(output_path, "tutorial_7_pfpr.png")
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    print(f"  Saved PfPR plot: {out_path}")


def handle_results(experiment, platform):
    """Checks experiment status, downloads results, and generates plots."""
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)

        output_path = "tutorial_7_results_pickup"

        process_results(experiment, platform, output_path)
        print(f"Downloaded results for experiment {experiment.id}.")

        plot_results(output_path)
        print(f"\nLook in '{output_path}' for the plots.")
    else:
        print(f"\nPickup experiment {experiment.id} failed.")


def run_experiment():
    """Loads burnin states and runs pickup simulations with interventions."""
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

    burnin_df = get_burnin_sim_outpaths(BURNIN_EXP_ID, platform, tag_columns=["Run_Number"])
    n_burnin  = len(burnin_df)

    builder = SimulationBuilder()
    builder.add_sweep_definition(
        partial(update_serialize_parameters, df=burnin_df),
        range(n_burnin)
    )
    builder.add_sweep_definition(sweep_run_number, range(N_SIMS_PER_PICKUP))

    experiment = Experiment.from_builder(builder, task, name="tutorial_7_pickup")
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print("\nTutorial 7-pickup is done.")

    return experiment


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
