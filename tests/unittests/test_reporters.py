import unittest
import pytest

from emodpy.reporters.base import Reporters, ReportFilter
from emodpy_malaria.reporters.reporters import (
    InsetChart,
    MalariaSummaryReport,
    MalariaPatientJSONReport,
    ReportMalariaFiltered,
    ReportMalariaFilteredIntraHost,
    MalariaImmunityReport,
    ReportVectorGenetics,
    ReportVectorGeneticsMalariaGenetics,
    ReportVectorStats,
    ReportVectorStatsMalariaGenetics,
    ReportVectorMigration,
    VectorHabitatReport,
    ReportMicrosporidia,
    ReportInfectionStatsMalaria,
    ReportAntibodies,
    ReportFpgOutput,
    ReportFpgNewInfections,
    SpatialReportMalariaFiltered,
    ReportInterventionPopAvg,
    MalariaSurveyAnalyzer,
    ReportSimpleMalariaTransmission,
    SqlReportMalaria,
    SqlReportMalariaGenetics,
    ReportNodeDemographicsMalaria,
    ReportNodeDemographicsMalariaGenetics,
)
from emodpy_malaria.utils.emod_enum import (
    VectorGender,
    VectorGeneticsStratification,
    VectorStateEnum,
    SpatialOutputChannel,
    DrugResistantStatisticType,
)

from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest  # noqa: E402


def _reporters():
    return Reporters(schema_path=manifest.schema_path)


@pytest.mark.unit
class TestInsetChart(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        ic = InsetChart(reporters_object=r)
        self.assertEqual(ic.parameters["Enable_Default_Reporting"], 1)
        self.assertEqual(ic.parameters["Inset_Chart_Has_IP"], [])
        self.assertEqual(ic.parameters["Inset_Chart_Has_Interventions"], [])
        self.assertEqual(ic.parameters["Inset_Chart_Include_Pregnancies"], 0)
        self.assertEqual(
            ic.parameters["Inset_Chart_Reporting_Include_30Day_Avg_Infection_Duration"], 0
        )

    def test_custom_params(self):
        r = _reporters()
        ic = InsetChart(
            reporters_object=r,
            has_ip=["Risk:High"],
            has_interventions=["SimpleBednet"],
            include_pregnancies=True,
            include_30day_avg_infection_duration=True,
        )
        self.assertEqual(ic.parameters["Inset_Chart_Has_IP"], ["Risk:High"])
        self.assertEqual(ic.parameters["Inset_Chart_Has_Interventions"], ["SimpleBednet"])
        self.assertEqual(ic.parameters["Inset_Chart_Include_Pregnancies"], 1)
        self.assertEqual(
            ic.parameters["Inset_Chart_Reporting_Include_30Day_Avg_Infection_Duration"], 1
        )


@pytest.mark.unit
class TestMalariaSummaryReport(unittest.TestCase):

    def test_minimal(self):
        r = _reporters()
        rpt = MalariaSummaryReport(reporters_object=r, reporting_interval=30)
        self.assertEqual(rpt.parameters["class"], "MalariaSummaryReport")
        self.assertEqual(rpt.parameters.Reporting_Interval, 30)
        self.assertEqual(rpt.parameters.Max_Number_Reports, 1)

    def test_all_params(self):
        r = _reporters()
        rpt = MalariaSummaryReport(
            reporters_object=r,
            reporting_interval=365,
            age_bins=[5, 15, 100],
            parasitemia_bins=[0, 50, 500, 5000],
            infectiousness_bins=[0, 20, 40, 60, 80, 100],
            max_number_reports=10,
            pretty_format=True,
            add_prevalence_by_hrp2=True,
            detection_threshold_true_hrp2=5.0,
            add_true_density_vs_threshold=True,
            detection_threshold_true_parasite_density=40.0,
            detection_threshold_true_gametocyte_density=10.0,
            include_data_by_time_and_pfpr=False,
            include_data_by_time_and_infectiousness=False,
        )
        self.assertEqual(rpt.parameters.Reporting_Interval, 365)
        self.assertEqual(rpt.parameters.Age_Bins, [5, 15, 100])
        self.assertEqual(rpt.parameters.Parasitemia_Bins, [0, 50, 500, 5000])
        self.assertEqual(rpt.parameters.Max_Number_Reports, 10)
        self.assertEqual(rpt.parameters.Pretty_Format, 1)
        self.assertEqual(rpt.parameters.Add_Prevalence_By_HRP2, 1)
        self.assertEqual(rpt.parameters.Detection_Threshold_True_HRP2, 5.0)
        self.assertEqual(rpt.parameters.Add_True_Density_Vs_Threshold, 1)
        self.assertEqual(
            rpt.parameters.Detection_Threshold_True_Parasite_Density, 40.0
        )
        self.assertEqual(
            rpt.parameters.Detection_Threshold_True_Gametocyte_Density, 10.0
        )
        self.assertEqual(
            rpt.parameters.Include_DataByTimeAndPfPRBinsAndAgeBins, 0
        )
        self.assertEqual(
            rpt.parameters.Include_DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins,
            0,
        )

    def test_hrp2_requires_threshold(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            MalariaSummaryReport(
                reporters_object=r,
                reporting_interval=30,
                add_prevalence_by_hrp2=True,
            )

    def test_hrp2_threshold_without_flag_warns(self):
        r = _reporters()
        with self.assertRaises(UserWarning):
            MalariaSummaryReport(
                reporters_object=r,
                reporting_interval=30,
                detection_threshold_true_hrp2=5.0,
            )

    def test_true_density_requires_both_thresholds(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            MalariaSummaryReport(
                reporters_object=r,
                reporting_interval=30,
                add_true_density_vs_threshold=True,
                detection_threshold_true_parasite_density=40.0,
            )

    def test_density_threshold_without_flag_warns(self):
        r = _reporters()
        with self.assertRaises(UserWarning):
            MalariaSummaryReport(
                reporters_object=r,
                reporting_interval=30,
                detection_threshold_true_parasite_density=40.0,
            )

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = MalariaSummaryReport(reporters_object=r, reporting_interval=30)
        with self.assertRaises(ValueError):
            rpt._set_start_year(1990.0, "MalariaSummaryReport")

    def test_blocked_end_year(self):
        r = _reporters()
        rpt = MalariaSummaryReport(reporters_object=r, reporting_interval=30)
        with self.assertRaises(ValueError):
            rpt._set_end_year(2020.0, "MalariaSummaryReport")

    def test_blocked_min_age(self):
        r = _reporters()
        rpt = MalariaSummaryReport(reporters_object=r, reporting_interval=30)
        with self.assertRaises(ValueError):
            rpt._set_min_age_years(5.0, "MalariaSummaryReport")

    def test_blocked_max_age(self):
        r = _reporters()
        rpt = MalariaSummaryReport(reporters_object=r, reporting_interval=30)
        with self.assertRaises(ValueError):
            rpt._set_max_age_years(100.0, "MalariaSummaryReport")

    def test_with_report_filter(self):
        r = _reporters()
        rf = ReportFilter(start_day=10, end_day=100, node_ids=[1, 2])
        rpt = MalariaSummaryReport(
            reporters_object=r, reporting_interval=30, report_filter=rf
        )
        self.assertEqual(rpt.parameters.Start_Day, 10)
        self.assertEqual(rpt.parameters.End_Day, 100)
        self.assertEqual(rpt.parameters.Node_IDs_Of_Interest, [1, 2])

    def test_filter_start_year_blocked(self):
        r = _reporters()
        rf = ReportFilter(start_year=2000.0)
        with self.assertRaises(ValueError):
            MalariaSummaryReport(
                reporters_object=r, reporting_interval=30, report_filter=rf
            )


@pytest.mark.unit
class TestMalariaPatientJSONReport(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = MalariaPatientJSONReport(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "MalariaPatientJSONReport")

    def test_with_filter(self):
        r = _reporters()
        rf = ReportFilter(start_day=5, end_day=50)
        rpt = MalariaPatientJSONReport(reporters_object=r, report_filter=rf)
        self.assertEqual(rpt.parameters.Start_Day, 5)
        self.assertEqual(rpt.parameters.End_Day, 50)

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = MalariaPatientJSONReport(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "MalariaPatientJSONReport")

    def test_blocked_end_year(self):
        r = _reporters()
        rpt = MalariaPatientJSONReport(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_end_year(2020.0, "MalariaPatientJSONReport")


@pytest.mark.unit
class TestReportMalariaFiltered(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportMalariaFiltered(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "ReportMalariaFiltered")
        self.assertEqual(rpt.parameters.Include_30Day_Avg_Infection_Duration, 1)
        self.assertEqual(rpt.parameters.Include_Pregnancies, 0)

    def test_custom_params(self):
        r = _reporters()
        rpt = ReportMalariaFiltered(
            reporters_object=r,
            has_ip=["Risk:High", "Access:Good"],
            has_interventions=["SimpleBednet"],
            include_30day_avg_infection_duration=False,
            include_pregnancies=True,
        )
        self.assertEqual(rpt.parameters.Has_IP, ["Risk:High", "Access:Good"])
        self.assertEqual(rpt.parameters.Has_Interventions, ["SimpleBednet"])
        self.assertEqual(rpt.parameters.Include_30Day_Avg_Infection_Duration, 0)
        self.assertEqual(rpt.parameters.Include_Pregnancies, 1)

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = ReportMalariaFiltered(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "ReportMalariaFiltered")


@pytest.mark.unit
class TestReportMalariaFilteredIntraHost(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportMalariaFilteredIntraHost(reporters_object=r)
        self.assertEqual(
            rpt.parameters["class"], "ReportMalariaFilteredIntraHost"
        )
        self.assertEqual(rpt.parameters.Include_30Day_Avg_Infection_Duration, 1)
        self.assertEqual(rpt.parameters.Include_Pregnancies, 0)

    def test_custom_params(self):
        r = _reporters()
        rpt = ReportMalariaFilteredIntraHost(
            reporters_object=r,
            has_ip=["Access:Low"],
            has_interventions=["Ivermectin"],
            include_30day_avg_infection_duration=False,
            include_pregnancies=True,
        )
        self.assertEqual(rpt.parameters.Has_IP, ["Access:Low"])
        self.assertEqual(rpt.parameters.Has_Interventions, ["Ivermectin"])
        self.assertEqual(rpt.parameters.Include_30Day_Avg_Infection_Duration, 0)
        self.assertEqual(rpt.parameters.Include_Pregnancies, 1)

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = ReportMalariaFilteredIntraHost(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "ReportMalariaFilteredIntraHost")


@pytest.mark.unit
class TestMalariaImmunityReport(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = MalariaImmunityReport(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "MalariaImmunityReport")
        self.assertEqual(rpt.parameters.Reporting_Interval, 1000000)
        self.assertEqual(rpt.parameters.Max_Number_Reports, 1000000)
        self.assertEqual(rpt.parameters.Pretty_Format, 0)

    def test_custom_params(self):
        r = _reporters()
        rpt = MalariaImmunityReport(
            reporters_object=r,
            reporting_interval=365,
            age_bins=[5, 15, 50, 125],
            max_number_reports=12,
            pretty_format=True,
        )
        self.assertEqual(rpt.parameters.Reporting_Interval, 365)
        self.assertEqual(rpt.parameters.Age_Bins, [5, 15, 50, 125])
        self.assertEqual(rpt.parameters.Max_Number_Reports, 12)
        self.assertEqual(rpt.parameters.Pretty_Format, 1)

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = MalariaImmunityReport(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "MalariaImmunityReport")

    def test_blocked_min_age(self):
        r = _reporters()
        rpt = MalariaImmunityReport(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_min_age_years(5.0, "MalariaImmunityReport")


@pytest.mark.unit
class TestReportVectorGenetics(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportVectorGenetics(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "ReportVectorGenetics")
        self.assertEqual(rpt.parameters.Gender, VectorGender.VECTOR_FEMALE)
        self.assertEqual(rpt.parameters.Include_Vector_State_Columns, 1)
        self.assertEqual(rpt.parameters.Include_Death_By_State_Columns, 0)
        self.assertEqual(rpt.parameters.Combine_Similar_Genomes, 0)
        self.assertEqual(
            rpt.parameters.Stratify_By, VectorGeneticsStratification.GENOME
        )

    def test_species_and_death_columns(self):
        r = _reporters()
        rpt = ReportVectorGenetics(
            reporters_object=r,
            species="gambiae",
            include_death_state_columns=True,
            include_vector_state_columns=False,
        )
        self.assertEqual(rpt.parameters.Species, "gambiae")
        self.assertEqual(rpt.parameters.Include_Death_By_State_Columns, 1)
        self.assertEqual(rpt.parameters.Include_Vector_State_Columns, 0)

    def test_specific_genome_stratification(self):
        r = _reporters()
        combos = [
            {"Allele_Combination": [["X", "X"], ["a0", "*"]]},
        ]
        rpt = ReportVectorGenetics(
            reporters_object=r,
            stratify_by=VectorGeneticsStratification.SPECIFIC_GENOME,
            specific_genome_combinations_for_stratification=combos,
        )
        self.assertEqual(
            rpt.parameters.Stratify_By,
            VectorGeneticsStratification.SPECIFIC_GENOME,
        )
        self.assertEqual(
            rpt.parameters.Specific_Genome_Combinations_For_Stratification,
            combos,
        )

    def test_specific_genome_requires_combos(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportVectorGenetics(
                reporters_object=r,
                stratify_by=VectorGeneticsStratification.SPECIFIC_GENOME,
            )

    def test_combos_without_specific_genome_warns(self):
        r = _reporters()
        with self.assertRaises(UserWarning):
            ReportVectorGenetics(
                reporters_object=r,
                specific_genome_combinations_for_stratification=[
                    {"Allele_Combination": [["X", "X"]]}
                ],
            )

    def test_allele_stratification(self):
        r = _reporters()
        combos = [["a0", "b0"], ["a1", "b1"]]
        rpt = ReportVectorGenetics(
            reporters_object=r,
            stratify_by=VectorGeneticsStratification.ALLELE,
            allele_combinations_for_stratification=combos,
        )
        self.assertEqual(
            rpt.parameters.Allele_Combinations_For_Stratification, combos
        )

    def test_allele_requires_combos(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportVectorGenetics(
                reporters_object=r,
                stratify_by=VectorGeneticsStratification.ALLELE,
            )

    def test_allele_freq_stratification(self):
        r = _reporters()
        alleles = ["a0", "a1", "b0"]
        rpt = ReportVectorGenetics(
            reporters_object=r,
            stratify_by=VectorGeneticsStratification.ALLELE_FREQ,
            alleles_for_stratification=alleles,
        )
        self.assertEqual(rpt.parameters.Alleles_For_Stratification, alleles)

    def test_allele_freq_requires_alleles(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportVectorGenetics(
                reporters_object=r,
                stratify_by=VectorGeneticsStratification.ALLELE_FREQ,
            )

    def test_combine_similar_only_with_genome(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportVectorGenetics(
                reporters_object=r,
                combine_similar_genomes=True,
                stratify_by=VectorGeneticsStratification.ALLELE,
                allele_combinations_for_stratification=[["a0"]],
            )

    def test_parasite_barcodes_switches_class(self):
        r = _reporters()
        rpt = ReportVectorGenetics(
            reporters_object=r, parasite_barcodes=["AABBCCDD"]
        )
        self.assertEqual(
            rpt.parameters["class"], "ReportVectorGeneticsMalariaGenetics"
        )
        self.assertEqual(rpt.parameters.Parasite_Barcodes, ["AABBCCDD"])

    def test_gender_string_accepted(self):
        r = _reporters()
        rpt = ReportVectorGenetics(
            reporters_object=r, gender="VECTOR_MALE"
        )
        self.assertEqual(rpt.parameters.Gender, VectorGender.VECTOR_MALE)

    def test_invalid_gender(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportVectorGenetics(reporters_object=r, gender="INVALID")

    def test_invalid_stratify_by(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportVectorGenetics(reporters_object=r, stratify_by="INVALID")

    def test_alias(self):
        self.assertIs(
            ReportVectorGeneticsMalariaGenetics, ReportVectorGenetics
        )

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = ReportVectorGenetics(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "ReportVectorGenetics")

    def test_blocked_min_age(self):
        r = _reporters()
        rpt = ReportVectorGenetics(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_min_age_years(5.0, "ReportVectorGenetics")

    def test_blocked_must_have_ip(self):
        r = _reporters()
        rpt = ReportVectorGenetics(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_must_have_ip_key_value("Risk:High", "ReportVectorGenetics")


@pytest.mark.unit
class TestReportVectorStats(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportVectorStats(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "ReportVectorStats")
        self.assertEqual(rpt.parameters.Include_Wolbachia_Columns, 0)
        self.assertEqual(rpt.parameters.Include_Gestation_Columns, 0)
        self.assertEqual(rpt.parameters.Include_Microsporidia_Columns, 0)
        self.assertEqual(rpt.parameters.Include_Death_By_State_Columns, 0)
        self.assertEqual(rpt.parameters.Stratify_By_Species, 0)

    def test_all_columns(self):
        r = _reporters()
        rpt = ReportVectorStats(
            reporters_object=r,
            species_list=["gambiae", "funestus"],
            include_wolbachia_columns=True,
            include_gestation_columns=True,
            include_microsporidia_columns=True,
            include_death_state_columns=True,
            stratify_by_species=True,
        )
        self.assertEqual(rpt.parameters.Species_List, ["gambiae", "funestus"])
        self.assertEqual(rpt.parameters.Include_Wolbachia_Columns, 1)
        self.assertEqual(rpt.parameters.Include_Gestation_Columns, 1)
        self.assertEqual(rpt.parameters.Include_Microsporidia_Columns, 1)
        self.assertEqual(rpt.parameters.Include_Death_By_State_Columns, 1)
        self.assertEqual(rpt.parameters.Stratify_By_Species, 1)

    def test_barcodes_switches_class(self):
        r = _reporters()
        rpt = ReportVectorStats(
            reporters_object=r, barcodes=["AAAAAA", "AA**AA"]
        )
        self.assertEqual(
            rpt.parameters["class"], "ReportVectorStatsMalariaGenetics"
        )
        self.assertEqual(rpt.parameters.Barcodes, ["AAAAAA", "AA**AA"])

    def test_alias(self):
        self.assertIs(ReportVectorStatsMalariaGenetics, ReportVectorStats)


@pytest.mark.unit
class TestReportVectorMigration(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportVectorMigration(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "ReportVectorMigration")
        self.assertEqual(rpt.parameters.Include_Genome_Data, 0)

    def test_custom_params(self):
        r = _reporters()
        rpt = ReportVectorMigration(
            reporters_object=r,
            include_genome_data=True,
            species_list=["gambiae"],
            must_be_from_node=[1, 2],
            must_be_to_node=[3],
            must_be_in_state=[
                VectorStateEnum.STATE_ADULT,
                VectorStateEnum.STATE_INFECTIOUS,
            ],
        )
        self.assertEqual(rpt.parameters.Include_Genome_Data, 1)
        self.assertEqual(rpt.parameters.Species_List, ["gambiae"])
        self.assertEqual(rpt.parameters.Must_Be_From_Node, [1, 2])
        self.assertEqual(rpt.parameters.Must_Be_To_Node, [3])
        self.assertEqual(len(rpt.parameters.Must_Be_In_State), 2)

    def test_state_string_accepted(self):
        r = _reporters()
        rpt = ReportVectorMigration(
            reporters_object=r,
            must_be_in_state=["STATE_MALE"],
        )
        self.assertEqual(len(rpt.parameters.Must_Be_In_State), 1)

    def test_invalid_state(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportVectorMigration(
                reporters_object=r,
                must_be_in_state=["INVALID_STATE"],
            )

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = ReportVectorMigration(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "ReportVectorMigration")

    def test_blocked_node_ids(self):
        r = _reporters()
        rpt = ReportVectorMigration(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_node_ids([1], "ReportVectorMigration")

    def test_blocked_must_have_ip(self):
        r = _reporters()
        rpt = ReportVectorMigration(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_must_have_ip_key_value("Risk:High", "ReportVectorMigration")


@pytest.mark.unit
class TestVectorHabitatReport(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = VectorHabitatReport(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "VectorHabitatReport")


@pytest.mark.unit
class TestReportMicrosporidia(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportMicrosporidia(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "ReportMicrosporidia")


@pytest.mark.unit
class TestReportInfectionStatsMalaria(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportInfectionStatsMalaria(reporters_object=r)
        self.assertEqual(
            rpt.parameters["class"], "ReportInfectionStatsMalaria"
        )
        self.assertEqual(rpt.parameters.Reporting_Interval, 1)
        self.assertEqual(rpt.parameters.Include_Column_Gametocyte, 0)
        self.assertEqual(rpt.parameters.Include_Column_Hepatocyte, 0)
        self.assertEqual(rpt.parameters.Include_Column_IRBC, 0)

    def test_gametocyte_column(self):
        r = _reporters()
        rpt = ReportInfectionStatsMalaria(
            reporters_object=r,
            include_column_gametocyte=True,
            include_data_threshold_gametocytes=100.0,
        )
        self.assertEqual(rpt.parameters.Include_Column_Gametocyte, 1)
        self.assertEqual(
            rpt.parameters.Include_Data_Threshold_Gametocytes, 100.0
        )

    def test_hepatocyte_column(self):
        r = _reporters()
        rpt = ReportInfectionStatsMalaria(
            reporters_object=r,
            include_column_hepatocyte=True,
            include_data_threshold_hepatocytes=50.0,
        )
        self.assertEqual(rpt.parameters.Include_Column_Hepatocyte, 1)
        self.assertEqual(
            rpt.parameters.Include_Data_Threshold_Hepatocytes, 50.0
        )

    def test_irbc_column(self):
        r = _reporters()
        rpt = ReportInfectionStatsMalaria(
            reporters_object=r,
            include_column_irbc=True,
            include_data_threshold_irbc=200.0,
        )
        self.assertEqual(rpt.parameters.Include_Column_IRBC, 1)
        self.assertEqual(rpt.parameters.Include_Data_Threshold_IRBC, 200.0)

    def test_gametocyte_requires_threshold(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportInfectionStatsMalaria(
                reporters_object=r, include_column_gametocyte=True
            )

    def test_hepatocyte_requires_threshold(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportInfectionStatsMalaria(
                reporters_object=r, include_column_hepatocyte=True
            )

    def test_irbc_requires_threshold(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportInfectionStatsMalaria(
                reporters_object=r, include_column_irbc=True
            )

    def test_threshold_without_column_warns_gametocyte(self):
        r = _reporters()
        with self.assertRaises(UserWarning):
            ReportInfectionStatsMalaria(
                reporters_object=r,
                include_data_threshold_gametocytes=100.0,
            )

    def test_threshold_without_column_warns_hepatocyte(self):
        r = _reporters()
        with self.assertRaises(UserWarning):
            ReportInfectionStatsMalaria(
                reporters_object=r,
                include_data_threshold_hepatocytes=50.0,
            )

    def test_threshold_without_column_warns_irbc(self):
        r = _reporters()
        with self.assertRaises(UserWarning):
            ReportInfectionStatsMalaria(
                reporters_object=r,
                include_data_threshold_irbc=200.0,
            )

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = ReportInfectionStatsMalaria(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "ReportInfectionStatsMalaria")

    def test_blocked_node_ids(self):
        r = _reporters()
        rpt = ReportInfectionStatsMalaria(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_node_ids([1], "ReportInfectionStatsMalaria")

    def test_blocked_min_age(self):
        r = _reporters()
        rpt = ReportInfectionStatsMalaria(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_min_age_years(5.0, "ReportInfectionStatsMalaria")

    def test_blocked_filename_suffix(self):
        r = _reporters()
        rpt = ReportInfectionStatsMalaria(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_filename_suffix("_test", "ReportInfectionStatsMalaria")


@pytest.mark.unit
class TestReportAntibodies(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportAntibodies(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "ReportAntibodies")
        self.assertEqual(rpt.parameters.Reporting_Interval, 1)
        self.assertEqual(rpt.parameters.Contain_Capacity_Data, 0)
        self.assertEqual(rpt.parameters.Infected_Only, 0)

    def test_custom_params(self):
        r = _reporters()
        rpt = ReportAntibodies(
            reporters_object=r,
            reporting_interval=30,
            contain_capacity_data=True,
            infected_only=True,
        )
        self.assertEqual(rpt.parameters.Reporting_Interval, 30)
        self.assertEqual(rpt.parameters.Contain_Capacity_Data, 1)
        self.assertEqual(rpt.parameters.Infected_Only, 1)

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = ReportAntibodies(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "ReportAntibodies")


@pytest.mark.unit
class TestReportFpgOutput(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportFpgOutput(reporters_object=r)
        self.assertEqual(
            rpt.parameters["class"], "ReportFpgOutputForObservationalModel"
        )
        self.assertEqual(rpt.parameters.Sampling_Period, 1)
        self.assertEqual(rpt.parameters.Minimum_Parasite_Density, 1)
        self.assertEqual(rpt.parameters.Include_Genome_IDs, 0)

    def test_custom_params(self):
        r = _reporters()
        rpt = ReportFpgOutput(
            reporters_object=r,
            sampling_period=30.4166667,
            minimum_parasite_density=10.0,
            include_genome_ids=True,
        )
        self.assertAlmostEqual(rpt.parameters.Sampling_Period, 30.4166667)
        self.assertEqual(rpt.parameters.Minimum_Parasite_Density, 10.0)
        self.assertEqual(rpt.parameters.Include_Genome_IDs, 1)

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = ReportFpgOutput(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "ReportFpgOutputForObservationalModel")

    def test_blocked_filename_suffix(self):
        r = _reporters()
        rpt = ReportFpgOutput(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_filename_suffix(
                "_test", "ReportFpgOutputForObservationalModel"
            )


@pytest.mark.unit
class TestReportFpgNewInfections(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportFpgNewInfections(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "ReportFpgNewInfections")
        self.assertEqual(rpt.parameters.Report_Crossover_Data_Instead, 0)

    def test_crossover(self):
        r = _reporters()
        rpt = ReportFpgNewInfections(
            reporters_object=r, report_crossover_data_instead=True
        )
        self.assertEqual(rpt.parameters.Report_Crossover_Data_Instead, 1)

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = ReportFpgNewInfections(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "ReportFpgNewInfections")


@pytest.mark.unit
class TestSpatialReportMalariaFiltered(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = SpatialReportMalariaFiltered(reporters_object=r)
        self.assertEqual(
            rpt.parameters["class"], "SpatialReportMalariaFiltered"
        )
        self.assertEqual(rpt.parameters.Reporting_Interval, 1)

    def test_channels(self):
        r = _reporters()
        rpt = SpatialReportMalariaFiltered(
            reporters_object=r,
            spatial_output_channels=[
                SpatialOutputChannel.PREVALENCE,
                SpatialOutputChannel.NEW_INFECTIONS,
            ],
            reporting_interval=7,
        )
        self.assertEqual(rpt.parameters.Reporting_Interval, 7)
        self.assertEqual(len(rpt.parameters.Spatial_Output_Channels), 2)

    def test_channel_string_accepted(self):
        r = _reporters()
        rpt = SpatialReportMalariaFiltered(
            reporters_object=r,
            spatial_output_channels=["Prevalence"],
        )
        self.assertEqual(len(rpt.parameters.Spatial_Output_Channels), 1)

    def test_invalid_channel(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            SpatialReportMalariaFiltered(
                reporters_object=r,
                spatial_output_channels=["INVALID_CHANNEL"],
            )

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = SpatialReportMalariaFiltered(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "SpatialReportMalariaFiltered")


@pytest.mark.unit
class TestReportInterventionPopAvg(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportInterventionPopAvg(reporters_object=r)
        self.assertEqual(
            rpt.parameters["class"], "ReportInterventionPopAvg"
        )

    def test_with_filter(self):
        r = _reporters()
        rf = ReportFilter(start_day=10, end_day=365)
        rpt = ReportInterventionPopAvg(reporters_object=r, report_filter=rf)
        self.assertEqual(rpt.parameters.Start_Day, 10)
        self.assertEqual(rpt.parameters.End_Day, 365)

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = ReportInterventionPopAvg(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "ReportInterventionPopAvg")


@pytest.mark.unit
class TestMalariaSurveyAnalyzer(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = MalariaSurveyAnalyzer(reporters_object=r)
        self.assertEqual(
            rpt.parameters["class"], "MalariaSurveyJSONAnalyzer"
        )
        self.assertEqual(rpt.parameters.Reporting_Interval, 365)
        self.assertEqual(rpt.parameters.Max_Number_Reports, 1000000)
        self.assertEqual(rpt.parameters.Pretty_Format, 0)

    def test_custom_params(self):
        r = _reporters()
        rpt = MalariaSurveyAnalyzer(
            reporters_object=r,
            event_trigger_list=["Received_Treatment", "NewClinicalCase"],
            reporting_interval=30,
            max_number_reports=12,
            pretty_format=True,
            ip_key_to_collect="Risk",
        )
        self.assertEqual(
            rpt.parameters.Event_Trigger_List,
            ["Received_Treatment", "NewClinicalCase"],
        )
        self.assertEqual(rpt.parameters.Reporting_Interval, 30)
        self.assertEqual(rpt.parameters.Max_Number_Reports, 12)
        self.assertEqual(rpt.parameters.Pretty_Format, 1)
        self.assertEqual(rpt.parameters.IP_Key_To_Collect, "Risk")

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = MalariaSurveyAnalyzer(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "MalariaSurveyJSONAnalyzer")


@pytest.mark.unit
class TestReportSimpleMalariaTransmission(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportSimpleMalariaTransmission(reporters_object=r)
        self.assertEqual(
            rpt.parameters["class"], "ReportSimpleMalariaTransmission"
        )
        self.assertEqual(
            rpt.parameters.Include_Human_To_Vector_Transmission, 0
        )

    def test_include_h2v(self):
        r = _reporters()
        rpt = ReportSimpleMalariaTransmission(
            reporters_object=r, include_human_to_vector_transmission=True
        )
        self.assertEqual(
            rpt.parameters.Include_Human_To_Vector_Transmission, 1
        )

    def test_blocked_start_year(self):
        r = _reporters()
        rpt = ReportSimpleMalariaTransmission(reporters_object=r)
        with self.assertRaises(ValueError):
            rpt._set_start_year(2000.0, "ReportSimpleMalariaTransmission")


@pytest.mark.unit
class TestSqlReportMalaria(unittest.TestCase):

    def test_default_malaria(self):
        r = _reporters()
        rpt = SqlReportMalaria(reporters_object=r)
        self.assertEqual(rpt.parameters["class"], "SqlReportMalaria")
        self.assertEqual(rpt.parameters.Include_Health_Table, 1)
        self.assertEqual(rpt.parameters.Include_Individual_Properties, 0)
        self.assertEqual(rpt.parameters.Include_Infection_Data_Table, 1)

    def test_genetics(self):
        r = _reporters()
        rpt = SqlReportMalaria(
            reporters_object=r, include_malaria_genetics=True
        )
        self.assertEqual(
            rpt.parameters["class"], "SqlReportMalariaGenetics"
        )

    def test_base_sql(self):
        r = _reporters()
        rpt = SqlReportMalaria(
            reporters_object=r, include_malaria=False
        )
        self.assertEqual(rpt.parameters["class"], "SqlReport")

    def test_drug_status_requires_malaria(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            SqlReportMalaria(
                reporters_object=r,
                include_malaria=False,
                include_drug_status_table=True,
            )

    def test_drug_status_with_malaria(self):
        r = _reporters()
        rpt = SqlReportMalaria(
            reporters_object=r,
            include_malaria=True,
            include_drug_status_table=True,
        )
        self.assertEqual(rpt.parameters.Include_Drug_Status_Table, 1)

    def test_drug_status_with_genetics(self):
        r = _reporters()
        rpt = SqlReportMalaria(
            reporters_object=r,
            include_malaria_genetics=True,
            include_drug_status_table=True,
        )
        self.assertEqual(
            rpt.parameters["class"], "SqlReportMalariaGenetics"
        )
        self.assertEqual(rpt.parameters.Include_Drug_Status_Table, 1)

    def test_alias(self):
        self.assertIs(SqlReportMalariaGenetics, SqlReportMalaria)


@pytest.mark.unit
class TestReportNodeDemographicsMalaria(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportNodeDemographicsMalaria(reporters_object=r)
        self.assertEqual(
            rpt.parameters["class"], "ReportNodeDemographicsMalaria"
        )
        self.assertEqual(rpt.parameters.Age_Bins, [])
        self.assertEqual(rpt.parameters.Stratify_By_Gender, 1)
        self.assertEqual(
            rpt.parameters.Stratify_By_Has_Clinical_Symptoms, 0
        )

    def test_custom_params(self):
        r = _reporters()
        rpt = ReportNodeDemographicsMalaria(
            reporters_object=r,
            age_bins=[5, 15, 50, 100],
            ip_key_to_collect="Risk",
            stratify_by_gender=False,
            stratify_by_has_clinical_symptoms=True,
        )
        self.assertEqual(rpt.parameters.Age_Bins, [5, 15, 50, 100])
        self.assertEqual(rpt.parameters.IP_Key_To_Collect, "Risk")
        self.assertEqual(rpt.parameters.Stratify_By_Gender, 0)
        self.assertEqual(
            rpt.parameters.Stratify_By_Has_Clinical_Symptoms, 1
        )

    def test_invalid_age_bins(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportNodeDemographicsMalaria(
                reporters_object=r, age_bins=[50, 15, 5]
            )


@pytest.mark.unit
class TestReportNodeDemographicsMalariaGenetics(unittest.TestCase):

    def test_default(self):
        r = _reporters()
        rpt = ReportNodeDemographicsMalariaGenetics(reporters_object=r)
        self.assertEqual(
            rpt.parameters["class"],
            "ReportNodeDemographicsMalariaGenetics",
        )
        self.assertEqual(rpt.parameters.Age_Bins, [])
        self.assertEqual(rpt.parameters.Stratify_By_Gender, 1)
        self.assertEqual(rpt.parameters.Include_Identity_By_XXX, 0)

    def test_custom_params(self):
        r = _reporters()
        rpt = ReportNodeDemographicsMalariaGenetics(
            reporters_object=r,
            age_bins=[5, 15, 100],
            ip_key_to_collect="Risk",
            stratify_by_gender=False,
            barcodes=["AABB", "CC**"],
            drug_resistant_and_hrp_statistic_type=DrugResistantStatisticType.NUM_INFECTIONS,
            drug_resistant_strings=["AT"],
            hrp_strings=["C"],
            include_identity_by_xxx=True,
        )
        self.assertEqual(rpt.parameters.Age_Bins, [5, 15, 100])
        self.assertEqual(rpt.parameters.IP_Key_To_Collect, "Risk")
        self.assertEqual(rpt.parameters.Stratify_By_Gender, 0)
        self.assertEqual(rpt.parameters.Barcodes, ["AABB", "CC**"])
        self.assertEqual(
            rpt.parameters.Drug_Resistant_And_HRP_Statistic_Type,
            str(DrugResistantStatisticType.NUM_INFECTIONS),
        )
        self.assertEqual(rpt.parameters.Drug_Resistant_Strings, ["AT"])
        self.assertEqual(rpt.parameters.HRP_Strings, ["C"])
        self.assertEqual(rpt.parameters.Include_Identity_By_XXX, 1)

    def test_statistic_type_string(self):
        r = _reporters()
        rpt = ReportNodeDemographicsMalariaGenetics(
            reporters_object=r,
            drug_resistant_and_hrp_statistic_type="NUM_INFECTIONS",
        )
        self.assertEqual(
            rpt.parameters.Drug_Resistant_And_HRP_Statistic_Type,
            str(DrugResistantStatisticType.NUM_INFECTIONS),
        )

    def test_invalid_statistic_type(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportNodeDemographicsMalariaGenetics(
                reporters_object=r,
                drug_resistant_and_hrp_statistic_type="INVALID",
            )

    def test_invalid_age_bins(self):
        r = _reporters()
        with self.assertRaises(ValueError):
            ReportNodeDemographicsMalariaGenetics(
                reporters_object=r, age_bins=[100, 50, 5]
            )


if __name__ == "__main__":
    unittest.main()
