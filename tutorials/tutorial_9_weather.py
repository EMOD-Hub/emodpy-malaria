"""
=== Tutorial 9 - Weather files ===

This tutorial creates site-specific weather data and adds it to a
multi-node simulation using CLIMATE_BY_DATA mode:
  - Synthetic daily weather     air temperature, rainfall, and relative
                                humidity generated as sinusoidal patterns
  - WeatherSet from DataFrame   converts tabular data into EMOD binary
                                weather files (.bin / .bin.json)
  - add_weather()               validates nodes, stamps IdReference, writes
                                files, and registers climate config

The simulation has two nodes with different baseline temperatures,
rainfall intensities, and humidity levels. Weather varies sinusoidally
over a 365-day period to represent seasonal patterns.

New in this tutorial (diff from tutorial_3_interventions.py):
  - build_demographics()  creates 2 nodes, builds weather from a DataFrame,
                          and attaches it via add_weather()
  - build_config()        does NOT set climate parameters (add_weather handles it)

=== INSTRUCTIONS ===
Select the correct platform in run_experiment() and update manifest.py if
using SLURM. See tutorial_1_intro.py for full platform details.
"""
import os
import pathlib

import numpy as np
import pandas as pd

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from emodpy.emod_task import EMODTask

import manifest

sim_years = 3


def sweep_run_number(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def build_config(config):
    import emodpy_malaria.malaria_config as malaria_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    # No climate config here -- add_weather() handles it
    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = sim_years * 365
    config.parameters.x_Base_Population = manifest.x_Base_Population_scale

    return config


def build_demographics():
    from emod_api.demographics.node import Node
    from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
    from emodpy_malaria.utils.distributions import ExponentialDistribution
    from emodpy_malaria.utils.emod_enum import ClimateUpdateResolution
    from emodpy_malaria.weather import WeatherVariable, WeatherSet

    # --- Two nodes at different locations ---
    nodes = [
        Node(lat=-2.0, lon=32.0, pop=5000, forced_id=1, name="Site_A"),
        Node(lat=-2.5, lon=32.5, pop=3000, forced_id=2, name="Site_B"),
    ]
    demog = MalariaDemographics(nodes=nodes, idref="tutorial_9")
    demog.set_birth_rate(40)
    demog.set_age_distribution(ExponentialDistribution(20))

    # --- Create synthetic weather as a DataFrame ---
    n_steps = sim_years * 365
    rows = []
    for node_id in [1, 2]:
        for d in range(n_steps):
            rows.append({
                "node": node_id,
                "step": d,
                "airtemp": 22.0 + 5.0 * (node_id - 1) + 5.0 * np.sin(2 * np.pi * d / 365),
                "rainfall": max(0.0, (8.0 + 5.0 * (node_id - 1)) * np.sin(2 * np.pi * d / 365)),
                "humidity": 0.65 + 0.15 * (node_id - 1),
            })
    df = pd.DataFrame(rows)

    ws = WeatherSet.from_dataframe(
        df,
        node_column="node",
        step_column="step",
        weather_columns={
            WeatherVariable.AIR_TEMPERATURE: "airtemp",
            WeatherVariable.RAINFALL: "rainfall",
            WeatherVariable.RELATIVE_HUMIDITY: "humidity",
        },
        notes="Synthetic sinusoidal weather for tutorial 9",
    )

    demog.add_weather(
        data=ws,
        update_resolution=ClimateUpdateResolution.CLIMATE_UPDATE_DAY,
    )

    return demog


def build_campaign(campaign):
    from emodpy_malaria.campaign.individual_intervention import AntimalarialDrug
    from emodpy_malaria.campaign.distributor import add_intervention_triggered
    from emodpy.campaign.common import TargetDemographicsConfig

    campaign.set_schema(manifest.schema_path)

    drug = AntimalarialDrug(campaign, drug_type="Artemether")
    add_intervention_triggered(
        campaign,
        intervention_list=[drug],
        triggers_list=["NewClinicalCase"],
        start_day=1,
        target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.5)
    )

    return campaign


def build_reports(reporters):
    from emodpy_malaria.reporters.reporters import InsetChart, MalariaSummaryReport
    from emodpy.reporters.base import ReportFilter

    reporters.add(InsetChart(reporters))

    reporters.add(MalariaSummaryReport(
        reporters,
        reporting_interval=30,
        age_bins=[0.25, 5, 115],
        max_number_reports=sim_years * 13,
        report_filter=ReportFilter(start_day=1, end_day=sim_years * 365,
                                   filename_suffix="monthly")
    ))

    return reporters


def process_results(experiment, platform, output_path):
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
    from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart

    plot_inset_chart(dir_name=output_path,
                     title="Tutorial 9 - Weather InsetChart",
                     output=output_path)


def handle_results(experiment, platform):
    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)

        output_path = "tutorial_9_results"
        process_results(experiment, platform, output_path)
        print(f"Downloaded results for experiment {experiment.id}.")

        plot_results(output_path)
        print(f"\nLook in '{output_path}' for the plots.")
    else:
        print(f"Experiment {experiment.id} failed.")


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
        report_builder=build_reports
    )

    if platform.get_platform_type() == "COMPS":
        task.set_sif(manifest.comps_sif_path, platform)
    elif platform.get_platform_type() == "Slurm":
        task.set_sif(manifest.slurm_sif_path, platform)

    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, [0])

    experiment = Experiment.from_builder(builder, task, name="tutorial_9_weather")
    experiment.run(wait_until_done=True, platform=platform)

    handle_results(experiment, platform)

    print("\nTutorial 9 is done.")

    return experiment


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_experiment()
