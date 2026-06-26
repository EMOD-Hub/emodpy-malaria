import math
import csv
import os
import warnings

import emod_api.schema_to_class as s2c
from emodpy_malaria.malaria_vector_species_params import species_params

from emodpy_malaria.utils.emod_enum import (
    InnateImmuneVariationType, MalariaStrainModel, ParasiteSwitchType,
    VarGeneRandomnessType, VectorSamplingType
)
from emodpy_malaria.utils.distributions import BaseDistribution, GaussianDistribution
from emodpy_malaria.drug_config import MalariaDrugTypeParameters, DrugModifier, DoseFractionByAge
from emodpy_malaria import vector_config
from emodpy_malaria.vector_config import (
    set_species_param,
    add_species,
    add_genes_and_alleles,
    add_mutation,
    create_trait,
    add_trait,
    add_blood_meal_mortality,
    add_insecticide_resistance,
    add_species_drivers,
    add_maternal_deposition,
    get_species_params,
    set_max_larval_capacity,
    add_microsporidia,
    add_vector_migration,
    VectorHabitat,
    VectorSpeciesParameters,
)

__all__ = [
    # malaria-specific
    "set_team_defaults",
    "set_team_drug_params",
    "set_parasite_genetics_params",
    "get_drug_params",
    "set_drug_param",
    "add_new_drug",
    "add_drug_resistance",
    # drug config classes
    "MalariaDrugTypeParameters",
    "DrugModifier",
    "DoseFractionByAge",
    # re-exported from vector_config
    "set_species_param",
    "add_species",
    "add_genes_and_alleles",
    "add_mutation",
    "create_trait",
    "add_trait",
    "add_blood_meal_mortality",
    "add_insecticide_resistance",
    "add_species_drivers",
    "add_maternal_deposition",
    "get_species_params",
    "set_max_larval_capacity",
    "add_microsporidia",
    "add_vector_migration",
    "VectorHabitat",
    "VectorSpeciesParameters",
]

#
# PUBLIC API section
#


def set_team_defaults(config, manifest):
    """
        Set configuration defaults using team-wide values, including drugs and vector species.
    """
    vector_config.set_team_defaults(config, manifest)
    config.parameters.Simulation_Type = "MALARIA_SIM"
    # removing Infectious_Period parameters because not allowed in MALARIA_SIM, but need in VECTOR SIM
    config.parameters.pop("Infectious_Period_Constant")
    config.parameters.pop("Infectious_Period_Distribution")
    config.parameters.Malaria_Strain_Model = MalariaStrainModel.FALCIPARUM_RANDOM_STRAIN
    config.parameters.Enable_Disease_Mortality = 0
    # config.parameters.Enable_Malaria_CoTransmission = 0

    # INFECTION
    config.parameters.Infection_Updates_Per_Timestep = 8
    config.parameters.Enable_Superinfection = 1
    config.parameters.Incubation_Period_Distribution = "CONSTANT_DISTRIBUTION"
    config.parameters.Incubation_Period_Constant = 7
    config.parameters.Antibody_IRBC_Kill_Rate = 1.596
    config.parameters.RBC_Destruction_Multiplier = 3.29
    config.parameters.Parasite_Switch_Type = ParasiteSwitchType.RATE_PER_PARASITE_7VARS

    # IMMUNITY; these are NOT schema defaults
    config.parameters.Antibody_CSP_Killing_Threshold = 20
    config.parameters.Antigen_Switch_Rate = math.pow(10, -9.116590124)
    config.parameters.Base_Gametocyte_Production_Rate = 0.06150582
    config.parameters.Base_Gametocyte_Mosquito_Survival_Rate = 0.002011099
    config.parameters.Innate_Immune_Variation_Type = InnateImmuneVariationType.NONE
    config.parameters.Pyrogenic_Threshold = 1.5e4
    config.parameters.Falciparum_MSP_Variants = 32
    config.parameters.Falciparum_Nonspecific_Types = 76
    config.parameters.Falciparum_PfEMP1_Variants = 1070
    config.parameters.Fever_IRBC_Kill_Rate = 1.4
    config.parameters.Gametocyte_Stage_Survival_Rate = 0.588569307
    config.parameters.Max_MSP1_Antibody_Growthrate = 0.045
    config.parameters.MSP1_Merozoite_Kill_Fraction = 0.511735322
    config.parameters.Max_Individual_Infections = 3
    config.parameters.Nonspecific_Antigenicity_Factor = 0.415111634
    config.parameters.Antibody_Capacity_Growth_Rate = 0.09
    config.parameters.Antibody_Stimulation_C50 = 30
    config.parameters.Antibody_Memory_Level = 0.34
    config.parameters.Min_Adapted_Response = 0.05
    config.parameters.Cytokine_Gametocyte_Inactivation = 0.01667
    config.parameters.Enable_Maternal_Antibodies_Transmission = 1
    config.parameters.Maternal_Antibodies_Type = "SIMPLE_WANING"
    config.parameters.Maternal_Antibody_Protection = 0.1327

    # SYMPTOMATICITY
    config.parameters.Anemia_Mortality_Inverse_Width = 1
    config.parameters.Anemia_Mortality_Threshold = 0.654726662830038
    config.parameters.Anemia_Severe_Inverse_Width = 10
    config.parameters.Anemia_Severe_Threshold = 4.50775824973078

    config.parameters.Fever_Mortality_Inverse_Width = 1895.51971624351
    config.parameters.Fever_Mortality_Threshold = 3.4005008555391
    config.parameters.Fever_Severe_Inverse_Width = 27.5653580403806
    config.parameters.Fever_Severe_Threshold = 3.98354299722192

    config.parameters.Parasite_Mortality_Inverse_Width = 327.51594505874
    config.parameters.Parasite_Mortality_Threshold = 10 ** 5.93
    config.parameters.Parasite_Severe_Inverse_Width = 56.5754896048744
    config.parameters.Parasite_Severe_Threshold = 10 ** 5.929945527

    config.parameters.Clinical_Fever_Threshold_High = 1.5
    config.parameters.Clinical_Fever_Threshold_Low = 0.5
    config.parameters.Min_Days_Between_Clinical_Incidents = 14

    # updated from mambrose Oct 11 2019, personal communication with M Plucinski
    config.parameters.PfHRP2_Boost_Rate = 0.018  # original value: 0.07
    config.parameters.PfHRP2_Decay_Rate = 0.167  # original value: 0.172

    config.parameters.Report_Detection_Threshold_Blood_Smear_Gametocytes = 20
    config.parameters.Report_Detection_Threshold_Blood_Smear_Parasites = 20
    config.parameters.Report_Detection_Threshold_Fever = 1.0
    config.parameters.Report_Detection_Threshold_PCR_Gametocytes = 0.05
    config.parameters.Report_Detection_Threshold_PCR_Parasites = 0.05
    config.parameters.Report_Detection_Threshold_PfHRP2 = 5.0
    config.parameters.Report_Detection_Threshold_True_Parasite_Density = 0.0

    config.parameters.Report_Gametocyte_Smear_Sensitivity = 0.1
    config.parameters.Report_Parasite_Smear_Sensitivity = 0.1  # 10/uL

    config = set_team_drug_params(config, manifest)

    return config


def set_team_drug_params(config, manifest):
    """
    Loads antimalarial drug parameters from the bundled CSV and appends them to
    the simulation config.

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest file containing the schema path

    Returns:
        (dict): configured config
    """
    csv_path = os.path.join(os.path.dirname(__file__), 'malaria_drug_params.csv')
    with open(csv_path, newline='') as csvfile:
        for row in csv.DictReader(csvfile):
            try:
                ages_str = row["Upper_Age_In_Years"].strip('[]').replace(' ', '')
                values_str = row["Fraction_Of_Adult_Dose"].strip('[]').replace(' ', '')
                if ages_str:
                    ages = [float(x) for x in ages_str.split(",")]
                    fractions = [float(x) for x in values_str.split(",")]
                    dose_fractions = [
                        DoseFractionByAge(age, frac)
                        for age, frac in zip(ages, fractions)
                    ]
                else:
                    dose_fractions = []
            except Exception as ex:
                warnings.warn(f"For drug {row['Name']}: {ex}. Defaulting to empty dose fractions.")
                dose_fractions = []

            drug = MalariaDrugTypeParameters(
                name=row["Name"],
                pkpd_model=row["PKPD_Model"],
                drug_cmax=float(row["Drug_Cmax"]),
                drug_decay_t1=float(row["Drug_Decay_T1"]),
                drug_decay_t2=float(row["Drug_Decay_T2"]),
                drug_vd=float(row["Drug_Vd"]),
                drug_pkpd_c50=float(row["Drug_PKPD_C50"]),
                drug_fulltreatment_doses=int(row["Drug_Fulltreatment_Doses"]),
                drug_dose_interval=float(row["Drug_Dose_Interval"]),
                drug_gametocyte02_killrate=float(row["Drug_Gametocyte02_Killrate"]),
                drug_gametocyte34_killrate=float(row["Drug_Gametocyte34_Killrate"]),
                drug_gametocytem_killrate=float(row["Drug_GametocyteM_Killrate"]),
                drug_hepatocyte_killrate=float(row["Drug_Hepatocyte_Killrate"]),
                max_drug_irbc_kill=float(row["Max_Drug_IRBC_Kill"]),
                bodyweight_exponent=float(row["Bodyweight_Exponent"]),
                fractional_dose_by_upper_age=dose_fractions,
            )
            config.parameters.Malaria_Drug_Params.append(drug.to_schema_dict(manifest))

    return config


def set_parasite_genetics_params(config, manifest,
                                 var_gene_randomness_type: VarGeneRandomnessType = VarGeneRandomnessType.ALL_RANDOM,
                                 sporozoites_per_oocyst: BaseDistribution = None):
    """
    Sets up the default parameters for parasite genetics simulations
    Malaria_Model = "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS"

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): schema path container
        var_gene_randomness_type (VarGeneRandomnessType): Controls randomness of var genes in new
            infections. Defaults to ``VarGeneRandomnessType.ALL_RANDOM``.
        sporozoites_per_oocyst (BaseDistribution): A [BaseDistribution](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/) that
            sets the Sporozoites_Per_Oocyst distribution parameters. Defaults to
            ``GaussianDistribution(mean=10000, std_dev=1000)``.

    Returns:
        (dict): configured config
    """
    if sporozoites_per_oocyst is None:
        sporozoites_per_oocyst = GaussianDistribution(mean=10000, std_dev=1000)
    if not isinstance(var_gene_randomness_type, VarGeneRandomnessType):
        try:
            var_gene_randomness_type = VarGeneRandomnessType(var_gene_randomness_type)
        except ValueError:
            valid_types = [v.value for v in VarGeneRandomnessType]
            raise ValueError(f"Invalid var_gene_randomness_type '{var_gene_randomness_type}'. "
                             f"Must be one of: {valid_types}")

    set_team_defaults(config, manifest)
    config.parameters.pop("Malaria_Strain_Model")  # removing incompatible Malaria_Strain_Model parameter
    # config.parameters.pop("Enable_Initial_Prevalence") # popping it here doesn't work
    config.parameters.Malaria_Model = "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS"
    config.parameters.Falciparum_MSP_Variants = 100
    config.parameters.Falciparum_Nonspecific_Types = 20
    config.parameters.Falciparum_PfEMP1_Variants = 1000
    config.parameters.Vector_Sampling_Type = VectorSamplingType.TRACK_ALL_VECTORS
    config.parameters.Max_Individual_Infections = 10
    # setting up Parasite_Genetics parameters
    fpg = s2c.get_class_with_defaults("idmType:ParasiteGenetics", schema_path=manifest.schema_file)
    fpg.Var_Gene_Randomness_Type = var_gene_randomness_type
    fpg.Sporozoite_Life_Expectancy = 25
    fpg.Num_Sporozoites_In_Bite_Fail = 12
    fpg.Probability_Sporozoite_In_Bite_Fails = 0.5
    fpg.Num_Oocyst_From_Bite_Fail = 3
    fpg.Probability_Oocyst_From_Bite_Fails = 0.5
    sporozoites_per_oocyst.set_intervention_distribution(fpg, "Sporozoites_Per_Oocyst")
    fpg.Crossover_Gamma_K = 2
    fpg.Crossover_Gamma_Theta = 0.38
    fpg.Drug_Resistant_Genome_Locations = []
    fpg.Barcode_Genome_Locations = [
        311500,
        1116500,
        2140000,
        3290000,
        4323333,
        4756667,
        5656667,
        6123333,
        7056667,
        7523333,
        8423333,
        8856667,
        9790000,
        10290000,
        11356667,
        11923333,
        13156667,
        13823333,
        15256667,
        16023333,
        17690000,
        18590000,
        20590000,
        21690000
    ]
    if var_gene_randomness_type == VarGeneRandomnessType.FIXED_NEIGHBORHOOD or var_gene_randomness_type == VarGeneRandomnessType.FIXED_MSP:
        fpg.MSP_Genome_Location = 200000
        fpg.Neighborhood_Size_MSP = 4
        if var_gene_randomness_type == VarGeneRandomnessType.FIXED_NEIGHBORHOOD:
            fpg.PfEMP1_Variants_Genome_Locations = [
                214333,
                428667,
                958667,
                1274333,
                1864900,
                2139900,
                2414900,
                2989900,
                3289900,
                3589900,
                4150000,
                4410000,
                4670000,
                4930000,
                5470000,
                5750000,
                6030000,
                6310000,
                6870000,
                7150000,
                7430000,
                7710000,
                8250000,
                8510000,
                8770000,
                9030000,
                9590000,
                9890000,
                10190000,
                10490000,
                11130000,
                11470000,
                11810000,
                12150000,
                12890000,
                13290000,
                13690000,
                14090000,
                14950000,
                15410000,
                15870000,
                16330000,
                17330000,
                17870000,
                18410000,
                18950000,
                20150000,
                20810000,
                21470000,
                22130000
            ]
            fpg.Neighborhood_Size_PfEMP1 = 10
    config.parameters.Parasite_Genetics = fpg
    # setting up gambiae parameters for parasite genetics
    fpg_gambiae_params = species_params(manifest, "fpg_gambiae")
    config.parameters.Vector_Species_Params = [fpg_gambiae_params]
    # end vector species
    return config


def get_drug_params(cb, drug_name):
    for idx, drug_params in enumerate(cb.parameters.Malaria_Drug_Params):
        if drug_params.Name == drug_name:
            return cb.parameters.Malaria_Drug_Params[idx]
    raise ValueError(f"{drug_name} not found.")


def add_new_drug(config, manifest, drug: MalariaDrugTypeParameters, overwrite: bool = False):
    """
    Adds a new drug to the simulation's **Malaria_Drug_Params** list.

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest file containing the schema path
        drug (MalariaDrugTypeParameters): fully configured drug object
        overwrite (bool): If ``True`` and a drug with the same name already exists,
            replace it. If ``False`` (default), raise ``ValueError`` on duplicate names.

    Returns:
        (dict): configured config

    **Example**::

        drug = MalariaDrugTypeParameters(
            name="MyNewDrug",
            pkpd_model=PKPDModel.CONCENTRATION_VERSUS_TIME,
            drug_cmax=200,
            drug_decay_t1=0.5,
            max_drug_irbc_kill=6.0,
        )
        add_new_drug(config, manifest, drug)
    """
    if not isinstance(drug, MalariaDrugTypeParameters):
        raise ValueError(
            f"'drug' must be a MalariaDrugTypeParameters instance, "
            f"got {type(drug).__name__}.")

    for idx, existing in enumerate(config.parameters.Malaria_Drug_Params):
        if existing.Name == drug.name:
            if overwrite:
                config.parameters.Malaria_Drug_Params[idx] = drug.to_schema_dict(manifest)
                return config
            raise ValueError(
                f"Drug '{drug.name}' already exists. "
                f"Set overwrite=True to replace it.")

    config.parameters.Malaria_Drug_Params.append(drug.to_schema_dict(manifest))
    return config


def set_drug_param(config, drug_name: str = None, parameter: str = None, value: any = None):
    """
     Set a drug parameter, by passing in drug name, parameter and the parameter value.
     Added to facilitate adding drug Resistances,
     **Example**::

         artemether_drug_resistance = [{
            "Drug_Resistant_String": "A",
            "PKPD_C50_Modifier": 2.0,
            "Max_IRBC_Kill_Modifier": 0.9}]
         set_drug_param(cb, drug_name='Artemether', parameter="Resistances", value=artemether_drug_resistance)

    Args:
        config (dict): schema-backed config smart dict
        drug_name (str): The drug that has a **parameter** to set
        parameter (str): The parameter to set
        value (any): The new value to set
    """

    if not drug_name or not parameter or value is None:
        raise Exception("Please pass in all: drug_name, parameter, and value.\n")
    for drug in config.parameters.Malaria_Drug_Params:
        if drug.Name == drug_name:
            if parameter not in drug:
                warnings.warn(f"Parameter '{parameter}' not found in drug '{drug_name}' parameters. "
                              f"It will be added — verify the spelling is correct.")
            drug[parameter] = value
            return  # should I return anything here?
    raise ValueError(f"{drug_name} not found.\n")


def add_drug_resistance(config, manifest, drugname: str, drug_resistant_string: str,
                        pkpd_c50_modifier: float = 1.0, max_irbc_kill_modifier: float = 1.0):
    """
    Adds a drug resistance modifier to an existing drug in the simulation config.

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest file containing the schema path
        drugname (str): name of the drug for which to assign resistances
        drug_resistant_string (str): Nucleotide base letters (A, C, G, T) representing
            resistance at specific genome locations.
        pkpd_c50_modifier (float): Multiplier applied to the drug's Drug_PKPD_C50
            when the parasite genome matches. Genomes with multiple markers have
            modifiers multiplied together. Default: 1.0.
        max_irbc_kill_modifier (float): Multiplier applied to the drug's
            Max_Drug_IRBC_Kill when the parasite genome matches. Default: 1.0.

    Returns:
        (dict): configured config
    """
    modifier = DrugModifier(
        drug_resistant_string=drug_resistant_string,
        pkpd_c50_modifier=pkpd_c50_modifier,
        max_irbc_kill_modifier=max_irbc_kill_modifier,
    )

    for drug_param in config.parameters.Malaria_Drug_Params:
        if drug_param.Name == drugname:
            drug_param.Resistances.append(modifier.to_schema_dict(manifest))
            return config

    raise ValueError(f"Drug name {drugname} not found.\n")
