import emod_api.config.default_from_schema_no_validation as dfs
import csv
import os
from . import vector_config
from emodpy_malaria.malaria_vector_species_params import species_params


#
# PUBLIC API section
#

def get_file_from_http(url):
    """
        Get data files from simple http server.
    """
    import urllib.request as req
    import tempfile

    path = tempfile.NamedTemporaryFile()
    path.close()
    req.urlretrieve(url, path.name)
    return path.name


def set_team_defaults(config, manifest):
    """
        Set configuration defaults using team-wide values, including drugs and vector species.
    """
    vector_config.set_team_defaults(config, manifest)
    config.parameters.Simulation_Type = "MALARIA_SIM"
    # removing Infectious_Period parameteres because not allowed in MALARIA_SIM, but need in VECTOR SIM
    config.parameters.pop("Infectious_Period_Constant")
    config.parameters.pop("Infectious_Period_Distribution")
    config.parameters.Malaria_Strain_Model = "FALCIPARUM_RANDOM_STRAIN"
    config.parameters.Enable_Disease_Mortality = 0
    # config.parameters.Enable_Malaria_CoTransmission = 0

    # INFECTION
    config.parameters.Max_MSP1_Antibody_Growthrate = 0
    config.parameters.Min_Adapted_Response = 0
    config.parameters.Infection_Updates_Per_Timestep = 8
    config.parameters.Enable_Superinfection = 1
    config.parameters.Incubation_Period_Distribution = "CONSTANT_DISTRIBUTION"
    config.parameters.Incubation_Period_Constant = 7
    config.parameters.Antibody_IRBC_Kill_Rate = 1.596
    config.parameters.RBC_Destruction_Multiplier = 3.29
    config.parameters.Parasite_Switch_Type = "RATE_PER_PARASITE_7VARS"

    # 150305 calibration by JG to Burkina data + 6 of Kevin's sites
    # N.B: severe disease re-calibration not done
    # 'Base_Gametocyte_Production_Rate': 0.044,
    # config.parameters.Gametocyte_Stage_Survival_Rate = 0.82,
    # 'Antigen_Switch_Rate': 2.96e-9,
    # 'Falciparum_PfEMP1_Variants': 1112,
    # 'Falciparum_MSP_Variants': 7,
    # 'MSP1_Merozoite_Kill_Fraction': 0.43,
    # 'Falciparum_Nonspecific_Types': 90,
    # 'Nonspecific_Antigenicity_Factor': 0.42,
    # 'Base_Gametocyte_Mosquito_Survival_Rate': 0.00088,
    # config.parameters.Max_Individual_Infections = 5,

    # 180824 Prashanth parameters [description?]
    import math
    config.parameters.Antigen_Switch_Rate = math.pow(10, -9.116590124)
    config.parameters.Base_Gametocyte_Production_Rate = 0.06150582
    config.parameters.Base_Gametocyte_Mosquito_Survival_Rate = 0.002011099
    config.parameters.Falciparum_MSP_Variants = 32
    config.parameters.Falciparum_Nonspecific_Types = 76
    config.parameters.Falciparum_PfEMP1_Variants = 1070
    config.parameters.Gametocyte_Stage_Survival_Rate = 0.588569307
    config.parameters.MSP1_Merozoite_Kill_Fraction = 0.511735322
    config.parameters.Max_Individual_Infections = 3
    config.parameters.Nonspecific_Antigenicity_Factor = 0.415111634

    # IMMUNITY; these are NOT schema defaults
    config.parameters.Antibody_CSP_Killing_Threshold = 20
    config.parameters.Antigen_Switch_Rate = math.pow(10, -9.116590124)
    config.parameters.Base_Gametocyte_Production_Rate = 0.06150582
    config.parameters.Base_Gametocyte_Mosquito_Survival_Rate = 0.002011099
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
    # TBD: load csv with drug params and populate from that.
    with open(os.path.join(os.path.dirname(__file__), 'malaria_drug_params.csv'), newline='') as csvfile:
        my_reader = csv.reader(csvfile)

        header = next(my_reader)
        drug_name_idx = header.index("Name")
        drug_pkpd_model_idx = header.index("PKPD_Model")
        drug_cmax_idx = header.index("Drug_Cmax")
        drug_decayt1_idx = header.index("Drug_Decay_T1")
        drug_decayt2_idx = header.index("Drug_Decay_T2")
        drug_vd_idx = header.index("Drug_Vd")
        drug_pkpdc50_idx = header.index("Drug_PKPD_C50")
        drug_ftdoses_idx = header.index("Drug_Fulltreatment_Doses")
        drug_dose_interval_idx = header.index("Drug_Dose_Interval")
        drug_gam02_idx = header.index("Drug_Gametocyte02_Killrate")
        drug_gam34_idx = header.index("Drug_Gametocyte34_Killrate")
        drug_gamM_idx = header.index("Drug_GametocyteM_Killrate")
        drug_hep_idx = header.index("Drug_Hepatocyte_Killrate")
        drug_maxirbc_idx = header.index("Max_Drug_IRBC_Kill")
        drug_adher_idx = header.index("Drug_Adherence_Rate")
        drug_bwexp_idx = header.index("Bodyweight_Exponent")
        drug_fracdos_key_idx = header.index("Upper_Age_In_Years")
        drug_fracdos_val_idx = header.index("Fraction_Of_Adult_Dose")

        # for each
        for row in my_reader:
            mdp = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:MalariaDrugTypeParameters"])
            mdp.parameters.Drug_Cmax = float(row[drug_cmax_idx])
            mdp.parameters.Drug_Decay_T1 = float(row[drug_decayt1_idx])
            mdp.parameters.Drug_Decay_T2 = float(row[drug_decayt2_idx])
            mdp.parameters.Drug_Vd = float(row[drug_vd_idx])
            mdp.parameters.Drug_PKPD_C50 = float(row[drug_pkpdc50_idx])
            mdp.parameters.Drug_Fulltreatment_Doses = float(row[drug_ftdoses_idx])
            mdp.parameters.Drug_Dose_Interval = float(row[drug_dose_interval_idx])
            mdp.parameters.Drug_Gametocyte02_Killrate = float(row[drug_gam02_idx])
            mdp.parameters.Drug_Gametocyte34_Killrate = float(row[drug_gam34_idx])
            mdp.parameters.Drug_GametocyteM_Killrate = float(row[drug_gamM_idx])
            mdp.parameters.Drug_Hepatocyte_Killrate = float(row[drug_hep_idx])
            mdp.parameters.Max_Drug_IRBC_Kill = float(row[drug_maxirbc_idx])
            mdp.parameters.PKPD_Model = row[drug_pkpd_model_idx]
            mdp.parameters.Name = row[drug_name_idx]
            # mdp.parameters.Drug_Adherence_Rate = float(row[ drug_adher_idx ])
            mdp.parameters.Bodyweight_Exponent = float(row[drug_bwexp_idx])

            try:
                key = row[drug_fracdos_key_idx].strip('[]').replace(' ','')
                if len(key) > 0:
                    ages = [float(x) for x in row[drug_fracdos_key_idx].strip('[]').split(",")]
                    values = [float(x) for x in row[drug_fracdos_val_idx].strip('[]').split(",")]
            except Exception as ex:
                print("For drug {}, {}".format(row[0], str(ex)))
                ages = []
                values = []
            for idx in range(len(ages)):
                fdbua = dict()
                # this is what we want but not ready yet 
                # fdbua = dfs.schema_to_config_subnode(mani.schema_file, ["idmTypes","idmType:DoseMap"] )
                # fdbua.Upper_Age_In_Years = ages[idx]
                # fdbua.Fraction_Of_Adult_Dose = values[idx]
                fdbua["Upper_Age_In_Years"] = ages[idx]
                fdbua["Fraction_Of_Adult_Dose"] = values[idx]
                # fdbua.finalize()
                mdp.parameters.Fractional_Dose_By_Upper_Age.append(fdbua)

            config.parameters.Malaria_Drug_Params.append(mdp.parameters)
    # end

    return config


def set_parasite_genetics_params(config, manifest, var_gene_randomness_type: str = "ALL_RANDOM"):
    """
    Sets up the default parameters for parasite genetics simulations
    Malaria_Model = "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS"

    Args:
        config: schema-backed config smart dict
        manifest: schema path container
        var_gene_randomness_type: possible values are "FIXED_NEIGHBORHOOD", "FIXED_MSP", "ALL_RANDOM" (default)

    Returns:
        configured config
    """
    set_team_defaults(config, manifest)
    config.parameters.pop("Malaria_Strain_Model")  # removing incompatible Malaria_Strain_Model parameter
    # config.parameters.pop("Enable_Initial_Prevalence") # popping it here doesn't work
    config.parameters.Malaria_Model = "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS"
    config.parameters.Falciparum_MSP_Variants = 100
    config.parameters.Falciparum_Nonspecific_Types = 20
    config.parameters.Falciparum_PfEMP1_Variants = 1000
    config.parameters.Vector_Sampling_Type = "TRACK_ALL_VECTORS"
    config.parameters.Max_Individual_Infections = 10
    # setting up Parasite_Genetics parameteres
    fpg = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:ParasiteGenetics"])
    fpg.parameters.Var_Gene_Randomness_Type = var_gene_randomness_type
    fpg.parameters.Sporozoite_Life_Expectancy = 25
    fpg.parameters.Num_Sporozoites_In_Bite_Fail = 12
    fpg.parameters.Probability_Sporozoite_In_Bite_Fails = 0.5
    fpg.parameters.Num_Oocyst_From_Bite_Fail = 3
    fpg.parameters.Probability_Oocyst_From_Bite_Fails = 0.5
    fpg.parameters.Sporozoites_Per_Oocyst_Distribution = "GAUSSIAN_DISTRIBUTION"
    fpg.parameters.Sporozoites_Per_Oocyst_Gaussian_Mean = 10000
    fpg.parameters.Sporozoites_Per_Oocyst_Gaussian_Std_Dev = 1000
    fpg.parameters.Crossover_Gamma_K = 2
    fpg.parameters.Crossover_Gamma_Theta = 0.38
    fpg.parameters.Drug_Resistant_Genome_Locations = []
    fpg.parameters.Barcode_Genome_Locations = [
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
    if var_gene_randomness_type == "FIXED_NEIGHBORHOOD" or var_gene_randomness_type == "FIXED_MSP":
        fpg.parameters.MSP_Genome_Location = 200000
        fpg.parameters.Neighborhood_Size_MSP = 4
        if var_gene_randomness_type == "FIXED_NEIGHBORHOOD":
            fpg.parameters.PfEMP1_Variants_Genome_Locations = [
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
            fpg.parameters.Neighborhood_Size_PfEMP1 = 10
    config.parameters.Parasite_Genetics = fpg.parameters
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
        config: schema-backed config smart dict
        drug_name: The drug that has a parameter to set
        parameter: The parameter to set
        value: The new value to set

    Returns:
        Nothing or error if drug name is not found
    """

    if not drug_name or not parameter or not value:
        raise Exception("Please pass in all: drug_name, parameter, and value.\n")
    for drug in config.parameters.Malaria_Drug_Params:
        if drug.Name == drug_name:
            drug[parameter] = value
            return  # should I return anything here?
    raise ValueError(f"{drug_name} not found.\n")


def add_drug_resistance(config, manifest, drugname: str = None, drug_resistant_string: str = None,
                        pkpd_c50_modifier: float = 1.0, max_irbc_kill_modifier: float = 1.0):
    """
    Adds drug resistances by drug name and parameters

    Args:
        config: schema-backed config smart dict
        manifest: manifest file containing the schema path
        drugname: name of the drug for which to assign resistances
        drug_resistant_string: A series of nucleotide base letters (A, C, G, T) that represent the drug resistant
            values at locations in the genome
        pkpd_c50_modifier: If the parasite has this genome marker, this value will be multiplied times the
            'Drug_PKPD_C50' value of the drug. Genomes with multiple markers will be simply multiplied together
        max_irbc_kill_modifier: If the parasite has this genome marker, this value will be multiplied times the
            'Max_Drug_IRBC_Kill' value of the drug.  Genomes with multiple markers will be simply multiplied together

    Returns:
        configured config
    """

    drugmod = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:DrugModifier"])
    drugmod.parameters.Drug_Resistant_String = drug_resistant_string
    drugmod.parameters.Max_IRBC_Kill_Modifier = max_irbc_kill_modifier
    drugmod.parameters.PKPD_C50_Modifier = pkpd_c50_modifier

    for drug_param in config.parameters.Malaria_Drug_Params:
        if drug_param.Name == drugname:
            drug_param.Resistances.append(drugmod.parameters)
            return config

    raise ValueError(f"Drug name {drugname} not found.\n")


def set_species_param(config, species, parameter, value, overwrite=False):
    """
        Pass through for vector version of function.
    """
    return vector_config.set_species_param(config, species, parameter, value, overwrite=overwrite)


def add_species(config, manifest, species_to_select):
    """
        Pass through for vector version of function.
    """
    vector_config.add_species(config, manifest, species_to_select)


def add_insecticide_resistance(config, manifest, insecticide_name: str = "", species: str = "",
                               allele_combo: list = None, blocking: float = 1.0, killing: float = 1.0,
                               repelling: float = 1.0, larval_killing: float = 1.0):
    """
        Pass through for vector version of function.
    """
    vector_config.add_insecticide_resistance(config, manifest, insecticide_name, species,
                                             allele_combo, blocking, killing,
                                             repelling, larval_killing)


def get_species_params(config, species: str = None):
    """
        Pass through for vector version of function.
    """
    return vector_config.get_species_params(config, species)


def set_max_larval_capacity(config, species_name: str, habitat_type: str, max_larval_capacity: int):
    """
    Set the Max_Larval_Capacity for a given species and habitat. Effectively doing something like:
    simulation.task.config.parameters.Vector_Species_Params[i]["Habitats"][j]["Max_Larval_Capacity"] = max_larval_capacity
    where i is index of species_name and j is index of habitat_type.

    Args:
        config: schema-backed config smart dict
        species_name: string. Species_Name to target.
        habitat_type: enum. Habitat_Type to target.
        max_larval_capacity: integer. New value of Max_Larval_Capacity.

    Returns:
        Nothing.

    """
    return vector_config.set_max_larval_capacity(config, species_name, habitat_type, max_larval_capacity)


def add_microsporidia(config, manifest, species_name: str = None,
                      strain_name: str = "Strain_A",
                      female_to_male_probability: float = 0,
                      female_to_egg_probability: float = 0,
                      male_to_female_probability: float = 0,
                      male_to_egg_probability: float = 0,
                      duration_to_disease_acquisition_modification: dict = None,
                      duration_to_disease_transmission_modification: dict = None,
                      larval_growth_modifier: float = 1,
                      female_mortality_modifier: float = 1,
                      male_mortality_modifier: float = 1):
    """
        Adds microsporidia parameters to the named species' parameters.

    Args:
        config: schema-backed config dictionary, written to config.json
        manifest: file that contains path to the schema file
        species_name: Species to target, **Name** parameter
        strain_name: **Strain_Name** The name/identifier of the collection of transmission parameters.
            Cannot be empty string
        female_to_male_probability: **Microsporidia_Female_to_Male_Transmission_Probability** The probability
            an infected female will infect an uninfected male.
        female_to_egg_probability: **Microsporidia_Female_To_Egg_Transmission_Probability** The probability
            an infected female will infect her eggs when laying them.
        male_to_female_probability: **Microsporidia_Male_To_Female_Transmission_Probability** The probability
            an infected male will infect an uninfected female
        male_to_egg_probability: **Microsporidia_Male_To_Egg_Transmission_Probability** The probability a female that
            mated with an infected male will infect her eggs when laying them, independent of her being infected and
            transmitting to her offspring.
        duration_to_disease_acquisition_modification: **Microsporidia_Duration_To_Disease_Acquisition_Modification**,
            A dictionary for "Times" and "Values" as an age-based modification that the female will acquire malaria.
            **Times** is an array of days in ascending order that represent the number of days since the vector became
            infected. **Values** is an array of probabilities with values from 0 to 1 where each probability is the
            probability that the vector will acquire malaria due to Microsporidia.

             **Example**::

                {
                    "Times": [    0,   3,   6,   9 ],
                    "Values": [ 1.0, 1.0, 0.5, 0.0 ]
                }
        duration_to_disease_transmission_modification: **Microsporidia_Duration_To_Disease_Transmission_Modification**,
            A dictionary for "Times" and "Values" as an age-based modification that the female will transmit malaria.
            **Times** is an array of days in ascending order that represent the number of days since the vector became
            infected. **Values** is an array of probabilities with values from 0 to 1 where each probability is the
            probability that the vector will acquire malaria due to Microsporidia.

             **Example**::

                {
                    "Times": [    0,   3,   6,   9 ],
                    "Values": [ 1.0, 1.0, 0.75, 0.5]
                }
        larval_growth_modifier: **Microsporidia_Larval_Growth_Modifier** A multiplier modifier to the daily, temperature
            dependent, larval growth progress.
        female_mortality_modifier: **Microsporidia_Female_Mortality_Modifier** A multiplier modifier on the death
            rate for female vectors due to general life expectancy, age, and dry heat
        male_mortality_modifier: **Microsporidia_Male_Mortality_Modifier** A multiplier modifier on the death rate for
            male vectors due to general life expectancy, age, and dry heat

    Returns:
        Nothing
    """
    vector_config.add_microsporidia(config, manifest,
                                    species_name=species_name,
                                    strain_name=strain_name,
                                    female_to_male_probability=female_to_male_probability,
                                    female_to_egg_probability=female_to_egg_probability,
                                    male_to_female_probability=male_to_female_probability,
                                    male_to_egg_probability=male_to_egg_probability,
                                    duration_to_disease_acquisition_modification=duration_to_disease_acquisition_modification,
                                    duration_to_disease_transmission_modification=duration_to_disease_transmission_modification,
                                    larval_growth_modifier=larval_growth_modifier,
                                    female_mortality_modifier=female_mortality_modifier,
                                    male_mortality_modifier=male_mortality_modifier)


def configure_linear_spline(manifest, max_larval_capacity: float = pow(10, 8),
                            capacity_distribution_number_of_years: int = 1,
                            capacity_distribution_over_time: dict = None):
    """
        Configures and returns a ReadOnlyDict of the LINEAR_SPLINE habitat parameters

    Args:
        manifest:  manifest file containing the schema path
        max_larval_capacity:  The maximum larval capacity. Sets **Max_Larval_Capacity**
        capacity_distribution_number_of_years:  The total length of time in
            years for the scaling.  If the simulation goes longer than this time, the pattern will repeat.  Ideally,
            this value times 365 is the last value in 'Capacity_Distribution_Over_Time'.
            Sets **Capacity_Distribution_Number_Of_Years**
        capacity_distribution_over_time:  "This allows one to scale the larval
            capacity over time.  The Times and Values arrays must be the same length where Times is in days and
            Values are a scale factor per degrees squared.  The value is multiplied times the max capacity and
            'Node_Grid_Size' squared/4. Ideally, you want the last value  to equal the first value if they are
            one day apart.  A point will be added if not. Sets **Capacity_Distribution_Over_Time**

            **Example**::

                {
                    "Times": [0,  30,  60,   91,  122, 152, 182, 213, 243, 274, 304, 334, 365 ],
                    "Values": [3, 0.8, 1.25, 0.1, 2.7, 8,    4,   35, 6.8, 6.5, 2.6, 2.1, 2]
                }

    Returns:
        Configured Habitat_Type: "LINEAR_SPLINE" parameters to be passed directly to "set_species_params" function
    """
    return vector_config.configure_linear_spline(manifest, max_larval_capacity, capacity_distribution_number_of_years,
                                                 capacity_distribution_over_time)
