#!/usr/bin/env python3

from pathlib import Path
import manifest
import sys
import importlib

# idmtools ...
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

from emodpy.emod_task import EMODTask

sys.path.append('../../emodpy_malaria/serialization')  # current root dir is "examples/serialization_replace_genomes", add "serialization" to the path Python searches for modules
import replace_genomes      # import from directory "serialization"
import replace_genomes_get_next_barcode

"""
This examples takes a serialized population and uses the function replace_genomes() to replace
the genome of an individual's infection and the vector population.   
"""
def set_param_fn(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    import emodpy_malaria.malaria_config as malaria_config
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, "gambiae")
    config.parameters.Simulation_Duration = 1   # Just to check if saved dtk file can be loaded
    config.parameters.Serialized_Population_Reading_Type = "READ"
    config.parameters.Serialization_Mask_Node_Read = 0
    config.parameters.Serialized_Population_Path = manifest.assets_input_dir # <--we uploaded files to here
    config.parameters.Serialized_Population_Filenames = [manifest.destination]
    config.parameters.Serialization_Precision = "REDUCED"
    config.parameters.Malaria_Model = "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS"
    config.parameters.Serialization_Time_Steps = [1]
    config.parameters.Parasite_Genetics.Sporozoites_Per_Oocyst_Distribution = "GAUSSIAN_DISTRIBUTION"

    config.parameters.Parasite_Genetics.PfEMP1_Variants_Genome_Locations = [
        214333,   428667,  958667, 1274333, 1864900, 2139900, 2414900,
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

def build_demog():
    """
        Builds demographics
    Returns:
        final demographics object
    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api
    return Demographics.from_params() # dummy, loading serialized population

def general_sim():
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    # Set platform
    platform = Platform("Calculon", num_cores=1, node_group="idm_48cores", priority="Highest")

    # use serialization files generated in burnin_create_parasite_genetics
    task = EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=None,
        schema_path=manifest.schema_file,
        param_custom_cb=set_param_fn,
        ep4_custom_cb=None,
        demog_builder=build_demog,
        plugin_report=None  # report
    )
    
    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)
    
    # We are creating one-simulation experiment straight from task.
    experiment_name = "Create simulation from serialized file with replaced genomes"
    experiment = Experiment.from_task(task=task, name=experiment_name)

    print("Adding asset dir...")
    task.common_assets.add_directory(assets_directory=manifest.ser_out_path)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        exit()

    print(f"Experiment {experiment.uid} succeeded.")

    # Save experiment id to file
    with open("experiment_id", "w") as fd:
        fd.write(experiment.uid.hex)
    print()
    print(experiment.uid.hex)


def run_example():
    # 1)  replace genomes in the serialized file created by burnin_create_parasite_genetics example
    source_dtk = Path(manifest.ser_path, manifest.source)
    destination_dtk = Path(manifest.ser_out_path, manifest.destination)
    get_next_barcode_fn = replace_genomes_get_next_barcode.get_next_barcode
    replace_genomes.replace_genomes(source_dtk, get_next_barcode_fn, destination_dtk)
    
    # 2) Check that modified dtk file contains the correct barcodes
    importlib.reload(replace_genomes_get_next_barcode)  # reimport module to reinitialize variables in module containing function to get next barcode
    replace_genomes.test_replace_genomes(destination_dtk, get_next_barcode_fn)

    # 3) Run sim with the modified file
    general_sim()



if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(Path(manifest.eradication_path).parent)
    run_example()

