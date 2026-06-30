import unittest
import pytest

from emod_api import campaign as api_campaign
import emodpy_malaria.utils.targeting_config as tc

from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest  # noqa: E402


@pytest.mark.unit
class TestTargetingConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.campaign = api_campaign
        cls.campaign.set_schema(manifest.schema_path)

    def test_HasIP(self):
        tc_obj = tc.HasIP(ip_key_value="Risk:HIGH")
        exp_json = {
            "class": "HasIP",
            "Is_Equal_To": 1,
            "IP_Key_Value": "Risk:HIGH",
        }
        self.assertDictEqual(exp_json, tc_obj.to_simple_dict(self.campaign))

    def test_HasIP_inverted(self):
        tc_obj = ~tc.HasIP(ip_key_value="Risk:HIGH")
        exp_json = {
            "class": "HasIP",
            "Is_Equal_To": 0,
            "IP_Key_Value": "Risk:HIGH",
        }
        self.assertDictEqual(exp_json, tc_obj.to_simple_dict(self.campaign))

    def test_HasIntervention(self):
        tc_obj = tc.HasIntervention(intervention_name="SimpleVaccine")
        exp_json = {
            "class": "HasIntervention",
            "Is_Equal_To": 1,
            "Intervention_Name": "SimpleVaccine",
        }
        self.assertDictEqual(exp_json, tc_obj.to_simple_dict(self.campaign))

    def test_HasIntervention_inverted(self):
        tc_obj = ~tc.HasIntervention(intervention_name="SimpleVaccine")
        exp_json = {
            "class": "HasIntervention",
            "Is_Equal_To": 0,
            "Intervention_Name": "SimpleVaccine",
        }
        self.assertDictEqual(exp_json, tc_obj.to_simple_dict(self.campaign))

    def test_IsPregnant(self):
        tc_obj = tc.IsPregnant()
        exp_json = {
            "class": "IsPregnant",
            "Is_Equal_To": 1,
        }
        self.assertDictEqual(exp_json, tc_obj.to_simple_dict(self.campaign))

    def test_IsPregnant_inverted(self):
        tc_obj = ~tc.IsPregnant()
        exp_json = {
            "class": "IsPregnant",
            "Is_Equal_To": 0,
        }
        self.assertDictEqual(exp_json, tc_obj.to_simple_dict(self.campaign))

    def test_and_logic(self):
        tc_obj = tc.HasIP(ip_key_value="Risk:HIGH") & tc.IsPregnant()
        result = tc_obj.to_simple_dict(self.campaign)
        self.assertEqual(result["class"], "TargetingLogic")
        self.assertEqual(len(result["Logic"]), 1)
        self.assertEqual(len(result["Logic"][0]), 2)
        self.assertEqual(result["Logic"][0][0]["class"], "HasIP")
        self.assertEqual(result["Logic"][0][1]["class"], "IsPregnant")

    def test_or_logic(self):
        tc_obj = tc.HasIP(ip_key_value="Risk:HIGH") | tc.IsPregnant()
        result = tc_obj.to_simple_dict(self.campaign)
        self.assertEqual(result["class"], "TargetingLogic")
        self.assertEqual(len(result["Logic"]), 2)
        self.assertEqual(result["Logic"][0][0]["class"], "HasIP")
        self.assertEqual(result["Logic"][1][0]["class"], "IsPregnant")

    def test_combined_and_or(self):
        tc_obj = (
            tc.HasIP(ip_key_value="Risk:HIGH") & ~tc.HasIntervention(intervention_name="ITN")
        ) | tc.IsPregnant()
        result = tc_obj.to_simple_dict(self.campaign)
        self.assertEqual(result["class"], "TargetingLogic")
        self.assertEqual(len(result["Logic"]), 2)

    def test_HasIP_empty_raises(self):
        with self.assertRaises(ValueError):
            tc.HasIP(ip_key_value="")

    def test_HasIntervention_empty_raises(self):
        with self.assertRaises(ValueError):
            tc.HasIntervention(intervention_name="")

    def test_IsPregnant_implicit_validates_birth_rate_dependence(self):
        self.campaign.implicits.clear()
        tc_obj = tc.IsPregnant()
        tc_obj.to_schema_dict(self.campaign)
        self.assertEqual(len(self.campaign.implicits), 1)

        class MockConfig:
            class parameters:
                Birth_Rate_Dependence = "FIXED_BIRTH_RATE"
        with self.assertRaises(ValueError) as ctx:
            self.campaign.implicits[0](MockConfig())
        self.assertIn("INDIVIDUAL_PREGNANCIES", str(ctx.exception))
        self.assertIn("IsPregnant", str(ctx.exception))

        MockConfig.parameters.Birth_Rate_Dependence = "INDIVIDUAL_PREGNANCIES"
        result = self.campaign.implicits[0](MockConfig())
        self.assertIsNotNone(result)

        MockConfig.parameters.Birth_Rate_Dependence = "INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR"
        result = self.campaign.implicits[0](MockConfig())
        self.assertIsNotNone(result)

    def test_module_exports(self):
        self.assertIn("HasIP", tc.__all__)
        self.assertIn("HasIntervention", tc.__all__)
        self.assertIn("IsPregnant", tc.__all__)
        self.assertIn("BaseTargetingConfig", tc.__all__)
        self.assertIn("AbstractTargetingConfig", tc.__all__)


if __name__ == "__main__":
    unittest.main()
