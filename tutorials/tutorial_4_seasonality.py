"""
=== Tutorial 4 - Seasonality ===

Real malaria transmission is seasonal: mosquito populations rise and fall with
rainfall, creating peaks of transmission during the wet season. This tutorial
replaces the constant larval habitat from previous tutorials with a LINEAR_SPLINE
habitat that captures a realistic wet/dry seasonal pattern.

EMOD supports weather-file-driven habitat, but LINEAR_SPLINE is easier to work
with: you define the seasonal shape directly as a scaling curve rather than
sourcing and formatting external climate data. This makes it simpler to control
and tune the seasonal pattern for your site.

LINEAR_SPLINE defines a scaling curve over one year (repeating each year) that
multiplies the maximum larval capacity. Values near zero represent the dry season;
the peak represents the wet season. Running for 3 years makes the repeating
seasonal pattern clearly visible in the output.

New in this tutorial (diff from tutorial_3_interventions.py):
  - configure_linear_spline()   defines the seasonal habitat scaling curve
  - set_species_param()         replaces the constant habitat with the spline
                                for all three vector species
  - sim_years                   increased from 1 to 3 to show seasonal cycles

Removed from tutorial_3_interventions.py:
  - use_treatment_seeking, use_itn flags and get_run_suffix()
    The scenario is now fixed — both interventions are always active.

=== INSTRUCTIONS ===
Select the correct platform in run_experiment() and update manifest.py if
using SLURM. See tutorial_1_intro.py for full platform details.
"""
import os
import pathlib

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
import emodpy.emod_task as emod_task

from emodpy_malaria.reporters.builtin import add_malaria_summary_report

import manifest

sim_years = 3


def sweep_run_number(simulation, value):
    """
    Callback used by SimulationBuilder to set the Run_Number parameter.
    Run_Number is the random seed — different values give different stochastic
    realizations of the same scenario.
    """
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def set_param_fn(config):
    """
    Configure simulation parameters. This function is passed as a callback to
    EMODTask and is called when building config.json.

    set_team_defaults() applies the malaria team's standard parameter set,
    which includes a constant TEMPORARY_RAINFALL habitat. configure_linear_spline()
    builds a seasonal replacement, and set_species_param(..., overwrite=True)
    replaces the constant habitat for each vector species.

    The seasonal curve has a pronounced wet-season peak around day 213 (August)
    and a dry-season trough around day 91 (April), representing a site in
    East Africa with a long rains season.
    """
    import emodpy_malaria.malaria_config as malaria_config
    import emodpy_malaria.vector_config as vector_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Simulation_Duration = sim_years * 365
    config.parameters.Run_Number = 0

    seasonal_habitat = vector_config.configure_linear_spline(
        manifest,
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

    return config


def build_demog():
    """
    Build the demographics file describing the simulated human population.

    from_template_node() creates a single-node population at the given lat/lon.
    SetEquilibriumVitalDynamics() sets birth and death rates equal so the
    population stays roughly stable over the simulation.
    SetAgeDistribution() initializes the population with a realistic age
    structure for sub-Saharan Africa.
    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics
    import emod_api.demographics.PreDefinedDistributions as Distributions

    demog = Demographics.from_template_node(lat=-3.2, lon=37.9, pop=1000,
                                            name="Tutorial_Site")
    demog.SetEquilibriumVitalDynamics()
    demog.SetAgeDistribution(Distributions.AgeDistribution_SSAfrica)
    return demog


def build_camp():
    """
    Build the campaign file with treatment seeking and ITN interventions.

    add_treatment_seeking() covers new clinical cases (70%) and severe cases
    (90%). The drug defaults to artemether-lumefantrine, the standard
    first-line therapy. broadcast_event_name defaults to "Received_Treatment".

    add_itn_scheduled() distributes nets to 50% of the population once on
    day 365. receiving_itn_broadcast_event="Received_ITN" causes EMOD to fire
    an event when a net is distributed.
    """
    import emod_api.campaign as campaign
    from emodpy_malaria.interventions.treatment_seeking import add_treatment_seeking
    from emodpy_malaria.interventions.bednet import add_itn_scheduled

    campaign.set_schema(manifest.schema_file)

    add_treatment_seeking(campaign,
                          start_day=365,
                          targets=[{"trigger": "NewClinicalCase", "coverage": 0.7},
                                   {"trigger": "NewSevereCase", "coverage": 0.9}])

    add_itn_scheduled(campaign,
                      start_day=365,
                      demographic_coverage=0.5,
                      receiving_itn_broadcast_event="Received_ITN")

    return campaign


def add_reporters(task):
    """
    Add output reports to the simulation task. Reports are added after EMODTask
    is created and before the experiment is run.

    Enable_Default_Reporting produces InsetChart.json — EMOD's built-in
    time-series overview of the simulation.

    Enable_Demographics_Reporting produces DemographicsSummary.json and
    BinnedReport.json. set_team_defaults() turns this off, so we re-enable
    it here. DemographicsSummary tracks population and vital dynamics and has
    the same channel report format as InsetChart, so it can be plotted the
    same way.

    MalariaSummaryReport provides population-level malaria metrics (PfPR,
    clinical incidence, etc.) grouped by age bin and reporting interval.
    max_number_reports is scaled with sim_years so the full simulation is
    covered.
    """
    task.config.parameters.Enable_Default_Reporting = 1
    task.config.parameters.Enable_Demographics_Reporting = 1

    add_malaria_summary_report(task, manifest,
                               start_day=1,
                               end_day=sim_years * 365,
                               reporting_interval=30,
                               age_bins=[0.25, 5, 115],
                               max_number_reports=sim_years * 13,
                               filename_suffix="monthly",
                               pretty_format=True)


def process_results(experiment, platform, output_path):
    """
    Download output files from each simulation into a local directory.

    DownloadAnalyzer is an idmtools built-in that copies specific files from
    each simulation's output/ folder. Using it here means this code works
    the same way whether simulations ran locally (Container), on COMPS, or
    on a SLURM cluster — the files always end up in output_path.

    AnalyzeManager orchestrates the download across all simulations in the
    experiment.
    """
    import shutil
    from idmtools.analysis.analyze_manager import AnalyzeManager
    from idmtools.analysis.download_analyzer import DownloadAnalyzer

    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    filenames = [
        "output/InsetChart.json",
        "output/DemographicsSummary.json",
        "output/MalariaSummaryReport_monthly.json"
    ]
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

    manager = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager.add_item(experiment)
    manager.analyze()


def plot_results(output_path):
    """
    Plot InsetChart from the downloaded output files.

    If tutorial_3_results is present, its InsetChart is used as the reference
    (plotted in red) so the impact of adding seasonality is directly visible:
    the flat constant-transmission baseline becomes a wave-shaped seasonal signal.
    """
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart
    from emodpy_malaria.plotting.helpers import get_filenames

    # Use Tutorial 3's InsetChart as the constant-transmission baseline if available.
    reference = None
    t3_path = "tutorial_3_results"
    if os.path.exists(t3_path):
        t3_files = get_filenames(dir_or_filename=t3_path,
                                 file_prefix="InsetChart",
                                 file_extension="json")
        if t3_files:
            reference = t3_files[0]

    plot_inset_chart(dir_name=output_path,
                     reference=reference,
                     title="Tutorial 4 - InsetChart",
                     output=output_path)

    demog_files = get_filenames(dir_or_filename=output_path,
                                file_prefix="DemographicsSummary",
                                file_extension="json")
    if demog_files:
        plot_inset_chart(comparison1=demog_files[0],
                         title="Tutorial 4 - DemographicsSummary",
                         output=output_path)


def handle_results(experiment, platform):
    """
    Save the experiment ID, download output files, and plot the results.
    Called after experiment.run() completes.
    """
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)

        output_path = "tutorial_4_results"
        process_results(experiment, platform, output_path)
        print(f"Downloaded results for experiment {experiment.id}.")

        plot_results(output_path)
        print(f"\nLook in '{output_path}' for the plots.")
    else:
        print(f"Experiment {experiment.id} failed.")


def run_experiment():
    """
    Set up the platform, create the EMODTask, build the experiment, and run it.
    """
    # ============================================================
    # UPDATE - Select the correct platform for your environment
    # ============================================================
    platform = Platform("Container", job_directory=manifest.job_dir,
                        docker_image=manifest.plat_image)

    # platform = Platform("Calculon", node_group="idm_48cores", priority="Normal")

    # platform = Platform("SLURM_LOCAL",
    #                     job_directory=manifest.job_dir,
    #                     time="02:00:00",
    #                     partition="cpu_short",
    #                     mail_user="you@example.org",   # UPDATE
    #                     mail_type="ALL",
    #                     max_running_jobs=1000000,
    #                     array_batch_size=1000000)

    # EMODTask defines how EMOD will be configured for each simulation:
    # which executable to run, which config/campaign/demographics callbacks
    # to call, and where to find supporting files.
    task = emod_task.EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_camp,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_param_fn,
        demog_builder=build_demog,
        plugin_report=None
    )

    # set_sif() tells EMOD which container image to use to run the executable.
    # For COMPS and SLURM, the image is a Singularity Image File (SIF);
    # for Container platform the image is specified via docker_image above.
    if platform.get_platform_type() == "COMPS":
        task.set_sif(manifest.comps_sif_path)           # no platform arg: loads AssetCollection from .id file
    elif platform.get_platform_type() == "Slurm":
        task.set_sif(manifest.slurm_sif_path, platform)

    # Reports are added to the task after EMODTask is created.
    add_reporters(task)

    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, [0])

    experiment = Experiment.from_builder(builder, task, name="tutorial_4_seasonality")

    # experiment.run() submits all simulations and blocks here until they finish.
    # Remove wait_until_done=True if you want to submit and check back later.
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print("\nTutorial 4 is done.")


if __name__ == "__main__":
    # Bootstrap downloads the EMOD executable and schema into the download/
    # directory defined in manifest.py. You only need to run this once —
    # after the files are downloaded, subsequent runs will skip this step.
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
