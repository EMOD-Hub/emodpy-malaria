import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pytest

from emodpy_malaria.migration import VectorMigrationData, VECTOR_MIGRATION_BY_GENETICS
from emodpy.migration.migration_data import SAME_FOR_BOTH_GENDERS, ONE_FOR_EACH_GENDER
from emodpy.utils.emod_enum import MigrationType, InterpolationType


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_RATES_3NODE = {
    (1, 2): 0.01, (2, 1): 0.01,
    (1, 3): 0.005, (3, 1): 0.005,
    (2, 3): 0.008, (3, 2): 0.008,
}

_GENETICS = {
    (): {(1, 2): 0.01, (2, 1): 0.01},
    (("a1", "X"),): {(1, 2): 0.05, (2, 1): 0.05},
    (("a1", "a0"), ("b0", "b1")): {(1, 2): 0.10, (2, 1): 0.10},
}


def _write_and_reload(data, tmp_dir, migration_type=MigrationType.LOCAL):
    """Round-trip helper: write to disk, reload, return reloaded object."""
    path = Path(tmp_dir) / "vector_mig.bin"
    data.to_migration_file(path, migration_type=migration_type)
    return VectorMigrationData.from_migration_file(path)


# ---------------------------------------------------------------------------
# from_rates
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFromRates(unittest.TestCase):

    def test_basic_creates_single_layer(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        self.assertEqual(data.num_layers, 1)
        self.assertEqual(data.gender_data_type, SAME_FOR_BOTH_GENDERS)

    def test_rates_stored_correctly(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        layer = data.get_layer(0)
        self.assertAlmostEqual(layer[(1, 2)], 0.01)
        self.assertAlmostEqual(layer[(2, 3)], 0.008)

    def test_node_ids_populated(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        self.assertEqual(data.node_ids, [1, 2, 3])

    def test_idref_stored(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE, idref="test_ref")
        self.assertEqual(data.idref, "test_ref")

    def test_female_rates_creates_two_layers(self):
        male = {(1, 2): 0.05, (2, 1): 0.03}
        female = {(1, 2): 0.02, (2, 1): 0.01}
        data = VectorMigrationData.from_rates(male, female_rates=female)
        self.assertEqual(data.num_layers, 2)
        self.assertEqual(data.gender_data_type, ONE_FOR_EACH_GENDER)

    def test_female_rates_stored_as_second_layer(self):
        male = {(1, 2): 0.05, (2, 1): 0.03}
        female = {(1, 2): 0.02, (2, 1): 0.01}
        data = VectorMigrationData.from_rates(male, female_rates=female)
        self.assertAlmostEqual(data.get_layer(0)[(1, 2)], 0.05)
        self.assertAlmostEqual(data.get_layer(1)[(1, 2)], 0.02)

    def test_allele_combinations_is_none(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        self.assertIsNone(data.allele_combinations)

    def test_rate_zero_rejected(self):
        with self.assertRaises(ValueError):
            VectorMigrationData.from_rates({(1, 2): -0.001})

    def test_rate_above_one_rejected(self):
        with self.assertRaises(ValueError):
            VectorMigrationData.from_rates({(1, 2): 1.001})

    def test_rate_exactly_one_accepted(self):
        data = VectorMigrationData.from_rates({(1, 2): 1.0})
        self.assertAlmostEqual(data.get_layer(0)[(1, 2)], 1.0)

    def test_from_node_zero_rejected(self):
        with self.assertRaises(ValueError):
            VectorMigrationData.from_rates({(0, 2): 0.01})

    def test_to_node_zero_rejected(self):
        with self.assertRaises(ValueError):
            VectorMigrationData.from_rates({(1, 0): 0.01})

    def test_female_rate_above_one_rejected(self):
        with self.assertRaises(ValueError):
            VectorMigrationData.from_rates(
                {(1, 2): 0.01}, female_rates={(1, 2): 1.5})

    def test_female_from_node_zero_rejected(self):
        with self.assertRaises(ValueError):
            VectorMigrationData.from_rates(
                {(1, 2): 0.01}, female_rates={(0, 2): 0.01})

    def test_returns_vector_migration_data_instance(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        self.assertIsInstance(data, VectorMigrationData)


# ---------------------------------------------------------------------------
# from_genetics
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFromGenetics(unittest.TestCase):

    def test_creates_one_layer_per_combo(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        self.assertEqual(data.num_layers, 3)

    def test_gender_data_type_is_genetics(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        self.assertEqual(data.gender_data_type, VECTOR_MIGRATION_BY_GENETICS)

    def test_allele_combinations_length_matches_layers(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        self.assertEqual(len(data.allele_combinations), data.num_layers)

    def test_default_combo_is_first(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        self.assertEqual(data.allele_combinations[0], [])

    def test_single_pair_combo_stored_correctly(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        self.assertEqual(data.allele_combinations[1], [["a1", "X"]])

    def test_two_pair_combo_stored_correctly(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        self.assertEqual(data.allele_combinations[2], [["a1", "a0"], ["b0", "b1"]])

    def test_ages_are_layer_indices(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        self.assertEqual(data._ages, [0, 1, 2])

    def test_rates_stored_per_layer(self):
        # Genetics layers are indexed via age_index (gender is always 0 for genetics)
        data = VectorMigrationData.from_genetics(_GENETICS)
        self.assertAlmostEqual(data.get_layer(0, 0)[(1, 2)], 0.01)
        self.assertAlmostEqual(data.get_layer(0, 1)[(1, 2)], 0.05)
        self.assertAlmostEqual(data.get_layer(0, 2)[(1, 2)], 0.10)

    def test_missing_default_combo_raises(self):
        with self.assertRaises(ValueError):
            VectorMigrationData.from_genetics({
                (("a1", "X"),): {(1, 2): 0.05}
            })

    def test_empty_dict_raises(self):
        with self.assertRaises(ValueError):
            VectorMigrationData.from_genetics({})

    def test_only_default_combo_allowed(self):
        data = VectorMigrationData.from_genetics({(): {(1, 2): 0.01}})
        self.assertEqual(data.num_layers, 1)
        self.assertEqual(data.allele_combinations[0], [])

    def test_rate_above_one_in_genetics_raises(self):
        with self.assertRaises(ValueError):
            VectorMigrationData.from_genetics({(): {(1, 2): 1.5}})

    def test_node_zero_in_genetics_raises(self):
        with self.assertRaises(ValueError):
            VectorMigrationData.from_genetics({(): {(0, 2): 0.01}})

    def test_idref_stored(self):
        data = VectorMigrationData.from_genetics(_GENETICS, idref="gen_ref")
        self.assertEqual(data.idref, "gen_ref")

    def test_returns_vector_migration_data_instance(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        self.assertIsInstance(data, VectorMigrationData)


# ---------------------------------------------------------------------------
# apply_modifier (not supported)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestApplyModifier(unittest.TestCase):

    def test_raises_not_implemented(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        with self.assertRaises(NotImplementedError):
            data.apply_modifier(ages=[0, 15], modifier_fn=lambda r, a, g: r)


# ---------------------------------------------------------------------------
# to_migration_file / from_migration_file round-trip
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRoundTripFromRates(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def test_binary_file_created(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        path = Path(self._tmp.name) / "mig.bin"
        data.to_migration_file(path)
        self.assertTrue(path.exists())

    def test_metadata_json_created(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        path = Path(self._tmp.name) / "mig.bin"
        data.to_migration_file(path)
        self.assertTrue(Path(str(path) + ".json").exists())

    def test_rates_survive_roundtrip(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        reloaded = _write_and_reload(data, self._tmp.name)
        for pair, rate in _RATES_3NODE.items():
            self.assertAlmostEqual(reloaded.get_layer(0)[pair], rate, places=10)

    def test_node_ids_survive_roundtrip(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        reloaded = _write_and_reload(data, self._tmp.name)
        self.assertEqual(reloaded.node_ids, [1, 2, 3])

    def test_gender_data_type_preserved(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        reloaded = _write_and_reload(data, self._tmp.name)
        self.assertEqual(reloaded.gender_data_type, SAME_FOR_BOTH_GENDERS)

    def test_interpolation_type_is_piecewise_constant(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        path = Path(self._tmp.name) / "mig.bin"
        data.to_migration_file(path)
        meta = json.loads(Path(str(path) + ".json").read_text())
        self.assertEqual(meta["Metadata"]["InterpolationType"],
                         str(InterpolationType.PIECEWISE_CONSTANT))

    def test_migration_type_written_to_metadata(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        path = Path(self._tmp.name) / "mig.bin"
        data.to_migration_file(path, migration_type=MigrationType.REGIONAL)
        meta = json.loads(Path(str(path) + ".json").read_text())
        self.assertIn("REGIONAL", meta["Metadata"]["MigrationType"].upper())

    def test_migration_type_string_accepted(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        path = Path(self._tmp.name) / "mig.bin"
        data.to_migration_file(path, migration_type="local")
        self.assertTrue(path.exists())

    def test_invalid_migration_type_raises(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        path = Path(self._tmp.name) / "mig.bin"
        with self.assertRaises(ValueError):
            data.to_migration_file(path, migration_type="bogus")

    def test_gender_specific_roundtrip(self):
        male = {(1, 2): 0.05, (2, 1): 0.03}
        female = {(1, 2): 0.02, (2, 1): 0.01}
        data = VectorMigrationData.from_rates(male, female_rates=female)
        reloaded = _write_and_reload(data, self._tmp.name)
        self.assertEqual(reloaded.num_layers, 2)
        self.assertEqual(reloaded.gender_data_type, ONE_FOR_EACH_GENDER)
        self.assertAlmostEqual(reloaded.get_layer(0)[(1, 2)], 0.05, places=10)
        self.assertAlmostEqual(reloaded.get_layer(1)[(1, 2)], 0.02, places=10)

    def test_idref_written_to_metadata(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE, idref="my_idref")
        path = Path(self._tmp.name) / "mig.bin"
        data.to_migration_file(path)
        meta = json.loads(Path(str(path) + ".json").read_text())
        self.assertEqual(meta["Metadata"]["IdReference"], "my_idref")

    def test_node_count_in_metadata(self):
        data = VectorMigrationData.from_rates(_RATES_3NODE)
        path = Path(self._tmp.name) / "mig.bin"
        data.to_migration_file(path)
        meta = json.loads(Path(str(path) + ".json").read_text())
        self.assertEqual(meta["Metadata"]["NodeCount"], 3)


@pytest.mark.unit
class TestRoundTripGenetics(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def test_genetics_rates_survive_roundtrip(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        reloaded = _write_and_reload(data, self._tmp.name)
        self.assertAlmostEqual(reloaded.get_layer(0, 0)[(1, 2)], 0.01, places=10)
        self.assertAlmostEqual(reloaded.get_layer(0, 1)[(1, 2)], 0.05, places=10)
        self.assertAlmostEqual(reloaded.get_layer(0, 2)[(1, 2)], 0.10, places=10)

    def test_allele_combinations_survive_roundtrip(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        reloaded = _write_and_reload(data, self._tmp.name)
        self.assertEqual(reloaded.allele_combinations[0], [])
        self.assertEqual(reloaded.allele_combinations[1], [["a1", "X"]])
        self.assertEqual(reloaded.allele_combinations[2], [["a1", "a0"], ["b0", "b1"]])

    def test_gender_data_type_is_genetics_after_reload(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        reloaded = _write_and_reload(data, self._tmp.name)
        self.assertEqual(reloaded.gender_data_type, VECTOR_MIGRATION_BY_GENETICS)

    def test_num_layers_preserved(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        reloaded = _write_and_reload(data, self._tmp.name)
        self.assertEqual(reloaded.num_layers, 3)

    def test_ages_years_in_metadata_are_indices(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        path = Path(self._tmp.name) / "mig.bin"
        data.to_migration_file(path)
        meta = json.loads(Path(str(path) + ".json").read_text())
        self.assertEqual(meta["Metadata"]["AgesYears"], [0, 1, 2])

    def test_allele_combinations_in_metadata(self):
        data = VectorMigrationData.from_genetics(_GENETICS)
        path = Path(self._tmp.name) / "mig.bin"
        data.to_migration_file(path)
        meta = json.loads(Path(str(path) + ".json").read_text())
        self.assertEqual(meta["Metadata"]["AlleleCombinations"][0], [])
        self.assertEqual(meta["Metadata"]["AlleleCombinations"][1], [["a1", "X"]])


# ---------------------------------------------------------------------------
# from_migration_file error cases
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFromMigrationFileErrors(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_binary_raises(self):
        with self.assertRaises(FileNotFoundError):
            VectorMigrationData.from_migration_file(
                Path(self._tmp.name) / "nonexistent.bin")

    def test_missing_metadata_raises(self):
        binary = Path(self._tmp.name) / "mig.bin"
        binary.write_bytes(b"\x00" * 24)
        with self.assertRaises(FileNotFoundError):
            VectorMigrationData.from_migration_file(binary)

    def test_age_based_file_rejected(self):
        """Files with AgesYears > 1 entry and non-genetics GenderDataType must be rejected."""
        tmp = Path(self._tmp.name)
        binary = tmp / "age_mig.bin"
        meta = tmp / "age_mig.bin.json"
        binary.write_bytes(b"\x00" * 24)
        meta.write_text(json.dumps({
            "Metadata": {
                "NodeCount": 1, "DatavalueCount": 1,
                "GenderDataType": SAME_FOR_BOTH_GENDERS,
                "AgesYears": [0, 15, 65],
                "IdReference": "",
            },
            "NodeOffsets": "0000000100000000",
        }))
        with self.assertRaises(ValueError):
            VectorMigrationData.from_migration_file(binary)

    def test_genetics_file_without_allele_combinations_raises(self):
        tmp = Path(self._tmp.name)
        binary = tmp / "gen_mig.bin"
        meta = tmp / "gen_mig.bin.json"
        binary.write_bytes(b"\x00" * 24)
        meta.write_text(json.dumps({
            "Metadata": {
                "NodeCount": 1, "DatavalueCount": 1,
                "GenderDataType": VECTOR_MIGRATION_BY_GENETICS,
                "AgesYears": [0],
                "IdReference": "",
            },
            "NodeOffsets": "0000000100000000",
        }))
        with self.assertRaises(ValueError):
            VectorMigrationData.from_migration_file(binary)

    def test_genetics_file_mismatched_ages_and_combos_raises(self):
        tmp = Path(self._tmp.name)
        binary = tmp / "gen_mig.bin"
        meta = tmp / "gen_mig.bin.json"
        binary.write_bytes(b"\x00" * 24)
        meta.write_text(json.dumps({
            "Metadata": {
                "NodeCount": 1, "DatavalueCount": 1,
                "GenderDataType": VECTOR_MIGRATION_BY_GENETICS,
                "AgesYears": [0, 1],
                "AlleleCombinations": [[]],
                "IdReference": "",
            },
            "NodeOffsets": "0000000100000000",
        }))
        with self.assertRaises(ValueError):
            VectorMigrationData.from_migration_file(binary)


# ---------------------------------------------------------------------------
# from_gravity_model
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFromGravityModel(unittest.TestCase):

    def _make_demographics(self):
        from emod_api.demographics.node import Node
        from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics

        nodes = [
            Node(lat=-2.0, lon=32.0, pop=5000, forced_id=1, name="A"),
            Node(lat=-2.1, lon=32.2, pop=2000, forced_id=2, name="B"),
            Node(lat=-2.3, lon=32.5, pop=500,  forced_id=3, name="C"),
        ]
        return MalariaDemographics(nodes=nodes, idref="grav_test")

    def test_returns_vector_migration_data_instance(self):
        demog = self._make_demographics()
        data = VectorMigrationData.from_gravity_model(
            demog, gravity_params=[7.5e-6, 0.3, 0.6, -1.1])
        self.assertIsInstance(data, VectorMigrationData)

    def test_single_layer_without_female_multiplier(self):
        demog = self._make_demographics()
        data = VectorMigrationData.from_gravity_model(
            demog, gravity_params=[7.5e-6, 0.3, 0.6, -1.1])
        self.assertEqual(data.num_layers, 1)
        self.assertEqual(data.gender_data_type, SAME_FOR_BOTH_GENDERS)

    def test_two_layers_with_female_multiplier(self):
        demog = self._make_demographics()
        data = VectorMigrationData.from_gravity_model(
            demog, gravity_params=[7.5e-6, 0.3, 0.6, -1.1],
            female_multiplier=0.5)
        self.assertEqual(data.num_layers, 2)
        self.assertEqual(data.gender_data_type, ONE_FOR_EACH_GENDER)

    def test_female_rates_scaled_by_multiplier(self):
        demog = self._make_demographics()
        data = VectorMigrationData.from_gravity_model(
            demog, gravity_params=[7.5e-6, 0.3, 0.6, -1.1],
            female_multiplier=0.5)
        for pair in data.get_layer(0):
            male_rate = data.get_layer(0)[pair]
            female_rate = data.get_layer(1)[pair]
            self.assertAlmostEqual(female_rate, male_rate * 0.5, places=10)

    def test_rates_are_non_negative(self):
        demog = self._make_demographics()
        data = VectorMigrationData.from_gravity_model(
            demog, gravity_params=[7.5e-6, 0.3, 0.6, -1.1])
        for rate in data.get_layer(0).values():
            self.assertGreaterEqual(rate, 0.0)

    def test_rates_are_at_most_one(self):
        demog = self._make_demographics()
        data = VectorMigrationData.from_gravity_model(
            demog, gravity_params=[7.5e-6, 0.3, 0.6, -1.1])
        for rate in data.get_layer(0).values():
            self.assertLessEqual(rate, 1.0)

    def test_node_ids_match_demographics(self):
        demog = self._make_demographics()
        data = VectorMigrationData.from_gravity_model(
            demog, gravity_params=[7.5e-6, 0.3, 0.6, -1.1])
        self.assertEqual(data.node_ids, [1, 2, 3])

    def test_apply_modifier_still_blocked(self):
        demog = self._make_demographics()
        data = VectorMigrationData.from_gravity_model(
            demog, gravity_params=[7.5e-6, 0.3, 0.6, -1.1])
        with self.assertRaises(NotImplementedError):
            data.apply_modifier(ages=[0, 15], modifier_fn=lambda r, a, g: r)
