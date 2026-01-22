#!/usr/bin/env python3


# idmtools ...
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from idmtools.builders import SimulationBuilder
# importing all the reports functions, they all start with add_
from emodpy_malaria.reporters.builtin import *

import manifest

"""
    This is an example that (somewhat) replicates Jon Russel's workflow with emodpy_malaria tools
"""


def build_campaign():
    """
        Addind one intervention, so this template is easier to use when adding other interventions, replacing this one
    Returns:
        campaign object
    """

    import emod_api.campaign as campaign
    from emodpy_malaria.interventions.outbreak import add_outbreak_malaria_genetics
    import emodpy_malaria.interventions.drug_campaign as drug_campaign
    import emodpy_malaria.interventions.spacespraying as space_spray

    # passing in schema file to verify that everything is correct.
    campaign.set_schema(manifest.schema_file)

    # set up outbreak
    allele_frequencies = [[1.00, 0.00, 0.00, 0.00], [0.00, 1.00, 0.00, 0.00], [0.00, 0.00, 1.00, 0.00],
                          [0.00, 0.00, 0.00, 1.00], [0.50, 0.50, 0.00, 0.00], [0.00, 0.50, 0.50, 0.00],
                          [0.00, 0.00, 0.50, 0.50], [0.25, 0.25, 0.25, 0.25], [0.10, 0.20, 0.30, 0.40],
                          [0.40, 0.30, 0.20, 0.10], [1.00, 0.00, 0.00, 0.00], [0.00, 1.00, 0.00, 0.00],
                          [0.00, 0.00, 1.00, 0.00], [0.00, 0.00, 0.00, 1.00], [0.50, 0.50, 0.00, 0.00],
                          [0.00, 0.50, 0.50, 0.00], [0.00, 0.00, 0.50, 0.50], [0.25, 0.25, 0.25, 0.25],
                          [0.10, 0.20, 0.30, 0.40], [0.40, 0.30, 0.20, 0.10], [1.00, 0.00, 0.00, 0.00],
                          [0.10, 0.20, 0.30, 0.40], [0.40, 0.30, 0.20, 0.10], [1.00, 0.00, 0.00, 0.00]
                          ]
    add_outbreak_malaria_genetics(campaign, start_day=4,
                                  target_num_individuals=25,
                                  create_nucleotide_sequence_from="ALLELE_FREQUENCIES",
                                  barcode_allele_frequencies_per_genome_location=allele_frequencies,
                                  drug_resistant_allele_frequencies_per_genome_location=[
                                      [0.7, 0.3, 0, 0]])

    space_spray.add_scheduled_space_spraying(campaign, start_day=20, spray_coverage=0.34,
                                             killing_initial_effect=0.88, killing_box_duration=12,
                                             killing_decay_time_constant=10)

    drug_campaign.add_drug_campaign(campaign=campaign, campaign_type="MDA", drug_code="AL", start_days=[11],
                                    repetitions=3, tsteps_btwn_repetitions=3, coverage=0.3,
                                    receiving_drugs_event_name="MDA")

    return campaign


def sweep_run_number(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


# experiment design
def update_larval_habitats(simulation, scale_factor):
    seasonality_type = "constant_capacity"
    seasonality_types = {'seasonal_capacity': [3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8, 6.5, 2.6, 2.1],
                         'constant_capacity': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                         }
    for species_params in simulation.task.config.parameters.Vector_Species_Params:
        habitats = species_params.Habitats
        for habitat in habitats:
            if habitat.Habitat_Type == "LINEAR_SPLINE":
                habitat.Max_Larval_Capacity = habitat.Max_Larval_Capacity * scale_factor
                habitat.Capacity_Distribution_Over_Time.Values = seasonality_types[seasonality_type]
    return {"scale_factor": scale_factor}


def set_config_parameters(config, habitat_scale_factor=1, seasonality_type='seasonal_capacity'):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    # You have to set simulation type explicitly before you set other parameters for the simulation

    # sets "default" parasite genetics parameters based on Jon Russel's config files
    import emodpy_malaria.malaria_config as malaria_config
    var_gene_randomness = "FIXED_NEIGHBORHOOD"  # you can pass this to set_parasite_genetics_params
    config = malaria_config.set_parasite_genetics_params(config, manifest, var_gene_randomness)
    # config.parameters.Var_Gene_Randomness_Type = "MSP_FIXED" # workaround due to inability to set this directly
    population_scale_factor = 0.6
    years = 1.1
    serialize_year = 1
    s_pop_filename = ""

    config.parameters.x_Base_Population = population_scale_factor
    config.parameters.Simulation_Duration = (years * 365) + 1

    # -------SERIALIZATION-----

    config.parameters.Serialization_Time_Steps = [serialize_year * 365]
    config.parameters.Serialized_Population_Writing_Type = "TIMESTEP"
    config.parameters.Serialized_Population_Reading_Type = "NONE"
    config.parameters.Serialization_Mask_Node_Write = 0
    # config.parameters.Serialization_Mask_Node_Read = 0
    config.parameters.Serialization_Precision = "REDUCED"
    # config.parameters.Serilization_Filenames = [s_pop_filename]
    # config.parameters.Serialized_Population_Path = r".\Assets"
    # config.parameters.Enable_Random_Generator_From_Serialized_Population = 0

    # adding drug resistances to drugs
    config.parameters.Parasite_Genetics.Drug_Resistant_Genome_Locations = [218302]
    malaria_config.add_drug_resistance(config, manifest, drugname='Artemether', drug_resistant_string="A",
                                       pkpd_c50_modifier=1000, max_irbc_kill_modifier=0.23)
    malaria_config.add_drug_resistance(config, manifest, drugname='Artemether', drug_resistant_string="T",
                                       pkpd_c50_modifier=122, max_irbc_kill_modifier=0.09)
    malaria_config.add_drug_resistance(config, manifest, drugname='Lumefantrine', drug_resistant_string="G",
                                       pkpd_c50_modifier=827, max_irbc_kill_modifier=0.73)

    return config


def build_demographics():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog
    settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in
    emod-api as much as possible.

    """
    import emodpy_malaria.demographics.MalariaDemographics as Demographics  # OK to call into emod-api

    demographics = Demographics.from_template_node(lat=0, lon=0, pop=10000, name=1, forced_id=1, init_prev=0)
    return demographics


def general_sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")
    report_year = 0.5
    years_to_report = 1

    experiment_name = "Malaria Parasite Genetics example"

    # create EMODTask
    print("Creating EMODTask (from files)...")
    task = emod_task.EMODTask.from_default2(
        config_path="config.json",
        eradication_path=manifest.eradication_path,
        campaign_builder=build_campaign,
        schema_path=manifest.schema_file,
        ep4_custom_cb=None,
        param_custom_cb=set_config_parameters,
        demog_builder=build_demographics
    )
    
    # set the singularity image to be used when running this experiment
    task.set_sif(manifest.sif_path)
    
    # set up sweeps
    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, [1, 4])
    builder.add_sweep_definition(update_larval_habitats, [0.3, 0.4])

    """THIS IS WHERE WE ADD THE REPORTS"""
    # ReportDrugStatus
    add_sql_report_malaria_genetics(task, manifest, start_day=13, end_day=92, include_infection_table=True,
                                    include_health_table=True,
                                    include_drug_table=True, include_individual_properties=False)
    add_report_fpg_output(task, manifest, start_day=300, end_day=380,
                          min_age_years=3, max_age_years=15, include_genome_ids=True,
                          minimum_parasite_density=3.3, sampling_period=5)
    add_report_fpg_new_infections(task, manifest, start_day=300, end_day=380,
                                  min_age_years=3, max_age_years=15, filename_suffix="NewInfections")

    # We are creating one-simulation experiment straight from task.
    # If you are doing a sweep, please see sweep_* examples.
    # create experiment from builder
    experiment = Experiment.from_builder(builder, task, name=experiment_name)
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


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    import pathlib

    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    general_sim()
