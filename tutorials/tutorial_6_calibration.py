"""
=== Tutorial 6 - Calibration ===

Calibration adjusts model parameters so that simulation output matches
observed reference data. This tutorial calibrates x_Temporary_Larval_Habitat —
a config-level scale factor that multiplies the larval habitat capacity for
all habitat types — to match a reference monthly PfPR curve for children
under 5 (tutorial_6_reference_pfpr.csv).

idmtools-calibra provides:
  - CalibManager    orchestrates the calibration loop (runs iterations, writes results)
  - OptimTool       gradient-free optimizer: proposes samples, updates on scores
  - CalibSite       bundles reference data and analyzers for one calibration target
  - BaseCalibrationAnalyzer
                    map/reduce framework: map() processes one simulation's output,
                    reduce() combines all map results into a score per sample.
                    Calibra MAXIMIZES the score, so reduce() returns 1/RMSE.

New in this tutorial (diff from tutorial_5_sweep.py):
  - CALIBRATION_PARAMETERS      log10_x_Temporary_Larval_Habitat
  - MalariaSummaryAnalyzer      reads JSON report, scores vs reference PfPR
  - TutorialCalibSite           CalibSite subclass with reference data
  - run_calibration()           replaces run_experiment()
  - plot_all_iterations()       convergence plots saved after every iteration

=== INSTRUCTIONS ===
Select the correct platform in run_calibration() and update manifest.py if
using SLURM. See tutorial_1_intro.py for full platform details.
"""
import os
import glob
import pathlib
import numpy as np
import pandas as pd

from idmtools.core.platform_factory import Platform
from emodpy.emod_task import EMODTask

from idmtools_calibra.calib_manager import CalibManager
from idmtools_calibra.calib_site import CalibSite
from idmtools_calibra.algorithms.optim_tool import OptimTool
from idmtools_calibra.analyzers.base_calibration_analyzer import BaseCalibrationAnalyzer

import manifest

_tutorials_dir = os.path.dirname(os.path.realpath(__file__))

sim_years = 5

CALIBRATION_PARAMETERS = [
    {
        "Name":    "log10_x_Temporary_Larval_Habitat",
        "Dynamic": True,
        "Guess":   -2.0,
        "Min":     -4.0,
        "Max":     -1.0,
    }
]

N_SAMPLES    = manifest.n_calibration_samples
N_ITERATIONS = manifest.n_calibration_iterations


def constrain_sample(sample):
    p = CALIBRATION_PARAMETERS[0]
    sample[p["Name"]] = float(np.clip(sample[p["Name"]], p["Min"], p["Max"]))
    return sample


def map_sample_to_model_input(simulation, sample):
    log_value = float(sample["log10_x_Temporary_Larval_Habitat"])
    value = 10 ** log_value
    simulation.task.config.parameters.x_Temporary_Larval_Habitat = value
    return {"x_Temporary_Larval_Habitat": value}


def plot_all_iterations(calib_dir, ref_pfpr):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    data_files = sorted(glob.glob(os.path.join(calib_dir, "iter*", "pfpr_records.csv")))
    if not data_files:
        return

    all_dfs = []
    for f in data_files:
        iter_name = os.path.basename(os.path.dirname(f))
        it = int(iter_name.replace("iter", "")) + 1
        df = pd.read_csv(f)
        df["iteration"] = it
        all_dfs.append(df)

    df_all    = pd.concat(all_dfs, ignore_index=True)
    cur_iter  = df_all["iteration"].max()
    months    = list(range(12))
    pfpr_cols = [f"pfpr_{m}" for m in months]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f"Calibration — through Iteration {cur_iter}", fontsize=13)

    cur_df   = df_all[df_all["iteration"] == cur_iter]
    vmin     = cur_df["rmse"].min()
    vmax     = cur_df["rmse"].max()
    if vmax == vmin:
        vmax = vmin + 1e-6
    norm_rmse = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap_rmse = plt.cm.RdYlGn_r

    for it in sorted(df_all["iteration"].unique()):
        sub = df_all[df_all["iteration"] == it]
        for _, row in sub.iterrows():
            pfpr = [row[c] for c in pfpr_cols]
            if it < cur_iter:
                axes[0].plot(months, pfpr, color="grey", alpha=0.25, linewidth=0.8)
            else:
                axes[0].plot(months, pfpr,
                             color=cmap_rmse(norm_rmse(row["rmse"])),
                             alpha=0.85, linewidth=1.4)

    axes[0].plot(months, ref_pfpr, "k-", linewidth=2.5, marker="o",
                 markersize=5, label="Reference", zorder=5)
    sm = plt.cm.ScalarMappable(cmap=cmap_rmse, norm=norm_rmse)
    sm.set_array([])
    plt.colorbar(sm, ax=axes[0], label="RMSE (current iteration)")
    axes[0].set_xlabel("Month")
    axes[0].set_ylabel("PfPR (under 5)")
    axes[0].set_xticks(months)
    axes[0].set_title("Simulated vs Reference PfPR")
    axes[0].legend(loc="upper left")

    iter_norm = mcolors.Normalize(vmin=1, vmax=max(cur_iter, 2))
    iter_cmap = plt.cm.viridis
    for it in sorted(df_all["iteration"].unique()):
        sub = df_all[df_all["iteration"] == it]
        axes[1].scatter(sub["param"], sub["rmse"],
                        color=iter_cmap(iter_norm(it)), s=50, alpha=0.8, zorder=3)

    best_idx = df_all["rmse"].idxmin()
    best     = df_all.loc[best_idx]
    axes[1].scatter([best["param"]], [best["rmse"]], color="green", s=180,
                    marker="*", zorder=5,
                    label=f"Best  x={best['param']:.3f}  RMSE={best['rmse']:.4f}")
    sm2 = plt.cm.ScalarMappable(cmap=iter_cmap, norm=iter_norm)
    sm2.set_array([])
    plt.colorbar(sm2, ax=axes[1], label="Iteration")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("x_Temporary_Larval_Habitat")
    axes[1].set_ylabel("RMSE")
    axes[1].set_title("Parameter vs RMSE (all iterations)")
    axes[1].legend()

    plot_dir = os.path.join(calib_dir, "plots")
    os.makedirs(plot_dir, exist_ok=True)
    out_path = os.path.join(plot_dir, f"iteration_{cur_iter:02d}.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    print(f"  Saved iteration plot: {out_path}")


class MalariaSummaryAnalyzer(BaseCalibrationAnalyzer):
    def __init__(self, site, uid=None):
        super().__init__(
            uid=uid or "pfpr_monthly",
            filenames=["output/MalariaSummaryReport_monthly.json"],
            reference_data=site.get_reference_data(),
        )

    def map(self, data, item):
        report = data["output/MalariaSummaryReport_monthly.json"]
        pfpr_by_time = report["DataByTimeAndAgeBins"]["PfPR by Age Bin"]
        sim_pfpr = [step[1] for step in pfpr_by_time[-12:]]
        return {"sim_pfpr": sim_pfpr}

    def reduce(self, all_data):
        iter_dir = os.path.normpath(self.working_dir)
        calib_dir = os.path.dirname(iter_dir)

        ref_pfpr = np.array(self.reference_data["pfpr_u5"])
        rmse_by_sample = {}
        sim_records = []

        for simulation, result in all_data.items():
            idx   = int(simulation.tags.get("__sample_index__", 0))
            param = float(simulation.tags.get("x_Temporary_Larval_Habitat", 1.0))
            pfpr  = result["sim_pfpr"]
            rmse  = float(np.sqrt(np.mean((np.array(pfpr) - ref_pfpr) ** 2)))
            rmse_by_sample.setdefault(idx, []).append(rmse)
            row = {"param": param, "rmse": rmse}
            row.update({f"pfpr_{m}": v for m, v in enumerate(pfpr)})
            sim_records.append(row)

        pd.DataFrame(sim_records).to_csv(
            os.path.join(iter_dir, "pfpr_records.csv"), index=False
        )

        plot_all_iterations(calib_dir, ref_pfpr.tolist())

        return pd.Series({
            idx: 1.0 / (float(np.mean(vals)) + 1e-9)
            for idx, vals in rmse_by_sample.items()
        })


class TutorialCalibSite(CalibSite):
    def __init__(self):
        self.reference = pd.read_csv(os.path.join(_tutorials_dir, "tutorial_6_reference_pfpr.csv"))
        super().__init__(name="Tutorial_Site")

    def get_reference_data(self, reference_type=None):
        return self.reference

    def get_analyzers(self):
        return [MalariaSummaryAnalyzer(site=self, uid="pfpr_monthly")]

    def get_setup_functions(self):
        return []


def build_config(config):
    import emodpy_malaria.malaria_config as malaria_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = sim_years * 365

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

    config.parameters.x_Base_Population = manifest.x_Base_Population_scale

    return config


def build_demographics():
    from emodpy_malaria.demographics.malaria_demographics import Demographics
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


def build_reports(reporters):
    from emodpy_malaria.reporters.reporters import MalariaSummaryReport, InsetChart
    from emodpy.reporters.base import ReportFilter

    reporters.add(MalariaSummaryReport(
        reporters,
        reporting_interval=30,
        age_bins=[0.25, 5, 115],
        max_number_reports=sim_years * 13,
        pretty_format=True,
        report_filter=ReportFilter(start_day=1, end_day=sim_years * 365, filename_suffix="monthly")
    ))

    reporters.add(InsetChart(reporters))

    return reporters


def run_calibration():
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
        report_builder=build_reports
    )

    if platform.get_platform_type() == "COMPS":
        task.set_sif(manifest.comps_sif_path, platform)
    elif platform.get_platform_type() == "Slurm":
        task.set_sif(manifest.slurm_sif_path, platform)

    site = TutorialCalibSite()

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

    print("\nCalibration complete.")
    print("Results are in the 'tutorial_6_calibration' directory.")
    print("Iteration plots are in 'tutorial_6_calibration/plots'.")
    print(f"\n{'=' * 60}")
    print("NEXT STEP: open tutorial_6_calibration/CalibManager.json, find")
    print("  final_samples -> log10_x_Temporary_Larval_Habitat[0]")
    print("  and paste that value into CALIBRATED_LOG10_X_LARVAL_HABITAT")
    print("  in tutorial_7_burnin.py and tutorial_7_pickup.py")
    print(f"{'=' * 60}")
    print("\nTutorial 6 is done.")


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_calibration()
