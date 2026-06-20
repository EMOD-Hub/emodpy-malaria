import copy

from emodpy_malaria.vector_config import VectorSpeciesParameters, VectorHabitat
from emodpy_malaria.utils.emod_enum import HabitatType
from emodpy.campaign.common import ValueMap

_BASE = VectorSpeciesParameters(
    name="gambiae",
    habitats=[
        VectorHabitat(habitat_type=HabitatType.WATER_VEGETATION, max_larval_capacity=20000000)
    ],
    anthropophily=0.65,
    acquire_modifier=0.8,
    adult_life_expectancy=20,
    aquatic_arrhenius_1=84200000000,
    aquatic_arrhenius_2=8328,
    aquatic_mortality_rate=0.1,
    days_between_feeds=3,
    egg_batch_size=100,
    immature_duration=2,
    indoor_feeding_fraction=0.95,
    infected_arrhenius_1=117000000000,
    infected_arrhenius_2=8336,
    infected_egg_batch_factor=0.8,
    infectious_human_feed_mortality_factor=1.5,
    male_life_expectancy=10,
    transmission_rate=0.9,
    vector_sugar_feeding_frequency="VECTOR_SUGAR_FEEDING_NONE",
)

_gambiae = _BASE

_arabiensis = copy.deepcopy(_BASE)
_arabiensis.name = "arabiensis"
_arabiensis.indoor_feeding_fraction = 0.5
_arabiensis.habitats = [
    VectorHabitat(habitat_type=HabitatType.TEMPORARY_RAINFALL, max_larval_capacity=800000000),
    VectorHabitat(habitat_type=HabitatType.CONSTANT, max_larval_capacity=80000000),
]

_funestus = copy.deepcopy(_BASE)
_funestus.name = "funestus"
_funestus.habitats = [
    VectorHabitat(habitat_type=HabitatType.TEMPORARY_RAINFALL, max_larval_capacity=800000000),
    VectorHabitat(habitat_type=HabitatType.CONSTANT, max_larval_capacity=80000000),
]

_fpg_gambiae = copy.deepcopy(_BASE)
_fpg_gambiae.name = "fpg_gambiae"
_fpg_gambiae.indoor_feeding_fraction = 0.5
_fpg_gambiae.vector_sugar_feeding_frequency = "VECTOR_SUGAR_FEEDING_EVERY_DAY"
_fpg_gambiae.habitats = [
    VectorHabitat(
        habitat_type=HabitatType.LINEAR_SPLINE,
        max_larval_capacity=316227766.01683795,
        capacity_distribution_number_of_years=1,
        capacity_distribution_over_time=ValueMap(
            times=[0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167, 334.583],
            values=[3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8, 6.5, 2.6, 2.1]
        ),
    ),
]

_minimus = copy.deepcopy(_BASE)
_minimus.name = "minimus"
_minimus.anthropophily = 0.5
_minimus.adult_life_expectancy = 25
_minimus.egg_batch_size = 70
_minimus.indoor_feeding_fraction = 0.6
_minimus.transmission_rate = 0.8
_minimus.habitats = [
    VectorHabitat(habitat_type=HabitatType.WATER_VEGETATION, max_larval_capacity=20000000),
    VectorHabitat(
        habitat_type=HabitatType.LINEAR_SPLINE,
        max_larval_capacity=30000000,
        capacity_distribution_number_of_years=1,
        capacity_distribution_over_time=ValueMap(
            times=[0, 1, 245, 275, 364],
            values=[0.2, 0.2, 0.7, 3, 3]
        ),
    ),
]

_dirus = copy.deepcopy(_BASE)
_dirus.name = "dirus"
_dirus.anthropophily = 0.5
_dirus.adult_life_expectancy = 30
_dirus.egg_batch_size = 70
_dirus.indoor_feeding_fraction = 0.01
_dirus.transmission_rate = 0.8
_dirus.habitats = [
    VectorHabitat(habitat_type=HabitatType.CONSTANT, max_larval_capacity=10000000),
    VectorHabitat(habitat_type=HabitatType.TEMPORARY_RAINFALL, max_larval_capacity=70000000),
]

_SPECIES_DATA = {
    "gambiae": _gambiae,
    "arabiensis": _arabiensis,
    "funestus": _funestus,
    "fpg_gambiae": _fpg_gambiae,
    "minimus": _minimus,
    "dirus": _dirus,
}

BUILTIN_SPECIES = list(_SPECIES_DATA.keys())


def species_params(manifest: object, species: str = None) -> object | list[str]:
    """
    Returns configured species parameters based on species name.

    Prefer :class:`~emodpy_malaria.vector_config.VectorSpeciesParameters`
    and its :meth:`from_preset` classmethod for new code.

    Args:
        manifest: module containing ``schema_file`` path
        species: name of the species to configure

    Returns:
        Schema-backed parameters dict if species is found;
        list of available species names otherwise.
    """
    if species not in _SPECIES_DATA:
        return BUILTIN_SPECIES

    preset = copy.deepcopy(_SPECIES_DATA[species])
    from emod_api import campaign as api_campaign
    if not api_campaign.get_schema():
        api_campaign.set_schema(manifest.schema_file)
    preset._campaign = api_campaign
    for h in preset.habitats:
        h._campaign = api_campaign
    return preset.to_schema_dict()
