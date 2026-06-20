import unittest
import pytest
from emodpy_malaria.campaign.individual_intervention import (
    AntimalarialDrug, AdherentDrug, MultiPackComboDrug, MalariaDiagnostic,
    SimpleBednet, UsageDependentBednet, MultiInsecticideUsageDependentBednet,
    IRSHousingModification, MultiInsecticideIRSHousingModification,
    ScreeningHousingModification, SpatialRepellentHousingModification,
    SimpleIndividualRepellent, IndoorIndividualEmanator, HumanHostSeekingTrap,
    Ivermectin, RTSSVaccine, BitingRisk, SimpleHealthSeekingBehavior,
    OutbreakIndividualMalariaGenetics, OutbreakIndividualMalariaVarGenes
)
import emodpy_malaria.campaign.waning_config as wc

from emod_api import campaign as api_campaign
from emodpy_malaria.campaign.common import CommonInterventionParameters
from emodpy_malaria.utils.distributions import ConstantDistribution, ExponentialDistribution
from emodpy_malaria.utils.emod_enum import (
    DiagnosticType, NonAdherenceOption, NucleotideSequenceOrigin
)

from copy import deepcopy
from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest  # noqa: E402


@pytest.mark.unit
class TestIntervention(unittest.TestCase):
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

    def assertCIP(self, intervention, cost=2, disqualifying_properties=["Risk:High"], dont_allow_duplicates=True,
                  intervention_name="TestIntervention", new_property_value="Risk:Low"):
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
    # AntimalarialDrug
    # -------------------------------------------------------------------------

    def test_AntimalarialDrug_default(self):
        drug = AntimalarialDrug(self.campaign, drug_type="Chloroquine")
        self.assertEqual(drug._intervention['class'], 'AntimalarialDrug')
        self.assertEqual(drug._intervention.Drug_Type, "Chloroquine")

    def test_AntimalarialDrug(self):
        drug = AntimalarialDrug(self.campaign, drug_type="Artemether",
                                common_intervention_parameters=self.CIP)
        self.assertEqual(drug._intervention['class'], 'AntimalarialDrug')
        self.assertEqual(drug._intervention.Drug_Type, "Artemether")
        self.assertCIP(intervention=drug._intervention)

    # -------------------------------------------------------------------------
    # AdherentDrug
    # -------------------------------------------------------------------------

    def test_AdherentDrug_default(self):
        drug = AdherentDrug(
            self.campaign,
            doses=[["Artemether", "Lumefantrine"]],
            adherence_config=wc.Constant(constant_effect=0.8),
            non_adherence_options=[NonAdherenceOption.NEXT_DOSAGE_TIME],
            non_adherence_distribution=[1.0])
        self.assertEqual(drug._intervention['class'], 'AdherentDrug')
        self.assertEqual(drug._intervention.Doses, [["Artemether", "Lumefantrine"]])
        self.assertEqual(drug._intervention.Dose_Interval, 1)
        self.assertEqual(drug._intervention.Non_Adherence_Options, [NonAdherenceOption.NEXT_DOSAGE_TIME])
        self.assertEqual(drug._intervention.Non_Adherence_Distribution, [1.0])
        self.assertEqual(drug._intervention.Adherence_Config['class'], 'WaningEffectConstant')

    def test_AdherentDrug(self):
        drug = AdherentDrug(
            self.campaign,
            doses=[["Artemether", "Lumefantrine"], ["Artemether", "Lumefantrine"], ["Artemether"]],
            adherence_config=wc.Constant(constant_effect=0.8),
            non_adherence_options=[NonAdherenceOption.NEXT_DOSAGE_TIME, NonAdherenceOption.STOP],
            non_adherence_distribution=[0.9, 0.1],
            dose_interval=0.5,
            max_dose_consideration_duration=7,
            took_dose_event="TookALDose",
            common_intervention_parameters=self.CIP)
        self.assertEqual(drug._intervention['class'], 'AdherentDrug')
        self.assertEqual(drug._intervention.Doses,
                         [["Artemether", "Lumefantrine"], ["Artemether", "Lumefantrine"], ["Artemether"]])
        self.assertEqual(drug._intervention.Dose_Interval, 0.5)
        self.assertEqual(drug._intervention.Max_Dose_Consideration_Duration, 7)
        self.assertEqual(drug._intervention.Non_Adherence_Options,
                         [NonAdherenceOption.NEXT_DOSAGE_TIME, NonAdherenceOption.STOP])
        self.assertEqual(drug._intervention.Non_Adherence_Distribution, [0.9, 0.1])
        self.assertEqual(drug._intervention.Took_Dose_Event, "TookALDose")
        self.assertCIP(intervention=drug._intervention)

    def test_AdherentDrug_invalid_non_adherence_option(self):
        with self.assertRaises(ValueError) as context:
            AdherentDrug(
                self.campaign,
                doses=[["Artemether"]],
                adherence_config=wc.Constant(constant_effect=0.8),
                non_adherence_options=["INVALID_OPTION"],
                non_adherence_distribution=[1.0])
        self.assertIn("NonAdherenceOption", str(context.exception))

    def test_AdherentDrug_mismatched_distribution_length(self):
        with self.assertRaises(ValueError) as context:
            AdherentDrug(
                self.campaign,
                doses=[["Artemether"]],
                adherence_config=wc.Constant(constant_effect=0.8),
                non_adherence_options=[NonAdherenceOption.NEXT_DOSAGE_TIME, NonAdherenceOption.STOP],
                non_adherence_distribution=[1.0])
        self.assertIn("same", str(context.exception))

    def test_AdherentDrug_duration_too_short(self):
        with self.assertRaises(ValueError) as context:
            AdherentDrug(
                self.campaign,
                doses=[["Artemether"]] * 10,
                adherence_config=wc.Constant(constant_effect=0.8),
                non_adherence_options=[NonAdherenceOption.NEXT_DOSAGE_TIME],
                non_adherence_distribution=[1.0],
                dose_interval=1,
                max_dose_consideration_duration=5)
        self.assertIn("max_dose_consideration_duration", str(context.exception))

    # -------------------------------------------------------------------------
    # MultiPackComboDrug
    # -------------------------------------------------------------------------

    def test_MultiPackComboDrug_default(self):
        drug = MultiPackComboDrug(self.campaign,
                                  doses=[["Sulfadoxine", "Pyrimethamine"]])
        self.assertEqual(drug._intervention['class'], 'MultiPackComboDrug')
        self.assertEqual(drug._intervention.Doses, [["Sulfadoxine", "Pyrimethamine"]])
        self.assertEqual(drug._intervention.Dose_Interval, 1)

    def test_MultiPackComboDrug(self):
        drug = MultiPackComboDrug(
            self.campaign,
            doses=[["Artemether", "Lumefantrine"], ["Artemether"]],
            dose_interval=0.5,
            common_intervention_parameters=self.CIP)
        self.assertEqual(drug._intervention['class'], 'MultiPackComboDrug')
        self.assertEqual(drug._intervention.Doses, [["Artemether", "Lumefantrine"], ["Artemether"]])
        self.assertEqual(drug._intervention.Dose_Interval, 0.5)
        self.assertCIP(intervention=drug._intervention)

    # -------------------------------------------------------------------------
    # MalariaDiagnostic
    # -------------------------------------------------------------------------

    def test_MalariaDiagnostic_event_default(self):
        diag = MalariaDiagnostic(
            self.campaign,
            diagnostic_type=DiagnosticType.BLOOD_SMEAR_PARASITES,
            positive_diagnosis="TestedPositive")
        self.assertEqual(diag._intervention['class'], 'MalariaDiagnostic')
        self.assertEqual(diag._intervention.Diagnostic_Type, DiagnosticType.BLOOD_SMEAR_PARASITES)
        self.assertEqual(diag._intervention.Detection_Threshold, 0)
        self.assertEqual(diag._intervention.Measurement_Sensitivity, 0.1)
        self.assertEqual(diag._intervention.Treatment_Fraction, 1)
        self.assertEqual(diag._intervention.Days_To_Diagnosis, 0)
        self.assertEqual(diag._intervention.Event_Or_Config, "Event")
        self.assertEqual(diag._intervention.Positive_Diagnosis_Event, "TestedPositive")

    def test_MalariaDiagnostic_event(self):
        diag = MalariaDiagnostic(
            self.campaign,
            diagnostic_type=DiagnosticType.PF_HRP2,
            positive_diagnosis="TestedPositive",
            negative_diagnosis="TestedNegative",
            detection_threshold=40,
            measurement_sensitivity=0.5,
            treatment_fraction=0.8,
            days_to_diagnosis=3,
            common_intervention_parameters=self.CIP)
        self.assertEqual(diag._intervention['class'], 'MalariaDiagnostic')
        self.assertEqual(diag._intervention.Diagnostic_Type, DiagnosticType.PF_HRP2)
        self.assertEqual(diag._intervention.Detection_Threshold, 40)
        self.assertEqual(diag._intervention.Measurement_Sensitivity, 0.5)
        self.assertEqual(diag._intervention.Treatment_Fraction, 0.8)
        self.assertEqual(diag._intervention.Days_To_Diagnosis, 3)
        self.assertEqual(diag._intervention.Positive_Diagnosis_Event, "TestedPositive")
        self.assertEqual(diag._intervention.Negative_Diagnosis_Event, "TestedNegative")
        self.assertEqual(diag._intervention.Event_Or_Config, "Event")
        self.assertCIP(intervention=diag._intervention)

    def test_MalariaDiagnostic_config(self):
        positive_config = AntimalarialDrug(self.campaign, drug_type="Chloroquine")
        diag = MalariaDiagnostic(
            self.campaign,
            diagnostic_type=DiagnosticType.BLOOD_SMEAR_PARASITES,
            positive_diagnosis=positive_config)
        self.assertEqual(diag._intervention['class'], 'MalariaDiagnostic')
        self.assertEqual(diag._intervention.Event_Or_Config, "Config")
        self.assertDictEqual(diag._intervention.Positive_Diagnosis_Config, positive_config._intervention)

    def test_MalariaDiagnostic_config_with_negative(self):
        positive_config = AntimalarialDrug(self.campaign, drug_type="Chloroquine")
        negative_config = AntimalarialDrug(self.campaign, drug_type="Artemether")
        diag = MalariaDiagnostic(
            self.campaign,
            diagnostic_type=DiagnosticType.BLOOD_SMEAR_PARASITES,
            positive_diagnosis=positive_config,
            negative_diagnosis=negative_config)
        self.assertEqual(diag._intervention.Event_Or_Config, "Config")
        self.assertDictEqual(diag._intervention.Positive_Diagnosis_Config, positive_config._intervention)
        self.assertDictEqual(diag._intervention.Negative_Diagnosis_Config, negative_config._intervention)

    def test_MalariaDiagnostic_invalid_diagnostic_type(self):
        with self.assertRaises(ValueError) as context:
            MalariaDiagnostic(
                self.campaign,
                diagnostic_type="INVALID_TYPE",
                positive_diagnosis="TestedPositive")
        self.assertIn("DiagnosticType", str(context.exception))

    def test_MalariaDiagnostic_mismatched_event_config(self):
        positive_config = AntimalarialDrug(self.campaign, drug_type="Chloroquine")
        with self.assertRaises(ValueError) as context:
            MalariaDiagnostic(
                self.campaign,
                diagnostic_type=DiagnosticType.BLOOD_SMEAR_PARASITES,
                positive_diagnosis=positive_config,
                negative_diagnosis="TestedNegative")
        self.assertIn("IndividualIntervention", str(context.exception))

    def test_MalariaDiagnostic_mismatched_config_event(self):
        negative_config = AntimalarialDrug(self.campaign, drug_type="Chloroquine")
        with self.assertRaises(ValueError) as context:
            MalariaDiagnostic(
                self.campaign,
                diagnostic_type=DiagnosticType.BLOOD_SMEAR_PARASITES,
                positive_diagnosis="TestedPositive",
                negative_diagnosis=negative_config)
        self.assertIn("string", str(context.exception))

    def test_MalariaDiagnostic_invalid_positive_type(self):
        with self.assertRaises(ValueError) as context:
            MalariaDiagnostic(
                self.campaign,
                diagnostic_type=DiagnosticType.BLOOD_SMEAR_PARASITES,
                positive_diagnosis=12345)
        self.assertIn("string", str(context.exception))

    # -------------------------------------------------------------------------
    # SimpleBednet
    # -------------------------------------------------------------------------

    def test_SimpleBednet_default(self):
        bednet = SimpleBednet(
            self.campaign,
            repelling_config=wc.Exponential(initial_effect=0.5, decay_time_constant=365),
            blocking_config=wc.Exponential(initial_effect=0.9, decay_time_constant=365),
            killing_config=wc.Exponential(initial_effect=0.6, decay_time_constant=365))
        self.assertEqual(bednet._intervention['class'], 'SimpleBednet')
        self.assertEqual(bednet._intervention.Repelling_Config['class'], 'WaningEffectExponential')
        self.assertEqual(bednet._intervention.Blocking_Config['class'], 'WaningEffectExponential')
        self.assertEqual(bednet._intervention.Killing_Config['class'], 'WaningEffectExponential')
        self.assertEqual(bednet._intervention.Usage_Config['class'], 'WaningEffectConstant')

    def test_SimpleBednet(self):
        bednet = SimpleBednet(
            self.campaign,
            repelling_config=wc.Exponential(initial_effect=0.5, decay_time_constant=365),
            blocking_config=wc.Exponential(initial_effect=0.9, decay_time_constant=365),
            killing_config=wc.Exponential(initial_effect=0.6, decay_time_constant=365),
            usage_config=wc.Constant(constant_effect=0.8),
            insecticide_name="Pyrethroid",
            common_intervention_parameters=self.CIP)
        self.assertEqual(bednet._intervention['class'], 'SimpleBednet')
        self.assertEqual(bednet._intervention.Repelling_Config.Initial_Effect, 0.5)
        self.assertEqual(bednet._intervention.Blocking_Config.Initial_Effect, 0.9)
        self.assertEqual(bednet._intervention.Killing_Config.Initial_Effect, 0.6)
        self.assertEqual(bednet._intervention.Usage_Config['class'], 'WaningEffectConstant')
        self.assertEqual(bednet._intervention.Insecticide_Name, "Pyrethroid")
        self.assertCIP(intervention=bednet._intervention)

    # -------------------------------------------------------------------------
    # UsageDependentBednet
    # -------------------------------------------------------------------------

    def test_UsageDependentBednet_default(self):
        bednet = UsageDependentBednet(
            self.campaign,
            blocking_config=wc.Exponential(initial_effect=0.9, decay_time_constant=365),
            killing_config=wc.Exponential(initial_effect=0.6, decay_time_constant=365),
            repelling_config=wc.Exponential(initial_effect=0.5, decay_time_constant=365),
            expiration_period_distribution=ConstantDistribution(730))
        self.assertEqual(bednet._intervention['class'], 'UsageDependentBednet')
        self.assertEqual(bednet._intervention.Blocking_Config['class'], 'WaningEffectExponential')
        self.assertEqual(bednet._intervention.Killing_Config['class'], 'WaningEffectExponential')
        self.assertEqual(bednet._intervention.Repelling_Config['class'], 'WaningEffectExponential')

    def test_UsageDependentBednet(self):
        bednet = UsageDependentBednet(
            self.campaign,
            blocking_config=wc.Exponential(initial_effect=0.9, decay_time_constant=365),
            killing_config=wc.Exponential(initial_effect=0.6, decay_time_constant=365),
            repelling_config=wc.Exponential(initial_effect=0.5, decay_time_constant=365),
            expiration_period_distribution=ConstantDistribution(730),
            usage_config_list=[wc.Constant(constant_effect=0.7)],
            insecticide_name="Pyrethroid",
            received_event="ReceivedBednet",
            using_event="UsingBednet",
            discard_event="DiscardedBednet",
            common_intervention_parameters=self.CIP)
        self.assertEqual(bednet._intervention['class'], 'UsageDependentBednet')
        self.assertEqual(bednet._intervention.Insecticide_Name, "Pyrethroid")
        self.assertEqual(bednet._intervention.Received_Event, "ReceivedBednet")
        self.assertEqual(bednet._intervention.Using_Event, "UsingBednet")
        self.assertEqual(bednet._intervention.Discard_Event, "DiscardedBednet")
        self.assertEqual(len(bednet._intervention.Usage_Config_List), 1)
        self.assertCIP(intervention=bednet._intervention)

    def test_UsageDependentBednet_invalid_distribution(self):
        with self.assertRaises(ValueError) as context:
            UsageDependentBednet(
                self.campaign,
                blocking_config=wc.Exponential(initial_effect=0.9, decay_time_constant=365),
                killing_config=wc.Exponential(initial_effect=0.6, decay_time_constant=365),
                repelling_config=wc.Exponential(initial_effect=0.5, decay_time_constant=365),
                expiration_period_distribution="not_a_distribution")
        self.assertIn("BaseDistribution", str(context.exception))

    # -------------------------------------------------------------------------
    # MultiInsecticideUsageDependentBednet
    # -------------------------------------------------------------------------

    def test_MultiInsecticideUsageDependentBednet_default(self):
        ins = wc.InsecticideWaningEffect_RBK(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.3),
            blocking_config=wc.Constant(constant_effect=0.5),
            killing_config=wc.Constant(constant_effect=0.7),
            insecticide_name="Pyrethroid")
        bednet = MultiInsecticideUsageDependentBednet(
            self.campaign,
            insecticides=[ins],
            expiration_period_distribution=ConstantDistribution(730))
        self.assertEqual(bednet._intervention['class'], 'MultiInsecticideUsageDependentBednet')
        self.assertEqual(len(bednet._intervention.Insecticides), 1)

    def test_MultiInsecticideUsageDependentBednet(self):
        CIP = deepcopy(self.CIP)
        CIP.disqualifying_properties = None
        CIP.dont_allow_duplicates = None
        CIP.intervention_name = None
        CIP.new_property_value = None
        ins1 = wc.InsecticideWaningEffect_RBK(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.3),
            blocking_config=wc.Constant(constant_effect=0.5),
            killing_config=wc.Constant(constant_effect=0.7),
            insecticide_name="Pyrethroid")
        ins2 = wc.InsecticideWaningEffect_RBK(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.2),
            blocking_config=wc.Constant(constant_effect=0.4),
            killing_config=wc.Constant(constant_effect=0.6),
            insecticide_name="PBO")
        bednet = MultiInsecticideUsageDependentBednet(
            self.campaign,
            insecticides=[ins1, ins2],
            expiration_period_distribution=ConstantDistribution(730),
            usage_config_list=[wc.Constant(constant_effect=0.7)],
            received_event="ReceivedBednet",
            using_event="UsingBednet",
            discard_event="DiscardedBednet",
            common_intervention_parameters=CIP)
        self.assertEqual(bednet._intervention['class'], 'MultiInsecticideUsageDependentBednet')
        self.assertEqual(len(bednet._intervention.Insecticides), 2)
        self.assertEqual(bednet._intervention.Received_Event, "ReceivedBednet")
        self.assertEqual(bednet._intervention.Using_Event, "UsingBednet")
        self.assertEqual(bednet._intervention.Discard_Event, "DiscardedBednet")
        self.assertCIP(intervention=bednet._intervention,
                       disqualifying_properties=None, dont_allow_duplicates=None,
                       intervention_name=None, new_property_value=None)

    def test_MultiInsecticideUsageDependentBednet_invalid_insecticide(self):
        with self.assertRaises(ValueError) as context:
            MultiInsecticideUsageDependentBednet(
                self.campaign,
                insecticides=["not_an_insecticide"],
                expiration_period_distribution=ConstantDistribution(730))
        self.assertIn("InsecticideWaningEffect_RBK", str(context.exception))

    # -------------------------------------------------------------------------
    # IRSHousingModification
    # -------------------------------------------------------------------------

    def test_IRSHousingModification_default(self):
        irs = IRSHousingModification(
            self.campaign,
            repelling_config=wc.Exponential(initial_effect=0.4, decay_time_constant=180),
            killing_config=wc.Exponential(initial_effect=0.7, decay_time_constant=180))
        self.assertEqual(irs._intervention['class'], 'IRSHousingModification')
        self.assertEqual(irs._intervention.Repelling_Config['class'], 'WaningEffectExponential')
        self.assertEqual(irs._intervention.Killing_Config['class'], 'WaningEffectExponential')

    def test_IRSHousingModification(self):
        irs = IRSHousingModification(
            self.campaign,
            repelling_config=wc.Exponential(initial_effect=0.4, decay_time_constant=180),
            killing_config=wc.Exponential(initial_effect=0.7, decay_time_constant=180),
            insecticide_name="Pyrethroid",
            common_intervention_parameters=self.CIP)
        self.assertEqual(irs._intervention['class'], 'IRSHousingModification')
        self.assertEqual(irs._intervention.Repelling_Config.Initial_Effect, 0.4)
        self.assertEqual(irs._intervention.Killing_Config.Initial_Effect, 0.7)
        self.assertEqual(irs._intervention.Insecticide_Name, "Pyrethroid")
        self.assertCIP(intervention=irs._intervention)

    # -------------------------------------------------------------------------
    # MultiInsecticideIRSHousingModification
    # -------------------------------------------------------------------------

    def test_MultiInsecticideIRSHousingModification_default(self):
        ins = wc.InsecticideWaningEffect_RK(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.3),
            killing_config=wc.Constant(constant_effect=0.7),
            insecticide_name="Pyrethroid")
        irs = MultiInsecticideIRSHousingModification(self.campaign, insecticides=[ins])
        self.assertEqual(irs._intervention['class'], 'MultiInsecticideIRSHousingModification')
        self.assertEqual(len(irs._intervention.Insecticides), 1)

    def test_MultiInsecticideIRSHousingModification(self):
        ins1 = wc.InsecticideWaningEffect_RK(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.3),
            killing_config=wc.Constant(constant_effect=0.7),
            insecticide_name="Pyrethroid")
        ins2 = wc.InsecticideWaningEffect_RK(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.2),
            killing_config=wc.Constant(constant_effect=0.6),
            insecticide_name="Pirimiphos-methyl")
        irs = MultiInsecticideIRSHousingModification(
            self.campaign, insecticides=[ins1, ins2],
            common_intervention_parameters=self.CIP)
        self.assertEqual(irs._intervention['class'], 'MultiInsecticideIRSHousingModification')
        self.assertEqual(len(irs._intervention.Insecticides), 2)
        self.assertCIP(intervention=irs._intervention)

    def test_MultiInsecticideIRSHousingModification_invalid_insecticide(self):
        with self.assertRaises(ValueError) as context:
            MultiInsecticideIRSHousingModification(
                self.campaign, insecticides=["not_an_insecticide"])
        self.assertIn("InsecticideWaningEffect_RK", str(context.exception))

    # -------------------------------------------------------------------------
    # ScreeningHousingModification
    # -------------------------------------------------------------------------

    def test_ScreeningHousingModification_default(self):
        screening = ScreeningHousingModification(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.5),
            killing_config=wc.Constant(constant_effect=0.3))
        self.assertEqual(screening._intervention['class'], 'ScreeningHousingModification')
        self.assertEqual(screening._intervention.Repelling_Config['class'], 'WaningEffectConstant')
        self.assertEqual(screening._intervention.Killing_Config['class'], 'WaningEffectConstant')

    def test_ScreeningHousingModification(self):
        screening = ScreeningHousingModification(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.5),
            killing_config=wc.Constant(constant_effect=0.3),
            insecticide_name="Pyrethroid",
            common_intervention_parameters=self.CIP)
        self.assertEqual(screening._intervention['class'], 'ScreeningHousingModification')
        self.assertEqual(screening._intervention.Insecticide_Name, "Pyrethroid")
        self.assertCIP(intervention=screening._intervention)

    # -------------------------------------------------------------------------
    # SpatialRepellentHousingModification
    # -------------------------------------------------------------------------

    def test_SpatialRepellentHousingModification_default(self):
        spatial = SpatialRepellentHousingModification(
            self.campaign,
            repelling_config=wc.Exponential(initial_effect=0.6, decay_time_constant=180))
        self.assertEqual(spatial._intervention['class'], 'SpatialRepellentHousingModification')
        self.assertEqual(spatial._intervention.Repelling_Config['class'], 'WaningEffectExponential')

    def test_SpatialRepellentHousingModification(self):
        spatial = SpatialRepellentHousingModification(
            self.campaign,
            repelling_config=wc.Exponential(initial_effect=0.6, decay_time_constant=180),
            insecticide_name="Transfluthrin",
            common_intervention_parameters=self.CIP)
        self.assertEqual(spatial._intervention['class'], 'SpatialRepellentHousingModification')
        self.assertEqual(spatial._intervention.Insecticide_Name, "Transfluthrin")
        self.assertCIP(intervention=spatial._intervention)

    # -------------------------------------------------------------------------
    # SimpleIndividualRepellent
    # -------------------------------------------------------------------------

    def test_SimpleIndividualRepellent_default(self):
        repellent = SimpleIndividualRepellent(
            self.campaign,
            repelling_config=wc.Exponential(initial_effect=0.7, decay_time_constant=90))
        self.assertEqual(repellent._intervention['class'], 'SimpleIndividualRepellent')
        self.assertEqual(repellent._intervention.Repelling_Config['class'], 'WaningEffectExponential')

    def test_SimpleIndividualRepellent(self):
        repellent = SimpleIndividualRepellent(
            self.campaign,
            repelling_config=wc.Exponential(initial_effect=0.7, decay_time_constant=90),
            insecticide_name="DEET",
            common_intervention_parameters=self.CIP)
        self.assertEqual(repellent._intervention['class'], 'SimpleIndividualRepellent')
        self.assertEqual(repellent._intervention.Insecticide_Name, "DEET")
        self.assertCIP(intervention=repellent._intervention)

    # -------------------------------------------------------------------------
    # IndoorIndividualEmanator
    # -------------------------------------------------------------------------

    def test_IndoorIndividualEmanator_default(self):
        emanator = IndoorIndividualEmanator(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.5),
            killing_config=wc.Constant(constant_effect=0.3))
        self.assertEqual(emanator._intervention['class'], 'IndoorIndividualEmanator')
        self.assertEqual(emanator._intervention.Repelling_Config['class'], 'WaningEffectConstant')
        self.assertEqual(emanator._intervention.Killing_Config['class'], 'WaningEffectConstant')

    def test_IndoorIndividualEmanator(self):
        emanator = IndoorIndividualEmanator(
            self.campaign,
            repelling_config=wc.Constant(constant_effect=0.5),
            killing_config=wc.Constant(constant_effect=0.3),
            insecticide_name="Metofluthrin",
            common_intervention_parameters=self.CIP)
        self.assertEqual(emanator._intervention['class'], 'IndoorIndividualEmanator')
        self.assertEqual(emanator._intervention.Insecticide_Name, "Metofluthrin")
        self.assertCIP(intervention=emanator._intervention)

    # -------------------------------------------------------------------------
    # HumanHostSeekingTrap
    # -------------------------------------------------------------------------

    def test_HumanHostSeekingTrap_default(self):
        trap = HumanHostSeekingTrap(
            self.campaign,
            attract_config=wc.Constant(constant_effect=0.8),
            killing_config=wc.Constant(constant_effect=0.5))
        self.assertEqual(trap._intervention['class'], 'HumanHostSeekingTrap')
        self.assertEqual(trap._intervention.Attract_Config['class'], 'WaningEffectConstant')
        self.assertEqual(trap._intervention.Killing_Config['class'], 'WaningEffectConstant')

    def test_HumanHostSeekingTrap(self):
        trap = HumanHostSeekingTrap(
            self.campaign,
            attract_config=wc.Constant(constant_effect=0.8),
            killing_config=wc.Constant(constant_effect=0.5),
            common_intervention_parameters=self.CIP)
        self.assertEqual(trap._intervention['class'], 'HumanHostSeekingTrap')
        self.assertEqual(trap._intervention.Attract_Config.Initial_Effect, 0.8)
        self.assertEqual(trap._intervention.Killing_Config.Initial_Effect, 0.5)
        self.assertCIP(intervention=trap._intervention)

    # -------------------------------------------------------------------------
    # Ivermectin
    # -------------------------------------------------------------------------

    def test_Ivermectin_default(self):
        ivm = Ivermectin(
            self.campaign,
            killing_config=wc.Box(constant_effect=0.9, box_duration=14))
        self.assertEqual(ivm._intervention['class'], 'Ivermectin')
        self.assertEqual(ivm._intervention.Killing_Config['class'], 'WaningEffectBox')
        self.assertEqual(ivm._intervention.Killing_Config.Initial_Effect, 0.9)
        self.assertEqual(ivm._intervention.Killing_Config.Box_Duration, 14)

    def test_Ivermectin(self):
        ivm = Ivermectin(
            self.campaign,
            killing_config=wc.Box(constant_effect=0.9, box_duration=14),
            insecticide_name="Ivermectin",
            common_intervention_parameters=self.CIP)
        self.assertEqual(ivm._intervention['class'], 'Ivermectin')
        self.assertEqual(ivm._intervention.Insecticide_Name, "Ivermectin")
        self.assertCIP(intervention=ivm._intervention)

    # -------------------------------------------------------------------------
    # RTSSVaccine
    # -------------------------------------------------------------------------

    def test_RTSSVaccine_default(self):
        vaccine = RTSSVaccine(self.campaign)
        self.assertEqual(vaccine._intervention['class'], 'RTSSVaccine')
        self.assertEqual(vaccine._intervention.Boosted_Antibody_Concentration, 1)

    def test_RTSSVaccine(self):
        vaccine = RTSSVaccine(self.campaign,
                              boosted_antibody_concentration=2.5,
                              common_intervention_parameters=self.CIP)
        self.assertEqual(vaccine._intervention['class'], 'RTSSVaccine')
        self.assertEqual(vaccine._intervention.Boosted_Antibody_Concentration, 2.5)
        self.assertCIP(intervention=vaccine._intervention)

    # -------------------------------------------------------------------------
    # BitingRisk
    # -------------------------------------------------------------------------

    def test_BitingRisk_default(self):
        risk = BitingRisk(self.campaign,
                          risk_distribution=ConstantDistribution(1.5))
        self.assertEqual(risk._intervention['class'], 'BitingRisk')

    def test_BitingRisk(self):
        CIP = deepcopy(self.CIP)
        CIP.cost = None
        risk = BitingRisk(self.campaign,
                          risk_distribution=ExponentialDistribution(5),
                          common_intervention_parameters=CIP)
        self.assertEqual(risk._intervention['class'], 'BitingRisk')
        self.assertCIP(intervention=risk._intervention, cost=None)

    def test_BitingRisk_invalid_distribution(self):
        with self.assertRaises(ValueError) as context:
            BitingRisk(self.campaign, risk_distribution="not_a_distribution")
        self.assertIn("BaseDistribution", str(context.exception))

    # -------------------------------------------------------------------------
    # SimpleHealthSeekingBehavior
    # -------------------------------------------------------------------------

    def test_SimpleHealthSeekingBehavior_event_default(self):
        hsb = SimpleHealthSeekingBehavior(
            self.campaign,
            actual_intervention="SeekingTreatment")
        self.assertEqual(hsb._intervention['class'], 'SimpleHealthSeekingBehavior')
        self.assertEqual(hsb._intervention.Tendency, 1)
        self.assertEqual(hsb._intervention.Single_Use, 1)
        self.assertEqual(hsb._intervention.Event_Or_Config, "Event")
        self.assertEqual(hsb._intervention.Actual_IndividualIntervention_Event, "SeekingTreatment")

    def test_SimpleHealthSeekingBehavior_event(self):
        CIP = deepcopy(self.CIP)
        CIP.cost = None
        hsb = SimpleHealthSeekingBehavior(
            self.campaign,
            actual_intervention="SeekingTreatment",
            tendency=0.8,
            single_use=False,
            common_intervention_parameters=CIP)
        self.assertEqual(hsb._intervention['class'], 'SimpleHealthSeekingBehavior')
        self.assertEqual(hsb._intervention.Tendency, 0.8)
        self.assertEqual(hsb._intervention.Single_Use, 0)
        self.assertEqual(hsb._intervention.Event_Or_Config, "Event")
        self.assertCIP(intervention=hsb._intervention, cost=None)

    def test_SimpleHealthSeekingBehavior_config(self):
        drug = AntimalarialDrug(self.campaign, drug_type="Chloroquine")
        hsb = SimpleHealthSeekingBehavior(
            self.campaign,
            actual_intervention=drug,
            tendency=0.6)
        self.assertEqual(hsb._intervention['class'], 'SimpleHealthSeekingBehavior')
        self.assertEqual(hsb._intervention.Event_Or_Config, "Config")
        self.assertDictEqual(hsb._intervention.Actual_IndividualIntervention_Config, drug._intervention)

    def test_SimpleHealthSeekingBehavior_invalid_intervention(self):
        with self.assertRaises(ValueError) as context:
            SimpleHealthSeekingBehavior(
                self.campaign,
                actual_intervention=12345)
        self.assertIn("string", str(context.exception))

    # -------------------------------------------------------------------------
    # OutbreakIndividualMalariaGenetics
    # -------------------------------------------------------------------------

    def test_OutbreakIndividualMalariaGenetics_barcode_default(self):
        outbreak = OutbreakIndividualMalariaGenetics(
            self.campaign,
            create_nucleotide_sequence_from=NucleotideSequenceOrigin.BARCODE_STRING,
            barcode_string="AATTCCGG")
        self.assertEqual(outbreak._intervention['class'], 'OutbreakIndividualMalariaGenetics')
        self.assertEqual(outbreak._intervention.Create_Nucleotide_Sequence_From,
                         NucleotideSequenceOrigin.BARCODE_STRING)
        self.assertEqual(outbreak._intervention.Barcode_String, "AATTCCGG")
        self.assertEqual(outbreak._intervention.Ignore_Immunity, 1)
        self.assertEqual(outbreak._intervention.Incubation_Period_Override, -1)

    def test_OutbreakIndividualMalariaGenetics_barcode(self):
        outbreak = OutbreakIndividualMalariaGenetics(
            self.campaign,
            create_nucleotide_sequence_from=NucleotideSequenceOrigin.BARCODE_STRING,
            barcode_string="AATTCCGG",
            drug_resistant_string="AA",
            hrp_string="AT",
            ignore_immunity=False,
            incubation_period_override=5)
        self.assertEqual(outbreak._intervention['class'], 'OutbreakIndividualMalariaGenetics')
        self.assertEqual(outbreak._intervention.Barcode_String, "AATTCCGG")
        self.assertEqual(outbreak._intervention.Drug_Resistant_String, "AA")
        self.assertEqual(outbreak._intervention.HRP_String, "AT")
        self.assertEqual(outbreak._intervention.Ignore_Immunity, 0)
        self.assertEqual(outbreak._intervention.Incubation_Period_Override, 5)

    def test_OutbreakIndividualMalariaGenetics_allele_frequencies(self):
        freqs = [[0.25, 0.25, 0.25, 0.25], [0.5, 0.5, 0.0, 0.0]]
        outbreak = OutbreakIndividualMalariaGenetics(
            self.campaign,
            create_nucleotide_sequence_from=NucleotideSequenceOrigin.ALLELE_FREQUENCIES,
            barcode_allele_frequencies_per_genome_location=freqs)
        self.assertEqual(outbreak._intervention['class'], 'OutbreakIndividualMalariaGenetics')
        self.assertEqual(outbreak._intervention.Create_Nucleotide_Sequence_From,
                         NucleotideSequenceOrigin.ALLELE_FREQUENCIES)
        self.assertEqual(outbreak._intervention.Barcode_Allele_Frequencies_Per_Genome_Location, freqs)

    def test_OutbreakIndividualMalariaGenetics_allele_freq_wrong_length(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.ALLELE_FREQUENCIES,
                barcode_allele_frequencies_per_genome_location=[[0.25, 0.25, 0.5], [0.5, 0.5, 0.0, 0.0]])
        self.assertIn("4 values", str(context.exception))
        self.assertIn("entry 0", str(context.exception))

    def test_OutbreakIndividualMalariaGenetics_allele_freq_not_sum_to_one(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.ALLELE_FREQUENCIES,
                barcode_allele_frequencies_per_genome_location=[[0.25, 0.25, 0.25, 0.25], [0.5, 0.5, 0.5, 0.0]])
        self.assertIn("sum to 1.0", str(context.exception))
        self.assertIn("entry 1", str(context.exception))

    def test_OutbreakIndividualMalariaGenetics_drug_resistant_freq_wrong_length(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.ALLELE_FREQUENCIES,
                drug_resistant_allele_frequencies_per_genome_location=[[0.5, 0.5]])
        self.assertIn("drug_resistant_allele_frequencies_per_genome_location", str(context.exception))
        self.assertIn("4 values", str(context.exception))

    def test_OutbreakIndividualMalariaGenetics_drug_resistant_freq_not_sum_to_one(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.ALLELE_FREQUENCIES,
                drug_resistant_allele_frequencies_per_genome_location=[[0.1, 0.1, 0.1, 0.1]])
        self.assertIn("drug_resistant_allele_frequencies_per_genome_location", str(context.exception))
        self.assertIn("sum to 1.0", str(context.exception))

    def test_OutbreakIndividualMalariaGenetics_hrp_freq_wrong_length(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.ALLELE_FREQUENCIES,
                hrp_allele_frequencies_per_genome_location=[[0.25, 0.25, 0.25, 0.25, 0.0]])
        self.assertIn("hrp_allele_frequencies_per_genome_location", str(context.exception))
        self.assertIn("4 values", str(context.exception))

    def test_OutbreakIndividualMalariaGenetics_hrp_freq_not_sum_to_one(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.ALLELE_FREQUENCIES,
                hrp_allele_frequencies_per_genome_location=[[0.9, 0.0, 0.0, 0.0]])
        self.assertIn("hrp_allele_frequencies_per_genome_location", str(context.exception))
        self.assertIn("sum to 1.0", str(context.exception))

    def test_OutbreakIndividualMalariaGenetics_nucleotide_sequence(self):
        pfemp1 = list(range(50))
        outbreak = OutbreakIndividualMalariaGenetics(
            self.campaign,
            create_nucleotide_sequence_from=NucleotideSequenceOrigin.NUCLEOTIDE_SEQUENCE,
            barcode_string="AATTCCGG",
            drug_resistant_string="AA",
            hrp_string="AT",
            msp_variant_value=5,
            pfemp1_variants_values=pfemp1)
        self.assertEqual(outbreak._intervention['class'], 'OutbreakIndividualMalariaGenetics')
        self.assertEqual(outbreak._intervention.Create_Nucleotide_Sequence_From,
                         NucleotideSequenceOrigin.NUCLEOTIDE_SEQUENCE)
        self.assertEqual(outbreak._intervention.MSP_Variant_Value, 5)
        self.assertEqual(outbreak._intervention.PfEMP1_Variants_Values, pfemp1)

    def test_OutbreakIndividualMalariaGenetics_barcode_missing_string(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.BARCODE_STRING)
        self.assertIn("barcode_string", str(context.exception))

    def test_OutbreakIndividualMalariaGenetics_nucleotide_missing_pfemp1(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.NUCLEOTIDE_SEQUENCE,
                barcode_string="AATTCCGG")
        self.assertIn("pfemp1_variants_values", str(context.exception))

    def test_OutbreakIndividualMalariaGenetics_nucleotide_wrong_pfemp1_length(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.NUCLEOTIDE_SEQUENCE,
                barcode_string="AATTCCGG",
                pfemp1_variants_values=[1, 2, 3])
        self.assertIn("50", str(context.exception))

    def test_OutbreakIndividualMalariaGenetics_barcode_with_allele_freq(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.BARCODE_STRING,
                barcode_string="AATTCCGG",
                barcode_allele_frequencies_per_genome_location=[[0.25, 0.25, 0.25, 0.25]])
        self.assertIn("ALLELE_FREQUENCIES", str(context.exception))

    def test_OutbreakIndividualMalariaGenetics_allele_freq_with_barcode_string(self):
        with self.assertRaises(ValueError) as context:
            OutbreakIndividualMalariaGenetics(
                self.campaign,
                create_nucleotide_sequence_from=NucleotideSequenceOrigin.ALLELE_FREQUENCIES,
                barcode_string="AATTCCGG")
        self.assertIn("BARCODE_STRING", str(context.exception))

    # -------------------------------------------------------------------------
    # OutbreakIndividualMalariaVarGenes
    # -------------------------------------------------------------------------

    def test_OutbreakIndividualMalariaVarGenes_default(self):
        outbreak = OutbreakIndividualMalariaVarGenes(self.campaign)
        self.assertEqual(outbreak._intervention['class'], 'OutbreakIndividualMalariaVarGenes')
        self.assertEqual(outbreak._intervention.MSP_Type, 0)
        self.assertEqual(outbreak._intervention.Ignore_Immunity, 1)
        self.assertEqual(outbreak._intervention.Incubation_Period_Override, -1)

    def test_OutbreakIndividualMalariaVarGenes(self):
        irbc = list(range(50))
        minor = list(range(50))
        outbreak = OutbreakIndividualMalariaVarGenes(
            self.campaign,
            msp_type=5,
            irbc_type=irbc,
            minor_epitope_type=minor,
            ignore_immunity=False,
            incubation_period_override=7)
        self.assertEqual(outbreak._intervention['class'], 'OutbreakIndividualMalariaVarGenes')
        self.assertEqual(outbreak._intervention.MSP_Type, 5)
        self.assertEqual(outbreak._intervention.IRBC_Type, irbc)
        self.assertEqual(outbreak._intervention.Minor_Epitope_Type, minor)
        self.assertEqual(outbreak._intervention.Ignore_Immunity, 0)
        self.assertEqual(outbreak._intervention.Incubation_Period_Override, 7)


    # -------------------------------------------------------------------------
    # Implicit config validation tests
    # -------------------------------------------------------------------------

    def test_OutbreakIndividualMalariaGenetics_implicit_validates_malaria_model(self):
        self.campaign.implicits.clear()
        OutbreakIndividualMalariaGenetics(
            self.campaign,
            create_nucleotide_sequence_from=NucleotideSequenceOrigin.BARCODE_STRING,
            barcode_string="AATTCCGG")
        self.assertEqual(len(self.campaign.implicits), 1)

        class MockConfig:
            class parameters:
                Malaria_Model = "MALARIA_MECHANISTIC_MODEL"
        with self.assertRaises(ValueError) as ctx:
            self.campaign.implicits[0](MockConfig())
        self.assertIn("MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS", str(ctx.exception))
        self.assertIn("OutbreakIndividualMalariaGenetics", str(ctx.exception))

        MockConfig.parameters.Malaria_Model = "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS"
        result = self.campaign.implicits[0](MockConfig())
        self.assertIsNotNone(result)

    def test_OutbreakIndividualMalariaVarGenes_implicit_validates_malaria_model(self):
        self.campaign.implicits.clear()
        OutbreakIndividualMalariaVarGenes(self.campaign)
        self.assertEqual(len(self.campaign.implicits), 1)

        class MockConfig:
            class parameters:
                Malaria_Model = "MALARIA_MECHANISTIC_MODEL"
        with self.assertRaises(ValueError) as ctx:
            self.campaign.implicits[0](MockConfig())
        self.assertIn("MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS", str(ctx.exception))
        self.assertIn("OutbreakIndividualMalariaVarGenes", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
