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
  - build_campaign(treatment_coverage)
                              coverage is now a parameter, not a constant
  - update_campaign()         sweep callback that rebuilds the campaign per
                              simulation using functools.partial
  - two sweep definitions     treatment_coverage x Run_Number cross-product
  - Run_Number sweep widened  [0] -> [0, 1, 2] for stochastic variation

Removed from tutorial_4_seasonality.py:
  - tutorial_3 reference in plot_results — with 9 simulations a single
    reference line would clutter the plot; the coverage spread is the story.

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


def update_campaign(simulation, treatment_coverage):
    """
    Sweep callback that rebuilds the campaign for each simulation with the
    given treatment-seeking coverage.

    partial() binds treatment_coverage to build_campaign so the resulting function takes
    no arguments, which is what create_campaign_from_callback() expects.
    The dict returned becomes a tag on the simulation, making it easy to
    identify which coverage value produced each result.
    """
    build_campaign_partial = partial(build_campaign, treatment_coverage=treatment_coverage)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"treatment_coverage": treatment_coverage}


def build_config(config):
    """
    Configure simulation parameters. This function is passed as a callback to
    EMODTask and is called when building config.json.

    set_team_defaults() applies the malaria team's standard parameter set,
    which includes a TEMPORARY_RAINFALL habitat. configure_linear_spline()
    builds a seasonal replacement, and set_species_param(..., overwrite=True)
    replaces the default habitat for each vector species.

    The seasonal curve has a pronounced wet-season peak around day 213 (August)
    and a dry-season trough around day 91 (April), representing a site in
    East Africa with a long rains season.
    """
    import emodpy_malaria.malaria_config as malaria_config
    import emodpy_malaria.vector_config as vector_config

    # applies the malaria team's standard parameter set
    config = malaria_config.set_team_defaults(config, manifest)

    # adds pre-configured species parameters for three Anopheles vector species
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = sim_years * 365

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


def build_campaign(treatment_coverage=0.8):
    """
    Build the campaign file with treatment seeking and ITN interventions.

    treatment_coverage controls treatment-seeking coverage for clinical and severe
    cases. ITN coverage is fixed at 0.5 — only treatment_coverage is swept in
    this tutorial.

    This function is called by update_campaign() via partial() for each
    simulation in the sweep, so each simulation gets a fresh campaign built
    with its assigned coverage value.
    """
    import emod_api.campaign as campaign
    from emodpy_malaria.interventions.treatment_seeking import add_treatment_seeking
    from emodpy_malaria.interventions.bednet import add_itn_scheduled

    campaign.set_schema(manifest.schema_file)

    add_treatment_seeking(campaign,
                          start_day=365,
                          targets=[{"trigger": "NewClinicalCase", "coverage": treatment_coverage},
                                   {"trigger": "NewSevereCase", "coverage": min(treatment_coverage + 0.2, 1.0)}])

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
    BinnedReport.json. DemographicsSummary tracks population and vital dynamics
    and has the same channel report format as InsetChart, so it can be plotted
    the same way.

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


def group_by_coverage(experiment, output_path):
    """
    Read the treatment_coverage tag from each simulation and move its downloaded
    directory into a subdirectory named by coverage value (e.g. treatment_coverage_0.3/).

    Using the experiment object to read tags works on all platforms — Container,
    COMPS, and SLURM — without requiring any extra files to be written.

    Returns a list of coverage subdirectory paths sorted by coverage value,
    ready to pass directly to plot_mean().
    """
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
    """
    Plot the mean InsetChart for each coverage group using plot_mean().

    Each directory in dirs becomes one labeled series in the plot — the
    directory name (e.g. treatment_coverage_0.3) is used as the legend label. show_raw_data
    overlays the individual simulation lines in a lighter color so the
    stochastic spread within each group is visible alongside the mean.
    """
    from emodpy_malaria.plotting.plot_inset_chart_mean_compare import plot_mean

    plot_mean(dir1=dirs[0],
              dir2=dirs[1],
              dir3=dirs[2],
              title="Tutorial 5 - InsetChart",
              show_raw_data=True,
              output=output_path)


def handle_results(experiment, platform):
    """
    Save the experiment ID, download output files, group by coverage, and plot.
    Called after experiment.run() completes.
    """
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
    """
    Set up the platform, create the EMODTask, build the experiment, and run it.

    For the Container platform, max_job controls how many simulations run at the
    same time — a new one starts as soon as a slot opens. For an experiment with
    nine simulations and max_job=4, simulations run roughly four at a time: four,
    then four, then one. 4 is a safe default on most laptops.
    """
    # ============================================================
    # UPDATE - Select the correct platform for your environment
    # ============================================================
    # max_job limits concurrent simulations — see docstring above
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

    # EMODTask defines how EMOD will be configured for each simulation:
    # which executable to run, which config/campaign/demographics callbacks
    # to call, and where to find supporting files.
    task = emod_task.EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_campaign,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=build_config,
        demog_builder=build_demog,
        plugin_report=None
    )

    # set_sif() tells EMOD which container image to use to run the executable.
    # For COMPS and SLURM, the image is a Singularity Image File (SIF);
    # for Container platform the image is specified via docker_image above.
    if platform.get_platform_type() == "COMPS":
        task.set_sif(manifest.comps_sif_path)
    elif platform.get_platform_type() == "Slurm":
        task.set_sif(manifest.slurm_sif_path, platform)

    # Reports are added to the task after EMODTask is created.
    add_reporters(task)

    # SimulationBuilder manages parameter sweeps across simulations.
    # Two sweep definitions combine as a cross-product: every treatment_coverage
    # value is paired with every Run_Number, giving 3 x 3 = 9 simulations.
    builder = SimulationBuilder()
    builder.add_sweep_definition(update_campaign, [0.3, 0.6, 0.9])
    builder.add_sweep_definition(sweep_run_number, [0, 1, 2])

    experiment = Experiment.from_builder(builder, task, name="tutorial_5_sweep")

    # experiment.run() submits all simulations and blocks here until they finish.
    # Remove wait_until_done=True if you want to submit and check back later.
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print("\nTutorial 5 is done.")


if __name__ == "__main__":
    # Extract the EMOD executable and schema needed to run simulations.
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
