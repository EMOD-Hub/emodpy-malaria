import unittest
import pytest
from emodpy_malaria.campaign.node_intervention import (
    LarvalHabitatMultiplierSpec, SpaceSpraying, IndoorSpaceSpraying,
    MultiInsecticideSpaceSpraying, MultiInsecticideIndoorSpaceSpraying,
    Larvicides, LarvalMicrosporidiaIntervention, InputEIR, MalariaChallenge,
    MosquitoRelease, ScaleLarvalHabitat, OutdoorRestKill, OutdoorNodeEmanator,
    SugarTrap, OvipositionTrap, SpatialRepellent, AnimalFeedKill, ArtificialDiet
)
import emodpy_malaria.campaign.waning_config as wc
from emod_api import campaign as api_campaign
from emodpy_malaria.campaign.common import CommonInterventionParameters
from emodpy_malaria.utils.distributions import ConstantDistribution
from emodpy_malaria.utils.emod_enum import (
    HabitatType, WolbachiaType, ArtificialDietTarget
)
from copy import deepcopy
from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest  # noqa: E402


@pytest.mark.unit
class TestNodeIntervention(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.campaign = api_campaign
        cls.campaign.set_schema(manifest.schema_path)
        cls.CIP = CommonInterventionParameters(
            cost=2,
            disqualifying_properties=["Risk:High"],
            dont_allow_duplicates=True,
            intervention_name="TestIntervention",
            new_property_value="Risk:Low"
        )

    def assertCIP(self, intervention, cost=2, disqualifying_properties=["Risk:High"],
                  dont_allow_duplicates=True, intervention_name="TestIntervention",
                  new_property_value="Risk:Low"):
        if cost is not None:
            self.assertEqual(intervention.Cost_To_Consumer, cost)
        if disqualifying_properties is not None:
            self.assertEqual(intervention.Disqualifying_Properties, disqualifying_properties)
        if dont_allow_duplicates is not None:
            self.assertEqual(intervention.Dont_Allow_Duplicates, dont_allow_duplicates)
        if intervention_name is not None:
            self.assertEqual(intervention.Intervention_Name, intervention_name)
        if new_property_value is not None:
            self.assertEqual(intervention.New_Property_Value, new_property_value)

    # -------------------------------------------------------------------------
    # LarvalHabitatMultiplierSpec (helper class)
    # -------------------------------------------------------------------------

    def test_LarvalHabitatMultiplierSpec_default(self):
        spec = LarvalHabitatMultiplierSpec(
            self.campaign,
            habitat=HabitatType.CONSTANT,
            factor=2.0)
        d = spec.to_schema_dict()
        self.assertEqual(d.Habitat, "CONSTANT")
        self.assertEqual(d.Factor, 2.0)
        self.assertEqual(d.Species, "ALL_SPECIES")

    def test_LarvalHabitatMultiplierSpec(self):
        spec = LarvalHabitatMultiplierSpec(
            self.campaign,
            habitat=HabitatType.TEMPORARY_RAINFALL,
            factor=0.5,
            species="gambiae")
        d = spec.to_schema_dict()
        self.assertEqual(d.Habitat, "TEMPORARY_RAINFALL")
        self.assertEqual(d.Factor, 0.5)
        self.assertEqual(d.Species, "gambiae")

    def test_LarvalHabitatMultiplierSpec_string_habitat(self):
        spec = LarvalHabitatMultiplierSpec(
            self.campaign,
            habitat="WATER_VEGETATION",
            factor=1.5)
        d = spec.to_schema_dict()
        self.assertEqual(d.Habitat, "WATER_VEGETATION")

    def test_LarvalHabitatMultiplierSpec_invalid_habitat(self):
        with self.assertRaises(ValueError) as context:
            LarvalHabitatMultiplierSpec(
                self.campaign,
                habitat="INVALID_HABITAT",
                factor=1.0)
        self.assertIn("HabitatType", str(context.exception))

    # -------------------------------------------------------------------------
    # SpaceSpraying
    # -------------------------------------------------------------------------

    def test_SpaceSpraying_default(self):
        iv = SpaceSpraying(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.5))
        self.assertEqual(iv._intervention['class'], 'SpaceSpraying')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectConstant')

    def test_SpaceSpraying(self):
        iv = SpaceSpraying(
            self.campaign,
            killing_config=wc.Exponential(initial_effect=0.8, decay_time_constant=180),
            spray_coverage=0.7,
            insecticide_name="Pyrethroid",
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'SpaceSpraying')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectExponential')
        self.assertEqual(iv._intervention.Spray_Coverage, 0.7)
        self.assertEqual(iv._intervention.Insecticide_Name, "Pyrethroid")
        self.assertCIP(intervention=iv._intervention)

    def test_SpaceSpraying_invalid_coverage(self):
        with self.assertRaises(ValueError):
            SpaceSpraying(
                self.campaign,
                killing_config=wc.Constant(constant_effect=0.5),
                spray_coverage=1.5)

    # -------------------------------------------------------------------------
    # IndoorSpaceSpraying
    # -------------------------------------------------------------------------

    def test_IndoorSpaceSpraying_default(self):
        iv = IndoorSpaceSpraying(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.6))
        self.assertEqual(iv._intervention['class'], 'IndoorSpaceSpraying')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectConstant')

    def test_IndoorSpaceSpraying(self):
        iv = IndoorSpaceSpraying(
            self.campaign,
            killing_config=wc.Exponential(initial_effect=0.9, decay_time_constant=365),
            spray_coverage=0.85,
            insecticide_name="Bendiocarb",
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'IndoorSpaceSpraying')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectExponential')
        self.assertEqual(iv._intervention.Spray_Coverage, 0.85)
        self.assertEqual(iv._intervention.Insecticide_Name, "Bendiocarb")
        self.assertCIP(intervention=iv._intervention)

    # -------------------------------------------------------------------------
    # MultiInsecticideSpaceSpraying
    # -------------------------------------------------------------------------

    def test_MultiInsecticideSpaceSpraying_default(self):
        ins = wc.InsecticideWaningEffect(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.7),
            insecticide_name="Pyrethroid")
        iv = MultiInsecticideSpaceSpraying(
            self.campaign,
            insecticides=[ins])
        self.assertEqual(iv._intervention['class'], 'MultiInsecticideSpaceSpraying')
        self.assertEqual(len(iv._intervention.Insecticides), 1)

    def test_MultiInsecticideSpaceSpraying(self):
        ins1 = wc.InsecticideWaningEffect(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.7),
            insecticide_name="Pyrethroid")
        ins2 = wc.InsecticideWaningEffect(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.5),
            insecticide_name="PBO")
        CIP = deepcopy(self.CIP)
        CIP.disqualifying_properties = None
        CIP.dont_allow_duplicates = None
        CIP.intervention_name = None
        CIP.new_property_value = None
        iv = MultiInsecticideSpaceSpraying(
            self.campaign,
            insecticides=[ins1, ins2],
            spray_coverage=0.9,
            common_intervention_parameters=CIP)
        self.assertEqual(iv._intervention['class'], 'MultiInsecticideSpaceSpraying')
        self.assertEqual(len(iv._intervention.Insecticides), 2)
        self.assertEqual(iv._intervention.Spray_Coverage, 0.9)
        self.assertCIP(intervention=iv._intervention,
                       disqualifying_properties=None, dont_allow_duplicates=None,
                       intervention_name=None, new_property_value=None)

    def test_MultiInsecticideSpaceSpraying_invalid_insecticide(self):
        with self.assertRaises(ValueError) as context:
            MultiInsecticideSpaceSpraying(
                self.campaign,
                insecticides=["not_an_insecticide"])
        self.assertIn("InsecticideWaningEffect", str(context.exception))

    # -------------------------------------------------------------------------
    # MultiInsecticideIndoorSpaceSpraying
    # -------------------------------------------------------------------------

    def test_MultiInsecticideIndoorSpaceSpraying_default(self):
        ins = wc.InsecticideWaningEffect(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.6),
            insecticide_name="Pyrethroid")
        iv = MultiInsecticideIndoorSpaceSpraying(
            self.campaign,
            insecticides=[ins])
        self.assertEqual(iv._intervention['class'], 'MultiInsecticideIndoorSpaceSpraying')
        self.assertEqual(len(iv._intervention.Insecticides), 1)

    def test_MultiInsecticideIndoorSpaceSpraying(self):
        ins1 = wc.InsecticideWaningEffect(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.6),
            insecticide_name="Pyrethroid")
        ins2 = wc.InsecticideWaningEffect(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.4),
            insecticide_name="PBO")
        CIP = deepcopy(self.CIP)
        CIP.disqualifying_properties = None
        CIP.dont_allow_duplicates = None
        CIP.intervention_name = None
        CIP.new_property_value = None
        iv = MultiInsecticideIndoorSpaceSpraying(
            self.campaign,
            insecticides=[ins1, ins2],
            spray_coverage=0.8,
            common_intervention_parameters=CIP)
        self.assertEqual(iv._intervention['class'], 'MultiInsecticideIndoorSpaceSpraying')
        self.assertEqual(len(iv._intervention.Insecticides), 2)
        self.assertEqual(iv._intervention.Spray_Coverage, 0.8)
        self.assertCIP(intervention=iv._intervention,
                       disqualifying_properties=None, dont_allow_duplicates=None,
                       intervention_name=None, new_property_value=None)

    # -------------------------------------------------------------------------
    # Larvicides
    # -------------------------------------------------------------------------

    def test_Larvicides_default(self):
        iv = Larvicides(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.4))
        self.assertEqual(iv._intervention['class'], 'Larvicides')
        self.assertEqual(iv._intervention.Larval_Killing_Config['class'], 'WaningEffectConstant')

    def test_Larvicides(self):
        iv = Larvicides(
            self.campaign,
            killing_config=wc.Exponential(initial_effect=0.7, decay_time_constant=90),
            habitat_target=HabitatType.TEMPORARY_RAINFALL,
            insecticide_name="Temephos",
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'Larvicides')
        self.assertEqual(iv._intervention.Larval_Killing_Config['class'], 'WaningEffectExponential')
        self.assertEqual(iv._intervention.Habitat_Target, "TEMPORARY_RAINFALL")
        self.assertEqual(iv._intervention.Insecticide_Name, "Temephos")
        self.assertCIP(intervention=iv._intervention)

    def test_Larvicides_invalid_habitat(self):
        with self.assertRaises(ValueError) as context:
            Larvicides(
                self.campaign,
                killing_config=wc.Constant(constant_effect=0.4),
                habitat_target="INVALID_HABITAT")
        self.assertIn("HabitatType", str(context.exception))

    # -------------------------------------------------------------------------
    # LarvalMicrosporidiaIntervention
    # -------------------------------------------------------------------------

    def test_LarvalMicrosporidiaIntervention_default(self):
        iv = LarvalMicrosporidiaIntervention(
            self.campaign,
            strain_name="Microsporidia_Strain_A")
        self.assertEqual(iv._intervention['class'], 'LarvalMicrosporidiaIntervention')
        self.assertEqual(iv._intervention.Strain_Name, "Microsporidia_Strain_A")

    def test_LarvalMicrosporidiaIntervention(self):
        iv = LarvalMicrosporidiaIntervention(
            self.campaign,
            strain_name="Microsporidia_Strain_B",
            habitat_target=HabitatType.CONSTANT,
            habitat_coverage=0.8,
            infectivity_config=wc.Constant(constant_effect=0.5),
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'LarvalMicrosporidiaIntervention')
        self.assertEqual(iv._intervention.Strain_Name, "Microsporidia_Strain_B")
        self.assertEqual(iv._intervention.Habitat_Target, "CONSTANT")
        self.assertEqual(iv._intervention.Habitat_Coverage, 0.8)
        self.assertCIP(intervention=iv._intervention)

    def test_LarvalMicrosporidiaIntervention_invalid_coverage(self):
        with self.assertRaises(ValueError):
            LarvalMicrosporidiaIntervention(
                self.campaign,
                strain_name="Microsporidia_Strain_A",
                habitat_coverage=1.5)

    # -------------------------------------------------------------------------
    # InputEIR
    # -------------------------------------------------------------------------

    def test_InputEIR_monthly_default(self):
        monthly = [10.0] * 12
        iv = InputEIR(self.campaign, monthly_eir=monthly)
        self.assertEqual(iv._intervention['class'], 'InputEIR')
        self.assertEqual(iv._intervention.EIR_Type, "MONTHLY")
        self.assertEqual(iv._intervention.Monthly_EIR, monthly)

    def test_InputEIR_daily(self):
        daily = [1.0] * 365
        CIP = deepcopy(self.CIP)
        CIP.cost = None
        iv = InputEIR(
            self.campaign,
            daily_eir=daily,
            common_intervention_parameters=CIP)
        self.assertEqual(iv._intervention['class'], 'InputEIR')
        self.assertEqual(iv._intervention.EIR_Type, "DAILY")
        self.assertEqual(iv._intervention.Daily_EIR, daily)
        self.assertCIP(intervention=iv._intervention, cost=None)

    def test_InputEIR_monthly_with_scaling(self):
        monthly = [5.0, 8.0, 12.0, 15.0, 20.0, 25.0, 20.0, 15.0, 10.0, 8.0, 5.0, 3.0]
        CIP = deepcopy(self.CIP)
        CIP.cost = None
        iv = InputEIR(
            self.campaign,
            monthly_eir=monthly,
            scaling_factor=2.0,
            common_intervention_parameters=CIP)
        self.assertEqual(iv._intervention.EIR_Type, "MONTHLY")
        self.assertEqual(iv._intervention.Scaling_Factor, 2.0)
        self.assertCIP(intervention=iv._intervention, cost=None)

    def test_InputEIR_both_provided(self):
        with self.assertRaises(ValueError) as context:
            InputEIR(
                self.campaign,
                monthly_eir=[10.0] * 12,
                daily_eir=[1.0] * 365)
        self.assertIn("not both", str(context.exception))

    def test_InputEIR_neither_provided(self):
        with self.assertRaises(ValueError) as context:
            InputEIR(self.campaign)
        self.assertIn("must be provided", str(context.exception))

    def test_InputEIR_wrong_monthly_length(self):
        with self.assertRaises(ValueError) as context:
            InputEIR(self.campaign, monthly_eir=[10.0] * 6)
        self.assertIn("12", str(context.exception))

    def test_InputEIR_wrong_daily_length(self):
        with self.assertRaises(ValueError) as context:
            InputEIR(self.campaign, daily_eir=[1.0] * 100)
        self.assertIn("365", str(context.exception))

    # -------------------------------------------------------------------------
    # MalariaChallenge
    # -------------------------------------------------------------------------

    def test_MalariaChallenge_sporozoite_default(self):
        iv = MalariaChallenge(
            self.campaign,
            sporozoite_count=100)
        self.assertEqual(iv._intervention['class'], 'MalariaChallenge')
        self.assertEqual(iv._intervention.Challenge_Type, "Sporozoites")

    def test_MalariaChallenge_infectious_bite(self):
        CIP = deepcopy(self.CIP)
        CIP.cost = None
        iv = MalariaChallenge(
            self.campaign,
            infectious_bite_count=5,
            coverage=0.8,
            common_intervention_parameters=CIP)
        self.assertEqual(iv._intervention['class'], 'MalariaChallenge')
        self.assertEqual(iv._intervention.Challenge_Type, "InfectiousBites")
        self.assertEqual(iv._intervention.Coverage, 0.8)
        self.assertCIP(intervention=iv._intervention, cost=None)

    def test_MalariaChallenge_both_provided(self):
        with self.assertRaises(ValueError) as context:
            MalariaChallenge(
                self.campaign,
                sporozoite_count=100,
                infectious_bite_count=5)
        self.assertIn("not both", str(context.exception))

    def test_MalariaChallenge_neither_provided(self):
        with self.assertRaises(ValueError) as context:
            MalariaChallenge(self.campaign)
        self.assertIn("must be provided", str(context.exception))

    # -------------------------------------------------------------------------
    # MosquitoRelease
    # -------------------------------------------------------------------------

    def test_MosquitoRelease_number_default(self):
        iv = MosquitoRelease(
            self.campaign,
            released_species="gambiae",
            released_genome=[["X", "X"], ["a0", "a1"]],
            released_number=1000)
        self.assertEqual(iv._intervention['class'], 'MosquitoRelease')
        self.assertEqual(iv._intervention.Released_Species, "gambiae")
        self.assertEqual(iv._intervention.Released_Type, "FIXED_NUMBER")

    def test_MosquitoRelease_ratio(self):
        iv = MosquitoRelease(
            self.campaign,
            released_species="arabiensis",
            released_genome=[["X", "X"], ["a0", "a0"]],
            released_ratio=0.5,
            released_infectious=0.1,
            released_mate_genome=[["X", "Y"], ["a0", "a0"]],
            released_wolbachia=WolbachiaType.VECTOR_WOLBACHIA_FREE,
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'MosquitoRelease')
        self.assertEqual(iv._intervention.Released_Species, "arabiensis")
        self.assertEqual(iv._intervention.Released_Type, "RATIO")
        self.assertEqual(iv._intervention.Released_Infectious, 0.1)
        self.assertCIP(intervention=iv._intervention)

    def test_MosquitoRelease_both_provided(self):
        with self.assertRaises(ValueError) as context:
            MosquitoRelease(
                self.campaign,
                released_species="gambiae",
                released_genome=[["X", "X"]],
                released_number=1000,
                released_ratio=0.5)
        self.assertIn("not both", str(context.exception))

    def test_MosquitoRelease_neither_provided(self):
        with self.assertRaises(ValueError) as context:
            MosquitoRelease(
                self.campaign,
                released_species="gambiae",
                released_genome=[["X", "X"]])
        self.assertIn("must be provided", str(context.exception))

    def test_MosquitoRelease_invalid_wolbachia(self):
        with self.assertRaises(ValueError) as context:
            MosquitoRelease(
                self.campaign,
                released_species="gambiae",
                released_genome=[["X", "X"]],
                released_number=1000,
                released_wolbachia="INVALID_TYPE")
        self.assertIn("WolbachiaType", str(context.exception))

    # -------------------------------------------------------------------------
    # ScaleLarvalHabitat
    # -------------------------------------------------------------------------

    def test_ScaleLarvalHabitat_default(self):
        spec = LarvalHabitatMultiplierSpec(
            self.campaign,
            habitat=HabitatType.CONSTANT,
            factor=2.0)
        iv = ScaleLarvalHabitat(
            self.campaign,
            larval_habitat_multiplier=[spec])
        self.assertEqual(iv._intervention['class'], 'ScaleLarvalHabitat')
        self.assertEqual(len(iv._intervention.Larval_Habitat_Multiplier), 1)

    def test_ScaleLarvalHabitat(self):
        spec1 = LarvalHabitatMultiplierSpec(
            self.campaign,
            habitat=HabitatType.CONSTANT,
            factor=2.0)
        spec2 = LarvalHabitatMultiplierSpec(
            self.campaign,
            habitat=HabitatType.TEMPORARY_RAINFALL,
            factor=0.5,
            species="gambiae")
        CIP = deepcopy(self.CIP)
        CIP.cost = None
        iv = ScaleLarvalHabitat(
            self.campaign,
            larval_habitat_multiplier=[spec1, spec2],
            common_intervention_parameters=CIP)
        self.assertEqual(iv._intervention['class'], 'ScaleLarvalHabitat')
        self.assertEqual(len(iv._intervention.Larval_Habitat_Multiplier), 2)
        self.assertCIP(intervention=iv._intervention, cost=None)

    def test_ScaleLarvalHabitat_empty_list(self):
        with self.assertRaises(ValueError) as context:
            ScaleLarvalHabitat(
                self.campaign,
                larval_habitat_multiplier=[])
        self.assertIn("at least one", str(context.exception).lower())

    def test_ScaleLarvalHabitat_invalid_type(self):
        with self.assertRaises(ValueError) as context:
            ScaleLarvalHabitat(
                self.campaign,
                larval_habitat_multiplier=["not_a_spec"])
        self.assertIn("LarvalHabitatMultiplierSpec", str(context.exception))

    # -------------------------------------------------------------------------
    # OutdoorRestKill
    # -------------------------------------------------------------------------

    def test_OutdoorRestKill_default(self):
        iv = OutdoorRestKill(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.3))
        self.assertEqual(iv._intervention['class'], 'OutdoorRestKill')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectConstant')

    def test_OutdoorRestKill(self):
        iv = OutdoorRestKill(
            self.campaign,
            killing_config=wc.Exponential(initial_effect=0.5, decay_time_constant=200),
            insecticide_name="Deltamethrin",
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'OutdoorRestKill')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectExponential')
        self.assertEqual(iv._intervention.Insecticide_Name, "Deltamethrin")
        self.assertCIP(intervention=iv._intervention)

    # -------------------------------------------------------------------------
    # OutdoorNodeEmanator
    # -------------------------------------------------------------------------

    def test_OutdoorNodeEmanator_default(self):
        iv = OutdoorNodeEmanator(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.4),
            killing_config=wc.Constant(constant_effect=0.2))
        self.assertEqual(iv._intervention['class'], 'OutdoorNodeEmanator')
        self.assertEqual(iv._intervention.Repelling_Config['class'], 'WaningEffectConstant')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectConstant')

    def test_OutdoorNodeEmanator(self):
        iv = OutdoorNodeEmanator(
            self.campaign,
            repelling_config=wc.Exponential(initial_effect=0.6, decay_time_constant=180),
            killing_config=wc.Exponential(initial_effect=0.3, decay_time_constant=180),
            insecticide_name="Transfluthrin",
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'OutdoorNodeEmanator')
        self.assertEqual(iv._intervention.Repelling_Config['class'], 'WaningEffectExponential')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectExponential')
        self.assertEqual(iv._intervention.Insecticide_Name, "Transfluthrin")
        self.assertCIP(intervention=iv._intervention)

    # -------------------------------------------------------------------------
    # SugarTrap
    # -------------------------------------------------------------------------

    def test_SugarTrap_default(self):
        iv = SugarTrap(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.5))
        self.assertEqual(iv._intervention['class'], 'SugarTrap')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectConstant')

    def test_SugarTrap(self):
        iv = SugarTrap(
            self.campaign,
            killing_config=wc.Exponential(initial_effect=0.8, decay_time_constant=90),
            expiration_period_distribution=ConstantDistribution(365),
            insecticide_name="Pyrethroid",
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'SugarTrap')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectExponential')
        self.assertEqual(iv._intervention.Insecticide_Name, "Pyrethroid")
        self.assertCIP(intervention=iv._intervention)

    # -------------------------------------------------------------------------
    # OvipositionTrap
    # -------------------------------------------------------------------------

    def test_OvipositionTrap_default(self):
        iv = OvipositionTrap(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.6))
        self.assertEqual(iv._intervention['class'], 'OvipositionTrap')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectConstant')

    def test_OvipositionTrap(self):
        iv = OvipositionTrap(
            self.campaign,
            killing_config=wc.Exponential(initial_effect=0.9, decay_time_constant=120),
            habitat_target=HabitatType.BRACKISH_SWAMP,
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'OvipositionTrap')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectExponential')
        self.assertEqual(iv._intervention.Habitat_Target, "BRACKISH_SWAMP")
        self.assertCIP(intervention=iv._intervention)

    # -------------------------------------------------------------------------
    # Implicit config validation tests
    # -------------------------------------------------------------------------

    def test_OvipositionTrap_implicit_validates_vector_sampling_type(self):
        self.campaign.implicits.clear()
        OvipositionTrap(self.campaign, killing_config=wc.Constant(constant_effect=0.5))
        self.assertEqual(len(self.campaign.implicits), 1)

        class MockConfig:
            class parameters:
                Vector_Sampling_Type = "VECTOR_COMPARTMENTS_NUMBER"
        with self.assertRaises(ValueError) as ctx:
            self.campaign.implicits[0](MockConfig())
        self.assertIn("TRACK_ALL_VECTORS", str(ctx.exception))
        self.assertIn("OvipositionTrap", str(ctx.exception))

        MockConfig.parameters.Vector_Sampling_Type = "TRACK_ALL_VECTORS"
        result = self.campaign.implicits[0](MockConfig())
        self.assertIsNotNone(result)

    def test_SugarTrap_implicit_validates_sugar_feeding(self):
        self.campaign.implicits.clear()
        SugarTrap(self.campaign, killing_config=wc.Constant(constant_effect=0.5))
        self.assertEqual(len(self.campaign.implicits), 1)

        class MockSpecies:
            Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_NONE"
        class MockConfig:
            class parameters:
                Vector_Species_Params = [MockSpecies()]
        with self.assertRaises(ValueError) as ctx:
            self.campaign.implicits[0](MockConfig())
        self.assertIn("VECTOR_SUGAR_FEEDING_NONE", str(ctx.exception))
        self.assertIn("SugarTrap", str(ctx.exception))

        MockConfig.parameters.Vector_Species_Params[0].Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_EVERY_DAY"
        result = self.campaign.implicits[0](MockConfig())
        self.assertIsNotNone(result)

    # -------------------------------------------------------------------------
    # SpatialRepellent
    # -------------------------------------------------------------------------

    def test_SpatialRepellent_default(self):
        iv = SpatialRepellent(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.5))
        self.assertEqual(iv._intervention['class'], 'SpatialRepellent')
        self.assertEqual(iv._intervention.Repelling_Config['class'], 'WaningEffectConstant')

    def test_SpatialRepellent(self):
        iv = SpatialRepellent(
            self.campaign,
            repelling_config=wc.Exponential(initial_effect=0.7, decay_time_constant=365),
            insecticide_name="DEET",
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'SpatialRepellent')
        self.assertEqual(iv._intervention.Repelling_Config['class'], 'WaningEffectExponential')
        self.assertEqual(iv._intervention.Insecticide_Name, "DEET")
        self.assertCIP(intervention=iv._intervention)

    # -------------------------------------------------------------------------
    # AnimalFeedKill
    # -------------------------------------------------------------------------

    def test_AnimalFeedKill_default(self):
        iv = AnimalFeedKill(
            self.campaign,
            killing_config=wc.Constant(constant_effect=0.3))
        self.assertEqual(iv._intervention['class'], 'AnimalFeedKill')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectConstant')

    def test_AnimalFeedKill(self):
        iv = AnimalFeedKill(
            self.campaign,
            killing_config=wc.Exponential(initial_effect=0.6, decay_time_constant=270),
            insecticide_name="Fipronil",
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'AnimalFeedKill')
        self.assertEqual(iv._intervention.Killing_Config['class'], 'WaningEffectExponential')
        self.assertEqual(iv._intervention.Insecticide_Name, "Fipronil")
        self.assertCIP(intervention=iv._intervention)

    # -------------------------------------------------------------------------
    # ArtificialDiet
    # -------------------------------------------------------------------------

    def test_ArtificialDiet_default(self):
        iv = ArtificialDiet(
            self.campaign,
            artificial_diet_target=ArtificialDietTarget.AD_OUTSIDE_VILLAGE,
            attraction_config=wc.Constant(constant_effect=0.5))
        self.assertEqual(iv._intervention['class'], 'ArtificialDiet')
        self.assertEqual(iv._intervention.Artificial_Diet_Target, "AD_OutsideVillage")

    def test_ArtificialDiet(self):
        iv = ArtificialDiet(
            self.campaign,
            artificial_diet_target=ArtificialDietTarget.AD_WITHIN_VILLAGE,
            attraction_config=wc.Exponential(initial_effect=0.8, decay_time_constant=365),
            common_intervention_parameters=self.CIP)
        self.assertEqual(iv._intervention['class'], 'ArtificialDiet')
        self.assertEqual(iv._intervention.Artificial_Diet_Target, "AD_WithinVillage")
        self.assertCIP(intervention=iv._intervention)

    def test_ArtificialDiet_invalid_target(self):
        with self.assertRaises(ValueError) as context:
            ArtificialDiet(
                self.campaign,
                artificial_diet_target="INVALID_TARGET",
                attraction_config=wc.Constant(constant_effect=0.5))
        self.assertIn("ArtificialDietTarget", str(context.exception))
