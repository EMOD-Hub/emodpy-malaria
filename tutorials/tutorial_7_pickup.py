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

New in this tutorial (diff from tutorial_7_burnin.py):
  - BURNIN_EXP_ID              paste the ID printed by the burnin script
  - sim_years                  pickup duration (shorter than burnin)
  - serialize_years            kept so we can compute the .dtk filename;
                               must match tutorial_7_burnin.py
  - build_config               write → read:
                               Serialized_Population_Reading_Type = "READ"
                               (Path and Filenames set per-sim by sweep)
  - build_campaign()           add_treatment_seeking + add_itn_scheduled
                               restored — same parameters as Tutorial 3
  - add_reporters()            MalariaSummaryReport restored
  - get_burnin_df()            loads burnin experiment and collects each
                               simulation's output path into a DataFrame;
                               handles Container/SLURM (get_directory) and
                               COMPS (hpc_jobs working_directory) separately
  - update_serialize_parameters()
                               sweep callback: links each pickup simulation
                               to one burnin run by setting
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
# UPDATE - Paste the log10 value from Tutorial 6.
# ============================================================
CALIBRATED_LOG10_X_LARVAL_HABITAT = -1.61  # must match the value used in tutorial_7_burnin.py

# ================================================================
# UPDATE - Paste the experiment ID printed by tutorial_7_burnin.py
# ================================================================
BURNIN_EXP_ID = "paste-your-burnin-experiment-id-here"

serialize_years      = 50   # must match tutorial_7_burnin.py (used to compute .dtk filename)
sim_years            = 3    # how many years to simulate after picking up from the burnin
N_SIMS_PER_PICKUP    = 3    # stochastic runs per burnin run


def sweep_run_number(simulation, value):
    """
    Callback used by SimulationBuilder to set the Run_Number parameter.
    Run_Number is the random seed — different values give different stochastic
    realizations of the same scenario.
    
    In this tutorial, we sweep Run_Number across each burnin run
    to add stochastic variation on top of the variation in immune history
    across burnin runs.
    """
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def build_config(config):
    """
    Configure simulation parameters for the pickup.

    The habitat shape, species, and x_Temporary_Larval_Habitat are
    unchanged from the burnin. The serialization mode switches from
    WRITE to READ.

    Serialized_Population_Path and Serialized_Population_Filenames are
    not set here because they differ per simulation — each pickup
    simulation reads from a different burnin run. Those two
    parameters are set by update_serialize_parameters() in the sweep.
    """
    import emodpy_malaria.malaria_config as malaria_config
    import emodpy_malaria.vector_config as vector_config

    # applies the malaria team's standard parameter set
    config = malaria_config.set_team_defaults(config, manifest)

    # adds pre-configured species parameters for three Anopheles vector species
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = sim_years * 365
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

    config.parameters.Serialized_Population_Reading_Type = "READ"
    config.parameters.Serialization_Mask_Node_Read       = 0

    return config


def build_demog():
    """
    Demographics are unchanged from the burnin.

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
    link each pickup simulation to the correct burnin run.

    Path resolution differs by platform:
      Container  get_directory() returns the host filesystem path, but EMOD
                 runs inside Docker where job_directory is mounted at
                 data_mount (default /home/container_data). map_container_path
                 converts the host path to the container-side path.
      SLURM      get_directory() returns the shared-filesystem path directly.
      COMPS      files live on a remote cluster filesystem; the cluster-side
                 path comes from hpc_jobs[0].working_directory. The
                 substitutions below convert the Windows UNC path to the
                 Linux mount path — adjust for your COMPS instance.
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
            outpath = path + "/output"
        elif hasattr(platform, 'data_mount'):
            # Container platform: EMOD runs inside Docker, so we must convert
            # the host path to the path as seen from inside the container.
            from idmtools_platform_container.utils.general import map_container_path
            host_path = str(sim.get_directory())
            container_path = map_container_path(
                platform.job_directory, platform.data_mount, host_path
            )
            outpath = container_path + "/output"   # already unix-style
        else:
            outpath = os.path.join(str(sim.get_directory()), "output")

        records.append({
            "run_number": int(sim.tags.get("Run_Number", 0)),
            "outpath":    outpath,
        })

    return pd.DataFrame(records).sort_values("run_number").reset_index(drop=True)


def update_serialize_parameters(simulation, x, df):
    """
    Link one pickup simulation to one burnin run.

    Called by the sweep builder once per row in burnin_df. Sets
    Serialized_Population_Path to the burnin simulation's output directory
    and Serialized_Population_Filenames to the .dtk snapshot written at
    the end of the burnin.

    The .dtk filename format is state-NNNNN.dtk where NNNNN is the
    timestep (simulation day) zero-padded to five digits. For a 50-year
    burnin (18250 days): state-18250.dtk. Multi-core simulations append a
    node index (e.g. state-18250-000.dtk) but these tutorials are single-core.
    """
    sim_path = df["outpath"][x]
    filename = f"state-{serialize_years * 365:05d}.dtk"
    simulation.task.config.parameters.Serialized_Population_Path      = sim_path
    simulation.task.config.parameters.Serialized_Population_Filenames = [filename]
    return {
        "Run_Number":                 int(df["run_number"][x]),
        "Serialized_Population_Path": sim_path,
    }


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
        "output/MalariaSummaryReport_monthly.json",
    ]
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

    manager = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager.add_item(experiment)
    manager.analyze()


def plot_results(output_path):
    """
    Plot InsetChart channels and a custom monthly PfPR figure.

    plot_inset_chart() overlays all simulations on the same axes so you can
    see stochastic spread across the burnin runs.

    The PfPR plot shows monthly under-5 PfPR across the pickup period with a
    vertical line marking when interventions start (day 365 = month 12).
    Compare the pre-intervention months against the Tutorial 6 reference to
    confirm the calibrated baseline carried through from the burnin.
    """
    import glob
    import json
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart

    # InsetChart: all simulations on the same axes
    plot_inset_chart(dir_name=output_path,
                     title="Tutorial 7 - Pickup InsetChart",
                     output=output_path)

    # Custom monthly PfPR plot from MalariaSummaryReport
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
        # age bin index 1 = under-5 (0.25-5 years), matching Tutorial 6
        monthly_pfpr = [step[1] for step in pfpr_by_time]
        ax.plot(range(len(monthly_pfpr)), monthly_pfpr, alpha=0.7, linewidth=1.2)

    # Mark when interventions start (day 365 = month 12 of the pickup run)
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
    """
    Download output files and plot results. Called after the experiment finishes.
    """
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
    """
    Load burnin output paths and run a cross-product sweep:
      burnin runs × N_SIMS_PER_PICKUP Run_Numbers

    Each burnin run represents a different immune history; each
    Run_Number adds independent stochastic variation on top of that. With
    N_BURNIN_RUNS=3 and N_SIMS_PER_PICKUP=3 this produces 9 pickup
    simulations. To also sweep an intervention parameter (e.g. coverage),
    add a third sweep definition following the same pattern as Tutorial 5.

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

    burnin_df = get_burnin_df(platform)
    n_burnin  = len(burnin_df)

    # SimulationBuilder manages parameter sweeps across simulations.
	# Here we are going to sweep each serialized file and Run_Number.
    builder = SimulationBuilder()
    builder.add_sweep_definition(
        partial(update_serialize_parameters, df=burnin_df),
        range(n_burnin)
    )
    builder.add_sweep_definition(sweep_run_number, range(N_SIMS_PER_PICKUP))

    experiment = Experiment.from_builder(builder, task, name="tutorial_7_pickup")
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print(f"\nTutorial 7-pickup is done.")


if __name__ == "__main__":
    # Extract the EMOD executable and schema needed to run simulations.
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
