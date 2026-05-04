"""
=== Tutorial 1 - Introduction to emodpy-malaria ===

emodpy-malaria is the Python interface for configuring and running EMOD malaria
simulations. This tutorial walks through the core building blocks of every
emodpy-malaria script:

  - manifest.py       paths to executables, outputs, and platform settings
  - set_param_fn()    configures config.json (simulation parameters)
  - build_demog()     builds the demographics file (human population)
  - run_experiment()  sets up the platform, task, and experiment, then runs it

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
import emodpy.emod_task as emod_task

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

    set_team_defaults() applies the malaria team's standard parameter set.
    add_species() adds the mosquito vector species to the simulation.
    """
    import emodpy_malaria.malaria_config as malaria_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Simulation_Duration = sim_years * 365
    config.parameters.Run_Number = 0
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


def handle_results(experiment):
    """
    Save the experiment ID and report success or failure.
    Called after experiment.run() completes.
    """
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)
    else:
        print(f"Experiment {experiment.id} failed.")


def run_experiment():
    """
    Set up the platform, create the EMODTask, build the experiment, and run it.
    """
    # ============================================================
    # UPDATE - Select the correct platform for your environment
    # ============================================================
    #platform = Platform("Container", job_directory=manifest.job_dir,
    #                    docker_image=manifest.plat_image)

    platform = Platform("Calculon", node_group="idm_48cores", priority="Normal")

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
        campaign_builder=None,
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

    # SimulationBuilder manages parameter sweeps across simulations.
    # Here we run a single simulation (Run_Number=0). Tutorial 4 covers
    # how to sweep over multiple values to run parameter studies.
    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, [0])

    experiment = Experiment.from_builder(builder, task, name="tutorial_1_intro")

    # experiment.run() submits all simulations and blocks here until they finish.
    # Remove wait_until_done=True if you want to submit and check back later.
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment)

    print("\nTutorial 1 is done.")


if __name__ == "__main__":
    # Bootstrap downloads the EMOD executable and schema into the download/
    # directory defined in manifest.py. You only need to run this once —
    # after the files are downloaded, subsequent runs will skip this step.
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
