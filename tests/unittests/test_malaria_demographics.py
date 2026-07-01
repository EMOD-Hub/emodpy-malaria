import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from emod_api.demographics.fertility_distribution import FertilityDistribution
from emod_api.demographics.node import Node
from emodpy_malaria.demographics import MalariaDemographics, MalariaNode
from emodpy_malaria.demographics.malaria_node import _set_enable_demog_risk
from emodpy_malaria.migration.vector_migration_data import VectorMigrationData
from emodpy_malaria.utils.distributions import (
    UniformDistribution,
    ConstantDistribution,
)
from emodpy_malaria.utils.emod_enum import ClimateUpdateResolution, InnateImmuneVariationType
from emodpy_malaria.weather.weather_set import WeatherSet
from emodpy_malaria.weather.weather_variable import WeatherVariable

_INVERSE = InnateImmuneVariationType.PYROGENIC_THRESHOLD_VS_AGE_INCREASING_AND_CYTOKINE_KILLING_INVERSE


def _make_fertility_distribution():
    return FertilityDistribution(
        ages_years=[0.0, 15.0, 49.0],
        calendar_years=[2000.0, 2010.0],
        pregnancy_rate_matrix=[[0.01, 0.02], [0.05, 0.06], [0.01, 0.01]],
    )


def _make_demographics(n_nodes=1):
    nodes = [
        MalariaNode(lat=0, lon=0, pop=1000, name=f"node_{i + 1}", forced_id=i + 1)
        for i in range(n_nodes)
    ]
    return MalariaDemographics(nodes=nodes)


@pytest.mark.unit
class TestMalariaNodeToDict(unittest.TestCase):

    def test_to_dict_includes_risk_distribution(self):
        node = MalariaNode(lat=0, lon=0, pop=100, forced_id=1)
        node._set_risk_simple_distribution(flag=1, value1=0.5, value2=1.5)
        d = node.to_dict()
        ia = d["IndividualAttributes"]
        self.assertEqual(ia["RiskDistributionFlag"], 1)
        self.assertEqual(ia["RiskDistribution1"], 0.5)
        self.assertEqual(ia["RiskDistribution2"], 1.5)

    def test_to_dict_includes_innate_immune_distribution(self):
        node = MalariaNode(lat=0, lon=0, pop=100, forced_id=1)
        node._set_innate_immune_simple_distribution(flag=3, value1=0.2, value2=0.8)
        d = node.to_dict()
        ia = d["IndividualAttributes"]
        self.assertEqual(ia["InnateImmuneDistributionFlag"], 3)
        self.assertEqual(ia["InnateImmuneDistribution1"], 0.2)
        self.assertEqual(ia["InnateImmuneDistribution2"], 0.8)

    def test_to_dict_without_distributions_has_no_extra_keys(self):
        node = MalariaNode(lat=0, lon=0, pop=100, forced_id=1)
        d = node.to_dict()
        ia = d.get("IndividualAttributes", {})
        self.assertNotIn("RiskDistributionFlag", ia)
        self.assertNotIn("InnateImmuneDistributionFlag", ia)

    def test_to_dict_replaces_none_value2_with_zero(self):
        node = MalariaNode(lat=0, lon=0, pop=100, forced_id=1)
        node._set_risk_simple_distribution(flag=0, value1=1.0, value2=None)
        d = node.to_dict()
        self.assertEqual(d["IndividualAttributes"]["RiskDistribution2"], 0)


@pytest.mark.unit
class TestMalariaNodeFromData(unittest.TestCase):

    def _node_dict_with_risk(self):
        return {
            "NodeID": 1,
            "NodeAttributes": {"Latitude": 0, "Longitude": 0, "InitialPopulation": 100},
            "IndividualAttributes": {
                "RiskDistributionFlag": 1,
                "RiskDistribution1": 0.5,
                "RiskDistribution2": 1.5,
            },
        }

    def _node_dict_with_innate_immune(self):
        return {
            "NodeID": 2,
            "NodeAttributes": {"Latitude": 0, "Longitude": 0, "InitialPopulation": 100},
            "IndividualAttributes": {
                "InnateImmuneDistributionFlag": 3,
                "InnateImmuneDistribution1": 0.2,
                "InnateImmuneDistribution2": 0.8,
            },
        }

    def test_from_data_loads_risk_distribution(self):
        node, implicits = MalariaNode.from_data(self._node_dict_with_risk())
        self.assertIsInstance(node, MalariaNode)
        self.assertEqual(node.individual_attributes.risk_distribution_flag, 1)
        self.assertEqual(node.individual_attributes.risk_distribution1, 0.5)
        self.assertEqual(node.individual_attributes.risk_distribution2, 1.5)

    def test_from_data_registers_risk_implicit(self):
        _, implicits = MalariaNode.from_data(self._node_dict_with_risk())
        self.assertIn(_set_enable_demog_risk, implicits)

    def test_from_data_loads_innate_immune_distribution(self):
        node, _ = MalariaNode.from_data(self._node_dict_with_innate_immune())
        self.assertEqual(node.individual_attributes.innate_immune_distribution_flag, 3)
        self.assertEqual(node.individual_attributes.innate_immune_distribution1, 0.2)

    def test_from_data_warns_for_innate_immune(self):
        with self.assertWarns(Warning):
            MalariaNode.from_data(self._node_dict_with_innate_immune())

    def test_from_data_without_distributions(self):
        data = {
            "NodeID": 3,
            "NodeAttributes": {"Latitude": 0, "Longitude": 0, "InitialPopulation": 100},
        }
        node, implicits = MalariaNode.from_data(data)
        self.assertIsInstance(node, MalariaNode)
        self.assertIsNone(getattr(node.individual_attributes, "risk_distribution_flag", None))

    def test_round_trip(self):
        original = self._node_dict_with_risk()
        node, _ = MalariaNode.from_data(original)
        d = node.to_dict()
        self.assertEqual(d["IndividualAttributes"]["RiskDistributionFlag"], 1)
        self.assertEqual(d["IndividualAttributes"]["RiskDistribution1"], 0.5)
        self.assertEqual(d["IndividualAttributes"]["RiskDistribution2"], 1.5)


@pytest.mark.unit
class TestMalariaDemographicsFactories(unittest.TestCase):

    def test_from_template_node_creates_malaria_nodes(self):
        demog = MalariaDemographics.from_template_node(pop=500)
        self.assertIsInstance(demog, MalariaDemographics)
        for node in demog.nodes:
            if node.id != 0:
                self.assertIsInstance(node, MalariaNode)


@pytest.mark.unit
class TestSetRiskDistribution(unittest.TestCase):

    def test_sets_risk_on_default_node(self):
        demog = _make_demographics()
        demog.set_risk_distribution(UniformDistribution(0.5, 1.5))
        default = demog.default_node
        self.assertEqual(default.individual_attributes.risk_distribution_flag, 1)
        self.assertEqual(default.individual_attributes.risk_distribution1, 0.5)
        self.assertEqual(default.individual_attributes.risk_distribution2, 1.5)

    def test_sets_risk_on_specific_node(self):
        demog = _make_demographics(n_nodes=2)
        demog.set_risk_distribution(ConstantDistribution(1.0), node_ids=[1])
        node1 = demog.get_node_by_id(1)
        node2 = demog.get_node_by_id(2)
        self.assertIsNotNone(
            getattr(node1.individual_attributes, "risk_distribution_flag", None)
        )
        self.assertIsNone(
            getattr(node2.individual_attributes, "risk_distribution_flag", None)
        )

    def test_registers_enable_demog_risk_implicit(self):
        demog = _make_demographics()
        initial_count = len(demog.implicits)
        demog.set_risk_distribution(UniformDistribution(0, 1))
        self.assertEqual(len(demog.implicits), initial_count + 1)
        config = SimpleNamespace(parameters=SimpleNamespace())
        demog.implicits[-1](config)
        self.assertEqual(config.parameters.Enable_Demographics_Risk, 1)

    def test_rejects_non_base_distribution(self):
        demog = _make_demographics()
        with self.assertRaises(TypeError):
            demog.set_risk_distribution("not a distribution")


@pytest.mark.unit
class TestSetInnateImmuneDistribution(unittest.TestCase):

    def test_sets_on_default_node(self):
        demog = _make_demographics()
        demog.set_innate_immune_distribution(
            UniformDistribution(0.1, 0.9),
            InnateImmuneVariationType.PYROGENIC_THRESHOLD,
        )
        default = demog.default_node
        self.assertEqual(default.individual_attributes.innate_immune_distribution_flag, 1)
        self.assertEqual(default.individual_attributes.innate_immune_distribution1, 0.1)
        self.assertEqual(default.individual_attributes.innate_immune_distribution2, 0.9)

    def test_sets_on_specific_node(self):
        demog = _make_demographics(n_nodes=2)
        demog.set_innate_immune_distribution(
            ConstantDistribution(0.5),
            InnateImmuneVariationType.CYTOKINE_KILLING,
            node_ids=[2],
        )
        node1 = demog.get_node_by_id(1)
        node2 = demog.get_node_by_id(2)
        self.assertIsNone(
            getattr(node1.individual_attributes, "innate_immune_distribution_flag", None)
        )
        self.assertIsNotNone(
            getattr(node2.individual_attributes, "innate_immune_distribution_flag", None)
        )

    def test_accepts_string_variation_type(self):
        demog = _make_demographics()
        demog.set_innate_immune_distribution(
            UniformDistribution(0.1, 0.9),
            "PYROGENIC_THRESHOLD",
        )

    def test_registers_variation_type_implicit(self):
        demog = _make_demographics()
        initial_count = len(demog.implicits)
        demog.set_innate_immune_distribution(
            UniformDistribution(0.1, 0.9),
            InnateImmuneVariationType.CYTOKINE_KILLING,
        )
        self.assertEqual(len(demog.implicits), initial_count + 1)
        config = SimpleNamespace(parameters=SimpleNamespace())
        demog.implicits[-1](config)
        self.assertEqual(config.parameters.Innate_Immune_Variation_Type, "CYTOKINE_KILLING")

    def test_rejects_none_variation_type(self):
        demog = _make_demographics()
        with self.assertRaises(ValueError) as ctx:
            demog.set_innate_immune_distribution(
                UniformDistribution(0.1, 0.9),
                InnateImmuneVariationType.NONE,
            )
        self.assertIn("NONE", str(ctx.exception))

    def test_rejects_none_string(self):
        demog = _make_demographics()
        with self.assertRaises(ValueError):
            demog.set_innate_immune_distribution(
                UniformDistribution(0.1, 0.9),
                "NONE",
            )

    def test_rejects_invalid_variation_type(self):
        demog = _make_demographics()
        with self.assertRaises(ValueError) as ctx:
            demog.set_innate_immune_distribution(
                UniformDistribution(0.1, 0.9),
                "TOTALLY_BOGUS",
            )
        self.assertIn("Valid options", str(ctx.exception))

    def test_rejects_non_base_distribution(self):
        demog = _make_demographics()
        with self.assertRaises(TypeError):
            demog.set_innate_immune_distribution(
                "not a distribution",
                InnateImmuneVariationType.PYROGENIC_THRESHOLD,
            )

    def test_accepts_all_non_none_non_inverse_variation_types(self):
        for vt in InnateImmuneVariationType:
            if vt in (InnateImmuneVariationType.NONE, _INVERSE):
                continue
            demog = _make_demographics()
            demog.set_innate_immune_distribution(UniformDistribution(0.1, 0.9), vt)

    def test_inverse_type_accepts_none_distribution(self):
        demog = _make_demographics()
        initial_count = len(demog.implicits)
        demog.set_innate_immune_distribution(None, _INVERSE)
        self.assertEqual(len(demog.implicits), initial_count + 1)
        config = SimpleNamespace(parameters=SimpleNamespace())
        demog.implicits[-1](config)
        self.assertEqual(
            config.parameters.Innate_Immune_Variation_Type,
            _INVERSE.value,
        )

    def test_inverse_type_rejects_non_none_distribution(self):
        demog = _make_demographics()
        with self.assertRaises(ValueError) as ctx:
            demog.set_innate_immune_distribution(UniformDistribution(0, 1), _INVERSE)
        self.assertIn("None", str(ctx.exception))

    def test_inverse_type_sets_no_node_distribution(self):
        demog = _make_demographics()
        demog.set_innate_immune_distribution(None, _INVERSE)
        default = demog.default_node
        self.assertIsNone(
            getattr(default.individual_attributes, "innate_immune_distribution_flag", None)
        )


@pytest.mark.unit
class TestSetFertilityDistribution(unittest.TestCase):

    def test_sets_fertility_on_default_node(self):
        demog = _make_demographics()
        fd = _make_fertility_distribution()
        demog.set_fertility_distribution(fd)
        self.assertIs(demog.default_node.individual_attributes.fertility_distribution, fd)

    def test_registers_birth_rate_dependence_implicit(self):
        demog = _make_demographics()
        initial_count = len(demog.implicits)
        demog.set_fertility_distribution(_make_fertility_distribution())
        self.assertEqual(len(demog.implicits), initial_count + 1)
        config = SimpleNamespace(parameters=SimpleNamespace())
        demog.implicits[-1](config)
        self.assertEqual(
            config.parameters.Birth_Rate_Dependence,
            "INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR",
        )

    def test_rejects_non_fertility_distribution(self):
        demog = _make_demographics()
        with self.assertRaises(TypeError):
            demog.set_fertility_distribution(UniformDistribution(0, 1))

    def test_sets_fertility_on_specific_node(self):
        demog = _make_demographics(n_nodes=2)
        demog.set_fertility_distribution(_make_fertility_distribution(), node_ids=[1])
        node1 = demog.get_node_by_id(1)
        node2 = demog.get_node_by_id(2)
        self.assertIsNotNone(node1.individual_attributes.fertility_distribution)
        self.assertIsNone(
            getattr(node2.individual_attributes, "fertility_distribution", None)
        )


@pytest.mark.unit
class TestSetPrevalenceDistribution(unittest.TestCase):

    def test_sets_prevalence_on_default_node(self):
        demog = _make_demographics()
        demog.set_prevalence_distribution(ConstantDistribution(0.1))
        ia = demog.default_node.individual_attributes
        self.assertIsNotNone(ia.prevalence_distribution_flag)
        self.assertEqual(ia.prevalence_distribution1, 0.1)

    def test_registers_enable_initial_prevalence_implicit(self):
        demog = _make_demographics()
        initial_count = len(demog.implicits)
        demog.set_prevalence_distribution(ConstantDistribution(0.2))
        self.assertEqual(len(demog.implicits), initial_count + 1)
        config = SimpleNamespace(parameters=SimpleNamespace())
        demog.implicits[-1](config)
        self.assertEqual(config.parameters.Enable_Initial_Prevalence, 1)

    def test_sets_prevalence_on_specific_node(self):
        demog = _make_demographics(n_nodes=2)
        demog.set_prevalence_distribution(UniformDistribution(0.0, 0.5), node_ids=[1])
        node1 = demog.get_node_by_id(1)
        node2 = demog.get_node_by_id(2)
        self.assertIsNotNone(
            getattr(node1.individual_attributes, "prevalence_distribution_flag", None)
        )
        self.assertIsNone(
            getattr(node2.individual_attributes, "prevalence_distribution_flag", None)
        )


def _make_vector_migration_data(node_ids, idref="test_idref"):
    rates = {(node_ids[i], node_ids[j]): 0.1
             for i in range(len(node_ids))
             for j in range(len(node_ids)) if i != j}
    return VectorMigrationData.from_rates(rates, idref=idref)


def _make_weather_set(node_ids):
    rows = [
        {"node": nid, "step": step, "airtemp": 25.0, "humidity": 0.8, "rainfall": 5.0}
        for nid in node_ids
        for step in range(365)
    ]
    df = pd.DataFrame(rows)
    return WeatherSet.from_dataframe(
        df,
        node_column="node",
        step_column="step",
        weather_columns={
            WeatherVariable.AIR_TEMPERATURE: "airtemp",
            WeatherVariable.RELATIVE_HUMIDITY: "humidity",
            WeatherVariable.RAINFALL: "rainfall",
        },
    )


def _make_demographics_with_idref(n_nodes=2, idref="test_idref"):
    nodes = [
        MalariaNode(lat=float(i), lon=float(i), pop=100, name=f"node_{i+1}", forced_id=i + 1)
        for i in range(n_nodes)
    ]
    return MalariaDemographics(nodes=nodes, idref=idref)


@pytest.mark.unit
class TestAddVectorMigration(unittest.TestCase):

    def test_requires_species(self):
        demog = _make_demographics_with_idref()
        data = _make_vector_migration_data([1, 2])
        with self.assertRaises(ValueError):
            demog.add_vector_migration(data, species="")

    def test_rejects_both_data_and_path(self):
        demog = _make_demographics_with_idref()
        data = _make_vector_migration_data([1, 2])
        with self.assertRaises(ValueError):
            demog.add_vector_migration(data, species="gambiae",
                                       vector_migration_filename_path="some/path.bin")

    def test_rejects_neither_data_nor_path(self):
        demog = _make_demographics_with_idref()
        with self.assertRaises(ValueError):
            demog.add_vector_migration(None, species="gambiae")

    def test_unknown_node_ids_raises(self):
        demog = _make_demographics_with_idref(n_nodes=2)
        data = _make_vector_migration_data([1, 2, 99])
        with self.assertRaises(ValueError) as ctx:
            demog.add_vector_migration(data, species="gambiae",
                                       filename="vec_mig.bin")
        self.assertIn("99", str(ctx.exception))

    def test_idref_mismatch_warns_and_updates(self):
        demog = _make_demographics_with_idref(idref="demog_idref")
        data = _make_vector_migration_data([1, 2], idref="other_idref")
        with patch.object(data, "to_migration_file"):
            with self.assertLogs("emodpy_malaria.demographics.malaria_demographics", level="WARNING"):
                demog.add_vector_migration(data, species="gambiae", filename="vec_mig.bin")
        self.assertEqual(data.idref, "demog_idref")

    def test_with_data_registers_file_and_implicit(self):
        demog = _make_demographics_with_idref()
        data = _make_vector_migration_data([1, 2], idref="test_idref")
        initial_files = len(demog.migration_files)
        initial_implicits = len(demog.implicits)
        with patch.object(data, "to_migration_file"):
            demog.add_vector_migration(data, species="gambiae", filename="vec_mig.bin")
        self.assertEqual(len(demog.migration_files), initial_files + 1)
        self.assertEqual(len(demog.implicits), initial_implicits + 1)

    def test_with_data_implicit_targets_correct_species(self):
        demog = _make_demographics_with_idref()
        data = _make_vector_migration_data([1, 2], idref="test_idref")
        with patch.object(data, "to_migration_file"):
            demog.add_vector_migration(data, species="gambiae", filename="vec_mig.bin")
        imp = demog.implicits[-1]
        self.assertEqual(imp.keywords["species"], "gambiae")

    def test_with_path_registers_file_and_implicit(self, tmp_path=None):
        import tempfile, os
        demog = _make_demographics_with_idref()
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
            bin_path = f.name
        try:
            initial_files = len(demog.migration_files)
            demog.add_vector_migration(None, species="gambiae",
                                       vector_migration_filename_path=bin_path)
            self.assertEqual(len(demog.migration_files), initial_files + 1)
            self.assertEqual(demog.migration_files[-1], Path(bin_path).absolute())
        finally:
            os.unlink(bin_path)

    def test_with_missing_path_raises(self):
        demog = _make_demographics_with_idref()
        with self.assertRaises(FileNotFoundError):
            demog.add_vector_migration(None, species="gambiae",
                                       vector_migration_filename_path="/nonexistent/path.bin")

    def test_x_vector_migration_passed_to_implicit(self):
        demog = _make_demographics_with_idref()
        data = _make_vector_migration_data([1, 2], idref="test_idref")
        with patch.object(data, "to_migration_file"):
            demog.add_vector_migration(data, species="gambiae",
                                       x_vector_migration=0.5, filename="vec_mig.bin")
        imp = demog.implicits[-1]
        self.assertEqual(imp.keywords["x_vector_migration"], 0.5)


@pytest.mark.unit
class TestAddWeather(unittest.TestCase):

    def test_rejects_non_weatherset(self):
        demog = _make_demographics_with_idref()
        with self.assertRaises(TypeError):
            demog.add_weather("not_a_weatherset")

    def test_rejects_invalid_update_resolution(self):
        demog = _make_demographics_with_idref()
        ws = _make_weather_set([1, 2])
        with self.assertRaises(TypeError):
            demog.add_weather(ws, update_resolution="DAILY")

    def test_node_mismatch_extra_raises(self):
        demog = _make_demographics_with_idref(n_nodes=1)
        ws = _make_weather_set([1, 2])
        with self.assertRaises(ValueError) as ctx:
            demog.add_weather(ws)
        self.assertIn("extra", str(ctx.exception))

    def test_node_mismatch_missing_raises(self):
        demog = _make_demographics_with_idref(n_nodes=2)
        ws = _make_weather_set([1])
        with self.assertRaises(ValueError) as ctx:
            demog.add_weather(ws)
        self.assertIn("missing", str(ctx.exception))

    def test_missing_weather_variable_raises(self):
        demog = _make_demographics_with_idref(n_nodes=1)
        rows = [{"node": 1, "step": s, "airtemp": 25.0} for s in range(365)]
        df = pd.DataFrame(rows)
        ws = WeatherSet.from_dataframe(df, node_column="node", step_column="step",
                                       weather_columns={WeatherVariable.AIR_TEMPERATURE: "airtemp"})
        with self.assertRaises(ValueError) as ctx:
            demog.add_weather(ws)
        self.assertIn("missing", str(ctx.exception).lower())

    def test_sets_idref_on_weatherset(self):
        demog = _make_demographics_with_idref(idref="my_idref")
        ws = _make_weather_set([1, 2])
        with patch.object(ws, "to_files"):
            demog.add_weather(ws)
        self.assertEqual(ws.id_reference, "my_idref")

    def test_registers_three_weather_files(self):
        demog = _make_demographics_with_idref()
        ws = _make_weather_set([1, 2])
        initial_files = len(demog.migration_files)
        with patch.object(ws, "to_files"):
            demog.add_weather(ws)
        self.assertEqual(len(demog.migration_files), initial_files + 3)

    def test_registers_one_implicit(self):
        demog = _make_demographics_with_idref()
        ws = _make_weather_set([1, 2])
        initial_implicits = len(demog.implicits)
        with patch.object(ws, "to_files"):
            demog.add_weather(ws)
        self.assertEqual(len(demog.implicits), initial_implicits + 1)

    def test_implicit_sets_climate_by_data(self):
        demog = _make_demographics_with_idref()
        ws = _make_weather_set([1, 2])
        with patch.object(ws, "to_files"):
            demog.add_weather(ws)
        config = SimpleNamespace(parameters=SimpleNamespace())
        demog.implicits[-1](config)
        self.assertEqual(str(config.parameters.Climate_Model), "CLIMATE_BY_DATA")

    def test_file_names_use_resolution_suffix(self):
        demog = _make_demographics_with_idref()
        ws = _make_weather_set([1, 2])
        with patch.object(ws, "to_files"):
            demog.add_weather(ws, update_resolution=ClimateUpdateResolution.CLIMATE_UPDATE_MONTH)
        names = [f.name for f in demog.migration_files]
        self.assertTrue(all("monthly" in n for n in names))


if __name__ == "__main__":
    unittest.main()
