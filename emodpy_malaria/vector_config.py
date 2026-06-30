import math
import os
import warnings
from typing import Union

import emod_api.schema_to_class as s2c
from emod_api import campaign as api_campaign

from emodpy.campaign.common import ValueMap

from emodpy_malaria.utils.config_utils import validate_allele_combo
from emodpy_malaria.utils.emod_enum import (
    VectorTrait, DriverType, VectorSamplingType, EggHatchDensityDependence,
    EggSaturationAtOviposition, HabitatType, ModifierEquationType,
    ClimateModel, ClimateUpdateResolution, PopulationScaleType,
    AgeDependentBitingRiskType
)


#
# PUBLIC API section
#
def set_team_defaults(config, manifest):
    """
    Set configuration defaults using team-wide values, including drugs and vector species.

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest file containing the schema path

    Returns:
        (dict): configured config
    """

    # INFECTION
    config.parameters.Simulation_Type = "VECTOR_SIM"
    config.parameters.Infection_Updates_Per_Timestep = 8
    config.parameters.Incubation_Period_Constant = 7
    config.parameters.Infectious_Period_Constant = 7

    # VECTOR_SIM parameters (formerly lived in dtk-tools/dtk/vector/params.py)
    config.parameters.Enable_Vector_Species_Report = 0
    config.parameters.Vector_Sampling_Type = VectorSamplingType.VECTOR_COMPARTMENTS_NUMBER
    # config.parameters.Mosquito_Weight = 1 # If this parameter is set, config.parameters.Vector_Sampling_Type is automatically changed to "SAMPLE_IND_VECTORS"

    config.parameters.Enable_Vector_Aging = 0
    config.parameters.Enable_Vector_Mortality = 1

    config.parameters.Age_Dependent_Biting_Risk_Type = AgeDependentBitingRiskType.SURFACE_AREA_DEPENDENT
    config.parameters.Human_Feeding_Mortality = 0.1

    config.parameters.Wolbachia_Infection_Modification = 1.0
    config.parameters.Wolbachia_Mortality_Modification = 1.0

    config.parameters.x_Temporary_Larval_Habitat = 1
    config.parameters.Vector_Species_Params = []
    config.parameters.Egg_Hatch_Density_Dependence = EggHatchDensityDependence.NO_DENSITY_DEPENDENCE
    config.parameters.Enable_Temperature_Dependent_Egg_Hatching = 0
    config.parameters.Enable_Egg_Mortality = 0
    config.parameters.Enable_Drought_Egg_Hatch_Delay = 0
    config.parameters.Insecticides = []

    # Other defaults from dtk-tools transition  #fixme very likely needs pruning
    config.parameters.Egg_Saturation_At_Oviposition = EggSaturationAtOviposition.SATURATION_AT_OVIPOSITION
    config.parameters.Enable_Demographics_Reporting = 0
    # config.parameters.Enable_Rainfall_Stochasticity = 1
    config.parameters.Node_Grid_Size = 0.042
    # config.parameters.Population_Density_C50 = 30
    config.parameters.Population_Scale_Type = PopulationScaleType.FIXED_SCALING

    # setting up parameters for climate constant
    config.parameters.Base_Rainfall = 10
    config.parameters.Base_Air_Temperature = 27
    config.parameters.Base_Land_Temperature = 27
    config.parameters.Base_Relative_Humidity = 0.75
    config.parameters.Climate_Model = ClimateModel.CLIMATE_CONSTANT
    config.parameters.Climate_Update_Resolution = ClimateUpdateResolution.CLIMATE_UPDATE_DAY  # not used with "CLIMATE_CONSTANT", nice to have
    config.parameters.Enable_Climate_Stochasticity = 0

    config.parameters.Simulation_Duration = 365
    config.parameters.Start_Time = 0  # default is 1, but interventions often start at 0, which will make them not work

    return config


def get_species_params(config, species: str = None):
    """
    Returns the species parameters dictionary with the matching species **Name**

    Args:
        config (dict): schema-backed config smart dict
        species (str): Species to look up

    Returns:
        (dict): Dictionary of species parameters with the matching name
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
        config (dict): schema-backed config smart dict
        species (str): name of species for which to set the parameter
        parameter (str): parameter to set
        value (Union[Any, list[Any]]): value to set the parameter to
        overwrite (bool): if set to True and parameter is a list, overwrites the parameter with value, appends by default
    """

    vector_species = get_species_params(config, species)

    if hasattr(value, 'to_schema_dict'):
        if getattr(value, '_campaign', None) is None:
            value._campaign = api_campaign
            for h in getattr(value, 'habitats', []):
                if getattr(h, '_campaign', None) is None:
                    h._campaign = api_campaign
        value = value.to_schema_dict()
    elif isinstance(value, list):
        for v in value:
            if hasattr(v, 'to_schema_dict') and getattr(v, '_campaign', None) is None:
                v._campaign = api_campaign
        value = [v.to_schema_dict() if hasattr(v, 'to_schema_dict') else v for v in value]

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


class VectorHabitat:
    """
    Defines a vector larval habitat entry for a species' **Habitats** list.
    Each habitat has a type, a maximum larval capacity, and — for
    ``LINEAR_SPLINE`` habitats — a time-varying capacity distribution.

    For non-spline habitat types (``TEMPORARY_RAINFALL``, ``WATER_VEGETATION``,
    ``HUMAN_POPULATION``, ``CONSTANT``, ``BRACKISH_SWAMP``), only
    ``habitat_type`` and ``max_larval_capacity`` are needed.

    For ``LINEAR_SPLINE``, ``capacity_distribution_over_time`` is required
    and ``capacity_distribution_number_of_years`` may optionally be set.

    Args:
        habitat_type (Union[HabitatType, str], required):
            The type of larval habitat. Use [HabitatType](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/)
            enum values (e.g. ``HabitatType.LINEAR_SPLINE``,
            ``HabitatType.TEMPORARY_RAINFALL``).

        max_larval_capacity (float, required):
            The maximum larval capacity for this habitat.

        capacity_distribution_over_time (Union[ValueMap, dict], optional):
            Required when ``habitat_type`` is ``LINEAR_SPLINE``. A
            [ValueMap](https://emod.idmod.org/emodpy/autoapi/emodpy/campaign/common/) or a dictionary with
            ``"Times"`` and ``"Values"`` keys that scales the larval capacity
            over time. Times is in days and Values are a scale factor per
            degrees squared. Ideally, the last value should equal the first
            value if they are one day apart.

            Example::

                {"Times": [0, 30, 60, 91, 122, 152, 182, 213, 243, 274, 304, 334, 365],
                 "Values": [3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8, 6.5, 2.6, 2.1, 2]}

        capacity_distribution_number_of_years (int, optional):
            Only used when ``habitat_type`` is ``LINEAR_SPLINE``. The total
            length of time in years for the scaling pattern. If the simulation
            runs longer than this, the pattern repeats.
            Default value: 1

    Example:
        Seasonal habitat with a linear spline::

            from emodpy_malaria.vector_config import VectorHabitat
            from emodpy_malaria.utils.emod_enum import HabitatType

            habitat = VectorHabitat(
                habitat_type=HabitatType.LINEAR_SPLINE,
                max_larval_capacity=1e8,
                capacity_distribution_over_time={
                    "Times":  [0, 30, 60, 91, 122, 152, 182, 213, 243, 274, 304, 334, 365],
                    "Values": [3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8, 6.5, 2.6, 2.1, 2]
                }
            )

    Example:
        Simple constant habitat::

            habitat = VectorHabitat(
                habitat_type=HabitatType.CONSTANT,
                max_larval_capacity=1e7
            )
    """

    def __init__(self,
                 habitat_type: Union[HabitatType, str],
                 max_larval_capacity: float,
                 capacity_distribution_over_time: Union[ValueMap, dict] = None,
                 capacity_distribution_number_of_years: int = 1,
                 campaign=None):
        if not isinstance(habitat_type, HabitatType):
            try:
                habitat_type = HabitatType(habitat_type)
            except ValueError:
                raise ValueError(
                    f"habitat_type must be a HabitatType enum value, got {habitat_type!r}. "
                    f"Valid options: {list(HabitatType)}")

        if habitat_type == HabitatType.LINEAR_SPLINE:
            if capacity_distribution_over_time is None:
                raise ValueError(
                    "capacity_distribution_over_time is required when "
                    "habitat_type is LINEAR_SPLINE.")

            if isinstance(capacity_distribution_over_time, dict):
                if "Times" not in capacity_distribution_over_time or "Values" not in capacity_distribution_over_time:
                    raise ValueError(
                        "capacity_distribution_over_time must be a dictionary "
                        "with 'Times' and 'Values' keys.")
                capacity_distribution_over_time = ValueMap(
                    times=capacity_distribution_over_time["Times"],
                    values=capacity_distribution_over_time["Values"]
                )

            if not isinstance(capacity_distribution_over_time, ValueMap):
                raise ValueError(
                    "capacity_distribution_over_time must be a ValueMap or a dict "
                    "with 'Times' and 'Values' keys.")

        self._campaign = campaign
        self._habitat_type = habitat_type
        self._max_larval_capacity = max_larval_capacity
        self._capacity_distribution_over_time = capacity_distribution_over_time
        self._capacity_distribution_number_of_years = capacity_distribution_number_of_years

    def to_schema_dict(self) -> s2c.ReadOnlyDict:
        obj = s2c.get_class_with_defaults(
            "idmType:VectorHabitat",
            schema_json=self._campaign.get_schema())
        obj.Habitat_Type = self._habitat_type
        obj.Max_Larval_Capacity = self._max_larval_capacity
        if self._habitat_type == HabitatType.LINEAR_SPLINE:
            obj.Capacity_Distribution_Number_Of_Years = self._capacity_distribution_number_of_years
            obj.Capacity_Distribution_Over_Time = self._capacity_distribution_over_time.to_schema_dict(self._campaign)
        obj.pop("schema", None)
        obj.pop("explicits", None)
        return obj


class VectorSpeciesParameters:
    """
    Defines a vector species and its biological parameters for use in
    **Vector_Species_Params**. Each species entry controls mosquito
    behavior: feeding preferences, life expectancy, habitat, transmission
    efficiency, and temperature-dependent development rates.

    Use the constructor to create a species from scratch, or use
    `from_preset()` to start from a built-in species template
    (gambiae, arabiensis, funestus, etc.) and override selected parameters.

    Args:
        name (str, required):
            Name of the vector species. Must be unique within the simulation's
            Vector_Species_Params list.

        habitats (list[VectorHabitat], required):
            List of [VectorHabitat](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/vector_config/) objects defining the larval habitat
            types and capacities for this species.

        anthropophily (float, optional):
            Fraction of blood meals taken from humans vs. animals.
            Default value: 0.65

        indoor_feeding_fraction (float, optional):
            Fraction of human feeds that occur indoors.
            Default value: 0.95

        adult_life_expectancy (float, optional):
            Average female mosquito lifespan in days.
            Default value: 20

        male_life_expectancy (float, optional):
            Average male mosquito lifespan in days.
            Default value: 10

        transmission_rate (float, optional):
            Probability that a bite from an infectious mosquito infects
            a naive, uninfected individual.
            Default value: 0.9

        acquire_modifier (float, optional):
            Modifier of the probability that a mosquito becomes infected
            when feeding on an infectious human.
            Default value: 0.8

        egg_batch_size (float, optional):
            Number of eggs laid per successful blood meal.
            Default value: 100

        days_between_feeds (float, optional):
            Average number of days between blood-feeding attempts.
            Default value: 3

        aquatic_mortality_rate (float, optional):
            Base daily mortality rate for aquatic-stage larvae.
            Default value: 0.1

        immature_duration (float, optional):
            Days for larvae to develop into adults.
            Default value: 2

        infected_egg_batch_factor (float, optional):
            Multiplier on egg batch size for infected females.
            Default value: 0.8

        infectious_human_feed_mortality_factor (float, optional):
            Multiplier on feeding mortality for infected mosquitoes.
            Default value: 1.5

        vector_sugar_feeding_frequency (str, optional):
            Sugar-feeding behavior. One of ``"VECTOR_SUGAR_FEEDING_NONE"``,
            ``"VECTOR_SUGAR_FEEDING_ON_EMERGENCE_ONLY"``,
            ``"VECTOR_SUGAR_FEEDING_EVERY_FEED"``,
            ``"VECTOR_SUGAR_FEEDING_EVERY_DAY"``.
            Default value: ``"VECTOR_SUGAR_FEEDING_NONE"``

    Example:
        Create a custom species with a seasonal spline habitat::

            habitat = VectorHabitat(HabitatType.LINEAR_SPLINE,
                                    max_larval_capacity=1e8,
                                    capacity_distribution_over_time={...})
            species = VectorSpeciesParameters(name="gambiae",
                                              habitats=[habitat],
                                              anthropophily=0.65,
                                              indoor_feeding_fraction=0.95)
            config.parameters.Vector_Species_Params.append(species.to_schema_dict())

    Example:
        Load a built-in preset and override one parameter::

            species = VectorSpeciesParameters.from_preset(campaign, manifest, "arabiensis")
            species.indoor_feeding_fraction = 0.3
            config.parameters.Vector_Species_Params.append(species.to_schema_dict())
    """

    def __init__(self,
                 name: str,
                 habitats: list,
                 anthropophily: float = 0.65,
                 indoor_feeding_fraction: float = 0.95,
                 adult_life_expectancy: float = 20,
                 male_life_expectancy: float = 10,
                 transmission_rate: float = 0.9,
                 acquire_modifier: float = 0.8,
                 egg_batch_size: float = 100,
                 days_between_feeds: float = 3,
                 aquatic_mortality_rate: float = 0.1,
                 immature_duration: float = 2,
                 infected_egg_batch_factor: float = 0.8,
                 infectious_human_feed_mortality_factor: float = 1.5,
                 aquatic_arrhenius_1: float = 84200000000,
                 aquatic_arrhenius_2: float = 8328,
                 infected_arrhenius_1: float = 117000000000,
                 infected_arrhenius_2: float = 8336,
                 cycle_arrhenius_1: float = 40900000000,
                 cycle_arrhenius_2: float = 7740,
                 cycle_arrhenius_reduction_factor: float = 1.0,
                 vector_sugar_feeding_frequency: str = "VECTOR_SUGAR_FEEDING_NONE",
                 temperature_dependent_feeding_cycle: str = "NO_TEMPERATURE_DEPENDENCE",
                 campaign=None):
        self._campaign = campaign
        self.name = name
        self.habitats = habitats
        self.anthropophily = anthropophily
        self.indoor_feeding_fraction = indoor_feeding_fraction
        self.adult_life_expectancy = adult_life_expectancy
        self.male_life_expectancy = male_life_expectancy
        self.transmission_rate = transmission_rate
        self.acquire_modifier = acquire_modifier
        self.egg_batch_size = egg_batch_size
        self.days_between_feeds = days_between_feeds
        self.aquatic_mortality_rate = aquatic_mortality_rate
        self.immature_duration = immature_duration
        self.infected_egg_batch_factor = infected_egg_batch_factor
        self.infectious_human_feed_mortality_factor = infectious_human_feed_mortality_factor
        self.aquatic_arrhenius_1 = aquatic_arrhenius_1
        self.aquatic_arrhenius_2 = aquatic_arrhenius_2
        self.infected_arrhenius_1 = infected_arrhenius_1
        self.infected_arrhenius_2 = infected_arrhenius_2
        self.cycle_arrhenius_1 = cycle_arrhenius_1
        self.cycle_arrhenius_2 = cycle_arrhenius_2
        self.cycle_arrhenius_reduction_factor = cycle_arrhenius_reduction_factor
        self.vector_sugar_feeding_frequency = vector_sugar_feeding_frequency
        self.temperature_dependent_feeding_cycle = temperature_dependent_feeding_cycle

    @classmethod
    def from_preset(cls, campaign: object, manifest: object, species_name: str) -> "VectorSpeciesParameters":
        """
        Create a VectorSpeciesParameters from a built-in species preset.

        Built-in species: gambiae, arabiensis, funestus, fpg_gambiae,
        minimus, dirus.

        Args:
            campaign (object): An instance of the emod_api.campaign module.
            manifest (object): Manifest module containing the schema path.
            species_name (str): Name of a built-in species.

        Returns:
            VectorSpeciesParameters: An instance with preset values that
            can be modified before calling ``to_schema_dict()``.
        """
        import copy
        from emodpy_malaria.malaria_vector_species_params import _SPECIES_DATA

        if species_name not in _SPECIES_DATA:
            available = list(_SPECIES_DATA.keys())
            raise ValueError(
                f"Species {species_name!r} not found. "
                f"Available presets: {available}")

        if not campaign.get_schema():
            campaign.set_schema(manifest.schema_file)

        species = copy.deepcopy(_SPECIES_DATA[species_name])
        species._campaign = campaign
        for h in species.habitats:
            h._campaign = campaign
        return species

    def to_schema_dict(self) -> s2c.ReadOnlyDict:
        obj = s2c.get_class_with_defaults(
            "idmType:VectorSpeciesParameters",
            schema_json=self._campaign.get_schema())
        obj.Name = self.name
        obj.Anthropophily = self.anthropophily
        obj.Indoor_Feeding_Fraction = self.indoor_feeding_fraction
        obj.Adult_Life_Expectancy = self.adult_life_expectancy
        obj.Male_Life_Expectancy = self.male_life_expectancy
        obj.Transmission_Rate = self.transmission_rate
        obj.Acquire_Modifier = self.acquire_modifier
        obj.Egg_Batch_Size = self.egg_batch_size
        obj.Days_Between_Feeds = self.days_between_feeds
        obj.Aquatic_Mortality_Rate = self.aquatic_mortality_rate
        obj.Immature_Duration = self.immature_duration
        obj.Infected_Egg_Batch_Factor = self.infected_egg_batch_factor
        obj.Infectious_Human_Feed_Mortality_Factor = self.infectious_human_feed_mortality_factor
        obj.Aquatic_Arrhenius_1 = self.aquatic_arrhenius_1
        obj.Aquatic_Arrhenius_2 = self.aquatic_arrhenius_2
        obj.Infected_Arrhenius_1 = self.infected_arrhenius_1
        obj.Infected_Arrhenius_2 = self.infected_arrhenius_2
        obj.Cycle_Arrhenius_1 = self.cycle_arrhenius_1
        obj.Cycle_Arrhenius_2 = self.cycle_arrhenius_2
        obj.Cycle_Arrhenius_Reduction_Factor = self.cycle_arrhenius_reduction_factor
        obj.Vector_Sugar_Feeding_Frequency = self.vector_sugar_feeding_frequency
        obj.Temperature_Dependent_Feeding_Cycle = self.temperature_dependent_feeding_cycle
        obj.Habitats = [h.to_schema_dict() if hasattr(h, 'to_schema_dict') else h
                        for h in self.habitats]
        obj.pop("schema", None)
        obj.pop("explicits", None)
        return obj


def add_species(config: object,
                manifest: object,
                species_to_select: Union[str, list, "VectorSpeciesParameters", list]) -> object:
    """
    Adds species with preset parameters from 'malaria_vector_species_params.py', if species
    name not found - "gambiae" parameters are added and the new species name assigned.

    Also accepts [VectorSpeciesParameters](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/vector_config/) objects directly.

    Args:
        config (object): schema-backed config smart dict
        manifest (object): manifest file containing the schema path
        species_to_select (Union[str, list, 'VectorSpeciesParameters', list]): a list of species names, a single
            species name, or one or more VectorSpeciesParameters objects.

    Returns:
        configured config
    """

    if not isinstance(species_to_select, list):
        species_to_select = [species_to_select]

    for species in species_to_select:
        if isinstance(species, VectorSpeciesParameters):
            if species._campaign is None:
                if not api_campaign.get_schema():
                    api_campaign.set_schema(manifest.schema_file)
                species._campaign = api_campaign
                for h in species.habitats:
                    if getattr(h, '_campaign', None) is None:
                        h._campaign = api_campaign
            config.parameters.Vector_Species_Params.append(species.to_schema_dict())
        else:
            from emodpy_malaria.malaria_vector_species_params import species_params
            vector_species_parameters = species_params(manifest, species)
            if isinstance(vector_species_parameters, list):
                raise ValueError(
                    f"'{species}' species not found in list, available species are: {vector_species_parameters}. "
                    f"We suggest adding 'gambiae' species and changing "
                    f"the name and relevant parameters with set_species_params() or "
                    f"adding your species to malaria_vector_species_params.py.\n")
            else:
                config.parameters.Vector_Species_Params.append(vector_species_parameters)

    return config


def add_genes_and_alleles(config, manifest, species: str, alleles: list[tuple]):
    """
    Adds alleles to a species

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest file containing the schema path
        species (str): species to which to assign the **alleles**
        alleles (list[tuple]): List of tuples of (Name, Initial_Allele_Frequency, Is_Y_Chromosome) for a set of alleles
            or (Name, Initial_Allele_Frequency), 1/0 or True/False can be used for Is_Y_Chromosome,
            third parameter is assumed False (0). If the third parameter is set to 1 in any of the tuples,
            we assume, this is a gender gene.

    Returns:
        (dict): configured config
    """

    if not species or not alleles or not config or not manifest:
        raise ValueError("Please set all parameters, 'alleles' needs to be a list of tuples.\n")

    gene = s2c.get_class_with_defaults("idmType:VectorGene", schema_path=manifest.schema_file)
    for allele in alleles:
        vector_allele = s2c.get_class_with_defaults("idmType:VectorAllele", schema_path=manifest.schema_file)
        vector_allele.Name = allele[0]
        vector_allele.Initial_Allele_Frequency = allele[1]
        if len(allele) == 3:
            if allele[2]:
                gene.Is_Gender_Gene = 1
                vector_allele.Is_Y_Chromosome = 1
        gene.Alleles.append(vector_allele)

    species_params = get_species_params(config, species)
    species_params.Genes.append(gene)

    return config


def add_mutation(config, manifest, species, mutate_from, mutate_to, probability):
    """
    Adds to **Mutations** parameter in a Gene which has the matching **Alleles**

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest file containing the schema path
        species (str): Name of vector species to which we're adding mutations
        mutate_from (str): The allele in the gamete that could mutate
        mutate_to (str): The allele that this locus will change to during gamete generation
        probability (float): The probability that the allele will mutate from one allele to the other during the
            creation of the gametes

    Returns:
        (dict): configured config
    """

    species_params = get_species_params(config, species)
    found = False
    for gene in species_params["Genes"]:
        allele_names = []
        for allele in gene["Alleles"]:
            allele_names.append(allele["Name"])
        if mutate_from in allele_names and mutate_to in allele_names:
            found = True
            mutations = s2c.get_class_with_defaults("idmType:VectorAlleleMutation", schema_path=manifest.schema_file)
            mutations.Mutate_From = mutate_from
            mutations.Mutate_To = mutate_to
            mutations.Probability_Of_Mutation = probability
            gene.Mutations.append(mutations)

    if not found:
        raise ValueError(f"Allele name(s) '{mutate_from}' and/or '{mutate_to}' were not found for {species}.\n")

    return config


def create_trait(manifest, trait: str = None, modifier: float = None,
                 sporozoite_barcode_string: str = None, gametocyte_a_barcode_string: str = None,
                 gametocyte_b_barcode_string: str = None):
    """
    Configures and returns a modifier trait.

    Args:
        manifest (ModuleType): manifest file containing the schema path
        trait (str): The trait to be modified of vectors with the given allele combination.
            Available traits are: "INFECTED_BY_HUMAN", "FECUNDITY", "FEMALE_EGG_RATIO", "STERILITY",
            "TRANSMISSION_TO_HUMAN", "ADJUST_FERTILE_EGGS", "MORTALITY", "INFECTED_PROGRESS", "OOCYST_PROGRESSION",
            "SPOROZOITE_MORTALITY"
        modifier (float): The multiplier to use to modify the given **trait** for vectors with the given allele combination.
        sporozoite_barcode_string (str): TBD
        gametocyte_a_barcode_string (str): TBD
        gametocyte_b_barcode_string (str): TBD

    Returns:
        (dict): trait parameters that can be added to a list and passed to add_trait() function
    """
    traits_available = [t.value for t in VectorTrait]
    if not trait or modifier is None:
        raise ValueError(f'Please define both trait and modifier. Available traits are: {traits_available}.\n')

    if not isinstance(trait, VectorTrait):
        try:
            trait = VectorTrait(trait)
        except ValueError:
            raise ValueError(f"Can't find trait '{trait}' in available traits. Traits available for use "
                             f"are {traits_available}")

    if trait == VectorTrait.OOCYST_PROGRESSION and not (gametocyte_a_barcode_string and gametocyte_b_barcode_string):
        raise ValueError("With trait = 'OOCYST_PROGRESSION', you need to define gametocyte_a_barcode_string and "
                         "gametocyte_b_barcode_string. \n")
    if trait == VectorTrait.SPOROZOITE_MORTALITY and not sporozoite_barcode_string:
        raise ValueError("With trait = 'SPOROZOITE_MORTALITY', you need to define sporozoite_barcode_string.\n")

    trait_modifier = s2c.get_class_with_defaults("idmType:TraitModifier", schema_path=manifest.schema_file)
    trait_modifier.Trait = trait
    trait_modifier.Modifier = modifier
    if trait == VectorTrait.SPOROZOITE_MORTALITY:
        trait_modifier.Sporozoite_Barcode_String = sporozoite_barcode_string
    if trait == VectorTrait.OOCYST_PROGRESSION:
        trait_modifier.Gametocyte_A_Barcode_String = gametocyte_a_barcode_string
        trait_modifier.Gametocyte_B_Barcode_String = gametocyte_b_barcode_string

    return trait_modifier


def add_trait(config, manifest, species, allele_combo: list = None, trait_modifiers: list = None):
    """
    Use this function to add traits as part of vector genetics configuration, the trait is assigned to the
    species' **Gene_To_Trait_Modifiers** parameter

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest file containing the schema path
        species (str): Name of species for which to add this  Gene_To_Trait_Modifiers
        allele_combo (list): List of lists, This defines a possible subset of allele pairs that a vector could have.
            Each pair are alleles from one gene.  If the vector has this subset, then the associated traits will
            be adjusted.  Order does not matter.  '*' is allowed when only the occurrence of one allele is important.
            Example::

            [[  "X",  "X" ], [ "a0", "a1" ]]

        trait_modifiers (list): list of trait modifier parameters created with create_trait() function.

    Returns:
        (dict): configured config
    """
    species_params = get_species_params(config, species)
    validate_allele_combo(species_params=species_params, allele_combo=allele_combo)

    if not trait_modifiers or not isinstance(trait_modifiers, list):
        raise ValueError("Please make sure to pass in a list of trait modifiers created by create_trait() function.\n")

    trait = s2c.get_class_with_defaults("idmType:GeneToTraitModifierConfig", schema_path=manifest.schema_file)
    trait.Allele_Combinations = allele_combo
    trait.Trait_Modifiers = trait_modifiers
    species_params.Gene_To_Trait_Modifiers.append(trait)

    return config


def add_blood_meal_mortality(config, manifest,
                             species: str,
                             allele_combo: list,
                             default_probability_of_death: float,
                             probability_of_death_for_allele_combo: float):
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
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest module containing the schema path
        species (str): Name of the species of vectors to give the specific probability to.
        allele_combo (list): The combination of alleles that a mosquito's genome must have in order to
            apply associated probability.  You do not need to specify alleles for every locus.
            The ones not defined are not considered in the match  This should be a two-dimensional
            array where each internal array has two strings representing two alleles of the same
            locus.  Each separate internal array represents locus, and you can only have one entry
            per locus.  You can use '*' for an allele to say any allele. For example,
            [ ["a1", "a1"], ["b1, "*"] ] says any mosquito with a1-a1 in the first locus and
            b1 in either chromosome of the second locus.
        default_probability_of_death (float): The probability used if the genome of the mosquito does not
            match any of the defined allele combinations in Genetic_Probabilities.
        probability_of_death_for_allele_combo (float): The probability to use if the genome of the mosquito
            has the matching Allele_Combinations.  The default is zero.

    Returns:
        (dict): configured config
    """

    # checks if species name is valid
    species_params = get_species_params(config, species)

    if (default_probability_of_death < 0.0) or (1.0 < default_probability_of_death):
        raise ValueError(f"Invalid value for 'default_probability_of_death'={default_probability_of_death}.\n"
                         f"The value must be between 0 and 1.\n")

    validate_allele_combo(species_params=species_params, allele_combo=allele_combo)

    if (probability_of_death_for_allele_combo < 0.0) or (1.0 < probability_of_death_for_allele_combo):
        raise ValueError(f"Invalid value for 'probability_of_death_for_allele_combo'={probability_of_death_for_allele_combo}.\n"
                         f"The value must be between 0 and 1.\n")

    acp = s2c.get_class_with_defaults("idmType:AlleleComboProbabilityConfig", schema_path=manifest.schema_file)
    acp.Allele_Combinations = allele_combo
    acp.Probability = probability_of_death_for_allele_combo

    species_params.Blood_Meal_Mortality.Genetic_Probabilities.append(acp)

    default_prob = species_params.Blood_Meal_Mortality.Default_Probability
    default_prob = 1.0 - ((1.0 - default_prob) * (1.0 - default_probability_of_death))
    species_params.Blood_Meal_Mortality.Default_Probability = default_prob

    return config


def add_insecticide_resistance(config, manifest, insecticide_name: str, species: str,
                               allele_combo: list[list[str]], blocking: float = 1.0, killing: float = 1.0,
                               repelling: float = 1.0, larval_killing: float = 1.0):
    """
        Use this function to add to the list of **Resistances** parameter for a specific insecticide
        Add each resistance separately.

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest file containing the schema path
        insecticide_name (str): The name of the insecticide to which attach the resistance.
        species (str): Name of the species of vectors. Must be one of the species defined for this simulation.
        allele_combo (list[list[str]]): List of combination of alleles that vectors must have in order to be resistant.
            All the genes defined for the **species** must be present in the combo, but not all the alleles need to be
            defined. You can use * symbol for alleles to say any allele. For example, [[a1,a1],[b0,*]] matches
            any vector with a1-a1 in the first gene and b0 in the second gene regardless of the other b-gene allele.
        blocking (float): The value used to modify (multiply) the blocking effectivity of an intervention. The intervention
            must have a blocking effect for this to have an effect.
            Default is 1, values less than 1 reduce the effectivity, and values greater than 1 increase the effectivity.
        killing (float): The value used to modify (multiply) the killing effectivity of an intervention. The intervention
            must have a killing effect for this to have an effect.
            Default is 1, values less than 1 reduce the effectivity, and values greater than 1 increase the effectivity.
        repelling (float): The value used to modify (multiply) the repelling effectivity of an intervention. The intervention
            must have a repelling effect for this to have an effect.
            Default is 1, values less than 1 reduce the effectivity, and values greater than 1 increase the effectivity.
        larval_killing (float): The value used to modify (multiply) the larval **killing** effectivity of an intervention.
            The intervention must have a larval **killing** effect for this to have an effect (e.g. larvicides).
            Default is 1, values less than 1 reduce the effectivity, and values greater than 1 increase the effectivity.

    Returns:
        (dict): configured config
    """

    # checks if species name is valid
    species_params = get_species_params(config, species)
    validate_allele_combo(species_params=species_params, allele_combo=allele_combo)

    resistance = s2c.get_class_with_defaults("idmType:ResistantAlleleComboProbabilityConfig", schema_path=manifest.schema_file)
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

    new_insecticide = s2c.get_class_with_defaults("idmType:Insecticide", schema_path=manifest.schema_file)
    new_insecticide.Name = insecticide_name
    new_insecticide.Resistances.append(resistance)
    config.parameters.Insecticides.append(new_insecticide)

    return config


def add_species_drivers(config, manifest, species: str = None, driving_allele: str = None, driver_type: str = "CLASSIC",
                        to_copy: str = None, to_replace: str = None, likelihood_list: list = None,
                        shredding_allele_required: str = None, allele_to_shred: str = None,
                        allele_to_shred_to: str = None, allele_shredding_fraction: float = None,
                        allele_to_shred_to_surviving_fraction: float = None):
    """
        Add a gene drive that propagates a particular set of alleles.
        Adds one **Alleles_Driven** item to the **Alleles_Driven** list, using 'driving_allele' as key if matching one
        already exists.

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest file containing the schema path
        species (str): Name of the species for which we're setting the drivers
        driving_allele (str): This is the allele that is known as the driver
        driver_type (str): This indicates the type of driver.
            CLASSIC - The driver can only drive if the one gamete has the driving allele and the other has a specific
            allele to be replaced
            INTEGRAL_AUTONOMOUS - At least one of the gametes must have the driver.  Alleles can still be driven if the
            driving allele is in both gametes or even if the driving allele cannot replace the allele in the
            other gamete
            X_SHRED, Y_SHRED -  cannot be used in the same **species** during one simulation/realization. The **driving_allele**
            must exist at least once in the genome for shredding to occur. If there is only one, it can exist in either
            half of the genome.
            DAISY_CHAIN -  can be used for drives that do not drive themselves but can be driven by another allele.
        to_copy (str): The main allele to be copied Allele_To_Copy
        to_replace (str): The allele that must exist and will be replaced by the copy Allele_To_Replace
        likelihood_list (list): A list of tuples in format: [(Copy_To_Allele, Likelihood),(),()] to assign to
            Copy_To_Likelyhood list
        shredding_allele_required (str): The genome must have this gender allele in order for shredding to occur.
            If the driver is X_SHRED, then the allele must be designated as a Y chromosome. If the driver is Y_SHRED,
            then the allele must NOT be designated as a Y chromosome
        allele_to_shred (str): The genome must have this gender allele in order for shredding to occur. If the driver is
            X_SHRED, then the allele must NOT be designated as a Y chromosome. If the driver is Y_SHRED, then the allele
            must be designated as a Y chromosome
        allele_to_shred_to (str): This is a gender allele that the 'shredding' will change the **allele_to_shred** into. It can
            be a temporary allele that never exists in the output or could be something that appears due to
            resistance/failures
        allele_shredding_fraction (float): This is the fraction of the alleles_to_Shred that will be converted to
            **allele_to_shred_to**. Values 0 to 1.  If this value is less than 1, then some of the **allele_to_shred** will
            remain and be part of the gametes.
        allele_to_shred_to_surviving_fraction (float): A trait modifier will automatically generated for
            [ Allele_To_Shred_To, * ], the trait ADJUST_FERTILE_EGGS, and this value as its modifier.  Values 0 to 1.
            A value of 0 implies perfect shredding such that no allele_to_Shred_To survive in the eggs. A value of 1
            means all of the 'shredded' alleles survive.

    Returns:
        (dict): configured config
    """
    if not config or not manifest or not species or not driving_allele or not to_copy or not to_replace or not likelihood_list:
        raise ValueError("Please define all the parameters for this function (except shredding, unless you're using them).\n")

    if not isinstance(driver_type, DriverType):
        try:
            driver_type = DriverType(driver_type)
        except ValueError:
            valid_types = [d.value for d in DriverType]
            raise ValueError(f"Invalid driver_type '{driver_type}'. Must be one of: {valid_types}\n")

    shred_types = (DriverType.X_SHRED, DriverType.Y_SHRED)
    has_shred_params = (shredding_allele_required or allele_to_shred
                        or allele_to_shred_to or allele_shredding_fraction
                        or allele_to_shred_to_surviving_fraction)
    if driver_type not in shred_types and has_shred_params:
        raise ValueError("Please do not define any shredding parameters if you're not using 'driver_type' = X_SHRED or Y_SHRED.\n")
    elif driver_type == DriverType.DAISY_CHAIN:
        for (copy_to_allele, likelihood) in likelihood_list:
            if copy_to_allele == driving_allele:
                raise ValueError(f"For DAISY_CHAIN driver_type, you cannot have the Driving_Allele (driving_allele) "
                                 f"= '{driving_allele}' be the same as any of the Copy_To_Allele (in likelihood_list) = "
                                 f"'({copy_to_allele}, {likelihood})'.\n")

    species_params = get_species_params(config, species)
    gender_allele_required = False
    gender_allele_to_shred = False
    gender_allele_to_shred_to = False

    gene_driver = s2c.get_class_with_defaults("idmType:VectorGeneDriver", schema_path=manifest.schema_file)
    gene_driver.Driving_Allele = driving_allele
    gene_driver.Driver_Type = driver_type

    if driver_type == DriverType.X_SHRED or driver_type == DriverType.Y_SHRED:
        if not allele_to_shred or not allele_to_shred_to or not shredding_allele_required:
            raise ValueError("For 'driver_type'= X_SHRED or Y_SHRED, please define all the shredding parameters.\n")
        for gene in species_params.Genes:
            if gene["Is_Gender_Gene"] == 1:
                for allele in gene["Alleles"]:
                    if allele["Name"] == shredding_allele_required:
                        gender_allele_required = True
                        if driver_type == DriverType.X_SHRED and allele["Is_Y_Chromosome"] == 0:
                            raise ValueError("For 'driver_type' = X_SHRED, 'shredding_allele_required' should be a Y chromosome.\n")
                        elif driver_type == DriverType.Y_SHRED and allele["Is_Y_Chromosome"] == 1:
                            raise ValueError("For 'driver_type' = Y_SHRED, 'shredding_allele_required' should be an X chromosome.\n")
                    elif allele["Name"] == allele_to_shred:
                        gender_allele_to_shred = True
                        if driver_type == DriverType.X_SHRED and allele["Is_Y_Chromosome"] == 1:
                            raise ValueError("For 'driver_type'= X_SHRED, 'allele_to_shred' should be X chromosome.\n")
                        elif driver_type == DriverType.Y_SHRED and allele["Is_Y_Chromosome"] == 0:
                            raise ValueError("For 'driver_type'= Y_SHRED, 'allele_to_shred' should be Y chromosome.\n")
                    elif allele["Name"] == allele_to_shred_to:
                        gender_allele_to_shred_to = True
                        if driver_type == DriverType.X_SHRED and allele["Is_Y_Chromosome"] == 1:
                            raise ValueError("For 'driver_type'= X_SHRED, 'allele_to_shred' should be X chromosome.\n")
                        elif driver_type == DriverType.Y_SHRED and allele["Is_Y_Chromosome"] == 0:
                            raise ValueError("For 'driver_type'= Y_SHRED, 'allele_to_shred_to' should be Y chromosome.\n")

        if not (gender_allele_required and gender_allele_to_shred and gender_allele_to_shred_to):
            raise ValueError("Looks like shredding_allele_required or allele_to_shred or allele_to_shred_to are not "
                             "on a gender gene, but they all should be. Please verify your settings.\n")

        shredding_alleles = s2c.get_class_with_defaults("idmType:ShreddingAlleles", schema_path=manifest.schema_file)
        shredding_alleles.Allele_Required = shredding_allele_required
        shredding_alleles.Allele_Shredding_Fraction = allele_shredding_fraction
        shredding_alleles.Allele_To_Shred = allele_to_shred
        shredding_alleles.Allele_To_Shred_To = allele_to_shred_to
        shredding_alleles.Allele_To_Shred_To_Surviving_Fraction = allele_to_shred_to_surviving_fraction
        gene_driver.Shredding_Alleles = shredding_alleles

    allele_driven = s2c.get_class_with_defaults("idmType:AlleleDriven", schema_path=manifest.schema_file)
    allele_driven.Allele_To_Copy = to_copy
    allele_driven.Allele_To_Replace = to_replace
    for index, likely in enumerate(likelihood_list):
        c2likelyhood = s2c.get_class_with_defaults("idmType:CopyToAlleleLikelihood", schema_path=manifest.schema_file)
        c2likelyhood.Copy_To_Allele = likely[0]
        c2likelyhood.Likelihood = likely[1]
        allele_driven.Copy_To_Likelihood.append(c2likelyhood)

    # check if the Driving_Allele already exists
    if "Drivers" in species_params:
        for driver in species_params.Drivers:
            if driving_allele == driver["Driving_Allele"]:
                if driver_type == driver["Driver_Type"]:
                    driver["Alleles_Driven"].append(allele_driven)
                    return config
                else:
                    raise ValueError(f"The gene driver with 'driving_allele'={driving_allele} must have exactly one "
                                     f"entry in 'Alleles_Driven' for this allele and therefore cannot be used for "
                                     f"multiple 'driver_type's.\n")

    if driver_type == DriverType.X_SHRED or driver_type == DriverType.Y_SHRED:
        gene_driver.Driving_Allele_Params = allele_driven
    else:
        gene_driver.Alleles_Driven = [allele_driven]

    gene_driver.Driver_Type = driver_type  # to circumvent the implicit settings
    species_params.Drivers.append(gene_driver)
    return config


def add_maternal_deposition(config, manifest, species: str, cas9_grna_from: str,
                            allele_to_cut: str, likelihood_list: list):
    """
        Adds a maternal deposition element for the specified species.
        After meiosis and fertilization, maternal deposition of Cas9 and gRNA can form additional drive-resistant alleles
        in the zygote or early embryo from wildtype alleles. These elements define the likelihoods of forming additional
        drive-resistant alleles.

    Args:
        config (dict): schema-backed config smart dict
        manifest (ModuleType): manifest file containing the schema path
        species (str): Name of the species for which we're adding the maternal deposition element.
        cas9_grna_from (str): This is an allele for presence of which in the mother we will be checking to see if additional
            resistance alleles will be formed. This is the allele must be one of the 'driving_alleles' from
            vector_config.add_species_drivers() function.
        allele_to_cut (str): The allele from which resistance alleles might be formed due to maternal deposition. This must
            be one of the 'to_replace' alleles defined in the vector_config.add_species_drivers() function.
        likelihood_list (list): A list of tuples in format: [(<cut_to_allele>, <likelihood>),(),()] which will be converted
            to an array of allele-to-likelihood dictionaries to be applied to the '**allele_to_cut**' for each
            '**cas9_grna_from**' present in the mother. The sum of likelihoods should be equal to 1.

    Returns:
        (dict): Config object with maternal deposition parameters added for the specified species.
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

    maternal_deposition = s2c.get_class_with_defaults("idmType:MaternalDeposition", schema_path=manifest.schema_file)
    maternal_deposition.Cas9_gRNA_From = cas9_grna_from
    maternal_deposition.Allele_To_Cut = allele_to_cut

    total = 0.0
    for index, likely in enumerate(likelihood_list):
        c2likelyhood = s2c.get_class_with_defaults("idmType:CutToAlleleLikelihood", schema_path=manifest.schema_file)
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


def set_max_larval_capacity(config, species_name: str, habitat_type: HabitatType, max_larval_capacity: float):
    """
    Set the **Max_Larval_Capacity** for a given species and habitat. The habitat must already
    exist in the species' **Habitats** list (added via `add_species()`).

    Args:
        config (dict): schema-backed config smart dict
        species_name (str): Name of the vector species to target.
        habitat_type (HabitatType): The [HabitatType](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/) of
            the habitat to update (e.g. ``HabitatType.TEMPORARY_RAINFALL``).
        max_larval_capacity (float): New value of Max_Larval_Capacity for the habitat.

    Raises:
        ValueError: If the species or habitat type is not found.
    """
    if not isinstance(habitat_type, HabitatType):
        try:
            habitat_type = HabitatType(habitat_type)
        except ValueError:
            valid_types = [h.value for h in HabitatType]
            raise ValueError(f"Invalid habitat_type '{habitat_type}'. Must be one of: {valid_types}")

    habitats = get_species_params(config, species_name).Habitats
    for hab in habitats:
        if hab['Habitat_Type'] == habitat_type:
            hab['Max_Larval_Capacity'] = max_larval_capacity
            return

    raise ValueError(f"Failed to find habitat_type '{habitat_type}' for species '{species_name}'.")


def add_microsporidia(config, manifest, species_name: str = None,
                      strain_name: str = "Strain_A",
                      female_to_male_probability: float = 0,
                      female_to_egg_probability: float = 0,
                      male_to_female_probability: float = 0,
                      male_to_egg_probability: float = 0,
                      duration_to_disease_acquisition_modification: Union[ValueMap, dict] = None,
                      duration_to_disease_transmission_modification: Union[ValueMap, dict] = None,
                      larval_growth_modifier: float = 1,
                      female_mortality_modifier: float = 1,
                      male_mortality_modifier: float = 1):
    """
        Adds microsporidia parameters to the named species' parameters.

    Args:
        config (dict): schema-backed config dictionary, written to config.json
        manifest (ModuleType): file that contains path to the schema file
        species_name (str): Species to target, Name parameter
        strain_name (str): Strain_Name The name/identifier of the collection of transmission parameters.
            Cannot be empty string
        female_to_male_probability (float): Microsporidia_Female_to_Male_Transmission_Probability The probability
            an infected female will infect an uninfected male.
        female_to_egg_probability (float): Microsporidia_Female_To_Egg_Transmission_Probability The probability
            an infected female will infect her eggs when laying them.
        male_to_female_probability (float): Microsporidia_Male_To_Female_Transmission_Probability The probability
            an infected male will infect an uninfected female
        male_to_egg_probability (float): Microsporidia_Male_To_Egg_Transmission_Probability The probability a female that
            mated with an infected male will infect her eggs when laying them, independent of her being infected and
            transmitting to her offspring.
        duration_to_disease_acquisition_modification (Union[ValueMap, dict]):
            Microsporidia_Duration_To_Disease_Acquisition_Modification,
            a [ValueMap](https://emod.idmod.org/emodpy/autoapi/emodpy/campaign/common/) or a dict with "Times" and "Values" keys
            as an age-based modification that the female will acquire malaria.
            Times is an array of days in ascending order since infection. Values are probabilities (0-1).
            Defaults to ``ValueMap(times=[0, 3, 6, 9], values=[1.0, 1.0, 0.5, 0.0])``.
        duration_to_disease_transmission_modification (Union[ValueMap, dict]):
            Microsporidia_Duration_To_Disease_Transmission_Modification,
            a [ValueMap](https://emod.idmod.org/emodpy/autoapi/emodpy/campaign/common/) or a dict with "Times" and "Values" keys
            as an age-based modification that the female will transmit malaria.
            Times is an array of days in ascending order since infection. Values are probabilities (0-1).
            Defaults to ``ValueMap(times=[0, 3, 6, 9], values=[1.0, 1.0, 0.75, 0.5])``.
        larval_growth_modifier (float): Microsporidia_Larval_Growth_Modifier A multiplier modifier to the daily, temperature
            dependent, larval growth progress.
        female_mortality_modifier (float): Microsporidia_Female_Mortality_Modifier A multiplier modifier on the death
            rate for female vectors due to general life expectancy, age, and dry heat
        male_mortality_modifier (float): Microsporidia_Male_Mortality_Modifier A multiplier modifier on the death rate for
            male vectors due to general life expectancy, age, and dry heat
    """
    if not strain_name:
        raise ValueError("Please define strain_name.\n")
    if duration_to_disease_acquisition_modification is None:
        duration_to_disease_acquisition_modification = ValueMap(times=[0, 3, 6, 9], values=[1.0, 1.0, 0.5, 0.0])
    elif isinstance(duration_to_disease_acquisition_modification, dict):
        duration_to_disease_acquisition_modification = ValueMap(
            times=duration_to_disease_acquisition_modification["Times"],
            values=duration_to_disease_acquisition_modification["Values"]
        )
    if duration_to_disease_transmission_modification is None:
        duration_to_disease_transmission_modification = ValueMap(times=[0, 3, 6, 9], values=[1.0, 1.0, 0.75, 0.5])
    elif isinstance(duration_to_disease_transmission_modification, dict):
        duration_to_disease_transmission_modification = ValueMap(
            times=duration_to_disease_transmission_modification["Times"],
            values=duration_to_disease_transmission_modification["Values"]
        )

    if not api_campaign.get_schema():
        api_campaign.set_schema(manifest.schema_file)

    species_parameters = get_species_params(config, species_name)
    microsporidia = s2c.get_class_with_defaults("idmType:MicrosporidiaParameters", schema_path=manifest.schema_file)
    microsporidia.Duration_To_Disease_Acquisition_Modification = duration_to_disease_acquisition_modification.to_schema_dict(api_campaign)
    microsporidia.Duration_To_Disease_Transmission_Modification = duration_to_disease_transmission_modification.to_schema_dict(api_campaign)
    microsporidia.Female_To_Male_Transmission_Probability = female_to_male_probability
    microsporidia.Male_To_Female_Transmission_Probability = male_to_female_probability
    microsporidia.Larval_Growth_Modifier = larval_growth_modifier
    microsporidia.Female_To_Egg_Transmission_Probability = female_to_egg_probability
    microsporidia.Female_Mortality_Modifier = female_mortality_modifier
    microsporidia.Male_Mortality_Modifier = male_mortality_modifier
    microsporidia.Male_To_Egg_Transmission_Probability = male_to_egg_probability
    microsporidia.Strain_Name = strain_name
    species_parameters.Microsporidia.append(microsporidia)


def _set_vector_migration_config(config, species, filename, x_vector_migration=None):
    """Implicit config function registered by MalariaDemographics.add_vector_migration().

    Called at task build time to set per-species vector migration parameters.

    Args:
        config (object): simulation config object with a ``parameters`` attribute
        species (str): species Name string
        filename (str): binary migration filename (name only, not full path)
        x_vector_migration (float): rate multiplier

    Returns:
        config with vector migration parameters set on the named species
    """
    params = get_species_params(config, species)
    params.Vector_Migration_Filename = filename
    if x_vector_migration is not None:
        params.x_Vector_Migration = x_vector_migration
    params.Vector_Migration_Modifier_Equation = ModifierEquationType.LINEAR.value
    params.Vector_Migration_Habitat_Modifier = 0
    params.Vector_Migration_Food_Modifier = 0
    params.Vector_Migration_Stay_Put_Modifier = 0
    return config


def add_vector_migration(task: object,
                         species: str = None,
                         vector_migration_data: object = None,
                         vector_migration_filename_path: str = None,
                         x_vector_migration: float = 1):
    """Adds vector migration parameters to the named species' parameters and adds the migration file to the
    common_assets in task.

    .. deprecated::
        Use `MalariaDemographics.add_vector_migration()` instead, which follows the
        deferred implicit pattern and does not require a task object upfront.

    Provide either ``vector_migration_data`` (a VectorMigrationData object) or
    ``vector_migration_filename_path`` (path to an existing binary file), not both.

    Args:
        task (emodpy.emod_task.EMODTask): contains config to edit and assets to add migration file to
        species (str): Species to target, Name parameter
        vector_migration_data (object): VectorMigrationData object. If provided, writes the binary file
            and registers it with the task.
        vector_migration_filename_path (str): Path with the filename of the migration file to use to avoid importing
            and writing the file from a VectorMigrationData object. If provided, registers the file with the task.
        x_vector_migration (float): Scale factor for the rate of vector migration to other nodes.
    """
    warnings.warn(
        "add_vector_migration(task, ...) is deprecated. "
        "Use MalariaDemographics.add_vector_migration(data, species, ...) instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    if vector_migration_data is not None and vector_migration_filename_path is not None:
        raise ValueError("Provide either vector_migration_data or vector_migration_filename_path, not both.")
    if vector_migration_data is None and not vector_migration_filename_path:
        raise ValueError("Provide either vector_migration_data (VectorMigrationData object) "
                         "or vector_migration_filename_path (path to existing binary file).")

    if vector_migration_data is not None:
        filename = f"vector_migration_{species}.bin" if species else "vector_migration.bin"
        path = vector_migration_data.to_migration_file(filename)
        vector_migration_filename_path = str(path)

    head, tail = os.path.split(vector_migration_filename_path)

    params = get_species_params(task.config, species)
    params.Vector_Migration_Filename = tail
    params.x_Vector_Migration = x_vector_migration
    params.Vector_Migration_Modifier_Equation = ModifierEquationType.LINEAR.value
    params.Vector_Migration_Habitat_Modifier = 0
    params.Vector_Migration_Food_Modifier = 0
    params.Vector_Migration_Stay_Put_Modifier = 0
    if not task.common_assets.has_asset(vector_migration_filename_path):
        task.common_assets.add_asset(vector_migration_filename_path)
    if not task.common_assets.has_asset(vector_migration_filename_path + ".json"):
        task.common_assets.add_asset(vector_migration_filename_path + ".json")
