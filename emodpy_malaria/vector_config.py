import emod_api.schema_to_class as s2c
import math
import os
from emodpy_malaria.malaria_vector_species_params import species_params
from enum import Enum
import copy


def _validate_allele_combo(species_params, allele_combo):
    """
    Internal method to validate that a user provided an acceptal allele_combo
    where it is a two dimentional array of strings and the inner array has 
    two elements where each element is an allele of the same gene.
    """
    if len(allele_combo) == 0:
        raise ValueError("allele_combo must define some alleles to target")
    
    for combo in allele_combo:
        if len(combo) != 2:
            raise ValueError(
                "Each combo in allele_combo must have two values - one for each chromosome, '*' is acceptable. \n")
        
    # Check that the alleles referenced here have been 'declared' previously
    allele_names = []
    allele_names_in_combo = []
    for gene in species_params.Genes:
        for allele in gene["Alleles"]:
            allele_names.append(allele["Name"])

    for combo in allele_combo:
        for allele_name in combo:
            if allele_name != "X" and allele_name != "Y" and allele_name != "*":
                allele_names_in_combo.append(allele_name)

    for alnic in allele_names_in_combo:
        if alnic not in allele_names:
            raise ValueError(f"Allele name {alnic} submitted in one of the allele_combos is not found"
                             f" in the Genes parameter for {species_params.Name}.\n")
        
    return


#
# PUBLIC API section
#
def set_team_defaults_vector(config):
    """
    Set configuration defaults using team-wide values, including drugs and vector species.

    Args:
        config: schema-backed config smart dict
        schema_json: json object that is the schema file

    Returns:
        configured config
    """

    # INFECTION
    config.parameters.Simulation_Type = "VECTOR_SIM"
    config.parameters.Infection_Updates_Per_Timestep = 8
    config.parameters.Incubation_Period_Constant = 7
    config.parameters.Infectious_Period_Constant = 7

    # VECTOR_SIM parameters (formerly lived in dtk-tools/dtk/vector/params.py)
    config.parameters.Enable_Vector_Species_Report = 0
    config.parameters.Vector_Sampling_Type = "VECTOR_COMPARTMENTS_NUMBER"
    # config.parameters.Mosquito_Weight = 1 # If this parameter is set, config.parameters.Vector_Sampling_Type is automatically changed to "SAMPLE_IND_VECTORS"

    config.parameters.Enable_Vector_Aging = 0
    config.parameters.Enable_Vector_Mortality = 1

    config.parameters.Age_Dependent_Biting_Risk_Type = "SURFACE_AREA_DEPENDENT"
    config.parameters.Human_Feeding_Mortality = 0.1

    config.parameters.Wolbachia_Infection_Modification = 1.0
    config.parameters.Wolbachia_Mortality_Modification = 1.0

    config.parameters.x_Temporary_Larval_Habitat = 1
    config.parameters.Vector_Species_Params = []
    config.parameters.Egg_Hatch_Density_Dependence = "NO_DENSITY_DEPENDENCE"
    config.parameters.Enable_Temperature_Dependent_Egg_Hatching = 0
    config.parameters.Enable_Egg_Mortality = 0
    config.parameters.Enable_Drought_Egg_Hatch_Delay = 0
    config.parameters.Insecticides = []

    # Other defaults from dtk-tools transition  #fixme very likely needs pruning
    config.parameters.Egg_Saturation_At_Oviposition = "SATURATION_AT_OVIPOSITION"
    config.parameters.Enable_Demographics_Reporting = 0
    # config.parameters.Enable_Rainfall_Stochasticity = 1
    config.parameters.Node_Grid_Size = 0.042
    # config.parameters.Population_Density_C50 = 30
    config.parameters.Population_Scale_Type = "FIXED_SCALING"

    # setting up parameters for climate constant
    config.parameters.Base_Rainfall = 10
    config.parameters.Base_Air_Temperature = 27
    config.parameters.Base_Land_Temperature = 27
    config.parameters.Base_Relative_Humidity = 0.75
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"
    config.parameters.Climate_Update_Resolution = "CLIMATE_UPDATE_DAY"  # not used with "CLIMATE_CONSTANT", nice to have
    config.parameters.Enable_Climate_Stochasticity = 0

    config.parameters.Simulation_Duration = 365
    config.parameters.Start_Time = 0  # default is 1, but interventions often start at 0, which will make them not work

    return config


def get_species_params(config, species: str = None):
    """
    Returns the species parameters dictionary with the matching species **Name**

    Args:
        config: schema-backed config smart dict
        species: Species to look up

    Returns:
        Dictionary of species parameters with the matching name
    """
    if not species:
        raise ValueError("Please define a species.")
    for vector_species in config.parameters.Vector_Species_Params:
        if vector_species.Name == species:
            return vector_species
    raise ValueError(f"Species {species} not found.")


def set_species_param(config, species, parameter, value, overwrite=False):
    """
        Sets a parameter value for a specific species.
        Raises value error if species not found

    Args:
        config: schema-backed config smart dict
        species: name of species for which to set the parameter
        parameter: parameter to set
        value: value to set the parameter to
        overwrite: if set to True and parameter is a list, overwrites the parameter with value, appends by default

    Returns:
        Nothing
    """

    vector_species = get_species_params(config, species)

    if parameter in vector_species:
        if isinstance(vector_species[parameter], list):
            if overwrite:
                if isinstance(value, list):
                    vector_species[parameter] = value
                else:
                    vector_species[parameter] = [value]
            else:
                if isinstance(value, list):
                    for val in value:
                        vector_species[parameter].append(val)
                else:
                    vector_species[parameter].append(value)
        else:
            vector_species[parameter] = value
    else:
        vector_species[parameter] = value


def configure_linear_spline(schema_json, max_larval_capacity: float = pow(10, 8),
                            capacity_distribution_number_of_years: int = 1,
                            capacity_distribution_over_time: dict = None):
    """
        Configures and returns a ReadOnlyDict of the LINEAR_SPLINE habitat parameters

    Args:
        schema_json: json object that is the schema file
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
        Configured Habitat_Type: "LINEAR_SPLINE" parameters to be passed directly to "set_species_param" function
    """
    if not capacity_distribution_over_time or "Times" not in capacity_distribution_over_time or "Values" not in capacity_distribution_over_time:
        raise ValueError("Please define capacity_distribution_over_time as a dictionary: {'Times':[], 'Values':[]}.\n")
    times_length = len(capacity_distribution_over_time["Times"])
    values_length = len(capacity_distribution_over_time["Values"])
    if not (values_length == times_length):
        raise ValueError(f"Please make sure the 'Times' and 'Values' lists in the capacity_distribution_over_time "
                         f"dictionary are of equal lengths. Currently 'Times' is {times_length} "
                         f"entrees and 'Values' is {values_length} entrees long.\n")

    habitat = s2c.get_class_with_defaults("idmType:VectorHabitat", schema_json=schema_json)
    habitat.Habitat_Type = "LINEAR_SPLINE"
    habitat.Max_Larval_Capacity = max_larval_capacity
    habitat.Capacity_Distribution_Number_Of_Years = capacity_distribution_number_of_years
    # adding larval capacity
    capacity_distribution =s2c.get_class_with_defaults("idmType:InterpolatedValueMap", schema_json=schema_json)
    capacity_distribution.Times = capacity_distribution_over_time["Times"]
    capacity_distribution.Values = capacity_distribution_over_time["Values"]
    habitat.Capacity_Distribution_Over_Time = capacity_distribution

    return habitat


def add_species(config, schema_json,species_to_select):
    """
    Adds species with preset parameters from 'malaria_vector_species_params.py', if species
    name not found - "gambiae" parameters are added and the new species name assigned.

    Args:
        config: schema-backed config smart dict
        schema_json: json object that is the schema file
        species_to_select: a list of species or a name of a single species you'd like to set from
            malaria_vector_species_params.py

    Returns:
        configured config
    """

    if type(species_to_select) is str:
        species_to_select = [species_to_select]

    for species in species_to_select:
        vector_species_parameters = species_params(schema_json, species)
        if isinstance(vector_species_parameters, list):
            raise ValueError(
                f"'{species}' species not found in list, available species are: {vector_species_parameters}. "
                f"We suggest adding 'gambiae' species and changing "
                f"the name and relevant parameters with set_species_param() or "
                f"adding your species to malaria_vector_species_params.py.\n")
        else:
            config.parameters.Vector_Species_Params.append(vector_species_parameters)

    return config


def add_genes_and_alleles(config, schema_json, species: str, alleles: list):
    """
        Adds alleles to a species

        **Example**::

            "Genes": [
                {
                    "Alleles": [
                        {
                            "Name": "X1",
                            "Initial_Allele_Frequency": 0.5,
                            "Is_Y_Chromosome": 0
                        },
                        {
                            "Name": "X2",
                            "Initial_Allele_Frequency": 0.25,
                            "Is_Y_Chromosome": 0
                        },
                        {
                            "Name": "Y1",
                            "Initial_Allele_Frequency": 0.15,
                            "Is_Y_Chromosome": 1
                        },
                        {
                            "Name": "Y2",
                            "Initial_Allele_Frequency": 0.1,
                            "Is_Y_Chromosome": 1
                        }
                    ],
                    "Is_Gender_Gene": 1,
                    "Mutations": []
                }
            ]

    Args:
        config: schema-backed config smart dict
        schema_json: json object that is the schema file
        species: species to which to assign the alleles
        alleles: List of tuples of (**Name**, **Initial_Allele_Frequency**, **Is_Y_Chromosome**) for a set of alleles
            or (**Name**, **Initial_Allele_Frequency**), 1/0 or True/False can be used for Is_Y_Chromosome,
            third parameter is assumed False (0). If the third parameter is set to 1 in any of the tuples,
            we assume, this is a gender gene.
            **Example**::

                [("X1", 0.25), ("X2", 0.35), ("Y1", 0.15), ("Y2", 0.25)]
                [("X1", 0.25, 0), ("X2", 0.35, 0), ("Y1", 0.15, 1), ("Y2", 0.25, 1)]

    Returns:
        configured config
    """

    gene_class = s2c.get_class_with_defaults("idmType:VectorGene", schema_json=schema_json)
    gene = copy.deepcopy(gene_class)
    for allele in alleles:
        vector_allele_class = s2c.get_class_with_defaults("idmType:VectorAllele", schema_json=schema_json)
        vector_allele = copy.deepcopy(vector_allele_class)
        vector_allele.Name = allele[0]
        vector_allele.Initial_Allele_Frequency = allele[1]
        if len(allele) == 3:
            if allele[2]:
                gene.Is_Gender_Gene = 1
                vector_allele.Is_Y_Chromosome = 1
        gene.Alleles.append(vector_allele)

    species_block = get_species_params(config, species)
    species_block.Genes.append(gene)

    return config


def add_mutation(config, schema_json, species, mutate_from, mutate_to, probability):
    """
    Adds to **Mutations** parameter in a Gene which has the matching **Alleles**

    Args:
        config: schema-backed config smart dict
         schema_json: json object that is the schema file
        species: Name of vector species to which we're adding mutations
        mutate_from: The allele in the gamete that could mutate
        mutate_to: The allele that this locus will change to during gamete generation
        probability: The probability that the allele will mutate from one allele to the other during the
            creation of the gametes

    Returns:
        configured config
    """

    these_species = get_species_params(config, species)
    found = False
    for gene in these_species["Genes"]:
        allele_names = []
        for allele in gene["Alleles"]:
            allele_names.append(allele["Name"])
        if mutate_from in allele_names and mutate_to in allele_names:
            found = True
            mutations =s2c.get_class_with_defaults("idmType:VectorAlleleMutation", schema_json=schema_json)
            mutations.Mutate_From = mutate_from
            mutations.Mutate_To = mutate_to
            mutations.Probability_Of_Mutation = probability
            gene.Mutations.append(mutations)

    if not found:
        raise ValueError(f"Allele name(s) '{mutate_from}' and/or '{mutate_to}' were not found for {species}.\n")

    return config


def create_trait(schema_json, trait: str = None, modifier: float = None,
                 sporozoite_barcode_string: str = None, gametocyte_a_barcode_string: str = None,
                 gametocyte_b_barcode_string: str = None):
    """
        Configures and returns a modifier trait.

    Args:
        schema_json: json object that is the schema file
        trait: The trait to be modified of vectors with the given allele combination.
            Available traits are: "INFECTED_BY_HUMAN", "FECUNDITY", "FEMALE_EGG_RATIO", "STERILITY",
            "TRANSMISSION_TO_HUMAN", "ADJUST_FERTILE_EGGS", "MORTALITY", "INFECTED_PROGRESS", "OOCYST_PROGRESSION",
            "SPOROZOITE_MORTALITY"
        modifier: The multiplier to use to modify the given trait for vectors with the given allele combination.
        sporozoite_barcode_string: TBD
        gametocyte_a_barcode_string: TBD
        gametocyte_b_barcode_string: TBD

    Returns:
        trait parameters that can be added to a list and passed to add_trait() function
    """
    traits_available = ["INFECTED_BY_HUMAN", "FECUNDITY", "FEMALE_EGG_RATIO", "STERILITY", "TRANSMISSION_TO_HUMAN",
                        "ADJUST_FERTILE_EGGS", "MORTALITY", "INFECTED_PROGRESS", "OOCYST_PROGRESSION",
                        "SPOROZOITE_MORTALITY"]
    if not trait or modifier is None:
        raise ValueError(f'Please define both trait and modifier. Available traits are: {traits_available}.\n')
    if trait == "OOCYST_PROGRESSION" and not (gametocyte_a_barcode_string and gametocyte_b_barcode_string):
        raise ValueError("With trait = 'OOCYST_PROGRESSION', you need to define gametocyte_a_barcode_string and "
                         "gametocyte_b_barcode_string. \n")
    if trait == "SPOROZOITE_MORTALITY" and not sporozoite_barcode_string:
        raise ValueError("With trait = 'SPOROZOITE_MORTALITY', you need to define sporozoite_barcode_string.\n")
    if trait not in traits_available:
        raise ValueError(f"Can't find trait '{trait}' in available traits. Traits available for use "
                         f"are {traits_available}")

    trait_modifier =s2c.get_class_with_defaults("idmType:TraitModifier", schema_json=schema_json)
    trait_modifier.Trait = trait
    trait_modifier.Modifier = modifier
    if trait == "SPOROZOITE_MORTALITY":
        trait_modifier.Sporozoite_Barcode_String = sporozoite_barcode_string
    if trait == "OOCYST_PROGRESSION":
        trait_modifier.Gametocyte_A_Barcode_String = gametocyte_a_barcode_string
        trait_modifier.Gametocyte_B_Barcode_String = gametocyte_b_barcode_string

    return trait_modifier


def add_trait(config, schema_json, species, allele_combo: list = None, trait_modifiers: list = None):
    """
    Use this function to add traits as part of vector genetics configuration, the trait is assigned to the
    species' **Gene_To_Trait_Modifiers** parameter
    Should produce something like **Example**::

                {
                    "Allele_Combinations" : [
                        [  "X",  "X" ],
                        [ "a0", "a1" ]
                    ],
                    "Trait_Modifiers" : [
                        {
                            "Trait" : "FECUNDITY",
                            "Modifier": 0.7
                        }
                    ]
                }

    Args:
        config: schema-backed config smart dict
        schema_json: json object that is the schema file
        species: **Name** of species for which to add this  **Gene_To_Trait_Modifiers**
        allele_combo: List of lists, This defines a possible subset of allele pairs that a vector could have.
            Each pair are alleles from one gene.  If the vector has this subset, then the associated traits will
            be adjusted.  Order does not matter.  '*' is allowed when only the occurrence of one allele is important.
            **Example**::

            [[  "X",  "X" ], [ "a0", "a1" ]]

        trait_modifiers: list of trait modifier parameters created with create_trait() function.

    Returns:
        configured config
    """
    species_params = get_species_params(config, species)
    _validate_allele_combo( species_params=species_params, allele_combo=allele_combo)

    if not trait_modifiers or not isinstance(trait_modifiers, list):
        raise ValueError("Please make sure to pass in a list of trait modifiers created by create_trait() funciton.\n")

    trait =s2c.get_class_with_defaults("idmType:GeneToTraitModifierConfig", schema_json=schema_json)
    trait.Allele_Combinations = allele_combo
    trait.Trait_Modifiers = trait_modifiers
    species_params.Gene_To_Trait_Modifiers.append(trait)

    return config

def add_blood_meal_mortality(config, schema_json,
                             default_probability_of_death: float = 0.0,
                             species: str = "",
                             allele_combo: list = None,
                             probability_of_death_for_allele_combo: float = 0.0):
    """
    Add a probability of death after a mosquito has a blood meal.  There are some genetically
    modified mosquitoes that have a fitness cost associated with the digestion of a blood meal.
    This affects vectors whether this is a human or animal blood meal.
    This is a GeneticProbability such that the probability used can depend on the genetic makeup
    of the mosquito.  The deaths from this are added to the "die after feeding" numbers for
    vectors that have fed on humans and "die before feeding on a human" for vectors that
    die after animal blood meal.
    
    If you need to add multiple allele combos for the same species, call this method once for
    each allele combo and associated probability.  If you do, please note that the default
    probability will be combined by OR'ing the different values together [1-((1-p1)*(1-p2))].
    Also note that the default probabilities for each species will be OR'd together.

    The probability selected for given genome will depend on the "complexity" of the allele
    combinations.  If an entry has more genes/loci positions than another, the combination with
    more will be considered first.  If they have the same number of genes and one has fewer
    possible genomes, the one with fewer possible genomes will be considered first.  For example,
    if you add a1-a1 in one call and b1-b0 in a second call, EMOD will first check if the genome
    has a1-a1.  If it has a1-a1, it will get that probability.  If it does not, it will check
    if the genome has b1-b0 or b0-b1.  The entered values are not combined in any way.  It is up
    to the user to specify the probability for specific combinations.

    Args:
        config: schema-backed config smart dict
        schema_json: json object that is the schema file
        default_probability_of_death: The probability used if the genome of the mosquito does not
            match any of the defined allele combinations in Genetic_Probabilities.
        species: Name of the species of vectors to give the specific probability to.
        allele_combo: The combination of alleles that a mosquito's genome must have in order to 
            apply associated Probability.  You do not need to specify alleles for every locus.
            The ones not defined are not considered in the match  This should be a two-dimensional
            array where each internal array has two strings representing two alleles of the same
            locus.  Each separate internal array represents locus and you can only have one entry
            per locus.  You can use '*' for an allele to say any allele. For example,
            [ ["a1", "a1"], ["b1, "*"] ] says any mosquito with a1-a1 in the first locus and
            b1 in either chromosome of the second locus.
        probability_of_death_for_allele_combo: The probability to use if the genome of the mosquito
            has the matching Allele_Combinations.  The default is zero.

    Returns:
        configured config
    """

    # checks if species name is valid
    species_params = get_species_params(config, species)
    
    if (default_probability_of_death < 0.0) or (1.0 < default_probability_of_death):
        raise ValueError(f"Invalid value for 'default_probability_of_death'={default_probability_of_death}.\n"
                         f"The value must be between 0 and 1.\n")
    
    _validate_allele_combo( species_params=species_params, allele_combo=allele_combo)

    if (probability_of_death_for_allele_combo < 0.0) or (1.0 < probability_of_death_for_allele_combo):
        raise ValueError(f"Invalid value for 'probability_of_death_for_allele_combo'={probability_of_death_for_allele_combo}.\n"
                         f"The value must be between 0 and 1.\n")

    acp =s2c.get_class_with_defaults("idmType:AlleleComboProbabilityConfig", schema_json=schema_json)
    acp.Allele_Combinations = allele_combo
    acp.Probability = probability_of_death_for_allele_combo

    species_params.Blood_Meal_Mortality.Genetic_Probabilities.append( acp)

    default_prob = species_params.Blood_Meal_Mortality.Default_Probability
    default_prob = 1.0 - ((1.0 - default_prob)*(1.0 - default_probability_of_death))
    species_params.Blood_Meal_Mortality.Default_Probability = default_prob

    return config


def add_insecticide_resistance(config, schema_json, insecticide_name: str = "", species: str = "",
                               allele_combo: list = None, blocking: float = 1.0, killing: float = 1.0,
                               repelling: float = 1.0, larval_killing: float = 1.0):
    """
        Use this function to add to the list of **Resistances** parameter for a specific insecticide
        Add each resistance separately.
        **Example**::

            Insecticides = [
            {
              "Name": "pyrethroid",
              "Resistances": [
                {
                  "Allele_Combinations": [
                  [
                    "a1",
                    "a1"
                  ]
                 ],
                "Blocking_Modifier": 1.0,
                "Killing_Modifier": 0.85,
                "Repelling_Modifier": 0.72,
                "Larval_Killing_Modifier": 0,
                "Species": "gambiae"
              }
             ]
            },
            {..}

    Args:
        config: schema-backed config smart dict
        schema_json: json object that is the schema file
        insecticide_name: The name of the insecticide to which attach the resistance.
        species: Name of the species of vectors.
        allele_combo: List of combination of alleles that vectors must have in order to be resistant.
        blocking: The value used to modify (multiply) the blocking effectivity of an intervention.
        killing: The value used to modify (multiply) the killing effectivity of an intervention.
        repelling: The value used to modify (multiply) the repelling effectivity of an intervention.
        larval_killing: The value used to modify (multiply) the larval killing effectivity of an intervention.

    Returns:
        configured config
    """

    # checks if species name is valid
    species_params = get_species_params(config, species)
    _validate_allele_combo(species_params=species_params, allele_combo=allele_combo)

    resistance = s2c.get_class_with_defaults("idmType:ResistantAlleleComboProbabilityConfig", schema_json=schema_json)
    resistance.Blocking_Modifier = blocking
    resistance.Killing_Modifier = killing
    resistance.Repelling_Modifier = repelling
    resistance.Larval_Killing_Modifier = larval_killing
    resistance.Species = species
    resistance.Allele_Combinations = allele_combo

    insecticides = config.parameters.Insecticides
    for an_insecticide in insecticides:
        if an_insecticide.Name == insecticide_name:
            an_insecticide.Resistances.append(resistance)
            return config

    new_insecticide =s2c.get_class_with_defaults("idmType:Insecticide", schema_json=schema_json)
    new_insecticide.Name = insecticide_name
    new_insecticide.Resistances.append(resistance)
    config.parameters.Insecticides.append(new_insecticide)

    return config


def add_species_drivers(config, schema_json, species: str, driving_allele: str, to_copy: str, to_replace: str,
                        likelihood_list: list, driver_type: str = "CLASSIC",
                        shredding_allele_required: str = None, allele_to_shred: str = None,
                        allele_to_shred_to: str = None, allele_shredding_fraction: float = None,
                        allele_to_shred_to_surviving_fraction: float = None):
    """
        Add a gene drive that propagates a particular set of alleles.
        Adds one **Alleles_Driven** item to the **Alleles_Driven** list, using 'driving_allele' as key if matching one
        already exists.

        **Example**::

            {
                "Driver_Type": "INTEGRAL_AUTONOMOUS",
                "Driving_Allele": "Ad",
                "Alleles_Driven": [
                    {
                        "Allele_To_Copy": "Ad",
                        "Allele_To_Replace": "Aw",
                        "Copy_To_Likelihood": [
                            {
                                "Copy_To_Allele": "Aw",
                                "Likelihood": 0.1
                            },
                            {
                                "Copy_To_Allele": "Ad",
                                "Likelihood": 0.3
                            },
                            {
                                "Copy_To_Allele": "Am",
                                "Likelihood": 0.6
                            }
                        ]
                    },
            {
                "Driver_Type" : "X_SHRED",
                "Driving_Allele" : "Ad",
                "Driving_Allele_Params" : {
                    "Allele_To_Copy"    : "Ad",
                    "Allele_To_Replace" : "Aw",
                    "Copy_To_Likelihood" : [
                        {
                            "Copy_To_Allele" : "Ad",
                            "Likelihood" : 1.0
                        },
                        {
                            "Copy_To_Allele" : "Aw",
                            "Likelihood" : 0.0
                        }
                    ]
                },
                "Shredding_Alleles" : {
                    "Allele_Required"    : "Yw",
                    "Allele_To_Shred"    : "Xw",
                    "Allele_To_Shred_To" : "Xm",
                    "Allele_Shredding_Fraction": 0.97,
                    "Allele_To_Shred_To_Surviving_Fraction" : 0.05
                }
                ]
            }

    Args:
        config: schema-backed config smart dict
        schema_json: json object that is the schema file
        species: Name of the species for which we're setting the drivers
        driving_allele: This is the allele that is known as the driver
        driver_type: This indicates the type of driver.
            CLASSIC - The driver can only drive if the one gamete has the driving allele and the other has a specific
            allele to be replaced
            INTEGRAL_AUTONOMOUS - At least one of the gametes must have the driver.  Alleles can still be driven if the
            driving allele is in both gametes or even if the driving allele cannot replace the allele in the
            other gamete
            X_SHRED, Y_SHRED -  cannot be used in the same species during one simulation/realization. The driving_allele
            must exist at least once in the genome for shredding to occur. If there is only one, it can exist in either
            half of the genome.
            DAISY_CHAIN -  can be used for drives that do not drive themselves but can be driven by another allele.
        to_copy: The main allele to be copied **Allele_To_Copy**
        to_replace: The allele that must exist and will be replaced by the copy **Allele_To_Replace**
        likelihood_list: A list of tuples in format: [(**Copy_To_Allele**, **Likelihood**),(),()] to assign to
            **Copy_To_Likelyhood** list
        shredding_allele_required: The genome must have this gender allele in order for shredding to occur.
            If the driver is X_SHRED, then the allele must be designated as a Y chromosome. If the driver is Y_SHRED,
            then the allele must NOT be designated as a Y chromosome
        allele_to_shred: The genome must have this gender allele in order for shredding to occur. If the driver is
            X_SHRED, then the allele must NOT be designated as a Y chromosome. If the driver is Y_SHRED, then the allele
            must be designated as a Y chromosome
        allele_to_shred_to: This is a gender allele that the 'shredding' will change the allele_to_shred into. It can
            be a temporary allele that never exists in the output or could be something that appears due to
            resistance/failures
        allele_shredding_fraction: This is the fraction of the alleles_to_Shred that will be converted to
            allele_to_shred_to. Values 0 to 1.  If this value is less than 1, then some of the allele_to_shred will
            remain and be part of the gametes.
        allele_to_shred_to_surviving_fraction: A trait modifier will automatically generated for
            [ Allele_To_Shred_To, * ], the trait ADJUST_FERTILE_EGGS, and this value as its modifier.  Values 0 to 1.
            A value of 0 implies perfect shredding such that no allele_to_Shred_To survive in the eggs. A value of 1
            means all of the 'shredded' alleles survive.

    Returns:
        configured config
    """

    # add_species_drivers(self.config, schema_path_file, "gambiae", driving_allele="one",
    #                     driver_type="X_SHRED", to_copy="one", to_replace="one",
    #                     likelihood_list=[("one", 0.15), ("two", 0.85)], shredding_allele_required="b",
    #                     allele_shredding_fraction=0.3, allele_to_shred="a",
    #                     allele_to_shred_to_surviving_fraction=0.1, allele_to_shred_to='c')

    if (driver_type != "X_SHRED" and driver_type != "Y_SHRED") and (shredding_allele_required or allele_to_shred
                                                                    or allele_to_shred_to or allele_shredding_fraction or allele_to_shred_to_surviving_fraction):
        raise ValueError(f"Please do not define any shredding parameters if you're not using 'driver_type' = X_SHRED or"
                         f"Y_SHRED.\n")
    elif driver_type == "DAISY_CHAIN":
        for (copy_to_allele, likelihood) in likelihood_list:
            if copy_to_allele == driving_allele:
                raise ValueError(f"For DAISY_CHAIN driver_type, you cannot have the Driving_Allele (driving_allele) "
                                 f"= '{driving_allele}' be the same as any of the Copy_To_Allele (in likelihood_list) = "
                                 f"'({copy_to_allele}, {likelihood})'.\n")

    species_parameters = get_species_params(config, species)
    gender_allele_required = False
    gender_allele_to_shred = False
    gender_allele_to_shred_to = False

    gene_driver = s2c.get_class_with_defaults("idmType:VectorGeneDriver", schema_json=schema_json)
    gene_driver.Driving_Allele = driving_allele
    gene_driver.Driver_Type = driver_type

    if driver_type == "X_SHRED" or driver_type == "Y_SHRED":
        if not allele_to_shred or not allele_to_shred_to or not shredding_allele_required:
            raise ValueError(f"For 'driver_type'= X_SHRED or Y_SHRED, please define all the shredding parameters.\n")
        for gene in species_parameters.Genes:
            if gene["Is_Gender_Gene"] == 1:
                for allele in gene["Alleles"]:
                    if allele["Name"] == shredding_allele_required:
                        gender_allele_required = True
                        if driver_type == "X_SHRED" and allele["Is_Y_Chromosome"] == 0:
                            raise ValueError(
                                f"For 'driver_type' = X_SHRED, 'shredding_allele_required' should be a Y chromosome.\n")
                        elif driver_type == "Y_SHRED" and allele["Is_Y_Chromosome"] == 1:
                            raise ValueError(
                                f"For 'driver_type' = Y_SHRED, 'shredding_allele_required' should be an X chromosome.\n")
                    elif allele["Name"] == allele_to_shred:
                        gender_allele_to_shred = True
                        if driver_type == "X_SHRED" and allele["Is_Y_Chromosome"] == 1:
                            raise ValueError(
                                f"For 'driver_type'= X_SHRED, 'allele_to_shred' should be X chromosome.\n")
                        elif driver_type == "Y_SHRED" and allele["Is_Y_Chromosome"] == 0:
                            raise ValueError(
                                f"For 'driver_type'= Y_SHRED, 'allele_to_shred' should be Y chromosome.\n")
                    elif allele["Name"] == allele_to_shred_to:
                        gender_allele_to_shred_to = True
                        if driver_type == "X_SHRED" and allele["Is_Y_Chromosome"] == 1:
                            raise ValueError(
                                f"For 'driver_type'= X_SHRED, 'allele_to_shred' should be X chromosome.\n")
                        elif driver_type == "Y_SHRED" and allele["Is_Y_Chromosome"] == 0:
                            raise ValueError(
                                f"For 'driver_type'= Y_SHRED, 'allele_to_shred_to' should be Y chromosome.\n")

        if not (gender_allele_required and gender_allele_to_shred and gender_allele_to_shred_to):
            raise ValueError(f"Looks like shredding_allele_required or allele_to_shred or allele_to_shred_to are not "
                             f"on a gender gene, "
                             f"but they all should be. Please verify your settings.\n")

        shredding_alleles = s2c.get_class_with_defaults( classname="idmType:ShreddingAlleles", schema_json=schema_json)
        shredding_alleles.Allele_Required = shredding_allele_required
        shredding_alleles.Allele_Shredding_Fraction = allele_shredding_fraction
        shredding_alleles.Allele_To_Shred = allele_to_shred
        shredding_alleles.Allele_To_Shred_To = allele_to_shred_to
        shredding_alleles.Allele_To_Shred_To_Surviving_Fraction = allele_to_shred_to_surviving_fraction
        gene_driver.Shredding_Alleles = shredding_alleles.finalize()

    allele_driven = s2c.get_class_with_defaults(classname="idmType:AlleleDriven", schema_json=schema_json)
    allele_driven.Allele_To_Copy = to_copy
    allele_driven.Allele_To_Replace = to_replace
    for index, likely in enumerate(likelihood_list):
        c2likelyhood = s2c.get_class_with_defaults( classname="idmType:CopyToAlleleLikelihood", schema_json=schema_json)
        c2likelyhood.Copy_To_Allele = likely[0]
        c2likelyhood.Likelihood = likely[1]
        allele_driven.Copy_To_Likelihood.append(c2likelyhood.finalize())

    # check if the Driving_Allele already exists
    if "Drivers" in species_parameters:
        for driver in species_parameters.Drivers:
            if driving_allele == driver["Driving_Allele"]:
                if driver_type == driver["Driver_Type"]:
                    driver["Alleles_Driven"].append(allele_driven)
                    return config
                else:
                    raise ValueError(f"The gene driver with 'driving_allele'={driving_allele} must have exactly one "
                                     f"entry in 'Alleles_Driven' for this allele and therefore cannot be used for "
                                     f"multiple 'driver_type's.\n")

    if driver_type == "X_SHRED" or driver_type == "Y_SHRED":
        gene_driver.Driving_Allele_Params = allele_driven
    else:
        gene_driver.Alleles_Driven = [allele_driven]

    gene_driver.Driver_Type = driver_type  # to circumvent the implicit settings
    species_parameters.Drivers.append(gene_driver.finalize())
    print(species_parameters)
    return config


def add_maternal_deposition(config, schema_json, species: str, cas9_grna_from: str,
                            allele_to_cut: str, likelihood_list: list):
    """
        Adds a maternal deposition element for the specified species.
        After meiosis and fertilization, maternal deposition of Cas9 and gRNA can form additional resistance alleles
        in the zygote or early embryo from wildtype alleles. These elements define the likelihoods of forming additional
        resistance alleles.

    Args:
        config: schema-backed config smart dict
        schema_json: json object that is the schema file
        species: Name of the species for which we're adding the maternal deposition element.
        cas9_grna_from: This is an allele for presence of which in the mother we will be checking to see if additional
            resistance alleles will be formed. This is the allele must be one of the 'driving_alleles' from
            vector_config.add_species_drivers() function.
        allele_to_cut: The allele from which resistance alleles might be formed due to maternal deposition. This must
            be one of the 'to_replace' alleles defined in the vector_config.add_species_drivers() function.
        likelihood_list: A list of tuples in format: [(<cut_to_allele>, <likelihood>),(),()] which will be converted
            to an array of allele-to-likelihood dictionaries to be applied to the 'allele_to_cut' for each
            'cas9_grna_from' present in the mother. The sum of likelihoods should be equal to 1.

    Returns:
        Config object with maternal deposition parameters added for the specified species.
    """

    sp_params = get_species_params(config, species)
    found_driver = False
    found_allele_to_cut = False
    allele_to_copy = ""
    for driver in sp_params.Drivers:
        if cas9_grna_from == driver.Driving_Allele:
            found_driver = True
            for allele_driven in driver.Alleles_Driven:
                if allele_to_cut == allele_driven.Allele_To_Replace:
                    found_allele_to_cut = True
                    allele_to_copy = allele_driven.Allele_To_Copy
                    break
    if not found_driver:
        raise ValueError(f"Failed to find 'cas9_grna_from' = '{cas9_grna_from}' in the drivers for species '{species}'."
                         f"\n'cas9_grna_from' must be one of the 'driving_alleles' defined in the "
                         f"vector_config.add_species_drivers() function.\n Please make sure the drivers are added "
                         f"before the maternal deposition.\n")
    if not found_allele_to_cut:
        raise ValueError(f"Failed to find 'allele_to_cut' = '{allele_to_cut}' in the drivers for species '{species}'.\n"
                         f"'allele_to_cut' must be one of the 'to_replace' alleles defined for 'driving_allele'="
                         f"'{cas9_grna_from}' in the "
                         f"vector_config.add_species_drivers() function.\n Please make sure the drivers are added "
                         f"before the maternal deposition.\n")

    maternal_deposition = s2c.get_class_with_defaults("idmType:MaternalDeposition", schema_json=schema_json)
    maternal_deposition.Cas9_gRNA_From = cas9_grna_from
    maternal_deposition.Allele_To_Cut = allele_to_cut

    total = 0.0
    for index, likely in enumerate(likelihood_list):
        c2likelyhood = s2c.get_class_with_defaults( "idmType:CutToAlleleLikelihood", schema_json=schema_json)
        if likely[0] == allele_to_copy:
            raise ValueError(f"Element at index '{index}' in the 'likelihood_list' has allele '{likely[0]}', but it "
                             f"is also an 'allele_to_copy' for the 'driving_allele' = '{cas9_grna_from}' and cannot be"
                             f" cut to in maternal deposition.\n")
        c2likelyhood.Cut_To_Allele = likely[0]
        total += likely[1]
        c2likelyhood.Likelihood = likely[1]
        maternal_deposition.Likelihood_Per_Cas9_gRNA_From.append(c2likelyhood)
    if not math.isclose(total, 1.0, rel_tol=1e-6):
        raise ValueError(f"The sum of likelihoods in the 'likelihood_list' must be equal to 1.0, but got {total}.\n")

    sp_params.Maternal_Deposition.append(maternal_deposition)

    return config



def set_max_larval_capacity(config, species_name, habitat_type, max_larval_capacity):
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

    habitats = get_species_params(config, species_name).Habitats
    # g_s_p raises a ValueError so if we get this far, we can use habitats unconditionally.
    for hab in habitats:
        if hab['Habitat_Type'] == habitat_type:
            hab['Max_Larval_Capacity'] = max_larval_capacity
            return

    raise ValueError(f"Failed to find habitat_type {habitat_type} for species {species_name}.")


def add_microsporidia(config, schema_json, species_name: str = None,
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
        schema_json: json object that is the schema file
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
    if not strain_name:
        raise ValueError("Please define strain_name.\n")
    if not duration_to_disease_acquisition_modification:
        duration_to_disease_acquisition_modification = {"Times": [0, 3, 6, 9], "Values": [1.0, 1.0, 0.5, 0.0]}
    if not duration_to_disease_transmission_modification:
        duration_to_disease_transmission_modification = {"Times": [0, 3, 6, 9], "Values": [1.0, 1.0, 0.75, 0.5]}

    species_parameters = get_species_params(config, species_name)
    d_t_d_a_m =s2c.get_class_with_defaults("idmType:InterpolatedValueMap", schema_json=schema_json)
    d_t_d_a_m.Times = duration_to_disease_acquisition_modification["Times"]
    d_t_d_a_m.Values = duration_to_disease_acquisition_modification["Values"]
    d_t_d_t_m =s2c.get_class_with_defaults("idmType:InterpolatedValueMap", schema_json=schema_json)
    d_t_d_t_m.Times = duration_to_disease_transmission_modification["Times"]
    d_t_d_t_m.Values = duration_to_disease_transmission_modification["Values"]
    microsporidia =s2c.get_class_with_defaults("idmType:MicrosporidiaParameters", schema_json=schema_json)
    microsporidia.Duration_To_Disease_Acquisition_Modification = d_t_d_a_m
    microsporidia.Duration_To_Disease_Transmission_Modification = d_t_d_t_m
    microsporidia.Female_To_Male_Transmission_Probability = female_to_male_probability
    microsporidia.Male_To_Female_Transmission_Probability = male_to_female_probability
    microsporidia.Larval_Growth_Modifier = larval_growth_modifier
    microsporidia.Female_To_Egg_Transmission_Probability = female_to_egg_probability
    microsporidia.Female_Mortality_Modifier = female_mortality_modifier
    microsporidia.Male_Mortality_Modifier = male_mortality_modifier
    microsporidia.Male_To_Egg_Transmission_Probability = male_to_egg_probability
    microsporidia.Strain_Name = strain_name
    species_parameters.Microsporidia = species_parameters.Microsporidia.append(microsporidia)


class ModifierEquationType(Enum):
    EXPONENTIAL = "EXPONENTIAL"
    LINEAR = "LINEAR"


def add_vector_migration(task,
                         species: str = None,
                         vector_migration_filename_path: str = None,
                         x_vector_migration: float = 1,
                         vector_migration_modifier_equation: ModifierEquationType = ModifierEquationType.LINEAR,
                         vector_migration_habitat_modifier: float = 0,
                         vector_migration_food_modifier: float = 0,
                         vector_migration_stay_put_modifier: float = 0):
    """
        Adds vector migration parameters to the named species' parameters and adds the migration file to the
        common_assets in task

    Args:
        task: contains config to edit and assets to add migration file to
        species: Species to target, **Name** parameter
        vector_migration_filename_path: Path with the filename of the migration file to use for
            **Vector_Migration_Filename**
        x_vector_migration: Scale factor for the rate of vector migration to other nodes.
        vector_migration_modifier_equation: Functional form of vector migration modifiers.
            This applies only to female migrating vectors. Default is ModifierEquationType.LINEAR.
        vector_migration_habitat_modifier: Preference of a vector to migrate toward a node with more habitat. This
            applies only to female migrating vectors.
        vector_migration_food_modifier: Preference of a vector to migrate toward a node currently occupied by humans,
            independent of the number of humans in the node. This only applies to female migrating vectors.
        vector_migration_stay_put_modifier: Preference of a vector to remain in its current node rather than migrate
            to another node. This applies only to female migrating vectors.


    Returns:

    """
    if not vector_migration_filename_path:
        raise ValueError("Please define vector_migration_filename.\n")
    head, tail = os.path.split(vector_migration_filename_path)

    params = get_species_params(task.config, species)
    params.Vector_Migration_Filename = tail
    params.x_Vector_Migration = x_vector_migration
    params.Vector_Migration_Modifier_Equation = vector_migration_modifier_equation.value
    params.Vector_Migration_Habitat_Modifier = vector_migration_habitat_modifier
    params.Vector_Migration_Food_Modifier = vector_migration_food_modifier
    params.Vector_Migration_Stay_Put_Modifier = vector_migration_stay_put_modifier
    # checking if present in case added previously (ex: if using same migration file for different species)
    if not task.common_assets.has_asset(vector_migration_filename_path):
        task.common_assets.add_asset(vector_migration_filename_path)
    if not task.common_assets.has_asset(vector_migration_filename_path + ".json"):
        task.common_assets.add_asset(vector_migration_filename_path + ".json")


# __all_exports: A list of classes that are intended to be exported from this module.
# the private classes are commented out until we have time to review and test them.
__all_exports = [
    set_species_param,
    set_team_defaults_vector,
    add_species,
    add_genes_and_alleles,
    add_blood_meal_mortality,
    add_insecticide_resistance,
    add_species_drivers,
    add_maternal_deposition,
    set_max_larval_capacity,
    add_microsporidia,
    ModifierEquationType,
    add_vector_migration,
    configure_linear_spline
]

# The following loop sets the __module__ attribute of each class in __all_exports to the name of the current module.
# This is done to ensure that when these classes are imported from this module, their __module__ attribute correctly
# reflects their source module.

for _ in __all_exports:
    _.__module__ = __name__

# __all__: A list that defines the public interface of this module.
# This is essential to ensure that Sphinx builds documentation for these classes, including those that are imported
# from emodpy.
# It contains the names of all the classes that should be accessible when this module is imported using the syntax
# 'from module import *'.
# Here, it is set to the names of all classes in __all_exports.

__all__ = [_.__name__ for _ in __all_exports]
