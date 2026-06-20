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

=== INSTRUCTIONS ===
1. Set CALIBRATED_LOG10_X_LARVAL_HABITAT to your best value from Tutorial 6.
2. Select the correct platform in run_experiment().
3. Run this script. When it finishes it prints the experiment ID — copy
   that ID into BURNIN_EXP_ID in tutorial_7_pickup.py.
"""
import os
import pathlib

from idmtools.core.platform_factory import Platform
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment
from emodpy.emod_task import EMODTask

import manifest

# ============================================================
# UPDATE - Paste the log10 value from Tutorial 6.
# ============================================================
CALIBRATED_LOG10_X_LARVAL_HABITAT = -1.61

serialize_years = manifest.burnin_serialize_years
N_BURNIN_RUNS   = 3


def sweep_run_number(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def build_config(config):
    import emodpy_malaria.malaria_config as malaria_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = serialize_years * 365
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

    from emodpy_malaria.utils.serialization import configure_serialization_write
    configure_serialization_write(config, times=[serialize_years * 365])

    config.parameters.x_Base_Population = manifest.x_Base_Population_scale

    return config


def build_demographics():
    from emodpy_malaria.demographics import MalariaDemographics as Demographics
    from emodpy_malaria.utils.distributions import UniformDistribution

    demog = Demographics.from_template_node(lat=-3.2, lon=37.9, pop=1000,
                                            name="Tutorial_Site")
    demog.set_birth_rate(40)
    demog.set_age_distribution(UniformDistribution(0, 60*365))
    demog.set_prevalence_distribution(UniformDistribution(0, 0.2))
    return demog


def build_campaign(campaign):
    campaign.set_schema(manifest.schema_path)
    return campaign


def process_results(experiment, platform, output_path):
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
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart

    plot_inset_chart(dir_name=output_path,
                     title="Tutorial 7 - Burnin InsetChart",
                     output=output_path)


def handle_results(experiment, platform):
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
        print("Copy this experiment ID into tutorial_7_pickup.py:")
        print(f"\n    BURNIN_EXP_ID = \"{experiment.id}\"\n")
    else:
        print(f"Burnin experiment {experiment.id} failed.")


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
        report_builder=None
    )

    if platform.get_platform_type() == "COMPS":
        task.set_sif(manifest.comps_sif_path, platform)
    elif platform.get_platform_type() == "Slurm":
        task.set_sif(manifest.slurm_sif_path, platform)

    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, range(N_BURNIN_RUNS))

    experiment = Experiment.from_builder(builder, task, name="tutorial_7_burnin")
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print("\nTutorial 7-burnin is done.")

    return experiment


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
