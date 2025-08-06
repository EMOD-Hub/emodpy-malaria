#!/usr/bin/env python

import pathlib # for a join
from functools import partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import RequirementsToAssetCollection
from idmtools_models.templated_script_task import get_script_wrapper_unix_task

# emodpy
from emodpy.emod_task import EMODTask
import emodpy.emod_task as emod_task


import params
import manifest

def update_sim_bic(simulation, value):
    simulation.task.config.parameters.Base_Infectivity_Constant = value*0.1
    return {"Base_Infectivity": value}

def update_sim_random_seed(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Random_Seed": value}

def set_param_fn( config ):
    import emodpy_malaria.malaria_config as conf
    config = conf.set_team_defaults(config, manifest)
    conf.add_species(config, manifest, ["gambiae"])
    config.parameters.x_Temporary_Larval_Habitat = 10
    config.parameters.Simulation_Duration = 365.0
    #config.parameters.Base_Infectivity_Constant = 1.0 
    #config.parameters.Enable_Infectivity_Scaling = 1
    #config.parameters.Enable_Demographics_Reporting = 0 
    #config.parameters.Incubation_Period_Constant = 2
    #config.parameters.Infectious_Period_Exponential = 4.0 
    #config.parameters.Minimum_End_Time = 90 
    #config.parameters.Enable_SQL_Reporter = 1 # [ "NewInfection", "NewlySymptomatic" ]

    return config


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.outbreak as ob

    print(f"Telling emod-api to use {manifest.schema_file} as schema.")
    campaign.set_schema(manifest.schema_file)
    
    # importation pressure
    ob.add_outbreak_individual(campaign, start_day=1, repetitions=-1, timesteps_between_repetitions=1,
                                target_num_individuals=2)
    return campaign

def build_demog():
    """
    Build a demographics input file for the DTK using emod_api.
    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics # OK to call into emod-api
    demog = Demographics.from_template_node( lat=0, lon=0, pop=10000, name=1, forced_id=1 )
    return demog

def ep4_fn( task ):
    task = emod_task.add_ep4_from_path(task, manifest.ep4_path)
    return task

def general_sim():
    # Create a platform
    platform = Platform("Container", job_directory="../example_jobs")
    task = EMODTask.from_default2(eradication_path=manifest.eradication_path,
                                  campaign_builder=build_camp,
                                  demog_builder=build_demog,
                                  schema_path=manifest.schema_file,
                                  param_custom_cb=set_param_fn,
                                  ep4_custom_cb=ep4_fn,
                                  config_path="config.json" )

    pathed_asset = Asset( manifest.schema_file, relative_path="python")
    task.common_assets.add_asset(pathed_asset)

    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition( update_sim_random_seed, range(params.nSims) )

    # create experiment from builder
    experiment = Experiment.from_builder(builder, task, name=params.exp_name)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True)

    # Check result
    print()
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
    else:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id.txt", "w") as fd:
            fd.write(experiment.id)
    

if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
