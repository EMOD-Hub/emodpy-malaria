from emodpy.campaign.node_intervention import MultiNodeInterventionDistributor
from emodpy.campaign.node_intervention import BroadcastCoordinatorEventFromNode as BroadcastCoordinatorEventFromNode  # noqa: F401
from emodpy.campaign.node_intervention import BroadcastNodeEvent
from emodpy.campaign.node_intervention import ImportPressure
from emodpy.campaign.node_intervention import MigrateFamily
from emodpy.campaign.node_intervention import NodePropertyValueChanger
from emodpy.campaign.node_intervention import Outbreak
from emodpy.campaign.base_intervention import NodeIntervention
from emodpy.campaign.common import CommonInterventionParameters
from emodpy.utils import validate_value_range
from emodpy_malaria.campaign.waning_config import AbstractWaningConfig, InsecticideWaningEffect
from emodpy_malaria.utils.config_utils import validate_insecticide_name, validate_vector_sampling_type, validate_sugar_feeding_frequency
from emodpy_malaria.utils.distributions import BaseDistribution, ConstantDistribution
from emodpy_malaria.utils.emod_enum import (
    HabitatType, EIRType, ChallengeType,
    MosquitoReleaseType, WolbachiaType,
    ArtificialDietTarget)

from emod_api import campaign as api_campaign
from emod_api import schema_to_class as s2c

from typing import Union
from functools import partial


class LarvalHabitatMultiplierSpec:
    """
    Defines a single entry in the **Larval_Habitat_Multiplier** array used
    by [ScaleLarvalHabitat](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/node_intervention/).
    Each entry specifies a multiplier (``factor``) to scale the larval
    habitat capacity for a given habitat type and, optionally, a specific
    mosquito species. Multiple entries can be combined in a list to target
    different habitat/species combinations independently.

    When ``habitat`` is set to ``HabitatType.ALL_HABITATS``, the factor
    applies to every habitat type. When ``species`` is ``"ALL_SPECIES"``
    (the default), the factor applies to all species that share that
    habitat type. If both ``ALL_HABITATS`` and ``"ALL_SPECIES"`` are used,
    the factor uniformly scales all larval habitat in the node.

    See [Larval Habitat](https://emod.idmod.org/emodpy-malaria/emod/parameter-configuration-larval/)
    for information on habitat type definitions and configuration.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        habitat (Union[HabitatType, str], required):
            The habitat type to which this multiplier applies. Use the
            [HabitatType](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/) enum
            values:

            * ``HabitatType.ALL_HABITATS`` -- Apply to all habitat types.
            * ``HabitatType.TEMPORARY_RAINFALL`` -- Temporary rainfall
              pools.
            * ``HabitatType.WATER_VEGETATION`` -- Semi-permanent water
              near vegetation.
            * ``HabitatType.HUMAN_POPULATION`` -- Habitat proportional to
              human population.
            * ``HabitatType.CONSTANT`` -- Constant-capacity habitat.
            * ``HabitatType.BRACKISH_SWAMP`` -- Brackish/swamp water.
            * ``HabitatType.LINEAR_SPLINE`` -- Habitat defined by a linear
              spline function.

        factor (float, required):
            The multiplier by which to scale the larval **habitat**
            availability. A value of 1.0 means no change, values less
            than 1.0 reduce **habitat** capacity, and values greater than 1.0
            increase it. Range: 0 to 3.4e+38.

        species (str, optional):
            The name of the mosquito species to which this multiplier
            applies. Must match one of the species names defined in
            Vector_Species_Params in the configuration, or
            ``"ALL_SPECIES"`` to apply to all species.
            Default value: "ALL_SPECIES"

    Example:
        Reduce all habitat by half for all species::

            from emodpy_malaria.campaign.node_intervention import LarvalHabitatMultiplierSpec
            from emodpy_malaria.utils.emod_enum import HabitatType

            spec = LarvalHabitatMultiplierSpec(
                campaign=campaign,
                habitat=HabitatType.ALL_HABITATS,
                factor=0.5
            )

    Example:
        Double temporary rainfall habitat for a specific species::

            spec = LarvalHabitatMultiplierSpec(
                campaign=campaign,
                habitat=HabitatType.TEMPORARY_RAINFALL,
                factor=2.0,
                species="arabiensis"
            )
    """

    def __init__(self, campaign, habitat: Union[HabitatType, str],
                 factor: float, species: str = "ALL_SPECIES"):
        if not isinstance(habitat, HabitatType):
            try:
                habitat = HabitatType(habitat)
            except ValueError:
                raise ValueError(
                    f"habitat must be a HabitatType enum value, got {habitat!r}. "
                    f"Valid options: {list(HabitatType)}")
        self._campaign = campaign
        self._habitat = habitat
        self._factor = factor
        self._species = species

    def to_schema_dict(self) -> s2c.ReadOnlyDict:
        obj = s2c.get_class_with_defaults(
            "idmType:LarvalHabitatMultiplierSpec",
            schema_json=self._campaign.get_schema())
        obj.Habitat = self._habitat
        obj.Factor = self._factor
        obj.Species = self._species
        obj.pop("schema", None)
        obj.pop("explicits", None)
        return obj


class SpaceSpraying(NodeIntervention):
    """
    The **SpaceSpraying** intervention class implements node-level vector
    control by spraying pesticides outdoors. This intervention targets
    specific habitat types, and imposes a mortality rate on all targeted
    (both immature and adult male and female) mosquitoes. All mosquitoes
    have daily mortality rates; mortality for adult females due to
    spraying is independent of whether or not they are feeding.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Yes. Can target sub-groups using genomes,
      especially to target specific sexes.
    - **Time-based expiration:** No
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Die Without Attempting To Feed
      and Die Before Attempting Human Feed
    - **Vector effects:** Killing
    - **Vector sexes affected:** Males and females
    - **Vector life stage affected:** Adult and immature

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy and waning for the outdoor spray. All
            targeted mosquitoes (male, female, adult, and immature) have a daily probability
            of dying based on this effect. The killing probability is multiplied by
            Spray_Coverage to determine the final kill rate.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        spray_coverage (float, optional):
            The proportion of the node that has been sprayed. This value is multiplied by
            the current efficacy of the waning effect to determine the final kill rate.
            Range: 0.0 to 1.0.
            Default value: 1.0

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 spray_coverage: float = 1.0,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SpaceSpraying', common_intervention_parameters)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class IndoorSpaceSpraying(NodeIntervention):
    """
    The **IndoorSpaceSpraying** intervention class is a node-level vector
    control mechanism that works by spraying insecticides indoors. This
    class is similar to
    [IRSHousingModification](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/)
    but ``IRSHousingModification`` is an individual-level intervention
    that uses both killing and blocking effects and
    ``IndoorSpaceSpraying`` is a node-level intervention that uses only
    a killing effect. Do not use these two interventions together. If
    used with ``IRSHousingModification``, the ``IndoorSpaceSpraying``
    will override ``IRSHousingModification``'s killing effect.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Yes. Can target subgroups using genomes,
      especially when targeting certain species.
    - **Time-based expiration:** No
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Indoor Die After Feeding,
      Indoor Die Before Feeding (when combined with
      HumanHostSeekingTrap)
    - **Vector effects:** Killing
    - **Vector sexes affected:** Indoor meal-seeking females only
    - **Vector life stage affected:** Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy and waning for the indoor spray. This
            effect applies to indoor meal-seeking female mosquitoes that encounter the
            sprayed surfaces. Do not use this intervention together with
            IRSHousingModification, as it will override the killing effect.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        spray_coverage (float, optional):
            The proportion of the node that has been sprayed. This value is multiplied by
            the current efficacy of the waning effect to determine the final kill rate.
            Range: 0.0 to 1.0.
            Default value: 1.0

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common parameters.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 spray_coverage: float = 1.0,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'IndoorSpaceSpraying', common_intervention_parameters)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class MultiInsecticideSpaceSpraying(NodeIntervention):
    """
    The **MultiInsecticideSpaceSpraying** intervention class is a
    node-level intervention that models the application of a
    multi-insecticide outdoor spray. As a spray, this kills male and
    female adult and immature mosquitoes. Mosquitoes have a daily
    probability of dying; feeding status does not impact the probability
    of death for adult female mosquitoes.

    The effectiveness of the intervention is combined using the
    following equation::

        Total efficacy = 1.0 - (1.0 - efficacy_1)
                             * (1.0 - efficacy_2)
                             * ... * (1.0 - efficacy_n)

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Yes. Can target subgroups using genomes,
      especially when targeting certain species.
    - **Time-based expiration:** No
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Die Without Attempting to Feed
      and Die Before Attempting Human Feed
    - **Vector effects:** Killing
    - **Vector sexes affected:** Both males and females
    - **Vector life stage affected:** Adult and immature

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        insecticides (list[InsecticideWaningEffect], required):
            A list of
            [InsecticideWaningEffect](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/)
            objects with killing config only (variant ``"K"``), each defining the killing
            waning effect and insecticide name for one insecticide. The total killing
            efficacy across insecticides is combined as
            ``1 - (1 - efficacy_1) * (1 - efficacy_2) * ... * (1 - efficacy_n)``.
            Only relevant when modeling insecticide resistance via the vector genetics
            system. The insecticide name in each entry must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a
            vector encounters this intervention, the insecticide's killing, blocking, and
            repelling effects are modified based on the vector's genotype and the resistance
            modifiers configured for that insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.

        spray_coverage (float, optional):
            The proportion of the node that has been sprayed. This value is multiplied by
            the current efficacy of the waning effect to determine the final kill rate.
            Range: 0.0 to 1.0.
            Default value: 1.0

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 insecticides: list[InsecticideWaningEffect],
                 spray_coverage: float = 1.0,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MultiInsecticideSpaceSpraying', common_intervention_parameters)

        for i, ins in enumerate(insecticides):
            if not isinstance(ins, InsecticideWaningEffect):
                raise ValueError(
                    f"'insecticides[{i}]' must be an InsecticideWaningEffect instance, "
                    f"got {type(ins).__name__}.")
            ins.require_variant("K", "MultiInsecticideSpaceSpraying")
        self._intervention.Insecticides = [ins.to_schema_dict() for ins in insecticides]
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)
        for ins in insecticides:
            if ins._insecticide_name is not None:
                campaign.implicits.append(partial(
                    validate_insecticide_name, insecticide_name=ins._insecticide_name,
                    intervention_name='MultiInsecticideSpaceSpraying'))


class MultiInsecticideIndoorSpaceSpraying(NodeIntervention):
    """
    The **MultiInsecticideIndoorSpaceSpraying** intervention class is a
    node-level intervention that uses Indoor Residual Spraying (IRS)
    with multiple insecticides. It builds on the
    [IndoorSpaceSpraying](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/node_intervention/)
    class by allowing for multiple insecticides, each with their own
    specified killing efficacy.

    The effectiveness of the intervention is combined using the
    following equation::

        Total efficacy = 1.0 - (1.0 - efficacy_1)
                             * (1.0 - efficacy_2)
                             * ... * (1.0 - efficacy_n)

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Yes. Can target subgroups using genomes,
      especially when targeting certain species.
    - **Time-based expiration:** No
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Indoor Die After Feeding
    - **Vector effects:** Killing
    - **Vector sexes affected:** Females only
    - **Vector life stage affected:** Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        insecticides (list[InsecticideWaningEffect], required):
            A list of
            [InsecticideWaningEffect](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/)
            objects with killing config only (variant ``"K"``), each defining the killing
            waning effect and insecticide name for one insecticide. The total killing
            efficacy across insecticides is combined as
            ``1 - (1 - efficacy_1) * (1 - efficacy_2) * ... * (1 - efficacy_n)``.
            Only relevant when modeling insecticide resistance via the vector genetics
            system. The insecticide name in each entry must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a
            vector encounters this intervention, the insecticide's killing, blocking, and
            repelling effects are modified based on the vector's genotype and the resistance
            modifiers configured for that insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.

        spray_coverage (float, optional):
            The proportion of the node that has been sprayed. This value is multiplied by
            the current efficacy of the waning effect to determine the final kill rate.
            Range: 0.0 to 1.0.
            Default value: 1.0

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 insecticides: list[InsecticideWaningEffect],
                 spray_coverage: float = 1.0,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MultiInsecticideIndoorSpaceSpraying', common_intervention_parameters)

        for i, ins in enumerate(insecticides):
            if not isinstance(ins, InsecticideWaningEffect):
                raise ValueError(
                    f"'insecticides[{i}]' must be an InsecticideWaningEffect instance, "
                    f"got {type(ins).__name__}.")
            ins.require_variant("K", "MultiInsecticideIndoorSpaceSpraying")
        self._intervention.Insecticides = [ins.to_schema_dict() for ins in insecticides]
        self._intervention.Spray_Coverage = validate_value_range(spray_coverage, 'spray_coverage', 0, 1, float)
        for ins in insecticides:
            if ins._insecticide_name is not None:
                campaign.implicits.append(partial(
                    validate_insecticide_name, insecticide_name=ins._insecticide_name,
                    intervention_name='MultiInsecticideIndoorSpaceSpraying'))


class Larvicides(NodeIntervention):
    """
    The **Larvicides** intervention class is a node-level intervention
    that configures a killing effect for larvae in specific habitats.
    This intervention can be used to simulate the application of
    larvicides to water bodies.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Yes. The vector genome can be used to
      target specific genders.
    - **Time-based expiration:** No. It will continue to exist even if
      efficacy is zero.
    - **Purge existing:** No. Already existing intervention(s) of this
      class continue to exist together with any new interventions. Their
      efficacies combine as 1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Combines with competition and
      rainfall to kill larvae every time step.
    - **Vector effects:** Killing
    - **Vector sexes affected:** Both male and female larvae
    - **Vector life stage affected:** Larval

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of larval killing efficacy and waning in the targeted habitat.
            This determines the daily probability of larvae dying due to the larvicide
            application. The effect combines with competition and rainfall to kill larvae
            every time step.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        habitat_target (Union[HabitatType, str], optional):
            Target habitat type for the larvicide. Use the
            [HabitatType](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/) enum values:

            * ``HabitatType.ALL_HABITATS`` -- Target all larval habitat types in the node.
            * ``HabitatType.TEMPORARY_RAINFALL`` -- Target temporary, rainfall-dependent habitats.
            * ``HabitatType.WATER_VEGETATION`` -- Target standing water with vegetation habitats.
            * ``HabitatType.HUMAN_POPULATION`` -- Target habitats that scale with human population.
            * ``HabitatType.CONSTANT`` -- Target habitats with constant capacity.
            * ``HabitatType.BRACKISH_SWAMP`` -- Target brackish swamp habitats.
            * ``HabitatType.LINEAR_SPLINE`` -- Target habitats defined by a linear spline function.

            Default value: HabitatType.ALL_HABITATS

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None

    Example:
        Apply larvicide to all habitats::

            from emodpy_malaria.campaign.node_intervention import Larvicides
            from emodpy_malaria.campaign.waning_config import Constant
            from emodpy_malaria.utils.emod_enum import HabitatType

            larvicide = Larvicides(
                campaign=campaign,
                killing_config=Constant(campaign, initial_effect=0.7),
                habitat_target=HabitatType.ALL_HABITATS
            )

    Example:
        Target only temporary rainfall habitats::

            larvicide = Larvicides(
                campaign=campaign,
                killing_config=Constant(campaign, initial_effect=0.9),
                habitat_target=HabitatType.TEMPORARY_RAINFALL,
                insecticide_name="Temephos"
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 habitat_target: Union[HabitatType, str] = HabitatType.ALL_HABITATS,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'Larvicides', common_intervention_parameters)

        self._intervention.Larval_Killing_Config = killing_config.to_schema_dict(campaign)

        if not isinstance(habitat_target, HabitatType):
            try:
                habitat_target = HabitatType(habitat_target)
            except ValueError:
                raise ValueError(
                    f"habitat_target must be a HabitatType enum value, got {habitat_target!r}. "
                    f"Valid options: {list(HabitatType)}")
        self._intervention.Habitat_Target = habitat_target

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class LarvalMicrosporidiaIntervention(NodeIntervention):
    """
    The **LarvalMicrosporidiaIntervention** is a node-level intervention
    that mimics seeding water bodies with microsporidia or other
    endosymbiont to infect mosquito larvae, reducing their ability to
    transmit malaria. The intervention distributes a specific
    microsporidia strain and can be limited to a particular larval
    habitat type. When no other ``LarvalMicrosporidiaIntervention``
    instances are present, the portion of larvae infected each day is
    the product of the current infectivity config value and habitat
    coverage. The infectivity waning effect can be configured to decay
    over time.

    Multiple LarvalMicrosporidiaInterventions can target larvae in the same habitat. The
    algorithm resolves these into a single map of strain to fraction
    newly infected: interventions are processed sequentially, each new
    intervention's coverage reaches into both already-claimed and
    unclaimed larvae, and overlapping portions are split proportionally
    by effect strength. Same-strain entries are merged with
    coverage-weighted averaging. Total coverage across all strains never
    exceeds 1.0.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** No
    - **Time-based expiration:** No. It will continue to exist even if
      efficacy is zero.
    - **Purge existing:** No. Already existing intervention(s) of this
      class continue to exist together with any new interventions. Their
      coverages and effects are resolved per the algorithm described
      above.
    - **Vector killing contributes to:** Does not apply
    - **Vector effects:** Microsporidia/endosymbiont infection of larvae
    - **Vector sexes affected:** Both male and female larvae
    - **Vector life stage affected:** Larval

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        strain_name (str, required):
            Name of the microsporidia strain (must match a strain defined in vector species config).

        habitat_target (Union[HabitatType, str], optional):
            Target habitat type for the intervention. Use the
            [HabitatType](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/) enum values:

            * ``HabitatType.ALL_HABITATS`` -- Target all larval habitat types in the node.
            * ``HabitatType.TEMPORARY_RAINFALL`` -- Target temporary, rainfall-dependent habitats.
            * ``HabitatType.WATER_VEGETATION`` -- Target standing water with vegetation habitats.
            * ``HabitatType.HUMAN_POPULATION`` -- Target habitats that scale with human population.
            * ``HabitatType.CONSTANT`` -- Target habitats with constant capacity.
            * ``HabitatType.BRACKISH_SWAMP`` -- Target brackish swamp habitats.
            * ``HabitatType.LINEAR_SPLINE`` -- Target habitats defined by a linear spline function.

            Default value: HabitatType.ALL_HABITATS

        habitat_coverage (float, optional):
            Fraction of targeted habitat(s) that receive the intervention.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        infectivity_config (AbstractWaningConfig, optional):
            The configuration of the daily microsporidia infectivity applied to larvae and
            its waning over time. This determines the probability that larvae acquire
            microsporidia from this intervention on each time step. The actual fraction of
            larvae infected is the product of this effect and **habitat_coverage**.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None

    Example:
        Introduce microsporidia into all habitats::

            from emodpy_malaria.campaign.node_intervention import LarvalMicrosporidiaIntervention
            from emodpy_malaria.campaign.waning_config import Constant
            from emodpy_malaria.utils.emod_enum import HabitatType

            microsporidia = LarvalMicrosporidiaIntervention(
                campaign=campaign,
                strain_name="Strain_A",
                habitat_target=HabitatType.ALL_HABITATS,
                habitat_coverage=0.8,
                infectivity_config=Constant(campaign, initial_effect=0.5)
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 strain_name: str,
                 habitat_target: Union[HabitatType, str] = HabitatType.ALL_HABITATS,
                 habitat_coverage: float = 1,
                 infectivity_config: AbstractWaningConfig = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'LarvalMicrosporidiaIntervention', common_intervention_parameters)

        self._intervention.Strain_Name = strain_name

        if not isinstance(habitat_target, HabitatType):
            try:
                habitat_target = HabitatType(habitat_target)
            except ValueError:
                raise ValueError(
                    f"habitat_target must be a HabitatType enum value, got {habitat_target!r}. "
                    f"Valid options: {list(HabitatType)}")
        self._intervention.Habitat_Target = habitat_target

        self._intervention.Habitat_Coverage = validate_value_range(habitat_coverage, 'habitat_coverage', 0, 1, float)
        if infectivity_config is not None:
            self._intervention.Infectivity_Config = infectivity_config.to_schema_dict(campaign)


class InputEIR(NodeIntervention):
    """
    The **InputEIR** intervention class enables the Entomological
    Inoculation Rate (EIR) to be configured either for each month or
    for each day of the year in a particular node. The EIR is the
    number of infectious mosquito bites received in a night, usually
    calculated by taking the number of mosquito bites received per
    night and multiplying by the proportion of those bites that are
    positive for sporozoites.

    Whether each individual actually becomes infected from the
    challenge is modified by individual-level factors. Each person's
    probability of infection is scaled by a combined ``relative_risk``
    that accounts for:

    * **Acquisition immunity** -- both naturally acquired immunity
      that develops over time through repeated exposure and any
      reduction from acquisition-blocking vaccines (e.g.,
      [SimpleVaccine](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/)
      with ``vaccine_type=VaccineType.ACQUISITION_BLOCKING``).
    * **Age-dependent biting risk** -- if
      ``config.parameters.Age_Dependent_Biting_Risk_Type`` is set to
      ``AgeDependentBitingRiskType.LINEAR`` or
      ``AgeDependentBitingRiskType.SURFACE_AREA_DEPENDENT``,
      younger (smaller) individuals receive proportionally fewer bites.
    * **Demographics-based risk** -- if individuals have unique
      biting risk set via
      [MalariaDemographics.set_risk_distribution()](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/demographics/MalariaDemographics/),
      each individual's personal risk factor further scales their
      exposure.

    Vector control interventions will not affect the EIR delivered by
    this intervention. If vectors are included when this class is used,
    the specified EIR is added on top of the EIR provided by vectors.
    When distributing ``InputEIR`` to a node that already has an
    existing ``InputEIR`` intervention, the existing intervention will
    be purged and replaced with the new one.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Does not apply
    - **Time-based expiration:** No
    - **Purge existing:** Yes. Adding a new intervention of this class
      will overwrite an existing intervention of the same class.
    - **Vector killing contributes to:** Does not apply
    - **Vector effects:** Does not apply
    - **Vector sexes affected:** Does not apply
    - **Vector life stage affected:** Does not apply

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        monthly_eir (list[float], optional):
            An array of exactly 12 values where each value is the mean
            number of infectious bites experienced by an individual for
            that month. Each value must be between 0 and 1000. The
            "current month" is based on time since the intervention was
            distributed, creating a 12-month repeating pattern from the
            distribution day. Exactly one of ``monthly_eir`` or
            ``daily_eir`` must be provided.
            Default value: None

        daily_eir (list[float], optional):
            An array of exactly 365 values where each value is the mean
            number of infectious bites experienced by an individual for
            that day of the year. Each value must be between 0 and 1000.
            Exactly one of ``monthly_eir`` or ``daily_eir`` must be
            provided.
            Default value: None

        scaling_factor (float, optional):
            A modifier that is multiplied by the EIR determined for the
            current day. Can be used to uniformly scale all EIR values
            up or down without modifying the input array. Must be
            between 0 and 10,000.
            Default value: 1.0

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None

    Example:
        Apply a seasonal monthly EIR pattern::

            from emodpy_malaria.campaign.node_intervention import InputEIR

            eir = InputEIR(
                campaign=campaign,
                monthly_eir=[5, 10, 20, 30, 25, 15, 10, 8, 12, 18, 10, 5]
            )

    Example:
        Apply daily EIR with a scaling factor::

            import numpy as np
            from emodpy_malaria.campaign.node_intervention import InputEIR

            daily_values = list(np.random.uniform(0, 2, 365))
            eir = InputEIR(
                campaign=campaign,
                daily_eir=daily_values,
                scaling_factor=0.5
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 monthly_eir: list[float] = None,
                 daily_eir: list[float] = None,
                 scaling_factor: float = 1.0,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'InputEIR', common_intervention_parameters)

        if monthly_eir is not None and daily_eir is not None:
            raise ValueError(
                "Only one of monthly_eir or daily_eir may be provided, not both.")
        if monthly_eir is None and daily_eir is None:
            raise ValueError(
                "Exactly one of monthly_eir or daily_eir must be provided.")

        if monthly_eir is not None:
            if len(monthly_eir) != 12:
                raise ValueError(
                    f"monthly_eir must contain exactly 12 values, got {len(monthly_eir)}.")
            self._intervention.EIR_Type = EIRType.MONTHLY
            self._intervention.Monthly_EIR = monthly_eir
        else:
            if len(daily_eir) != 365:
                raise ValueError(
                    f"daily_eir must contain exactly 365 values, got {len(daily_eir)}.")
            self._intervention.EIR_Type = EIRType.DAILY
            self._intervention.Daily_EIR = daily_eir

        self._intervention.Scaling_Factor = validate_value_range(scaling_factor, 'scaling_factor', 0, 10000, float)


class MalariaChallenge(NodeIntervention):
    """
    The **MalariaChallenge** intervention class is a node-level
    intervention similar to
    [Outbreak](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/node_intervention/).
    However, instead of distributing infections, it distributes malaria
    challenges by either inflicting sporozoites or infectious
    mosquito bites.

    Whether each individual actually becomes infected from the
    challenge is modified by individual-level factors. Each person's
    probability of infection is scaled by a combined ``relative_risk``
    that accounts for:

    * **Acquisition immunity** -- both naturally acquired immunity
      that develops over time through repeated exposure and any
      reduction from acquisition-blocking vaccines (e.g.,
      [SimpleVaccine](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/)
      with ``vaccine_type=VaccineType.ACQUISITION_BLOCKING``).
    * **Age-dependent biting risk** -- if
      ``config.parameters.Age_Dependent_Biting_Risk_Type`` is set to
      ``AgeDependentBitingRiskType.LINEAR`` or
      ``AgeDependentBitingRiskType.SURFACE_AREA_DEPENDENT``,
      younger (smaller) individuals receive proportionally fewer bites.
    * **Demographics-based risk** -- if individuals have unique
      biting risk set via
      [MalariaDemographics.set_risk_distribution()](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/demographics/MalariaDemographics/),
      each individual's personal risk factor further scales their
      exposure.

    This intervention cannot be used with parasite genetics
    (``MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS``). Use
    [OutbreakIndividualMalariaGenetics](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/)
    instead.

    - **Distributed to:** Nodes

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        sporozoite_count (int, optional): Number of sporozoites per individual.
            Exactly one of ``sporozoite_count`` or ``infectious_bite_count`` must be provided,
            but not both.
            Default value: None

        infectious_bite_count (int, optional):
            Number of infectious bites per individual. Exactly one of ``sporozoite_count`` or
            ``infectious_bite_count`` must be provided, but not both.
            Default value: None

        coverage (float, optional):
            The fraction of the population that receives the challenge. Must be between 0 and 1.
            Default value: 1.0

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None

    Example:
        Create a challenge with 5 infectious bites::

            from emodpy_malaria.campaign.node_intervention import MalariaChallenge
            from emodpy_malaria.utils.emod_enum import ChallengeType

            challenge = MalariaChallenge(
                campaign=campaign,
                challenge_type=ChallengeType.INFECTIOUS_BITES,
                infectious_bite_count=5
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 sporozoite_count: int = None,
                 infectious_bite_count: int = None,
                 coverage: float = 1.0,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MalariaChallenge', common_intervention_parameters)

        if sporozoite_count is not None and infectious_bite_count is not None:
            raise ValueError(
                "Only one of sporozoite_count or infectious_bite_count may be provided, not both.")
        if sporozoite_count is None and infectious_bite_count is None:
            raise ValueError(
                "Exactly one of sporozoite_count or infectious_bite_count must be provided.")

        if sporozoite_count is not None:
            self._intervention.Challenge_Type = ChallengeType.SPOROZOITES
            self._intervention.Sporozoite_Count = sporozoite_count
        else:
            self._intervention.Challenge_Type = ChallengeType.INFECTIOUS_BITES
            self._intervention.Infectious_Bite_Count = infectious_bite_count

        self._intervention.Coverage = validate_value_range(coverage, 'coverage', 0, 1, float)


class MosquitoRelease(NodeIntervention):
    """
    The **MosquitoRelease** intervention class adds mosquito release
    vector control programs to the simulation. Mosquito release is a
    key vector control mechanism that allows the release of sterile
    males, genetically modified mosquitoes, or even Wolbachia- or
    Microsporidia-infected mosquitoes. See
    [Vector Control](https://emod.idmod.org/emodpy-malaria/emod/parameter-configuration-vector-control/)
    for related configuration parameters.

    Released vectors are added to the population and participate in
    the vector life cycle and mating system the same day. You can
    also release already-mated females to guarantee specific genomes
    in the offspring by setting the ``released_mate_genome`` parameter.
    When ``released_mate_genome`` is provided, the released females
    will be fully gestated and ready to lay eggs immediately.

    The number of mosquitoes released can be specified as a fixed
    count (``released_number``) or as a ratio relative to the
    existing population of the same gender from the previous timestep
    (``released_ratio``). Exactly one of these must be provided.

    See [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for
    information on defining vector genomes, gene drivers, and
    insecticide resistance alleles. See
    [Microsporidia Infection Model](https://emod.idmod.org/emodpy-malaria/emod/vector-model-microsporidia/)
    for information on microsporidia strains and their transmission
    dynamics within vector populations.

    - **Distributed to:** Nodes
    - **Expires:** Immediately (one-time release)

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        released_species (str, required):
            The name of the released mosquito species, such as
            *arabiensis*. The Vector_Species_Params configuration
            parameter must contain this specific species.

        released_genome (list[list[str]], required):
            Defines the alleles of the genome of the vectors to be
            released. Must define all alleles including the gender
            gene. Wildcards (``*``) are not allowed. See
            Vector_Species_Params for the gene definitions for
            each species.

        released_number (int, optional):
            The number of mosquitoes released in the intervention.
            Exactly one of ``released_number`` or ``released_ratio``
            must be provided. Range: 1 to 100,000,000.
            Default value: None

        released_ratio (float, optional):
            The number of released mosquitoes as a proportion of the
            mosquito population of that species from the previous timestep,
            specifically considering mosquitoes of the same gender as
            those being released. Exactly one of ``released_number``
            or ``released_ratio`` must be provided. Range: 0 to
            3.4e+38.
            Default value: None

        released_infectious (float, optional):
            The fraction of released female vectors that are
            infectious (carrying sporozoites). Cannot be used with
            male releases. Cannot be used when Malaria_Model is
            set to
            ``MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS``.
            Range: 0 to 1.
            Default value: 0.0

        released_mate_genome (list[list[str]], optional):
            Defines the alleles of the genome of the mate for
            pre-mated female releases. When provided,
            ``released_genome`` must be female and
            ``released_mate_genome`` must be male. Must define all
            alleles including the gender gene. Wildcards (``*``) are
            not allowed. The released females will be fully gestated
            and ready to lay eggs, which will be the product of
            ``released_genome`` and ``released_mate_genome``.
            Default value: None

        released_wolbachia (Union[WolbachiaType, str], optional):
            The Wolbachia type of released mosquitoes. Use the
            [WolbachiaType](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/)
            enum values:

            * ``WolbachiaType.VECTOR_WOLBACHIA_FREE`` -- No Wolbachia
              infection.
            * ``WolbachiaType.VECTOR_WOLBACHIA_A`` -- Wolbachia type A.
            * ``WolbachiaType.VECTOR_WOLBACHIA_B`` -- Wolbachia type B.
            * ``WolbachiaType.VECTOR_WOLBACHIA_AB`` -- Wolbachia types
              A and B.

            Default value: WolbachiaType.VECTOR_WOLBACHIA_FREE

        released_microsporidia_strain (str, optional):
            The name of the microsporidia strain for the released
            mosquitoes. The strain name must match a strain defined in
            Vector_Species_Params > Microsporidia for the
            species being released. An empty string or None indicates
            no microsporidia infection.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None

    Example:
        Release 10,000 sterile male mosquitoes::

            from emodpy_malaria.campaign.node_intervention import MosquitoRelease

            release = MosquitoRelease(
                campaign=campaign,
                released_species="arabiensis",
                released_genome=[["X", "Y"], ["a0", "a0"]],
                released_number=10000
            )

    Example:
        Release pre-mated Wolbachia-infected females at a ratio::

            from emodpy_malaria.campaign.node_intervention import MosquitoRelease
            from emodpy_malaria.utils.emod_enum import WolbachiaType

            release = MosquitoRelease(
                campaign=campaign,
                released_species="arabiensis",
                released_genome=[["X", "X"], ["a1", "a1"]],
                released_ratio=0.1,
                released_mate_genome=[["X", "Y"], ["a0", "a0"]],
                released_wolbachia=WolbachiaType.VECTOR_WOLBACHIA_A
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 released_species: str,
                 released_genome: list[list[str]],
                 released_number: int = None,
                 released_ratio: float = None,
                 released_infectious: float = 0.0,
                 released_mate_genome: list[list[str]] = None,
                 released_wolbachia: Union[WolbachiaType, str] = WolbachiaType.VECTOR_WOLBACHIA_FREE,
                 released_microsporidia_strain: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MosquitoRelease', common_intervention_parameters)

        self._intervention.Released_Species = released_species
        self._intervention.Released_Genome = released_genome

        if released_number is not None and released_ratio is not None:
            raise ValueError(
                "Only one of released_number or released_ratio may be provided, not both.")
        if released_number is None and released_ratio is None:
            raise ValueError(
                "Exactly one of released_number or released_ratio must be provided.")

        if released_number is not None:
            self._intervention.Released_Type = MosquitoReleaseType.FIXED_NUMBER
            self._intervention.Released_Number = released_number
        else:
            self._intervention.Released_Type = MosquitoReleaseType.RATIO
            self._intervention.Released_Ratio = released_ratio

        self._intervention.Released_Infectious = validate_value_range(
            released_infectious, 'released_infectious', 0, 1, float)

        if released_mate_genome is not None:
            self._intervention.Released_Mate_Genome = released_mate_genome

        if not isinstance(released_wolbachia, WolbachiaType):
            try:
                released_wolbachia = WolbachiaType(released_wolbachia)
            except ValueError:
                raise ValueError(
                    f"released_wolbachia must be a WolbachiaType enum value, got {released_wolbachia!r}. "
                    f"Valid options: {list(WolbachiaType)}")
        self._intervention.Released_Wolbachia = released_wolbachia

        if released_microsporidia_strain is not None:
            self._intervention.Released_Microsporidia_Strain = released_microsporidia_strain


class ScaleLarvalHabitat(NodeIntervention):
    """
    The **ScaleLarvalHabitat** intervention class is a node-level
    intervention that enables species-specific habitat modification
    within shared habitat types. This intervention has a similar
    function to the demographic parameter ``ScaleLarvalMultiplier``,
    but enables habitat availability to be modified at any time or at
    any location during the simulation, as specified in the campaign
    event.

    The value by which to scale the larval habitat availability
    (specified in **Habitats** in the configuration file) can be set
    per intervention, across all habitat types, for specific habitat
    types, or for specific mosquito species within each habitat type.
    See [Larval Habitat](https://emod.idmod.org/emodpy-malaria/emod/parameter-configuration-larval/)
    for more information on larval habitat configuration.

    To reset the multiplier, you must either replace the existing one
    with a new intervention with the same ``Intervention_Name`` where
    the multiplier/factor is 1.0 or use ``Disqualifying_Properties``
    to cause the intervention to abort.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** No
    - **Time-based expiration:** No. It will continue to exist even if
      the efficacy is zero.
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Does not apply
    - **Vector effects:** Does not apply
    - **Vector sexes affected:** Both
    - **Vector life stage affected:** Eggs and larvae, depending on
      oviposition settings

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        larval_habitat_multiplier (list[LarvalHabitatMultiplierSpec], required):
            A list of
            [LarvalHabitatMultiplierSpec](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/node_intervention/)
            objects, each specifying a habitat type, a scaling factor,
            and optionally a target species. Multiple entries can be
            used to apply different multipliers to different
            habitat/species combinations.

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None

    Example:
        Reduce all habitats by half for all species::

            from emodpy_malaria.campaign.node_intervention import (
                ScaleLarvalHabitat, LarvalHabitatMultiplierSpec)
            from emodpy_malaria.utils.emod_enum import HabitatType

            slh = ScaleLarvalHabitat(
                campaign=campaign,
                larval_habitat_multiplier=[
                    LarvalHabitatMultiplierSpec(
                        campaign=campaign,
                        habitat=HabitatType.ALL_HABITATS,
                        factor=0.5
                    )
                ]
            )

    Example:
        Apply different multipliers per habitat type and species::

            slh = ScaleLarvalHabitat(
                campaign=campaign,
                larval_habitat_multiplier=[
                    LarvalHabitatMultiplierSpec(
                        campaign=campaign,
                        habitat=HabitatType.TEMPORARY_RAINFALL,
                        factor=2.0,
                        species="arabiensis"
                    ),
                    LarvalHabitatMultiplierSpec(
                        campaign=campaign,
                        habitat=HabitatType.CONSTANT,
                        factor=0.1,
                        species="funestus"
                    )
                ]
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 larval_habitat_multiplier: list[LarvalHabitatMultiplierSpec],
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'ScaleLarvalHabitat', common_intervention_parameters)

        if not larval_habitat_multiplier:
            raise ValueError("larval_habitat_multiplier must contain at least one entry.")
        for i, spec in enumerate(larval_habitat_multiplier):
            if not isinstance(spec, LarvalHabitatMultiplierSpec):
                raise ValueError(
                    f"larval_habitat_multiplier[{i}] must be a LarvalHabitatMultiplierSpec instance, "
                    f"got {type(spec).__name__}.")
        self._intervention.Larval_Habitat_Multiplier = [
            spec.to_schema_dict() for spec in larval_habitat_multiplier
        ]


class OutdoorRestKill(NodeIntervention):
    """
    The **OutdoorRestKill** intervention class imposes node-targeted
    mortality to a vector that is at rest in an outdoor environment
    after a feed. This affects female vectors that have fed indoors and
    outdoors as well as males.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Yes. Can target sub-groups using genomes
      or specific sexes.
    - **Time-based expiration:** No. It will continue to exist even if
      efficacy is zero.
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Outdoor Die After Feeding.
      Note that it is a node-level intervention but does not impact the
      other node-level probabilities.
    - **Vector effects:** Killing
    - **Vector sexes affected:** Males and meal-seeking females
    - **Vector life stage affected:** Adults

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy for vectors resting outdoors after
            feeding. This applies to female vectors that have fed both indoors and outdoors.
            This also applied to male vectors every time step.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'OutdoorRestKill', common_intervention_parameters)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class OutdoorNodeEmanator(NodeIntervention):
    """
    The **OutdoorNodeEmanator** intervention class implements
    node-level outdoor emanators against blood meal-seeking vectors.
    This imitates the use of outdoor insecticide sprays. These
    interventions release insecticides into the air to repel or kill
    mosquitoes within the node. The intervention is distributed to
    nodes and affects all the meal-seeking vectors in the node.

    Female vectors seeking a blood meal are repelled at
    ``final_repelling = coverage * repelling_rate`` and killed at
    ``final_killing = coverage * killing_rate``. Vectors that are
    neither repelled nor killed continue to seek a meal indoors or
    outdoors (human and non-human) and are subject to other
    interventions. After successfully feeding, vectors are subjected
    again to the killing effect of the emanator as they exit indoors
    or remain outdoors after the meal. The intervention contributes to
    "survive without successful feed", "die before attempt human feed",
    and "die after feeding" statistics.

    If there are multiple ``OutdoorNodeEmanator`` instances in the
    node, their efficacies combine as
    ``1 - (1 - final_eff) * (1 - new_coverage * new_eff)``.
    The emanator also affects the entire male population of the node
    at every time step, applying only the killing effect.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Yes. Can target subgroups using genomes.
    - **Time-based expiration:** No
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Survive Without Successful
      Feed, Die Before Attempt Human Feed, Die After Feeding, male
      vector daily mortality
    - **Vector effects:** Repelling, killing
    - **Vector sexes affected:** Females seeking blood meal and all
      males
    - **Vector life stage affected:** Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            The configuration of repelling efficacy and waning for the outdoor emanator.
            This effect is applied first. An outdoor-meal seeking
            vector is repelled before any killing can occur. Repelled female vectors survive
            but do not attempt to feed again until the next day and are not subjected to the
            killing effect. This does not affect male vectors.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy and waning for the outdoor emanator. The
            killing effect applies to outdoor meal-seeking female vectors that were not repelled, and
            is applied again after vectors exit post-feeding. Males are subjected to the
            killing effect daily.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 killing_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'OutdoorNodeEmanator', common_intervention_parameters)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class SugarTrap(NodeIntervention):
    """
    The **SugarTrap** intervention class implements a vector
    sugar-baited trap to collect and kill sugar-feeding mosquitoes,
    sometimes called an attractive toxic sugar bait (ATSB). This
    intervention affects all mosquitoes living and feeding at a given
    node. Male vectors sugar-feed daily and female vectors sugar-feed
    once per blood meal (or upon emergence), so these traps can impact
    male survival on a daily basis. Efficacy can be modified using
    per-sex insecticide resistance.

    The impact of sugar-baited traps depends on the sugar-feeding
    behavior specified in the configuration file via
    ``Vector_Sugar_Feeding_Frequency``, whether there is no sugar
    feeding, sugar feeding occurs once at emergence, sugar feeding
    occurs once per blood meal, or sugar feeding occurs every day. If
    it is set to ``VECTOR_SUGAR_FEEDING_NONE``, this intervention will
    have no effect.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Yes. Can target sub-groups using genomes
      or specific sexes.
    - **Time-based expiration:** Yes. Expiration time can be specified
      using specific distributions.
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Sugar Trap Killing
    - **Vector effects:** Killing
    - **Vector sexes affected:** Males and females
    - **Vector life stage affected:** Adult and immature when they are
      emerging (if configured)

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy for the sugar-baited trap. Male vectors
            sugar-feed daily and female vectors sugar-feed once per blood meal (or upon
            emergence), so this effect impacts male survival on a daily basis. The impact
            depends on Vector_Sugar_Feeding_Frequency in the configuration file; if set
            to ``VECTOR_SUGAR_FEEDING_NONE``, this intervention will have no effect.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        expiration_period_distribution (BaseDistribution, optional):
            The distribution used to determine when each instance of this
            intervention expires and is removed from the node. Each
            instance draws an expiration duration from this distribution
            at the time of distribution. Use the distribution classes
            from [Distributions](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/):

            * [ConstantDistribution](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/)
            * [UniformDistribution](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/)
            * [GaussianDistribution](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/)
            * [ExponentialDistribution](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/)
            * [PoissonDistribution](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/)
            * [LogNormalDistribution](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/)
            * [WeibullDistribution](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/)
            * [DualConstantDistribution](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/)
            * [DualExponentialDistribution](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/distributions/)

            Default value: ``ConstantDistribution(3.40282e+38)``,
            which effectively means the intervention never expires.

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 expiration_period_distribution: BaseDistribution = None,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SugarTrap', common_intervention_parameters)
        campaign.implicits.append(validate_sugar_feeding_frequency)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        if expiration_period_distribution is None:
            expiration_period_distribution = ConstantDistribution(3.40282e+38)
        if not isinstance(expiration_period_distribution, BaseDistribution):
            raise ValueError(
                f"'expiration_period_distribution' must be an instance of BaseDistribution, "
                f"not {type(expiration_period_distribution)}.")
        self.set_distribution(expiration_period_distribution, 'Expiration_Period')
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class OvipositionTrap(NodeIntervention):
    """
    The **OvipositionTrap** intervention class utilizes an oviposition
    trap to collect host-seeking mosquitoes, based upon imposing a
    mortality to egg hatching from oviposition. This is a node-targeted
    intervention and affects all mosquitoes living and feeding at a
    given node. This trap requires the use of individual mosquitoes in
    the simulation configuration file (``Vector_Sampling_Type`` must be
    set to ``TRACK_ALL_VECTORS`` or ``SAMPLE_IND_VECTORS``), rather
    than the cohort model.

    The trap calculates a habitat-weighted average based on the current
    capacity of the habitat and uses this average to determine if the
    vector dies while laying eggs. A vector only lays eggs on the day
    she feeds. In the individual model, each vector has its own timer
    indicating when it should feed, and this duration can be
    temperature-dependent.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** No
    - **Time-based expiration:** No. It will continue to exist even if
      the efficacy is zero.
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Die Laying Eggs
    - **Vector effects:** Killing
    - **Vector sexes affected:** Recently-fed females only
    - **Vector life stage affected:** Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of the killing effects for the fraction of oviposition cycles
            that end in the female mosquito's death. If there is skip oviposition, this does
            not configure the mortality per skip, but instead configures the effective net
            mortality per gonotrophic cycle over all skips. The trap calculates a
            habitat-weighted average based on the current capacity of the habitat.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        habitat_target (Union[HabitatType, str], optional):
            Target habitat type for the trap. Use the
            [HabitatType](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/) enum values:

            * ``HabitatType.ALL_HABITATS`` -- Target all larval habitat types in the node.
            * ``HabitatType.TEMPORARY_RAINFALL`` -- Target temporary, rainfall-dependent habitats.
            * ``HabitatType.WATER_VEGETATION`` -- Target standing water with vegetation habitats.
            * ``HabitatType.HUMAN_POPULATION`` -- Target habitats that scale with human population.
            * ``HabitatType.CONSTANT`` -- Target habitats with constant capacity.
            * ``HabitatType.BRACKISH_SWAMP`` -- Target brackish swamp habitats.
            * ``HabitatType.LINEAR_SPLINE`` -- Target habitats defined by a linear spline function.

            Default value: HabitatType.ALL_HABITATS

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None

    Example:
        Place oviposition traps targeting all habitats::

            from emodpy_malaria.campaign.node_intervention import OvipositionTrap
            from emodpy_malaria.campaign.waning_config import Constant
            from emodpy_malaria.utils.emod_enum import HabitatType

            trap = OvipositionTrap(
                campaign=campaign,
                killing_config=Constant(campaign, initial_effect=0.8),
                habitat_target=HabitatType.ALL_HABITATS
            )
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 habitat_target: Union[HabitatType, str] = HabitatType.ALL_HABITATS,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'OvipositionTrap', common_intervention_parameters)
        campaign.implicits.append(partial(
            validate_vector_sampling_type,
            intervention_name="OvipositionTrap"))

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)

        if not isinstance(habitat_target, HabitatType):
            try:
                habitat_target = HabitatType(habitat_target)
            except ValueError:
                raise ValueError(
                    f"habitat_target must be a HabitatType enum value, got {habitat_target!r}. "
                    f"Valid options: {list(HabitatType)}")
        self._intervention.Habitat_Target = habitat_target

        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class SpatialRepellent(NodeIntervention):
    """
    The **SpatialRepellent** intervention class implements node-level
    spatial repellents exclusively against vectors looking to feed
    that day.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Yes. Can target subgroups using genomes.
    - **Time-based expiration:** No
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** No killing, but Survive
      Without Successful Feed
    - **Vector effects:** Repelling
    - **Vector sexes affected:** Females only
    - **Vector life stage affected:** Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        repelling_config (AbstractWaningConfig, required):
            The configuration of repelling efficacy and waning for the spatial repellent.
            This repels female vectors that are looking to feed that day, preventing them
            from attempting to blood feed. Repelled vectors survive and do not attempt to
            feed again until the following day.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 repelling_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SpatialRepellent', common_intervention_parameters)

        self._intervention.Repelling_Config = repelling_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class AnimalFeedKill(NodeIntervention):
    """
    The **AnimalFeedKill** intervention class imposes node-targeted
    mortality to a vector that feeds on animals.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** Yes. Can be used to target sub-groups
      using genomes.
    - **Time-based expiration:** No
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** Die Before Attempting to Feed
    - **Vector effects:** Killing
    - **Vector sexes affected:** Females seeking non-human blood meals
      only
    - **Vector life stage affected:** Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        killing_config (AbstractWaningConfig, required):
            The configuration of killing efficacy for vectors that feed on animals. This
            applies to female vectors seeking non-human blood meals. Portion of vectors
            seeking non-human blood meals is determined by the "Anthropophily" parameter in the species configuration.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 killing_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'AnimalFeedKill', common_intervention_parameters)

        self._intervention.Killing_Config = killing_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


class ArtificialDiet(NodeIntervention):
    """
    The **ArtificialDiet** intervention class is used to include feeding
    stations for vectors within a node in a simulation. This is a
    node-targeted intervention and takes effect at the broad village
    level rather than at the individual level. For individual-level
    effects, use
    [HumanHostSeekingTrap](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/individual_intervention/)
    instead. An artificial diet diverts some of the vectors seeking to
    blood feed that day, resulting in a two-fold benefit: uninfected
    mosquitoes avoid biting infected humans some of the time, decreasing
    human-to-vector transmission, and infectious vectors are diverted to
    feed on the artificial diet instead of humans, decreasing
    vector-to-human transmission.

    - **Distributed to:** Nodes
    - **Serialized:** No. Must be redistributed when starting from a
      serialized file.
    - **Uses insecticides:** No
    - **Time-based expiration:** No
    - **Purge existing:** Adding a new intervention of this class
      overwrites any existing intervention of the same class with the
      same ``Intervention_Name``. If ``Intervention_Name`` differs, both
      coexist and their efficacies combine as
      1-(1-prob1)*(1-prob2) etc.
    - **Vector killing contributes to:** No killing
    - **Vector effects:** Artificial Diet Feed instead of Human or
      Animal Feed
    - **Vector sexes affected:** Meal-seeking females only
    - **Vector life stage affected:** Adult

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        artificial_diet_target (Union[ArtificialDietTarget, str], required):
            The targeted deployment of the artificial diet. Use the
            [ArtificialDietTarget](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/utils/emod_enum/)
            enum values:

            * ``ArtificialDietTarget.AD_WITHIN_VILLAGE`` -- Within village
              deployment. Impacted by both SpaceSpraying and
              SpatialRepellent interventions.
            * ``ArtificialDietTarget.AD_OUTSIDE_VILLAGE`` -- Outside village
              deployment. Only impacted by SpaceSpraying.

        attraction_config (AbstractWaningConfig, required):
            The configuration for the fraction of blood-meal-seeking vectors attracted to the
            artificial diet and its waning over time. Attracted vectors feed on the diet
            instead of on humans or animals, reducing both human-to-vector and vector-to-human
            transmission.
            Available types are defined in [Waning Effects](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/campaign/waning_config/).

        insecticide_name (str, optional):
            The name of the insecticide used. Only relevant when modeling insecticide resistance
            via the vector genetics system. The name must match an insecticide defined via
            ``malaria_config.add_insecticide_resistance()`` in the config builder. When a vector
            encounters this intervention, the insecticide's killing, blocking, and repelling
            effects are modified based on the vector's genotype and the resistance modifiers
            configured for this insecticide. See
            [Insecticide Resistance](https://emod.idmod.org/emodpy-malaria/emod/vector-model-insecticide-resistance/)
            and [Vector Genetics](https://emod.idmod.org/emodpy-malaria/emod/vector-model-genetics/) for details.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 artificial_diet_target: Union[ArtificialDietTarget, str],
                 attraction_config: AbstractWaningConfig,
                 insecticide_name: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'ArtificialDiet', common_intervention_parameters)

        if not isinstance(artificial_diet_target, ArtificialDietTarget):
            try:
                artificial_diet_target = ArtificialDietTarget(artificial_diet_target)
            except ValueError:
                raise ValueError(
                    f"artificial_diet_target must be an ArtificialDietTarget enum value, "
                    f"got {artificial_diet_target!r}. "
                    f"Valid options: {list(ArtificialDietTarget)}")
        self._intervention.Artificial_Diet_Target = artificial_diet_target

        self._intervention.Attraction_Config = attraction_config.to_schema_dict(campaign)
        if insecticide_name is not None:
            self._intervention.Insecticide_Name = insecticide_name
            campaign.implicits.append(partial(
                validate_insecticide_name, insecticide_name=insecticide_name,
                intervention_name=type(self).__name__))


__all_exports = [
    BroadcastCoordinatorEventFromNode,
    LarvalHabitatMultiplierSpec,
    MultiNodeInterventionDistributor,
    BroadcastNodeEvent,
    ImportPressure,
    MigrateFamily,
    NodePropertyValueChanger,
    Outbreak,
    SpaceSpraying,
    IndoorSpaceSpraying,
    MultiInsecticideSpaceSpraying,
    MultiInsecticideIndoorSpaceSpraying,
    Larvicides,
    LarvalMicrosporidiaIntervention,
    InputEIR,
    MalariaChallenge,
    MosquitoRelease,
    ScaleLarvalHabitat,
    OutdoorRestKill,
    OutdoorNodeEmanator,
    SugarTrap,
    OvipositionTrap,
    SpatialRepellent,
    AnimalFeedKill,
    ArtificialDiet,
]

for _ in __all_exports:
    _.__module__ = __name__

__all__ = [_.__name__ for _ in __all_exports]
