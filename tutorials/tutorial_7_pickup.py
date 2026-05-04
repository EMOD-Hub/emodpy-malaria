"""
=== Tutorial 7 - Serialization Part 2: Pickup ===

This script reads the serialized population states produced by
tutorial_7_burnin.py and starts new simulations from those saved states,
adding treatment-seeking care and ITNs — the same interventions from
Tutorial 3, now evaluated against a fully equilibrated population.

Starting from a serialized state instead of time zero means:
  - Each simulation begins in year 51 of the population's history with
    a realistic age structure, pre-existing immunity, and ongoing
    transmission — not a cold-start artifact
  - Running multiple burnin replicates as starting points captures the
    natural stochastic spread of outcomes under the same intervention
  - Only the pickup portion (sim_years) needs to be re-run when changing
    intervention parameters — the 50-year burnin is reused as-is

New in this tutorial (diff from tutorial_7_burnin.py):
  - BURNIN_EXP_ID              paste the ID printed by the burnin script
  - sim_years                  pickup duration (shorter than burnin)
  - serialize_years            kept so we can compute the .dtk filename;
                               must match tutorial_7_burnin.py
  - set_param_fn               write → read:
                               Serialized_Population_Reading_Type = "READ"
                               (Path and Filenames set per-sim by sweep)
  - build_camp()               add_treatment_seeking + add_itn_scheduled
                               restored — same parameters as Tutorial 3
  - add_reporters()            MalariaSummaryReport restored
  - get_burnin_df()            loads burnin experiment and collects each
                               simulation's output path into a DataFrame;
                               handles Container/SLURM (get_directory) and
                               COMPS (hpc_jobs working_directory) separately
  - update_serialize_parameters()
                               sweep callback: links each pickup simulation
                               to one burnin replicate by setting
                               Serialized_Population_Path and
                               Serialized_Population_Filenames

=== INSTRUCTIONS ===
1. Run tutorial_7_burnin.py first.
2. Paste the printed experiment ID into BURNIN_EXP_ID below.
3. Set CALIBRATED_X_LARVAL_HABITAT to the same value used in the burnin.
4. Select the correct platform in run_experiment().
"""
import os
import pathlib
import pandas as pd
from functools import partial

from idmtools.core.platform_factory import Platform
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment
import emodpy.emod_task as emod_task

from emodpy_malaria.reporters.builtin import add_malaria_summary_report

import manifest

# ============================================================
# UPDATE - Paste the experiment ID printed by tutorial_7_burnin.py
# ============================================================
BURNIN_EXP_ID = "paste-your-burnin-experiment-id-here"

# Must match the value used in tutorial_7_burnin.py
CALIBRATED_X_LARVAL_HABITAT = 1.0

serialize_years = 50   # must match tutorial_7_burnin.py (used to compute .dtk filename)
sim_years       = 3    # how many years to simulate after picking up from the burnin


def set_param_fn(config):
    """
    Configure simulation parameters for the pickup.

    The habitat shape, species, and x_Temporary_Larval_Habitat are
    unchanged from the burnin. The serialization mode switches from
    WRITE to READ.

    Serialized_Population_Path and Serialized_Population_Filenames are
    not set here because they differ per simulation — each pickup
    simulation reads from a different burnin replicate. Those two
    parameters are set by update_serialize_parameters() in the sweep.
    """
    import emodpy_malaria.malaria_config as malaria_config
    import emodpy_malaria.vector_config as vector_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Simulation_Duration = sim_years * 365
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

    config.parameters.Serialized_Population_Reading_Type = "READ"
    config.parameters.Serialization_Mask_Node_Read       = 0

    return config


def build_demog():
    """
    Demographics are unchanged from the burnin.
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
    Add treatment-seeking care and ITNs, both starting on day 365 of the
    pickup run (year 2 relative to the serialized starting point, giving
    the population one year to settle before interventions begin).

    These are the same interventions from Tutorial 3.
    """
    import emod_api.campaign as campaign
    from emodpy_malaria.interventions.treatment_seeking import add_treatment_seeking
    from emodpy_malaria.interventions.bednet import add_itn_scheduled

    campaign.set_schema(manifest.schema_file)

    add_treatment_seeking(campaign,
                          start_day=365,
                          targets=[{"trigger": "NewClinicalCase", "coverage": 0.7},
                                   {"trigger": "NewSevereCase",   "coverage": 0.9}])

    add_itn_scheduled(campaign,
                      start_day=365,
                      demographic_coverage=0.5,
                      receiving_itn_broadcast_event="Received_ITN")

    return campaign


def add_reporters(task):
    """
    Add the MalariaSummaryReport to track PfPR through the pickup period.
    The report covers the full sim_years run so you can compare pre- and
    post-intervention transmission.
    """
    task.config.parameters.Enable_Default_Reporting = 1

    add_malaria_summary_report(task, manifest,
                               start_day=1,
                               end_day=sim_years * 365,
                               reporting_interval=30,
                               age_bins=[0.25, 5, 115],
                               max_number_reports=sim_years * 13,
                               filename_suffix="monthly",
                               pretty_format=True)


def get_burnin_df(platform):
    """
    Build a DataFrame of burnin simulation output paths for the sweep.

    Loads the burnin experiment by ID, retrieves each simulation's output
    directory, and returns a DataFrame sorted by Run_Number — one row per
    burnin simulation. update_serialize_parameters() uses the row index to
    link each pickup simulation to the correct burnin replicate.

    Path resolution differs by platform:
      Container / SLURM  simulation.get_directory() returns the local or
                         shared-filesystem path directly.
      COMPS              files live on a remote cluster filesystem; the
                         cluster-side path comes from hpc_jobs[0].working_directory.
                         The substitutions below convert the Windows UNC path to
                         the Linux mount path used by COMPS compute nodes — adjust
                         them if your COMPS instance uses different mount paths.
    """
    platform_type = platform.get_platform_type()
    children = (["tags", "configuration", "files", "hpc_jobs"]
                if platform_type == "COMPS"
                else ["tags", "configuration"])

    exp = Experiment.from_id(BURNIN_EXP_ID, children=False)
    exp.simulations = platform.get_children(exp.id, exp.item_type, children=children)

    records = []
    for sim in exp.simulations:
        if platform_type == "COMPS":
            path = sim.get_platform_object().hpc_jobs[0].working_directory
            # Convert Windows UNC path to Linux mount path on COMPS compute nodes.
            # UPDATE these substitutions if your COMPS instance uses different paths.
            path = path.replace("\\", "/")
            path = path.replace("internal.idm.ctr", "mnt")
            path = path.replace("IDM2", "idm2")
        else:
            path = str(sim.get_directory())

        records.append({
            "run_number": int(sim.tags.get("Run_Number", 0)),
            "outpath":    os.path.join(path, "output"),
        })

    return pd.DataFrame(records).sort_values("run_number").reset_index(drop=True)


def update_serialize_parameters(simulation, x, df):
    """
    Link one pickup simulation to one burnin replicate.

    Called by the sweep builder once per row in burnin_df. Sets
    Serialized_Population_Path to the burnin simulation's output directory
    and Serialized_Population_Filenames to the .dtk snapshot written at
    the end of the burnin.

    The .dtk filename format is state-NNNNN-000.dtk where NNNNN is the
    timestep (simulation day) zero-padded to five digits. For a 50-year
    burnin (18250 days) with a single node: state-18250-000.dtk.
    """
    sim_path = df["outpath"][x]
    filename = f"state-{serialize_years * 365:05d}-000.dtk"
    simulation.task.config.parameters.Serialized_Population_Path      = sim_path
    simulation.task.config.parameters.Serialized_Population_Filenames = [filename]
    return {
        "Run_Number":                 int(df["run_number"][x]),
        "Serialized_Population_Path": sim_path,
    }


def run_experiment():
    """
    Load burnin output paths, sweep to link each pickup simulation to one
    burnin replicate, and run the experiment.

    The sweep over range(n_burnin) creates one pickup simulation per burnin
    replicate. update_serialize_parameters() receives the row index x and
    uses it to look up the correct burnin output path from burnin_df.
    """
    # ============================================================
    # UPDATE - Select the correct platform for your environment
    # ============================================================
    platform = Platform("Container", job_directory=manifest.job_dir,
                        docker_image=manifest.plat_image,
                        max_job=10)

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
        task.set_sif(manifest.comps_sif_path, platform)
    elif platform.get_platform_type() == "Slurm":
        task.set_sif(manifest.slurm_sif_path, platform)

    add_reporters(task)

    burnin_df = get_burnin_df(platform)
    n_burnin  = len(burnin_df)

    builder = SimulationBuilder()
    builder.add_sweep_definition(
        partial(update_serialize_parameters, df=burnin_df),
        range(n_burnin)
    )

    experiment = Experiment.from_builder(builder, task, name="tutorial_7_pickup")
    experiment.run(wait_until_done=True, platform=platform)

    if experiment.succeeded:
        print(f"\nPickup complete. {n_burnin} simulations finished.")
        print(f"Results are in the job directory under experiment {experiment.id}.")
        print(f"\nTutorial 7 is done.")
    else:
        print(f"\nPickup experiment {experiment.id} failed.")


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
