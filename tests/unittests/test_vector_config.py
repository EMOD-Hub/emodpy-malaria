import unittest
import warnings
import pytest

import emod_api.config.default_from_schema_no_validation as dfs
from emod_api import campaign as api_campaign

from emodpy_malaria import vector_config
from emodpy_malaria.vector_config import (
    VectorHabitat, VectorSpeciesParameters,
    get_species_params, set_species_param, add_species,
    add_genes_and_alleles, add_mutation,
    create_trait, add_trait,
    add_blood_meal_mortality, add_insecticide_resistance,
    add_species_drivers, add_maternal_deposition,
    set_max_larval_capacity, add_microsporidia,
    add_vector_migration,
)
from emodpy_malaria.utils.emod_enum import (
    HabitatType, VectorTrait, DriverType, VectorSamplingType,
    ModifierEquationType,
)

from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest  # noqa: E402


def _fresh_config():
    return dfs.get_default_config_from_schema(manifest.schema_file, as_rod=True)


def _vector_config():
    config = _fresh_config()
    vector_config.set_team_defaults(config, manifest)
    return config


def _vector_config_with_species(species="gambiae"):
    config = _vector_config()
    add_species(config, manifest, species)
    return config


def _config_with_genes(species="gambiae"):
    """Config with gambiae + a simple gene (a0/a1) added."""
    config = _vector_config_with_species(species)
    add_genes_and_alleles(config, manifest, species=species,
                          alleles=[("a0", 0.5), ("a1", 0.5)])
    return config


def _config_with_gender_gene(species="gambiae"):
    """Config with gambiae + a gender gene (X/Y)."""
    config = _vector_config_with_species(species)
    add_genes_and_alleles(config, manifest, species=species,
                          alleles=[("X", 0.5, 0), ("Y", 0.5, 1)])
    return config


# ---------------------------------------------------------------------------
# set_team_defaults
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSetTeamDefaults(unittest.TestCase):

    def test_simulation_type(self):
        config = _fresh_config()
        vector_config.set_team_defaults(config, manifest)
        self.assertEqual(config.parameters.Simulation_Type, "VECTOR_SIM")

    def test_vector_params(self):
        config = _vector_config()
        self.assertEqual(config.parameters.Enable_Vector_Mortality, 1)
        self.assertEqual(config.parameters.Enable_Vector_Aging, 0)
        self.assertEqual(config.parameters.Vector_Sampling_Type,
                         VectorSamplingType.VECTOR_COMPARTMENTS_NUMBER)

    def test_climate_params(self):
        config = _vector_config()
        self.assertEqual(config.parameters.Base_Air_Temperature, 27)
        self.assertEqual(config.parameters.Base_Rainfall, 10)
        self.assertEqual(config.parameters.Base_Relative_Humidity, 0.75)
        self.assertEqual(config.parameters.Climate_Model, "CLIMATE_CONSTANT")

    def test_simulation_duration(self):
        config = _vector_config()
        self.assertEqual(config.parameters.Simulation_Duration, 365)
        self.assertEqual(config.parameters.Start_Time, 0)

    def test_empty_species_list(self):
        config = _vector_config()
        self.assertEqual(len(config.parameters.Vector_Species_Params), 0)

    def test_returns_config(self):
        config = _fresh_config()
        result = vector_config.set_team_defaults(config, manifest)
        self.assertIs(result, config)


# ---------------------------------------------------------------------------
# VectorHabitat
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestVectorHabitat(unittest.TestCase):

    def test_constant_habitat(self):
        h = VectorHabitat(habitat_type=HabitatType.CONSTANT, max_larval_capacity=1e7)
        self.assertEqual(h._habitat_type, HabitatType.CONSTANT)
        self.assertEqual(h._max_larval_capacity, 1e7)

    def test_string_habitat_type(self):
        h = VectorHabitat(habitat_type="TEMPORARY_RAINFALL", max_larval_capacity=1e8)
        self.assertEqual(h._habitat_type, HabitatType.TEMPORARY_RAINFALL)

    def test_invalid_habitat_type(self):
        with self.assertRaises(ValueError):
            VectorHabitat(habitat_type="INVALID", max_larval_capacity=1e7)

    def test_linear_spline_requires_distribution(self):
        with self.assertRaises(ValueError):
            VectorHabitat(habitat_type=HabitatType.LINEAR_SPLINE, max_larval_capacity=1e8)

    def test_linear_spline_with_dict(self):
        h = VectorHabitat(
            habitat_type=HabitatType.LINEAR_SPLINE,
            max_larval_capacity=1e8,
            capacity_distribution_over_time={
                "Times": [0, 182, 365],
                "Values": [1.0, 5.0, 1.0],
            },
        )
        self.assertEqual(h._habitat_type, HabitatType.LINEAR_SPLINE)

    def test_linear_spline_dict_missing_keys(self):
        with self.assertRaises(ValueError):
            VectorHabitat(
                habitat_type=HabitatType.LINEAR_SPLINE,
                max_larval_capacity=1e8,
                capacity_distribution_over_time={"Times": [0, 365]},
            )

    def test_to_schema_dict(self):
        if not api_campaign.get_schema():
            api_campaign.set_schema(manifest.schema_file)
        h = VectorHabitat(
            habitat_type=HabitatType.WATER_VEGETATION,
            max_larval_capacity=2e7,
            campaign=api_campaign,
        )
        d = h.to_schema_dict()
        self.assertEqual(d.Habitat_Type, "WATER_VEGETATION")
        self.assertEqual(d.Max_Larval_Capacity, 2e7)


# ---------------------------------------------------------------------------
# VectorSpeciesParameters
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestVectorSpeciesParameters(unittest.TestCase):

    def test_defaults(self):
        h = VectorHabitat(habitat_type=HabitatType.CONSTANT, max_larval_capacity=1e7)
        sp = VectorSpeciesParameters(name="test_sp", habitats=[h])
        self.assertEqual(sp.name, "test_sp")
        self.assertEqual(sp.anthropophily, 0.65)
        self.assertEqual(sp.indoor_feeding_fraction, 0.95)
        self.assertEqual(sp.adult_life_expectancy, 20)
        self.assertEqual(sp.transmission_rate, 0.9)

    def test_custom_params(self):
        h = VectorHabitat(habitat_type=HabitatType.CONSTANT, max_larval_capacity=1e7)
        sp = VectorSpeciesParameters(
            name="custom",
            habitats=[h],
            anthropophily=0.3,
            indoor_feeding_fraction=0.1,
            adult_life_expectancy=30,
        )
        self.assertEqual(sp.anthropophily, 0.3)
        self.assertEqual(sp.indoor_feeding_fraction, 0.1)
        self.assertEqual(sp.adult_life_expectancy, 30)

    def test_to_schema_dict(self):
        if not api_campaign.get_schema():
            api_campaign.set_schema(manifest.schema_file)
        h = VectorHabitat(
            habitat_type=HabitatType.CONSTANT,
            max_larval_capacity=1e7,
            campaign=api_campaign,
        )
        sp = VectorSpeciesParameters(name="gambiae", habitats=[h], campaign=api_campaign)
        d = sp.to_schema_dict()
        self.assertEqual(d.Name, "gambiae")
        self.assertEqual(d.Anthropophily, 0.65)

    def test_from_preset(self):
        if not api_campaign.get_schema():
            api_campaign.set_schema(manifest.schema_file)
        sp = VectorSpeciesParameters.from_preset(api_campaign, manifest, "arabiensis")
        self.assertEqual(sp.name, "arabiensis")
        self.assertEqual(sp.indoor_feeding_fraction, 0.5)

    def test_from_preset_invalid(self):
        if not api_campaign.get_schema():
            api_campaign.set_schema(manifest.schema_file)
        with self.assertRaises(ValueError):
            VectorSpeciesParameters.from_preset(api_campaign, manifest, "nonexistent")


# ---------------------------------------------------------------------------
# add_species
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddSpecies(unittest.TestCase):

    def test_add_single_species_by_name(self):
        config = _vector_config()
        add_species(config, manifest, "gambiae")
        self.assertEqual(len(config.parameters.Vector_Species_Params), 1)
        self.assertEqual(config.parameters.Vector_Species_Params[0].Name, "gambiae")

    def test_add_multiple_species_by_name(self):
        config = _vector_config()
        add_species(config, manifest, ["gambiae", "arabiensis"])
        self.assertEqual(len(config.parameters.Vector_Species_Params), 2)
        names = [sp.Name for sp in config.parameters.Vector_Species_Params]
        self.assertIn("gambiae", names)
        self.assertIn("arabiensis", names)

    def test_add_species_object(self):
        config = _vector_config()
        h = VectorHabitat(habitat_type=HabitatType.CONSTANT, max_larval_capacity=1e7)
        sp = VectorSpeciesParameters(name="custom_sp", habitats=[h])
        add_species(config, manifest, sp)
        self.assertEqual(len(config.parameters.Vector_Species_Params), 1)
        self.assertEqual(config.parameters.Vector_Species_Params[0].Name, "custom_sp")

    def test_add_unknown_species_raises(self):
        config = _vector_config()
        with self.assertRaises(ValueError):
            add_species(config, manifest, "nonexistent_species")

    def test_returns_config(self):
        config = _vector_config()
        result = add_species(config, manifest, "gambiae")
        self.assertIs(result, config)


# ---------------------------------------------------------------------------
# get_species_params / set_species_param
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetSetSpeciesParams(unittest.TestCase):

    def test_get_existing(self):
        config = _vector_config_with_species()
        sp = get_species_params(config, "gambiae")
        self.assertEqual(sp.Name, "gambiae")

    def test_get_nonexistent_raises(self):
        config = _vector_config_with_species()
        with self.assertRaises(ValueError):
            get_species_params(config, "nonexistent")

    def test_get_empty_species_raises(self):
        config = _vector_config()
        with self.assertRaises(ValueError):
            get_species_params(config, "")

    def test_get_none_species_raises(self):
        config = _vector_config()
        with self.assertRaises(ValueError):
            get_species_params(config, None)

    def test_set_scalar_param(self):
        config = _vector_config_with_species()
        set_species_param(config, "gambiae", "Anthropophily", 0.99)
        sp = get_species_params(config, "gambiae")
        self.assertEqual(sp.Anthropophily, 0.99)

    def test_set_list_param_append(self):
        config = _vector_config_with_species()
        original_len = len(get_species_params(config, "gambiae").Habitats)
        if not api_campaign.get_schema():
            api_campaign.set_schema(manifest.schema_file)
        new_hab = VectorHabitat(
            habitat_type=HabitatType.CONSTANT,
            max_larval_capacity=5e6,
            campaign=api_campaign,
        )
        set_species_param(config, "gambiae", "Habitats", new_hab)
        self.assertEqual(len(get_species_params(config, "gambiae").Habitats),
                         original_len + 1)

    def test_set_list_param_overwrite(self):
        config = _vector_config_with_species()
        if not api_campaign.get_schema():
            api_campaign.set_schema(manifest.schema_file)
        new_hab = VectorHabitat(
            habitat_type=HabitatType.CONSTANT,
            max_larval_capacity=5e6,
            campaign=api_campaign,
        )
        set_species_param(config, "gambiae", "Habitats", new_hab, overwrite=True)
        self.assertEqual(len(get_species_params(config, "gambiae").Habitats), 1)


# ---------------------------------------------------------------------------
# add_genes_and_alleles
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddGenesAndAlleles(unittest.TestCase):

    def test_add_simple_gene(self):
        config = _vector_config_with_species()
        add_genes_and_alleles(config, manifest, species="gambiae",
                              alleles=[("a0", 0.9), ("a1", 0.1)])
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Genes), 1)
        self.assertEqual(len(sp.Genes[0].Alleles), 2)
        self.assertEqual(sp.Genes[0].Alleles[0].Name, "a0")
        self.assertAlmostEqual(sp.Genes[0].Alleles[0].Initial_Allele_Frequency, 0.9)

    def test_add_gender_gene(self):
        config = _vector_config_with_species()
        add_genes_and_alleles(config, manifest, species="gambiae",
                              alleles=[("X", 0.5, 0), ("Y", 0.5, 1)])
        sp = get_species_params(config, "gambiae")
        self.assertEqual(sp.Genes[0].Is_Gender_Gene, 1)

    def test_add_multiple_genes(self):
        config = _vector_config_with_species()
        add_genes_and_alleles(config, manifest, species="gambiae",
                              alleles=[("a0", 0.5), ("a1", 0.5)])
        add_genes_and_alleles(config, manifest, species="gambiae",
                              alleles=[("b0", 0.7), ("b1", 0.3)])
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Genes), 2)

    def test_missing_params_raises(self):
        config = _vector_config_with_species()
        with self.assertRaises(ValueError):
            add_genes_and_alleles(config, manifest, species="gambiae", alleles=None)
        with self.assertRaises(ValueError):
            add_genes_and_alleles(config, manifest, species=None,
                                  alleles=[("a0", 0.5)])

    def test_returns_config(self):
        config = _vector_config_with_species()
        result = add_genes_and_alleles(config, manifest, species="gambiae",
                                       alleles=[("a0", 0.5), ("a1", 0.5)])
        self.assertIs(result, config)


# ---------------------------------------------------------------------------
# add_mutation
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddMutation(unittest.TestCase):

    def test_add_mutation(self):
        config = _config_with_genes()
        add_mutation(config, manifest, species="gambiae",
                     mutate_from="a0", mutate_to="a1", probability=0.01)
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Genes[0].Mutations), 1)
        self.assertEqual(sp.Genes[0].Mutations[0].Mutate_From, "a0")
        self.assertEqual(sp.Genes[0].Mutations[0].Mutate_To, "a1")
        self.assertAlmostEqual(sp.Genes[0].Mutations[0].Probability_Of_Mutation, 0.01)

    def test_mutation_not_found_raises(self):
        config = _config_with_genes()
        with self.assertRaises(ValueError):
            add_mutation(config, manifest, species="gambiae",
                         mutate_from="a0", mutate_to="NONEXISTENT", probability=0.01)

    def test_returns_config(self):
        config = _config_with_genes()
        result = add_mutation(config, manifest, species="gambiae",
                              mutate_from="a0", mutate_to="a1", probability=0.01)
        self.assertIs(result, config)


# ---------------------------------------------------------------------------
# create_trait / add_trait
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCreateAndAddTrait(unittest.TestCase):

    def test_create_trait_infected_by_human(self):
        t = create_trait(manifest, trait="INFECTED_BY_HUMAN", modifier=0.5)
        self.assertEqual(t.Trait, "INFECTED_BY_HUMAN")
        self.assertEqual(t.Modifier, 0.5)

    def test_create_trait_enum(self):
        t = create_trait(manifest, trait=VectorTrait.FECUNDITY, modifier=0.8)
        self.assertEqual(t.Trait, VectorTrait.FECUNDITY)

    def test_create_trait_missing_params_raises(self):
        with self.assertRaises(ValueError):
            create_trait(manifest, trait=None, modifier=0.5)
        with self.assertRaises(ValueError):
            create_trait(manifest, trait="FECUNDITY", modifier=None)

    def test_create_trait_invalid_trait_raises(self):
        with self.assertRaises(ValueError):
            create_trait(manifest, trait="NOT_A_TRAIT", modifier=0.5)

    def test_add_trait(self):
        config = _config_with_genes()
        t = create_trait(manifest, trait="INFECTED_BY_HUMAN", modifier=0.5)
        add_trait(config, manifest, species="gambiae",
                  allele_combo=[["a0", "a1"]], trait_modifiers=[t])
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Gene_To_Trait_Modifiers), 1)
        self.assertEqual(sp.Gene_To_Trait_Modifiers[0].Allele_Combinations, [["a0", "a1"]])

    def test_add_trait_no_modifiers_raises(self):
        config = _config_with_genes()
        with self.assertRaises(ValueError):
            add_trait(config, manifest, species="gambiae",
                      allele_combo=[["a0", "a1"]], trait_modifiers=None)

    def test_add_trait_invalid_allele_raises(self):
        config = _config_with_genes()
        t = create_trait(manifest, trait="FECUNDITY", modifier=0.5)
        with self.assertRaises(ValueError):
            add_trait(config, manifest, species="gambiae",
                      allele_combo=[["NONEXISTENT", "a1"]], trait_modifiers=[t])

    def test_add_trait_empty_allele_combo_raises(self):
        config = _config_with_genes()
        t = create_trait(manifest, trait="FECUNDITY", modifier=0.5)
        with self.assertRaises(ValueError):
            add_trait(config, manifest, species="gambiae",
                      allele_combo=[], trait_modifiers=[t])

    def test_add_trait_wrong_combo_size_raises(self):
        config = _config_with_genes()
        t = create_trait(manifest, trait="FECUNDITY", modifier=0.5)
        with self.assertRaises(ValueError):
            add_trait(config, manifest, species="gambiae",
                      allele_combo=[["a0"]], trait_modifiers=[t])

    def test_add_trait_returns_config(self):
        config = _config_with_genes()
        t = create_trait(manifest, trait="FECUNDITY", modifier=0.5)
        result = add_trait(config, manifest, species="gambiae",
                           allele_combo=[["a0", "a1"]], trait_modifiers=[t])
        self.assertIs(result, config)


# ---------------------------------------------------------------------------
# add_blood_meal_mortality
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddBloodMealMortality(unittest.TestCase):

    def test_add_blood_meal_mortality(self):
        config = _config_with_genes()
        add_blood_meal_mortality(config, manifest,
                                default_probability_of_death=0.1,
                                species="gambiae",
                                allele_combo=[["a0", "a1"]],
                                probability_of_death_for_allele_combo=0.5)
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Blood_Meal_Mortality.Genetic_Probabilities), 1)
        self.assertAlmostEqual(
            sp.Blood_Meal_Mortality.Genetic_Probabilities[0].Probability, 0.5)

    def test_default_probability_or_combined(self):
        config = _config_with_genes()
        add_blood_meal_mortality(config, manifest,
                                default_probability_of_death=0.2,
                                species="gambiae",
                                allele_combo=[["a0", "a0"]],
                                probability_of_death_for_allele_combo=0.3)
        add_blood_meal_mortality(config, manifest,
                                default_probability_of_death=0.3,
                                species="gambiae",
                                allele_combo=[["a1", "a1"]],
                                probability_of_death_for_allele_combo=0.4)
        sp = get_species_params(config, "gambiae")
        # default is OR'd: 1 - (1-0.2)*(1-0.3) = 0.44
        self.assertAlmostEqual(sp.Blood_Meal_Mortality.Default_Probability, 0.44)

    def test_invalid_default_probability_raises(self):
        config = _config_with_genes()
        with self.assertRaises(ValueError):
            add_blood_meal_mortality(config, manifest,
                                    default_probability_of_death=1.5,
                                    species="gambiae",
                                    allele_combo=[["a0", "a1"]],
                                    probability_of_death_for_allele_combo=0.5)

    def test_invalid_combo_probability_raises(self):
        config = _config_with_genes()
        with self.assertRaises(ValueError):
            add_blood_meal_mortality(config, manifest,
                                    default_probability_of_death=0.1,
                                    species="gambiae",
                                    allele_combo=[["a0", "a1"]],
                                    probability_of_death_for_allele_combo=-0.1)

    def test_returns_config(self):
        config = _config_with_genes()
        result = add_blood_meal_mortality(config, manifest,
                                          default_probability_of_death=0.1,
                                          species="gambiae",
                                          allele_combo=[["a0", "a1"]],
                                          probability_of_death_for_allele_combo=0.5)
        self.assertIs(result, config)


# ---------------------------------------------------------------------------
# add_insecticide_resistance
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddInsecticideResistance(unittest.TestCase):

    def test_add_resistance(self):
        config = _config_with_genes()
        add_insecticide_resistance(config, manifest,
                                   insecticide_name="pyrethroid",
                                   species="gambiae",
                                   allele_combo=[["a1", "a1"]],
                                   blocking=0.5, killing=0.3,
                                   repelling=0.2, larval_killing=0.1)
        self.assertEqual(len(config.parameters.Insecticides), 1)
        insecticide = config.parameters.Insecticides[0]
        self.assertEqual(insecticide.Name, "pyrethroid")
        self.assertEqual(len(insecticide.Resistances), 1)
        self.assertAlmostEqual(insecticide.Resistances[0].Blocking_Modifier, 0.5)
        self.assertAlmostEqual(insecticide.Resistances[0].Killing_Modifier, 0.3)

    def test_add_resistance_to_existing_insecticide(self):
        config = _config_with_genes()
        add_insecticide_resistance(config, manifest,
                                   insecticide_name="pyrethroid",
                                   species="gambiae",
                                   allele_combo=[["a0", "a0"]],
                                   killing=0.5)
        add_insecticide_resistance(config, manifest,
                                   insecticide_name="pyrethroid",
                                   species="gambiae",
                                   allele_combo=[["a1", "a1"]],
                                   killing=0.2)
        self.assertEqual(len(config.parameters.Insecticides), 1)
        self.assertEqual(len(config.parameters.Insecticides[0].Resistances), 2)

    def test_add_resistance_new_insecticide(self):
        config = _config_with_genes()
        add_insecticide_resistance(config, manifest,
                                   insecticide_name="pyrethroid",
                                   species="gambiae",
                                   allele_combo=[["a0", "a0"]],
                                   killing=0.5)
        add_insecticide_resistance(config, manifest,
                                   insecticide_name="organophosphate",
                                   species="gambiae",
                                   allele_combo=[["a1", "a1"]],
                                   killing=0.3)
        self.assertEqual(len(config.parameters.Insecticides), 2)

    def test_returns_config(self):
        config = _config_with_genes()
        result = add_insecticide_resistance(config, manifest,
                                            insecticide_name="pyrethroid",
                                            species="gambiae",
                                            allele_combo=[["a0", "a1"]],
                                            killing=0.5)
        self.assertIs(result, config)


# ---------------------------------------------------------------------------
# add_species_drivers
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddSpeciesDrivers(unittest.TestCase):

    def test_classic_driver(self):
        config = _config_with_genes()
        add_species_drivers(config, manifest, species="gambiae",
                            driving_allele="a1", driver_type="CLASSIC",
                            to_copy="a1", to_replace="a0",
                            likelihood_list=[("a1", 1.0)])
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Drivers), 1)
        self.assertEqual(sp.Drivers[0].Driving_Allele, "a1")
        self.assertEqual(sp.Drivers[0].Driver_Type, "CLASSIC")

    def test_integral_autonomous_driver(self):
        config = _config_with_genes()
        add_species_drivers(config, manifest, species="gambiae",
                            driving_allele="a1",
                            driver_type=DriverType.INTEGRAL_AUTONOMOUS,
                            to_copy="a1", to_replace="a0",
                            likelihood_list=[("a1", 1.0)])
        sp = get_species_params(config, "gambiae")
        self.assertEqual(sp.Drivers[0].Driver_Type, "INTEGRAL_AUTONOMOUS")

    def test_missing_params_raises(self):
        config = _config_with_genes()
        with self.assertRaises(ValueError):
            add_species_drivers(config, manifest, species="gambiae",
                                driving_allele=None, to_copy="a1",
                                to_replace="a0", likelihood_list=[("a1", 1.0)])

    def test_invalid_driver_type_raises(self):
        config = _config_with_genes()
        with self.assertRaises(ValueError):
            add_species_drivers(config, manifest, species="gambiae",
                                driving_allele="a1", driver_type="INVALID",
                                to_copy="a1", to_replace="a0",
                                likelihood_list=[("a1", 1.0)])

    def test_shredding_params_with_non_shred_driver_raises(self):
        config = _config_with_genes()
        with self.assertRaises(ValueError):
            add_species_drivers(config, manifest, species="gambiae",
                                driving_allele="a1", driver_type="CLASSIC",
                                to_copy="a1", to_replace="a0",
                                likelihood_list=[("a1", 1.0)],
                                shredding_allele_required="X")

    def test_daisy_chain_copy_equals_driving_raises(self):
        config = _config_with_genes()
        with self.assertRaises(ValueError):
            add_species_drivers(config, manifest, species="gambiae",
                                driving_allele="a1",
                                driver_type=DriverType.DAISY_CHAIN,
                                to_copy="a1", to_replace="a0",
                                likelihood_list=[("a1", 1.0)])

    def test_add_second_allele_driven_to_same_driver(self):
        config = _vector_config_with_species()
        add_genes_and_alleles(config, manifest, species="gambiae",
                              alleles=[("a0", 0.4), ("a1", 0.3), ("a2", 0.3)])
        add_species_drivers(config, manifest, species="gambiae",
                            driving_allele="a1", driver_type="CLASSIC",
                            to_copy="a1", to_replace="a0",
                            likelihood_list=[("a1", 1.0)])
        add_species_drivers(config, manifest, species="gambiae",
                            driving_allele="a1", driver_type="CLASSIC",
                            to_copy="a1", to_replace="a2",
                            likelihood_list=[("a1", 1.0)])
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Drivers), 1)
        self.assertEqual(len(sp.Drivers[0].Alleles_Driven), 2)

    def test_returns_config(self):
        config = _config_with_genes()
        result = add_species_drivers(config, manifest, species="gambiae",
                                     driving_allele="a1", driver_type="CLASSIC",
                                     to_copy="a1", to_replace="a0",
                                     likelihood_list=[("a1", 1.0)])
        self.assertIs(result, config)


# ---------------------------------------------------------------------------
# add_maternal_deposition
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddMaternalDeposition(unittest.TestCase):

    def _config_with_driver(self):
        config = _config_with_genes()
        add_species_drivers(config, manifest, species="gambiae",
                            driving_allele="a1", driver_type="CLASSIC",
                            to_copy="a1", to_replace="a0",
                            likelihood_list=[("a1", 0.9), ("a0", 0.1)])
        return config

    def test_add_maternal_deposition(self):
        config = self._config_with_driver()
        add_maternal_deposition(config, manifest, species="gambiae",
                                cas9_grna_from="a1", allele_to_cut="a0",
                                likelihood_list=[("a0", 1.0)])
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Maternal_Deposition), 1)
        self.assertEqual(sp.Maternal_Deposition[0].Cas9_gRNA_From, "a1")

    def test_missing_driver_raises(self):
        config = _config_with_genes()
        with self.assertRaises(ValueError):
            add_maternal_deposition(config, manifest, species="gambiae",
                                    cas9_grna_from="NONEXISTENT",
                                    allele_to_cut="a0",
                                    likelihood_list=[("a0", 1.0)])

    def test_missing_allele_to_cut_raises(self):
        config = self._config_with_driver()
        with self.assertRaises(ValueError):
            add_maternal_deposition(config, manifest, species="gambiae",
                                    cas9_grna_from="a1",
                                    allele_to_cut="NONEXISTENT",
                                    likelihood_list=[("a0", 1.0)])

    def test_cut_to_allele_equals_copy_raises(self):
        config = self._config_with_driver()
        with self.assertRaises(ValueError):
            add_maternal_deposition(config, manifest, species="gambiae",
                                    cas9_grna_from="a1",
                                    allele_to_cut="a0",
                                    likelihood_list=[("a1", 1.0)])

    def test_likelihood_sum_not_one_raises(self):
        config = self._config_with_driver()
        with self.assertRaises(ValueError):
            add_maternal_deposition(config, manifest, species="gambiae",
                                    cas9_grna_from="a1",
                                    allele_to_cut="a0",
                                    likelihood_list=[("a0", 0.5)])

    def test_returns_config(self):
        config = self._config_with_driver()
        result = add_maternal_deposition(config, manifest, species="gambiae",
                                         cas9_grna_from="a1",
                                         allele_to_cut="a0",
                                         likelihood_list=[("a0", 1.0)])
        self.assertIs(result, config)


# ---------------------------------------------------------------------------
# set_max_larval_capacity
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSetMaxLarvalCapacity(unittest.TestCase):

    def test_set_capacity(self):
        config = _vector_config_with_species()
        sp = get_species_params(config, "gambiae")
        original_type = sp.Habitats[0]["Habitat_Type"]
        set_max_larval_capacity(config, "gambiae", original_type, 999)
        self.assertEqual(sp.Habitats[0]["Max_Larval_Capacity"], 999)

    def test_string_habitat_type(self):
        config = _vector_config_with_species()
        set_max_larval_capacity(config, "gambiae", "WATER_VEGETATION", 12345)
        sp = get_species_params(config, "gambiae")
        self.assertEqual(sp.Habitats[0]["Max_Larval_Capacity"], 12345)

    def test_invalid_habitat_type_raises(self):
        config = _vector_config_with_species()
        with self.assertRaises(ValueError):
            set_max_larval_capacity(config, "gambiae", "INVALID_TYPE", 100)

    def test_habitat_not_found_raises(self):
        config = _vector_config_with_species()
        with self.assertRaises(ValueError):
            set_max_larval_capacity(config, "gambiae", HabitatType.BRACKISH_SWAMP, 100)

    def test_species_not_found_raises(self):
        config = _vector_config_with_species()
        with self.assertRaises(ValueError):
            set_max_larval_capacity(config, "nonexistent",
                                    HabitatType.WATER_VEGETATION, 100)


# ---------------------------------------------------------------------------
# add_microsporidia
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddMicrosporidia(unittest.TestCase):

    def test_add_default(self):
        config = _vector_config_with_species()
        add_microsporidia(config, manifest, species_name="gambiae")
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Microsporidia), 1)
        self.assertEqual(sp.Microsporidia[0].Strain_Name, "Strain_A")

    def test_add_custom(self):
        config = _vector_config_with_species()
        add_microsporidia(config, manifest, species_name="gambiae",
                          strain_name="Custom_Strain",
                          female_to_male_probability=0.5,
                          female_to_egg_probability=0.3,
                          larval_growth_modifier=0.8,
                          female_mortality_modifier=1.2)
        sp = get_species_params(config, "gambiae")
        m = sp.Microsporidia[0]
        self.assertEqual(m.Strain_Name, "Custom_Strain")
        self.assertAlmostEqual(m.Female_To_Male_Transmission_Probability, 0.5)
        self.assertAlmostEqual(m.Female_To_Egg_Transmission_Probability, 0.3)
        self.assertAlmostEqual(m.Larval_Growth_Modifier, 0.8)

    def test_with_dict_durations(self):
        config = _vector_config_with_species()
        add_microsporidia(config, manifest, species_name="gambiae",
                          duration_to_disease_acquisition_modification={
                              "Times": [0, 5, 10], "Values": [1.0, 0.5, 0.0]
                          },
                          duration_to_disease_transmission_modification={
                              "Times": [0, 5, 10], "Values": [1.0, 0.8, 0.6]
                          })
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Microsporidia), 1)

    def test_empty_strain_name_raises(self):
        config = _vector_config_with_species()
        with self.assertRaises(ValueError):
            add_microsporidia(config, manifest, species_name="gambiae",
                              strain_name="")

    def test_add_multiple_strains(self):
        config = _vector_config_with_species()
        add_microsporidia(config, manifest, species_name="gambiae",
                          strain_name="Strain_A")
        add_microsporidia(config, manifest, species_name="gambiae",
                          strain_name="Strain_B")
        sp = get_species_params(config, "gambiae")
        self.assertEqual(len(sp.Microsporidia), 2)


# ---------------------------------------------------------------------------
# add_vector_migration (deprecated)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAddVectorMigration(unittest.TestCase):

    def test_deprecated_warning(self):
        config = _vector_config_with_species()

        class FakeAssets:
            def __init__(self):
                self._assets = []
            def has_asset(self, path):
                return path in self._assets
            def add_asset(self, path):
                self._assets.append(path)

        class FakeTask:
            def __init__(self, cfg):
                self.config = cfg
                self.common_assets = FakeAssets()

        task = FakeTask(config)
        with self.assertWarns(DeprecationWarning):
            add_vector_migration(task, species="gambiae",
                                 vector_migration_filename_path="fake_file.bin")

    def test_both_data_and_path_raises(self):
        config = _vector_config_with_species()

        class FakeTask:
            def __init__(self, cfg):
                self.config = cfg

        task = FakeTask(config)
        with self.assertRaises(ValueError):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                add_vector_migration(task, species="gambiae",
                                     vector_migration_data="some_data",
                                     vector_migration_filename_path="some_path.bin")

    def test_neither_data_nor_path_raises(self):
        config = _vector_config_with_species()

        class FakeTask:
            def __init__(self, cfg):
                self.config = cfg

        task = FakeTask(config)
        with self.assertRaises(ValueError):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                add_vector_migration(task, species="gambiae")
