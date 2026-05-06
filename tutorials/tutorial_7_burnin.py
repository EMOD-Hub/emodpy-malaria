"""
=== Tutorial 7 - Serialization Part 1: Burnin ===

Serialization solves a common problem in malaria modeling: studying the
effect of interventions on a population with a realistic history of infections
and immunity. Running the model from scratch for every scenario means waiting
50+ simulated years for the right age structure, infection history, and vector
dynamics to develop — before interventions even begin.

The solution is a burnin: run one set of long simulations to develop that
history, save (serialize) the full population state to disk, then start
every subsequent intervention scenario from that saved state rather than
from scratch.

This script (Part 1) runs the burnin:
  - Simulates serialize_years years with no interventions
  - Uses x_Temporary_Larval_Habitat calibrated in Tutorial 6 so that
    baseline transmission matches the reference data
  - At the end of each simulation EMOD writes the population to a .dtk
    file — one per simulation, saved in that simulation's output directory
  - Runs N_BURNIN_RUNS runs (different random seeds) to capture
    natural stochastic variation across independent starting populations

Tutorial 7 Part 2 (tutorial_7_pickup.py) reads those .dtk files and
starts new simulations from the saved states, adding interventions.

New in this tutorial (diff from tutorial_6_calibration.py):
  - CALIBRATED_X_LARVAL_HABITAT  replaces calibra machinery — set this
                                  to the best value from Tutorial 6
  - serialize_years               replaces sim_years
  - Serialization parameters      four new lines in build_config that write
                                  a population snapshot at end of simulation
  - CalibManager/OptimTool/MalariaSummaryAnalyzer  removed
  - SimulationBuilder + Experiment.from_builder     restored
  - run_experiment()              replaces run_calibration()

=== INSTRUCTIONS ===
1. Set CALIBRATED_X_LARVAL_HABITAT to your best value from Tutorial 6.
2. Select the correct platform in run_experiment().
3. Run this script. When it finishes it prints the experiment ID — copy
   that ID into BURNIN_EXP_ID in tutorial_7_pickup.py.

Note: 50 simulated years takes longer than previous tutorials.
"""
import os
import pathlib
from functools import partial

from idmtools.core.platform_factory import Platform
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment
import emodpy.emod_task as emod_task

import manifest

# ============================================================
# UPDATE - Paste the log10 value from Tutorial 6.
# ============================================================
CALIBRATED_LOG10_X_LARVAL_HABITAT = -1.61  # example from Tutorial 6; replace with your value

serialize_years = 50   # years to simulate before serializing
N_BURNIN_RUNS   = 3    # number of stochastic runs to serialize


def sweep_run_number(simulation, value):
    """
    Callback used by SimulationBuilder to set the Run_Number parameter.
    Run_Number is the random seed — different values give different stochastic
    realizations of the same scenario.
    """
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def build_config(config):
    """
    Configure simulation parameters for the burnin. This function is
    passed as a callback to EMODTask and is called when building config.json.

    The habitat shape and species are unchanged from Tutorial 6.
    x_Temporary_Larval_Habitat is set to the calibrated value so that
    transmission intensity matches the reference data.

    The four Serialization parameters tell EMOD to write a population
    snapshot at the day listed in Serialization_Time_Steps — here, the
    last day of the simulation. REDUCED precision gives smaller files
    with negligible loss of accuracy.
    """
    import emodpy_malaria.malaria_config as malaria_config
    import emodpy_malaria.vector_config as vector_config

    # applies the malaria team's standard parameter set
    config = malaria_config.set_team_defaults(config, manifest)

    # adds pre-configured species parameters for three Anopheles vector species
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = serialize_years * 365
    config.parameters.x_Temporary_Larval_Habitat = 10 ** CALIBRATED_LOG10_X_LARVAL_HABITAT

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

    # Write a population snapshot at the end of the simulation.
    # The .dtk file will be named state-NNNNN.dtk where NNNNN is the
    # timestep zero-padded to 5 digits (e.g. state-18250.dtk for day 18250).
    # Multi-core simulations append a node index (state-18250-000.dtk) but
    # these tutorials run single-core.
    config.parameters.Serialized_Population_Writing_Type = "TIME"
    config.parameters.Serialization_Times                = [serialize_years * 365]
    config.parameters.Serialization_Precision            = "REDUCED"

    return config


def build_demog():
    """
    Demographics are unchanged from Tutorial 6.

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


def build_campaign():
    """
    No interventions during the burnin. The population runs to equilibrium
    under baseline transmission only. Interventions are added in
    tutorial_7_pickup.py, after the population has developed realistic immunity.
    """
    import emod_api.campaign as campaign

    campaign.set_schema(manifest.schema_file)
    return campaign


def add_reporters(task):
    """
    Enable InsetChart.json output for the burnin simulations.
    """
    task.config.parameters.Enable_Default_Reporting = 1


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
        "output/InsetChart.json"
    ]
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

    manager = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager.add_item(experiment)
    manager.analyze()


def plot_results(output_path):
    """
    Plot InsetChart channels for all burnin runs on the same axes.
    Overlay of N_BURNIN_RUNS lines shows the stochastic spread at equilibrium.
    """
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart

    plot_inset_chart(dir_name=output_path,
                     title="Tutorial 7 - Burnin InsetChart",
                     output=output_path)


def handle_results(experiment, platform):
    """
    Save the experiment ID, download output files, and plot the results.
    Called after experiment.run() completes.  The experiment ID will
    be needed in tutorial_7_pickup.py
    """
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)

        output_path = "tutorial_7_results_burnin"

        process_results(experiment, platform, output_path)
        print(f"Downloaded results for experiment {experiment.id}.")

        plot_results(output_path)
        print(f"\nLook in '{output_path}' for the plots.")

        print(f"\nBurnin complete. {N_BURNIN_RUNS} serialized populations saved.")
        print(f"Copy this experiment ID into tutorial_7_pickup.py:")
        print(f"\n    BURNIN_EXP_ID = \"{experiment.id}\"\n")
    else:
        print(f"\nBurnin experiment {experiment.id} failed.")


def run_experiment():
    """
    Run N_BURNIN_RUNS simulations with different random seeds so that
    tutorial_7_pickup.py can launch multiple independent intervention
    scenarios, each starting from a different population state.

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
    # Here we run a single simulation (Run_Number=0). Tutorial 5 covers
    # how to sweep over multiple values to run parameter studies.
    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, range(N_BURNIN_RUNS))

    experiment = Experiment.from_builder(builder, task, name="tutorial_7_burnin")

    # experiment.run() submits all simulations and blocks here until they finish.
    # Remove wait_until_done=True if you want to submit and check back later.
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print("\nTutorial 7-burnin is done.")


if __name__ == "__main__":
    # Extract the EMOD executable and schema needed to run simulations.
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
