import unittest
from types import SimpleNamespace

import pytest

from emod_api.demographics.node import Node
from emodpy_malaria.demographics import MalariaDemographics, MalariaNode
from emodpy_malaria.demographics.malaria_node import _set_enable_demog_risk
from emodpy_malaria.utils.distributions import (
    UniformDistribution,
    ConstantDistribution,
)
from emodpy_malaria.utils.emod_enum import InnateImmuneVariationType


def _make_demographics(n_nodes=1):
    nodes = [
        MalariaNode(lat=0, lon=0, pop=1000, name=f"node_{i + 1}", forced_id=i + 1)
        for i in range(n_nodes)
    ]
    return MalariaDemographics(nodes=nodes)


@pytest.mark.unit
class TestMalariaNodeSetters(unittest.TestCase):

    def test_set_risk_simple_distribution(self):
        node = MalariaNode(lat=0, lon=0, pop=100, forced_id=1)
        node._set_risk_simple_distribution(flag=1, value1=0.5, value2=1.5)
        self.assertEqual(node.individual_attributes.risk_distribution_flag, 1)
        self.assertEqual(node.individual_attributes.risk_distribution1, 0.5)
        self.assertEqual(node.individual_attributes.risk_distribution2, 1.5)

    def test_set_innate_immune_simple_distribution(self):
        node = MalariaNode(lat=0, lon=0, pop=100, forced_id=1)
        node._set_innate_immune_simple_distribution(flag=3, value1=0.2, value2=0.8)
        self.assertEqual(node.individual_attributes.innate_immune_distribution_flag, 3)
        self.assertEqual(node.individual_attributes.innate_immune_distribution1, 0.2)
        self.assertEqual(node.individual_attributes.innate_immune_distribution2, 0.8)


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

    def test_accepts_all_non_none_variation_types(self):
        for vt in InnateImmuneVariationType:
            if vt == InnateImmuneVariationType.NONE:
                continue
            demog = _make_demographics()
            demog.set_innate_immune_distribution(UniformDistribution(0.1, 0.9), vt)


if __name__ == "__main__":
    unittest.main()
