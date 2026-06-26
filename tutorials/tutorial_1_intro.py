"""
=== Tutorial 1 - Introduction to emodpy-malaria ===

emodpy-malaria is the Python interface for configuring and running EMOD malaria
simulations. This tutorial walks through the core building blocks of every
emodpy-malaria script:

  - manifest.py                paths to executables, outputs, and platform settings
  - build_config(config)       configures config.json (simulation parameters)
  - build_campaign(campaign)   configures campaign.json (interventions and events)
  - build_demographics()       builds the demographics file (human population)
  - build_reporters(reporter)  configures various reporters for data output
  - run_experiment()           sets up the platform, task, and experiment, then runs it

=== INSTRUCTIONS ===
There are two places below you may need to update depending on your platform:
  1. The platform block in run_experiment() - select Container, COMPS, or SLURM
  2. For SLURM: update mail_user and slurm_sif_path in manifest.py

--- Platform options ---
Container    - Docker-based, runs locally or in GitHub Codespaces (default)
COMPS        - IDM's cloud HPC; requires an account at comps.idmod.org
SLURM_LOCAL  - A SLURM cluster; requires access and a SIF file
"""
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

    # Set the base population according to the manifest setting.
    # This is just an example of how you can use the manifest to set parameters in the config.
    # In a real script, you might have more complex logic to determine how to set parameters based
    # on the manifest or other inputs.

    # This parameter lets us run small test simulations before running with the full population
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

    # This will set the initial prevalence of infection in the population to be uniformly distributed between 0 and 20%
    # for every new simulation that is run.
    demog.set_prevalence_distribution(UniformDistribution(0, 0.2))
    return demog


def build_reports(reporters):
    """Adds InsetChart reporter for basic simulation output."""
    from emodpy_malaria.reporters.reporters import InsetChart
    reporters.add(InsetChart(reporters))
    return reporters


def process_results(experiment, platform, output_path):
    """Downloads InsetChart output from completed simulations."""
    import os
    import shutil
    from idmtools.analysis.analyze_manager import AnalyzeManager
    from idmtools.analysis.download_analyzer import DownloadAnalyzer

    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    filenames = ["output/InsetChart.json"]
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

    manager = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager.add_item(experiment)
    manager.analyze()


def plot_results(output_path):
    """Plots InsetChart channels over time."""
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart
    plot_inset_chart(dir_name=output_path,
                     title="Tutorial 1 - InsetChart",
                     output=output_path)


def handle_results(experiment, platform):
    """Checks experiment status, downloads results, and generates plots."""
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)

        output_path = "tutorial_1_results"
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

    experiment = Experiment.from_builder(builder, task, name="tutorial_1_intro")
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print("\nTutorial 1 is done.")

    return experiment


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
