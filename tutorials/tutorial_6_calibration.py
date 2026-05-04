"""
=== Tutorial 6 - Calibration ===

Calibration adjusts model parameters so that simulation output matches
observed reference data. This tutorial calibrates x_Temporary_Larval_Habitat —
a config-level scale factor that multiplies the larval habitat capacity for
all habitat types — to match a reference monthly PfPR curve for children
under 5 (tutorial_6_reference_pfpr.csv).

Calibrating x_Temporary_Larval_Habitat is common because it controls
transmission intensity without requiring changes to the habitat shape or type.
If the scenario included multiple habitat types, one scale factor would adjust
them all in proportion.

idmtools-calibra provides:
  - CalibManager    orchestrates the calibration loop (runs iterations, writes results)
  - OptimTool       gradient-free optimizer: proposes samples, updates on scores
  - CalibSite       bundles reference data and analyzers for one calibration target
  - BaseCalibrationAnalyzer
                    map/reduce framework: map() processes one simulation's output,
                    reduce() combines all map results into a score per sample.
                    Calibra MAXIMIZES the score, so reduce() returns 1/RMSE.

New in this tutorial (diff from tutorial_5_sweep.py):
  - sim_years                   increased from 3 to 5 (longer run reaches equilibrium
                                without interventions before the reference period)
  - CALIBRATION_PARAMETERS      x_Temporary_Larval_Habitat with bounds and initial guess
  - N_SAMPLES / N_ITERATIONS    calibration budget constants
  - constrain_sample()          clips sampled values to declared bounds
  - map_sample_to_model_input() sets x_Temporary_Larval_Habitat on each simulation
  - MalariaSummaryAnalyzer      BaseCalibrationAnalyzer that reads the JSON report
  - TutorialCalibSite           CalibSite subclass with reference data and analyzer
  - run_calibration()           replaces run_experiment(); CalibManager drives the loop
  - plot_iteration()            two-panel figure saved after every iteration: PfPR
                                curves colored by fit quality (green=close, red=far)
                                and a parameter-vs-RMSE scatter with the best point
                                marked. Watch these to gauge convergence and stop
                                early once the fit is close enough.

Removed from tutorial_5_sweep.py:
  - from functools import partial
  - SimulationBuilder, Experiment (CalibManager creates experiments internally)
  - update_campaign()           was the sweep callback; CalibManager does the sweep
  - build_camp(cm_coverage)     coverage parameter dropped; interventions removed so
                                calibration targets baseline (unadjusted) transmission
  - add_treatment_seeking, add_itn_scheduled in build_camp
  - process_results(), plot_results(), handle_results()
                                CalibManager writes its own output directory

=== INSTRUCTIONS ===
Select the correct platform in run_calibration() and update manifest.py if
using SLURM. See tutorial_1_intro.py for full platform details.
"""
import os
import pathlib
import numpy as np
import pandas as pd

from idmtools.core.platform_factory import Platform
import emodpy.emod_task as emod_task

from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.calib_site import CalibSite
from idmtools_calibra.algorithms.optim_tool import OptimTool
from idmtools_calibra.analyzers.base_calibration_analyzer import BaseCalibrationAnalyzer

from emodpy_malaria.reporters.builtin import add_malaria_summary_report

import manifest

sim_years = 5

CALIBRATION_PARAMETERS = [
    {
        "Name": "x_Temporary_Larval_Habitat",
        "Dynamic": True,
        "Guess": 1.0,   # default multiplier — no change from team defaults
        "Min":   0.01,
        "Max":  10.0,
    }
]

N_SAMPLES    = 10   # parameter samples per iteration
N_ITERATIONS =  5   # number of calibration iterations


def constrain_sample(sample):
    """
    Clip each parameter to its declared [Min, Max] bounds.
    OptimTool can propose values outside the bounds; this ensures they stay valid.
    """
    p = CALIBRATION_PARAMETERS[0]
    sample[p["Name"]] = float(np.clip(sample[p["Name"]], p["Min"], p["Max"]))
    return sample


def map_sample_to_model_input(simulation, sample):
    """
    Apply one calibration parameter sample to a simulation before it runs.

    x_Temporary_Larval_Habitat multiplies the larval habitat capacity for all
    temporary habitat types. Values above 1 increase transmission; values below
    1 reduce it. CalibManager calls this once per simulation.
    """
    value = float(sample["x_Temporary_Larval_Habitat"])
    simulation.task.config.parameters.x_Temporary_Larval_Habitat = value
    return {"x_Temporary_Larval_Habitat": value}


def plot_iteration(iteration, sim_records, ref_pfpr, plot_dir):
    """
    Save a two-panel figure for one calibration iteration.

    Left panel: every simulated PfPR seasonal curve overlaid on the reference,
    colored green-to-red by RMSE so the best fits stand out at a glance.
    Right panel: x_Temporary_Larval_Habitat vs RMSE with the best sample
    marked by a green star.

    Plots accumulate in plot_dir (one file per iteration) so you can review
    convergence as it happens and stop early once the fit looks close enough.
    There is no automated stopping criterion — that judgment is yours.
    """
    import matplotlib
    matplotlib.use("Agg")           # non-interactive backend; safe on headless servers
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    months = list(range(12))
    params = [r["param"] for r in sim_records]
    rmses  = [r["rmse"]  for r in sim_records]
    curves = [r["pfpr"]  for r in sim_records]

    vmin, vmax = min(rmses), max(rmses)
    if vmax == vmin:                # all samples clipped to same value — avoid flat colormap
        vmax = vmin + 1e-6
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.cm.RdYlGn_r         # low RMSE → green (good), high RMSE → red (bad)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f"Calibration — Iteration {iteration}", fontsize=13)

    # --- Left panel: PfPR curves ---
    for param, rmse, pfpr in zip(params, rmses, curves):
        axes[0].plot(months, pfpr, color=cmap(norm(rmse)), alpha=0.75, linewidth=1.2)
    axes[0].plot(months, ref_pfpr, "k-", linewidth=2.5, marker="o",
                 markersize=5, label="Reference", zorder=5)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=axes[0], label="RMSE")
    axes[0].set_xlabel("Month")
    axes[0].set_ylabel("PfPR (under 5)")
    axes[0].set_xticks(months)
    axes[0].set_title("Simulated vs Reference PfPR")
    axes[0].legend(loc="upper left")

    # --- Right panel: parameter vs RMSE ---
    best_i = rmses.index(min(rmses))
    axes[1].scatter(params, rmses, color="steelblue", s=60, zorder=3)
    axes[1].scatter([params[best_i]], [rmses[best_i]], color="green", s=150,
                    marker="*", zorder=4,
                    label=f"Best  x={params[best_i]:.3f}  RMSE={rmses[best_i]:.4f}")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("x_Temporary_Larval_Habitat")
    axes[1].set_ylabel("RMSE")
    axes[1].set_title("Parameter vs RMSE")
    axes[1].legend()

    os.makedirs(plot_dir, exist_ok=True)
    out_path = os.path.join(plot_dir, f"iteration_{iteration:02d}.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    print(f"  Saved iteration plot: {out_path}")


class MalariaSummaryAnalyzer(BaseCalibrationAnalyzer):
    """
    Extract monthly PfPR for children under 5 from the last year of each
    simulation and score each sample by comparing to the reference data.

    MalariaSummaryReport JSON structure:
      ["DataByTimeAndAgeBins"]["PfPR by Age Bin"][time_index][age_bin_index]
    With age_bins=[0.25, 5, 115], index 1 is the under-5 age group (0.25-5 years).

    Calibra maximizes the score, so reduce() returns 1/RMSE: higher is better.
    """

    def __init__(self, site, uid=None):
        super().__init__(
            uid=uid or "pfpr_monthly",
            filenames=["output/MalariaSummaryReport_monthly.json"],
            reference_data=site.get_reference_data(),
        )
        self._iteration = 0

    def map(self, data, item):
        """
        Extract the last 12 monthly PfPR values (under-5 age group) from one simulation.
        Called once per simulation; the returned dict is passed to reduce().
        """
        report = data["output/MalariaSummaryReport_monthly.json"]
        pfpr_by_time = report["DataByTimeAndAgeBins"]["PfPR by Age Bin"]
        # Last 12 time steps = last year; age bin 1 = 0.25-5 years (under 5)
        sim_pfpr = [step[1] for step in pfpr_by_time[-12:]]
        return {"sim_pfpr": sim_pfpr}

    def reduce(self, all_data):
        """
        Compute a score per parameter sample, save an iteration plot, and return scores.

        all_data maps each simulation object to the dict returned by map().
        simulation.tags["__sample_index__"] identifies which parameter set
        produced that simulation; simulation.tags["x_Temporary_Larval_Habitat"]
        gives the parameter value used, which is needed for the plot.

        Returns a pandas Series indexed by sample index. Calibra maximizes the
        score, so return 1/RMSE (not RMSE) — closer match = higher score.
        """
        self._iteration += 1
        ref_pfpr = np.array(self.reference_data["pfpr_u5"])
        rmse_by_sample = {}
        sim_records = []

        for simulation, result in all_data.items():
            idx   = int(simulation.tags.get("__sample_index__", 0))
            param = float(simulation.tags.get("x_Temporary_Larval_Habitat", 1.0))
            rmse  = float(np.sqrt(np.mean((np.array(result["sim_pfpr"]) - ref_pfpr) ** 2)))
            rmse_by_sample.setdefault(idx, []).append(rmse)
            sim_records.append({"param": param, "rmse": rmse, "pfpr": result["sim_pfpr"]})

        plot_iteration(
            iteration=self._iteration,
            sim_records=sim_records,
            ref_pfpr=ref_pfpr.tolist(),
            plot_dir=os.path.join("tutorial_6_calibration", "plots"),
        )

        return pd.Series({
            idx: 1.0 / (float(np.mean(vals)) + 1e-9)
            for idx, vals in rmse_by_sample.items()
        })


class TutorialCalibSite(CalibSite):
    """
    Calibration site: supplies reference PfPR data and the MalariaSummaryAnalyzer.

    get_reference_data() returns a DataFrame with columns [month, pfpr_u5]
    read from tutorial_6_reference_pfpr.csv.
    """

    def __init__(self):
        self.reference = pd.read_csv("tutorial_6_reference_pfpr.csv")
        super().__init__(name="Tutorial_Site")

    def get_reference_data(self, reference_type=None):
        return self.reference

    def get_analyzers(self):
        return [MalariaSummaryAnalyzer(site=self, uid="pfpr_monthly")]

    def get_setup_functions(self):
        return []


def set_param_fn(config):
    """
    Configure simulation parameters. The seasonal habitat shape from Tutorial 4
    is retained here. x_Temporary_Larval_Habitat (default 1.0) is overridden
    per simulation by map_sample_to_model_input during calibration.
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
    Build the campaign file. Interventions are removed for calibration so that
    simulated PfPR reflects baseline (unadjusted) transmission only. Tutorial 7
    adds interventions back after the right transmission intensity is established.
    """
    import emod_api.campaign as campaign

    campaign.set_schema(manifest.schema_file)
    return campaign


def add_reporters(task):
    """
    Add the MalariaSummaryReport. MalariaSummaryAnalyzer reads this file to
    extract under-5 PfPR. reporting_interval=30 gives monthly reports;
    max_number_reports covers the full 5-year simulation. age_bins=[0.25, 5, 115]
    puts the under-5 population in index 1, matching the analyzer.
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


def run_calibration():
    """
    Set up the platform, create the EMODTask, and run the calibration.

    CalibManager orchestrates the calibration loop:
    1. OptimTool proposes N_SAMPLES values of x_Temporary_Larval_Habitat.
    2. CalibManager runs one simulation per value, calling map_sample_to_model_input
       to set x_Temporary_Larval_Habitat on each simulation's config.
    3. MalariaSummaryAnalyzer scores each simulation against the reference PfPR.
    4. OptimTool uses the scores to propose better values for the next iteration.
    5. Repeat for N_ITERATIONS iterations.

    Results are written to the 'tutorial_6_calibration' directory.
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

    # EMODTask defines how EMOD will be configured for each simulation.
    # CalibManager calls map_sample_to_model_input before each simulation runs
    # to set x_Temporary_Larval_Habitat to the current sampled value.
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

    site = TutorialCalibSite()

    # OptimTool implements a gradient-free optimization method.
    # Each iteration it runs samples_per_iteration simulations, scores them,
    # and refines the search region around the best-performing sample.
    optimtool = OptimTool(
        CALIBRATION_PARAMETERS,
        constrain_sample_fn=constrain_sample,
        samples_per_iteration=N_SAMPLES,
        center_repeats=1,
    )

    calib_manager = CalibManager(
        name="tutorial_6_calibration",
        task=task,
        map_sample_to_model_input_fn=map_sample_to_model_input,
        sites=[site],
        next_point=optimtool,
        sim_runs_per_param_set=1,
        max_iterations=N_ITERATIONS,
    )
    calib_manager.platform = platform

    calib_manager.run_calibration()

    print(f"\nCalibration complete.")
    print(f"Results are in the 'tutorial_6_calibration' directory.")
    print(f"Iteration plots are in 'tutorial_6_calibration/plots'.")
    print("\nTutorial 6 is done.")


if __name__ == "__main__":
    # Bootstrap downloads the EMOD executable and schema into the download/
    # directory defined in manifest.py. You only need to run this once —
    # after the files are downloaded, subsequent runs will skip this step.
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_calibration()
