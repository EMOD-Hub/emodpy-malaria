"""
Simple Example

The goal of this example is to introduce you to running EMOD-Malaria via emodpy-malaria.
The example configures a simulation that:
- runs for 80 simulation days
- has 100 people
- distributes ivermectin to all of the people on day three.

The example also demonstrates other features that are useful when modeling:

- SWEEP - It sweeps the parameter Run_Number which is the random number seed.  This will result
in a colleciton of simulations that are only different by their initial random number seed.

- DOWNLOAD - Once the simulations are done, it will "download" the report files to a directory called
"results" for easier access.

- PLOT - Once the files are downloaded, the results of the simulations will be plotted and
an image will be produced.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plot_inset_chart as pic

from emodpy.emod_task import EMODTask

import manifest
from idmtools.entities.experiment import Experiment
from idmtools.core.platform_factory import Platform
from idmtools.builders import SimulationBuilder


def set_config_parameters(config):
    """
    Set the simulation wide configuration parameters.
    You tell EMODTask.from_defaults2() to use this method to set the simulation
    parameters.
    """
    
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)

    # add the following mosquito species to the simulation.
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    # Set how many days you want the simulation to run
    config.parameters.Simulation_Duration = 80

    return config


def build_campaign():
    """
    Distribute ivermectin to everyone in the scenario on Day 3.
    You tell EMODTask.from_defaults2() to use this method to create the campaign
    object and it will be responsible for what happens afterwards.

    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.ivermectin as ivermectin

    # passing in schema file to verify that the campaign is configured correctly
    campaign.set_schema(manifest.schema_file)

    # add an ivermectin intervention scheduled to be distributed on day 3
    ivermectin.add_scheduled_ivermectin(campaign=campaign, start_day=3)

    return campaign


def build_demog():
    """
    Create a demographics object with 100 people.
    You tell EMODTask.from_defaults2() to use this method to create the demographics
    object and it will be responsible for what happens afterwards.

    Returns:
        complete demographics
    """

    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    demog = Demographics.from_template_node(lat=0, lon=0, pop=100, name=1, forced_id=1)

    return demog


def process_results(experiment, platform, output_path):
    """
    This function will use the `idmtools` concept of an "analyzer".
    Analyzers are intended to be Python logic that you use to process the output of your
    simulations.  We will use the built-in `DownloadAnalyzer` to copy
    the reports to a directory defined by output_path.

    In this method, we will also use the `AnalyzeManager` to execute the `DownloadAnalyzer`.
    One could have multiple analyzers. Imagine you have multiple report files and want to
    summarize each of those reports separately. You could create an analyzer for each report.
    """
    import os, shutil
    from idmtools.analysis.analyze_manager import AnalyzeManager
    from idmtools.analysis.download_analyzer import DownloadAnalyzer

    # Clean up 'outputs' dir
    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    # files to be downloaded from each sim
    filenames = [
        'output/InsetChart.json'
    ]
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

    manager = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager.add_item(experiment)
    manager.analyze()

    return


def plot_results(output_path):
    """
    The following code uses a plotting script that is part of the examples.
    It will create an image and store it in the directory defined by "output_path".
    """
    pic.plot_inset_chart(dir_name=output_path,
                         title="Simple Example",
                         output=output_path)

    return


def update_sim_random_seed(simulation, value):
    """
    This function is called by the SimulationBuilder to set the 
    random seed (Run_Number) for each simulation.
    """
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value} # the tag for the simulation


def general_sim():
    """
    This is the main function that will run the simulations.
    """
    # Create platform that determines WHERE you will run the simulations
    platform = Platform('Container', job_directory="../example_jobs")

    # Create EMODTask that determines HOW to configure the simulations
    print("Creating EMODTask (from files)...")
    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=None,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_config_parameters,
        demog_builder=build_demog
    )

    # Create a builder that builds multiple simulations by building a SWEEP
    builder = SimulationBuilder()
    builder.add_sweep_definition(update_sim_random_seed, range(3)) # sweep 1, 2, 3

    # Create the Experiment of three simulations using the builder
    experiment = Experiment.from_builder(builder, task, name="random_seed")

    # Start/run the experiment - execution will wait here until the simulations are done
    experiment.run(wait_until_done=True)

    # Check result
    print()
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
    else:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id.txt", "w") as fd:
            fd.write(experiment.id)

        # Download the reports/data to a directory called "results"
        output_path = "results"
        process_results(experiment, platform, output_path)

        print(f"Downloaded results for experiment {experiment.uid}.")

        # Create plots/images in the "results" directory
        plot_results(output_path)

        print(f"\nLook in the '{output_path}' directory for the plots of the data.")


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    # Extract the simulation binary and schema to be used from the emod_malaria package
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)

    # Run the simulations
    general_sim()
