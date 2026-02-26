#!/usr/bin/env python3

# idmtools
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
from emodpy.emod_task import EMODTask

import manifest

"""
This example shows how to configure a malaria simulation with parasite genetics.
After some time steps the population is saved. The saved population serves as input for other examples.
"""

def set_param_fn(config):
    """
    This is a call-back function that sets parameters.
    Here we are getting "default" parameters for a MALARIA_SIM and
    explicitly adding Serialization_Parameters

    Args:
        config:

    Returns:
        completed configuration
    """

    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, "gambiae")
    config.parameters.Vector_Sampling_Type = "SAMPLE_IND_VECTORS"
    # config.parameters.Vector_Sampling_Type = "VECTOR_COMPARTMENTS_NUMBER"
    # config.parameters.Vector_Sampling_Type = "TRACK_ALL_VECTORS"
    config.parameters.Simulation_Duration = 51
    config.parameters.Serialization_Time_Steps = [50]
    config.parameters.Serialized_Population_Writing_Type = "TIMESTEP"
    config.parameters.Serialization_Mask_Node_Write = 0
    config.parameters.Serialization_Precision = "REDUCED"
    config.parameters.Malaria_Model = "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS"
    config.parameters.Parasite_Genetics.Sporozoites_Per_Oocyst_Distribution = "GAUSSIAN_DISTRIBUTION"
    config.parameters.Parasite_Genetics.PfEMP1_Variants_Genome_Locations = [
        214333, 428667, 958667, 1274333, 1864900, 2139900, 2414900,
        2989900, 3289900, 3589900, 4150000, 4410000, 4670000, 4930000,
        5470000, 5750000, 6030000, 6310000, 6870000, 7150000, 7430000,
        7710000, 8250000, 8510000, 8770000, 9030000, 9590000, 9890000,
        10190000, 10490000, 11130000, 11470000, 11810000, 12150000,
        12890000, 13290000, 13690000, 14090000, 14950000, 15410000,
        15870000, 16330000, 17330000, 17870000, 18410000, 18950000,
        20150000, 20810000, 21470000, 22130000]

    config.parameters.Parasite_Genetics.Barcode_Genome_Locations = [
        311500, 1116500, 2140000, 3290000, 4323333, 4756667, 5656667, 6123333,
        7056667, 7523333, 8423333, 8856667, 9790000, 10290000, 11356667, 11923333,
        13156667, 13823333, 15256667, 16023333, 17690000, 18590000, 20590000, 21690000]

    return config


def build_camp():
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    import emod_api.campaign as campaign
    import emodpy_malaria.interventions.outbreak as outbreak

    campaign.schema_path = manifest.schema_file
    outbreak.add_outbreak_malaria_genetics(campaign, target_num_individuals=100, barcode_string="TAAAAAAAAAAAAAAAAAAAAAAA")
    return campaign


def build_demog():
    """
    Builds demographics

    Returns:
        final demographics object
    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demog = Demographics.from_params(tot_pop=100, num_nodes=4)
    return demog


def general_sim():
    """
    This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.

    Returns:
        Nothing
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    #platform = Platform("Calculon", num_cores=1, node_group="idm_48cores", priority="Highest")
    platform = Platform("SLURMStage", num_retries=0)

    # create EMODTask 
    print("Creating EMODTask (from files)...")

    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_camp,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_param_fn,  # THIS IS WHERE SERIALIZATION PARAMETERS ARE ADDED
        demog_builder=build_demog,
        plugin_report=None  # report
    )
    
    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)
    
    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    experiment_name = "Create a serialized population with parasite genetics"
    experiment = Experiment.from_task(task=task, name=experiment_name)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.id} failed.\n")
        exit()

    print(f"Experiment {experiment.id} succeeded.")

    # Save experiment id to file
    with open("experiment_id", "w") as fd:
        fd.write(experiment.id)
    print()
    print(experiment.id)
    
    # important bit
    # WE ARE GOING TO USE SERIALIZATION FILES GENERATED IN burnin_create
    from idmtools_platform_comps.utils.download.download import DownloadWorkItem, CompressType
    dl_wi = DownloadWorkItem(
                             related_experiments=[experiment.id],
                             file_patterns=["output/*.dtk"],
                             simulation_prefix_format_str='serialization_files',
                             verbose=True,
                             output_path="",
                             delete_after_download=False,
                             include_assets=True,
                             compress_type=CompressType.deflate)

    dl_wi.run(wait_until_done=True, platform=platform)
    print("SHOULD BE DOWNLOADED")


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    
    general_sim()
