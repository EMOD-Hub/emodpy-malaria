"""
=== Tutorial 7 - Serialization Part 1: Burnin ===

Serialization solves a common problem in malaria modeling: studying the
effect of interventions on a realistic, equilibrated population. Running
the model from scratch for every scenario means waiting 50+ simulated years
for the right age structure, infection history, and vector dynamics to
establish — before interventions even begin.

The solution is a burnin: run one set of long simulations to reach
equilibrium, save (serialize) the full population state to disk, then start
every subsequent intervention scenario from that saved state rather than
from scratch.

This script (Part 1) runs the burnin:
  - Simulates serialize_years years with no interventions
  - Uses x_Temporary_Larval_Habitat calibrated in Tutorial 6 so that
    baseline transmission matches the reference data
  - At the end of each simulation EMOD writes the population to a .dtk
    file — one per simulation, saved in that simulation's output directory
  - Runs N_BURNIN_RUNS replicates (different random seeds) to capture
    natural stochastic variation across independent starting populations

Tutorial 7 Part 2 (tutorial_7_pickup.py) reads those .dtk files and
starts new simulations from the saved states, adding interventions.

New in this tutorial (diff from tutorial_6_calibration.py):
  - CALIBRATED_X_LARVAL_HABITAT  replaces calibra machinery — set this
                                  to the best value from Tutorial 6
  - serialize_years               replaces sim_years
  - Serialization parameters      four new lines in set_param_fn that write
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
# UPDATE - Set this to your best value from Tutorial 6.
# Look at the right panel of your final calibration plot —
# the green star marks the x value with the lowest RMSE.
# ============================================================
CALIBRATED_X_LARVAL_HABITAT = 0.0245

serialize_years = 5   # years to simulate before serializing
N_BURNIN_RUNS   = 3    # number of stochastic replicates to serialize


def sweep_run_number(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def set_param_fn(config):
    """
    Configure simulation parameters for the burnin.

    The habitat shape and species are unchanged from Tutorial 6.
    x_Temporary_Larval_Habitat is set to the calibrated value so the
    equilibrated population has the right transmission intensity.

    The four Serialization parameters tell EMOD to write a population
    snapshot at the day listed in Serialization_Time_Steps — here, the
    last day of the simulation. REDUCED precision gives smaller files
    with negligible loss of accuracy.
    """
    import emodpy_malaria.malaria_config as malaria_config
    import emodpy_malaria.vector_config as vector_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Simulation_Duration = serialize_years * 365
    config.parameters.x_Temporary_Larval_Habitat = CALIBRATED_X_LARVAL_HABITAT

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
    config.parameters.Serialized_Population_Writing_Type = "TIMESTEP"
    config.parameters.Serialization_Time_Steps           = [serialize_years * 365]
    config.parameters.Serialization_Mask_Node_Write      = 0
    config.parameters.Serialization_Precision            = "REDUCED"

    return config


def build_demog():
    """
    Demographics are unchanged from Tutorial 6.
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
    No interventions during the burnin. The population runs to equilibrium
    under baseline transmission only. Interventions are added in
    tutorial_7_pickup.py, after the population has fully equilibrated.
    """
    import emod_api.campaign as campaign

    campaign.set_schema(manifest.schema_file)
    return campaign


def run_experiment():
    """
    Run N_BURNIN_RUNS simulations with different random seeds so that
    tutorial_7_pickup.py can launch multiple independent intervention
    scenarios, each starting from a different equilibrium state.
    """
    # ============================================================
    # UPDATE - Select the correct platform for your environment
    # ============================================================
    platform = Platform("Container", job_directory=manifest.job_dir,
                        docker_image=manifest.plat_image,
                        max_job=N_BURNIN_RUNS)

    # platform = Platform("Calculon", node_group="idm_48cores", priority="Normal")

    # platform = Platform("SLURM_LOCAL",
    #                     job_directory=manifest.job_dir,
    #                     time="02:00:00",
    #                     partition="cpu_short",
    #                     mail_user="you@example.org",   # UPDATE
    #                     mail_type="ALL",
    #                     max_running_jobs=1000000,
    #                     array_batch_size=1000000)

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

    if platform.get_platform_type() == "COMPS":
        task.set_sif(manifest.comps_sif_path)           # no platform arg: loads AssetCollection from .id file
    elif platform.get_platform_type() == "Slurm":
        task.set_sif(manifest.slurm_sif_path, platform)

    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, range(N_BURNIN_RUNS))

    experiment = Experiment.from_builder(builder, task, name="tutorial_7_burnin")
    experiment.run(wait_until_done=True, platform=platform)

    if experiment.succeeded:
        print(f"\nBurnin complete. {N_BURNIN_RUNS} serialized populations saved.")
        print(f"Copy this experiment ID into tutorial_7_pickup.py:")
        print(f"\n    BURNIN_EXP_ID = \"{experiment.id}\"\n")
    else:
        print(f"\nBurnin experiment {experiment.id} failed.")


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
