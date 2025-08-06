from emodpy.analyzers.adult_vectors_analyzer import AdultVectorsAnalyzer
from emodpy.analyzers.timeseries_analyzer import TimeseriesAnalyzer
from emodpy.emod_task import EMODTask
from idmtools.analysis.analyze_manager import AnalyzeManager
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType

import manifest
from idmtools.entities.experiment import Experiment
from idmtools.core.platform_factory import Platform


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # You have to set simulation type explicitly before you set other parameters for the simulation
    config.parameters.Simulation_Type = "MALARIA_SIM"
    # sets "default" malaria parameters as determined by the malaria team
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])
    config.parameters.Simulation_Duration = 80

    return config


def build_campaign():
    """
        Addind one intervention, so this template is easier to use when adding other interventions, replacing this one
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.ivermectin as ivermectin

    # passing in schema file to verify that everything is correct.
    campaign.set_schema(manifest.schema_file)
    # adding a scheduled ivermectin intervention
    ivermectin.add_scheduled_ivermectin(campaign=campaign, start_day=3)

    return campaign


def build_demog():
    """
        Builds demographics
    Returns:
        complete demographics
    """

    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    demog = Demographics.from_template_node(lat=0, lon=0, pop=100, name=1, forced_id=1)

    return demog


def general_sim():
    # Set platform
    platform = Platform('Container', job_directory=manifest.job_directory)

    # create EMODTask
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
    builder = SimulationBuilder()

    def update_sim_random_seed(simulation, value):
        simulation.task.config.parameters.Run_Number = value
        return {"Run_Number": value}

    builder.add_sweep_definition(update_sim_random_seed, range(10))
    # create Experiment
    experiment = Experiment.from_builder(builder, task, name="random_seed")

    # run the experiment
    experiment.run(wait_until_done=True)

    # Analyze
    filenames = ['output/InsetChart.json']
    analyzers = [AdultVectorsAnalyzer(), TimeseriesAnalyzer(filenames=filenames)]

    manager = AnalyzeManager(platform=platform, ids=[(experiment.id, ItemType.EXPERIMENT)], analyzers=analyzers)
    manager.analyze()


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
