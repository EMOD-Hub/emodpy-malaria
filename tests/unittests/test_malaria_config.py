import unittest
import pytest

import emod_api.config.default_from_schema_no_validation as dfs
from emodpy_malaria import malaria_config
from emodpy_malaria.drug_config import MalariaDrugTypeParameters, DrugModifier, DoseFractionByAge
from emodpy_malaria.utils.emod_enum import (
    InnateImmuneVariationType, MalariaStrainModel, ParasiteSwitchType,
    VarGeneRandomnessType, VectorSamplingType, PKPDModel
)
from emodpy_malaria.utils.distributions import GaussianDistribution

from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest  # noqa: E402


def _fresh_config():
    return dfs.get_default_config_from_schema(manifest.schema_file, as_rod=True)


@pytest.mark.unit
class TestSetTeamDefaults(unittest.TestCase):

    def test_simulation_type(self):
        config = _fresh_config()
        config = malaria_config.set_team_defaults(config, manifest)
        self.assertEqual(config.parameters.Simulation_Type, "MALARIA_SIM")

    def test_malaria_strain_model(self):
        config = _fresh_config()
        config = malaria_config.set_team_defaults(config, manifest)
        self.assertEqual(config.parameters.Malaria_Strain_Model,
                         MalariaStrainModel.FALCIPARUM_RANDOM_STRAIN)

    def test_infection_params(self):
        config = _fresh_config()
        config = malaria_config.set_team_defaults(config, manifest)
        self.assertEqual(config.parameters.Infection_Updates_Per_Timestep, 8)
        self.assertEqual(config.parameters.Enable_Superinfection, 1)
        self.assertEqual(config.parameters.Incubation_Period_Constant, 7)
        self.assertEqual(config.parameters.Antibody_IRBC_Kill_Rate, 1.596)
        self.assertEqual(config.parameters.RBC_Destruction_Multiplier, 3.29)
        self.assertEqual(config.parameters.Parasite_Switch_Type,
                         ParasiteSwitchType.RATE_PER_PARASITE_7VARS)

    def test_immunity_params(self):
        config = _fresh_config()
        config = malaria_config.set_team_defaults(config, manifest)
        self.assertEqual(config.parameters.Innate_Immune_Variation_Type,
                         InnateImmuneVariationType.NONE)
        self.assertEqual(config.parameters.Pyrogenic_Threshold, 1.5e4)
        self.assertEqual(config.parameters.Falciparum_MSP_Variants, 32)
        self.assertEqual(config.parameters.Falciparum_Nonspecific_Types, 76)
        self.assertEqual(config.parameters.Falciparum_PfEMP1_Variants, 1070)
        self.assertEqual(config.parameters.Max_Individual_Infections, 3)

    def test_symptomaticity_params(self):
        config = _fresh_config()
        config = malaria_config.set_team_defaults(config, manifest)
        self.assertEqual(config.parameters.Clinical_Fever_Threshold_High, 1.5)
        self.assertEqual(config.parameters.Clinical_Fever_Threshold_Low, 0.5)
        self.assertEqual(config.parameters.Min_Days_Between_Clinical_Incidents, 14)

    def test_report_thresholds(self):
        config = _fresh_config()
        config = malaria_config.set_team_defaults(config, manifest)
        self.assertEqual(config.parameters.Report_Detection_Threshold_Blood_Smear_Parasites, 20)
        self.assertEqual(config.parameters.Report_Detection_Threshold_PCR_Parasites, 0.05)
        self.assertEqual(config.parameters.Report_Detection_Threshold_PfHRP2, 5.0)

    def test_infectious_period_removed(self):
        config = _fresh_config()
        config = malaria_config.set_team_defaults(config, manifest)
        self.assertFalse(hasattr(config.parameters, "Infectious_Period_Constant"))
        self.assertFalse(hasattr(config.parameters, "Infectious_Period_Distribution"))

    def test_drugs_loaded(self):
        config = _fresh_config()
        config = malaria_config.set_team_defaults(config, manifest)
        self.assertGreater(len(config.parameters.Malaria_Drug_Params), 0)
        drug_names = [d.Name for d in config.parameters.Malaria_Drug_Params]
        self.assertIn("Chloroquine", drug_names)
        self.assertIn("Artemether", drug_names)
        self.assertIn("DHA", drug_names)

    def test_returns_config(self):
        config = _fresh_config()
        result = malaria_config.set_team_defaults(config, manifest)
        self.assertIs(result, config)


@pytest.mark.unit
class TestSetTeamDrugParams(unittest.TestCase):

    def test_loads_all_csv_drugs(self):
        config = _fresh_config()
        config = malaria_config.set_team_drug_params(config, manifest)
        drug_names = [d.Name for d in config.parameters.Malaria_Drug_Params]
        expected = [
            "Artemether", "Lumefantrine", "DHA", "Piperaquine", "Primaquine",
            "Chloroquine", "Artesunate", "Sulfadoxine", "Pyrimethamine",
            "moAmodiaquine", "Amodiaquine", "Amodiaquine1",
            "Amodiaquine_for_AS_combination", "Abstract", "Vehicle",
            "SulfadoxinePyrimethamine", "moSulfadoxinePyrimethamine"
        ]
        for name in expected:
            self.assertIn(name, drug_names)

    def test_drug_params_values(self):
        config = _fresh_config()
        config = malaria_config.set_team_drug_params(config, manifest)
        chloroquine = None
        for d in config.parameters.Malaria_Drug_Params:
            if d.Name == "Chloroquine":
                chloroquine = d
                break
        self.assertIsNotNone(chloroquine)
        self.assertEqual(chloroquine.Drug_Cmax, 150)
        self.assertEqual(chloroquine.Drug_Decay_T1, 8.9)
        self.assertEqual(chloroquine.Drug_Decay_T2, 244)
        self.assertEqual(chloroquine.Drug_Vd, 3.9)
        self.assertEqual(chloroquine.PKPD_Model, "CONCENTRATION_VERSUS_TIME")

    def test_dose_fractions_loaded(self):
        config = _fresh_config()
        config = malaria_config.set_team_drug_params(config, manifest)
        chloroquine = None
        for d in config.parameters.Malaria_Drug_Params:
            if d.Name == "Chloroquine":
                chloroquine = d
                break
        self.assertEqual(len(chloroquine.Fractional_Dose_By_Upper_Age), 3)

    def test_vehicle_empty_dose_fractions(self):
        config = _fresh_config()
        config = malaria_config.set_team_drug_params(config, manifest)
        vehicle = None
        for d in config.parameters.Malaria_Drug_Params:
            if d.Name == "Vehicle":
                vehicle = d
                break
        self.assertIsNotNone(vehicle)
        self.assertEqual(len(vehicle.Fractional_Dose_By_Upper_Age), 0)


@pytest.mark.unit
class TestSetParasiteGeneticsParams(unittest.TestCase):

    def test_default(self):
        config = _fresh_config()
        config = malaria_config.set_parasite_genetics_params(config, manifest)
        self.assertEqual(config.parameters.Malaria_Model,
                         "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS")
        self.assertEqual(config.parameters.Parasite_Genetics.Var_Gene_Randomness_Type,
                         VarGeneRandomnessType.ALL_RANDOM)

    def test_default_sporozoites_distribution(self):
        config = _fresh_config()
        config = malaria_config.set_parasite_genetics_params(config, manifest)
        self.assertEqual(config.parameters.Parasite_Genetics.Sporozoites_Per_Oocyst_Distribution,
                         "GAUSSIAN_DISTRIBUTION")
        self.assertEqual(config.parameters.Parasite_Genetics.Sporozoites_Per_Oocyst_Gaussian_Mean,
                         10000)
        self.assertEqual(config.parameters.Parasite_Genetics.Sporozoites_Per_Oocyst_Gaussian_Std_Dev,
                         1000)

    def test_custom_sporozoites_distribution(self):
        config = _fresh_config()
        dist = GaussianDistribution(mean=5000, std_dev=500)
        config = malaria_config.set_parasite_genetics_params(config, manifest,
                                                              sporozoites_per_oocyst=dist)
        self.assertEqual(config.parameters.Parasite_Genetics.Sporozoites_Per_Oocyst_Gaussian_Mean,
                         5000)

    def test_barcode_genome_locations(self):
        config = _fresh_config()
        config = malaria_config.set_parasite_genetics_params(config, manifest)
        self.assertEqual(len(config.parameters.Parasite_Genetics.Barcode_Genome_Locations), 24)

    def test_malaria_strain_model_removed(self):
        config = _fresh_config()
        config = malaria_config.set_parasite_genetics_params(config, manifest)
        self.assertFalse(hasattr(config.parameters, "Malaria_Strain_Model"))

    def test_vector_sampling_type(self):
        config = _fresh_config()
        config = malaria_config.set_parasite_genetics_params(config, manifest)
        self.assertEqual(config.parameters.Vector_Sampling_Type,
                         VectorSamplingType.TRACK_ALL_VECTORS)

    def test_fixed_neighborhood(self):
        config = _fresh_config()
        config = malaria_config.set_parasite_genetics_params(
            config, manifest,
            var_gene_randomness_type=VarGeneRandomnessType.FIXED_NEIGHBORHOOD)
        pg = config.parameters.Parasite_Genetics
        self.assertEqual(pg.Var_Gene_Randomness_Type,
                         VarGeneRandomnessType.FIXED_NEIGHBORHOOD)
        self.assertEqual(pg.MSP_Genome_Location, 200000)
        self.assertEqual(pg.Neighborhood_Size_MSP, 4)
        self.assertEqual(pg.Neighborhood_Size_PfEMP1, 10)
        self.assertEqual(len(pg.PfEMP1_Variants_Genome_Locations), 50)

    def test_fixed_msp(self):
        config = _fresh_config()
        config = malaria_config.set_parasite_genetics_params(
            config, manifest,
            var_gene_randomness_type=VarGeneRandomnessType.FIXED_MSP)
        pg = config.parameters.Parasite_Genetics
        self.assertEqual(pg.MSP_Genome_Location, 200000)
        self.assertFalse(hasattr(pg, "PfEMP1_Variants_Genome_Locations") and
                         len(pg.PfEMP1_Variants_Genome_Locations) > 0)

    def test_string_var_gene_randomness_type(self):
        config = _fresh_config()
        config = malaria_config.set_parasite_genetics_params(
            config, manifest, var_gene_randomness_type="ALL_RANDOM")
        self.assertEqual(config.parameters.Parasite_Genetics.Var_Gene_Randomness_Type,
                         VarGeneRandomnessType.ALL_RANDOM)

    def test_invalid_var_gene_randomness_type(self):
        config = _fresh_config()
        with self.assertRaises(ValueError):
            malaria_config.set_parasite_genetics_params(
                config, manifest, var_gene_randomness_type="INVALID")


@pytest.mark.unit
class TestGetDrugParams(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = _fresh_config()
        malaria_config.set_team_defaults(cls.config, manifest)

    def test_get_existing_drug(self):
        dp = malaria_config.get_drug_params(self.config, "Chloroquine")
        self.assertEqual(dp.Name, "Chloroquine")

    def test_get_nonexistent_drug(self):
        with self.assertRaises(ValueError):
            malaria_config.get_drug_params(self.config, "NonexistentDrug")


@pytest.mark.unit
class TestSetDrugParam(unittest.TestCase):

    def test_set_existing_param(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        malaria_config.set_drug_param(config, drug_name="Chloroquine",
                                      parameter="Drug_Cmax", value=999)
        dp = malaria_config.get_drug_params(config, "Chloroquine")
        self.assertEqual(dp.Drug_Cmax, 999)

    def test_set_new_param_warns(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        with self.assertWarns(UserWarning):
            malaria_config.set_drug_param(config, drug_name="Chloroquine",
                                          parameter="New_Param", value=42)

    def test_nonexistent_drug(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        with self.assertRaises(ValueError):
            malaria_config.set_drug_param(config, drug_name="FakeDrug",
                                          parameter="Drug_Cmax", value=1)

    def test_missing_args(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        with self.assertRaises(Exception):
            malaria_config.set_drug_param(config)
        with self.assertRaises(Exception):
            malaria_config.set_drug_param(config, drug_name="Chloroquine")
        with self.assertRaises(Exception):
            malaria_config.set_drug_param(config, drug_name="Chloroquine",
                                          parameter="Drug_Cmax")


@pytest.mark.unit
class TestAddNewDrug(unittest.TestCase):

    def test_add_new_drug(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        count_before = len(config.parameters.Malaria_Drug_Params)
        drug = MalariaDrugTypeParameters(name="BrandNewDrug", drug_cmax=500)
        malaria_config.add_new_drug(config, manifest, drug)
        self.assertEqual(len(config.parameters.Malaria_Drug_Params), count_before + 1)
        dp = malaria_config.get_drug_params(config, "BrandNewDrug")
        self.assertEqual(dp.Drug_Cmax, 500)

    def test_add_duplicate_raises(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        drug = MalariaDrugTypeParameters(name="Chloroquine", drug_cmax=500)
        with self.assertRaises(ValueError):
            malaria_config.add_new_drug(config, manifest, drug)

    def test_add_duplicate_with_overwrite(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        count_before = len(config.parameters.Malaria_Drug_Params)
        drug = MalariaDrugTypeParameters(name="Chloroquine", drug_cmax=999)
        malaria_config.add_new_drug(config, manifest, drug, overwrite=True)
        self.assertEqual(len(config.parameters.Malaria_Drug_Params), count_before)
        dp = malaria_config.get_drug_params(config, "Chloroquine")
        self.assertEqual(dp.Drug_Cmax, 999)

    def test_invalid_drug_type(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        with self.assertRaises(ValueError):
            malaria_config.add_new_drug(config, manifest, drug="not a drug object")


@pytest.mark.unit
class TestAddDrugResistance(unittest.TestCase):

    def test_add_resistance(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        malaria_config.add_drug_resistance(config, manifest,
                                           drugname="Chloroquine",
                                           drug_resistant_string="A",
                                           pkpd_c50_modifier=2.0,
                                           max_irbc_kill_modifier=0.9)
        dp = malaria_config.get_drug_params(config, "Chloroquine")
        self.assertEqual(len(dp.Resistances), 1)
        self.assertEqual(dp.Resistances[0].Drug_Resistant_String, "A")
        self.assertEqual(dp.Resistances[0].PKPD_C50_Modifier, 2.0)
        self.assertEqual(dp.Resistances[0].Max_IRBC_Kill_Modifier, 0.9)

    def test_add_multiple_resistances(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        malaria_config.add_drug_resistance(config, manifest,
                                           drugname="Chloroquine",
                                           drug_resistant_string="A")
        malaria_config.add_drug_resistance(config, manifest,
                                           drugname="Chloroquine",
                                           drug_resistant_string="C",
                                           pkpd_c50_modifier=3.0)
        dp = malaria_config.get_drug_params(config, "Chloroquine")
        self.assertEqual(len(dp.Resistances), 2)

    def test_nonexistent_drug(self):
        config = _fresh_config()
        malaria_config.set_team_defaults(config, manifest)
        with self.assertRaises(ValueError):
            malaria_config.add_drug_resistance(config, manifest,
                                               drugname="FakeDrug",
                                               drug_resistant_string="A")


@pytest.mark.unit
class TestDrugConfig(unittest.TestCase):

    def test_dose_fraction_by_age(self):
        df = DoseFractionByAge(upper_age_in_years=5, fraction_of_adult_dose=0.5)
        self.assertEqual(df.upper_age_in_years, 5)
        self.assertEqual(df.fraction_of_adult_dose, 0.5)
        result = df.to_schema_dict(manifest)
        self.assertEqual(result.Upper_Age_In_Years, 5)
        self.assertEqual(result.Fraction_Of_Adult_Dose, 0.5)

    def test_dose_fraction_invalid_age(self):
        with self.assertRaises(ValueError):
            DoseFractionByAge(upper_age_in_years=-1, fraction_of_adult_dose=0.5)

    def test_dose_fraction_invalid_fraction(self):
        with self.assertRaises(ValueError):
            DoseFractionByAge(upper_age_in_years=5, fraction_of_adult_dose=1.5)

    def test_drug_modifier(self):
        dm = DrugModifier(drug_resistant_string="ACT", pkpd_c50_modifier=2.0,
                          max_irbc_kill_modifier=0.8)
        self.assertEqual(dm.drug_resistant_string, "ACT")
        self.assertEqual(dm.pkpd_c50_modifier, 2.0)
        self.assertEqual(dm.max_irbc_kill_modifier, 0.8)
        result = dm.to_schema_dict(manifest)
        self.assertEqual(result.Drug_Resistant_String, "ACT")
        self.assertEqual(result.PKPD_C50_Modifier, 2.0)

    def test_malaria_drug_type_parameters_defaults(self):
        drug = MalariaDrugTypeParameters(name="TestDrug")
        self.assertEqual(drug.name, "TestDrug")
        self.assertEqual(drug.pkpd_model, PKPDModel.FIXED_DURATION_CONSTANT_EFFECT)

    def test_malaria_drug_type_parameters_full(self):
        dose_fracs = [DoseFractionByAge(5, 0.5), DoseFractionByAge(10, 0.75)]
        resistances = [DrugModifier("A", 2.0, 0.9)]
        drug = MalariaDrugTypeParameters(
            name="FullDrug",
            pkpd_model=PKPDModel.CONCENTRATION_VERSUS_TIME,
            drug_cmax=200,
            drug_decay_t1=0.5,
            drug_decay_t2=1.0,
            drug_vd=5,
            drug_pkpd_c50=50,
            drug_fulltreatment_doses=3,
            drug_dose_interval=1,
            drug_gametocyte02_killrate=2.5,
            drug_gametocyte34_killrate=1.5,
            drug_gametocytem_killrate=0.7,
            drug_hepatocyte_killrate=0.1,
            max_drug_irbc_kill=8.0,
            bodyweight_exponent=1,
            fractional_dose_by_upper_age=dose_fracs,
            resistances=resistances,
        )
        result = drug.to_schema_dict(manifest)
        self.assertEqual(result.Name, "FullDrug")
        self.assertEqual(result.PKPD_Model, "CONCENTRATION_VERSUS_TIME")
        self.assertEqual(result.Drug_Cmax, 200)
        self.assertEqual(len(result.Fractional_Dose_By_Upper_Age), 2)
        self.assertEqual(len(result.Resistances), 1)

    def test_malaria_drug_type_string_pkpd_model(self):
        drug = MalariaDrugTypeParameters(
            name="StringPKPD",
            pkpd_model="CONCENTRATION_VERSUS_TIME")
        self.assertEqual(drug.pkpd_model, PKPDModel.CONCENTRATION_VERSUS_TIME)

    def test_malaria_drug_type_invalid_pkpd_model(self):
        with self.assertRaises(ValueError):
            MalariaDrugTypeParameters(name="BadDrug", pkpd_model="INVALID")
