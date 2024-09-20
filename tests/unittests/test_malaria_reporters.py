import unittest
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from emodpy_malaria.reporters.builtin import *
import schema_path_file


class TestMalariaReport(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_reporter = None
        self.p_dict = None

    # region vector stats
    def test_vector_stats_default(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_report_vector_stats(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Stratify_By_Species'], 0)
        self.assertEqual(self.p_dict['Species_List'], [])
        self.assertEqual(self.p_dict['Include_Wolbachia_Columns'], 0)
        self.assertEqual(self.p_dict['Include_Gestation_Columns'], 0)
        pass

    def test_vector_stats_custom(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_report_vector_stats(None, schema_path_file,
                                                    include_gestation=1,
                                                    include_wolbachia=1,
                                                    species_list=["gambiae", "SillySkeeter"],
                                                    stratify_by_species=1)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Stratify_By_Species'], 1)
        self.assertEqual(self.p_dict['Species_List'], ["gambiae", "SillySkeeter"])
        self.assertEqual(self.p_dict['Include_Wolbachia_Columns'], 1)
        self.assertEqual(self.p_dict['Include_Gestation_Columns'], 1)
        pass

    # endregion

    # region ReportVectorGenetics
    def test_vector_genetics_default(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_report_vector_genetics(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Duration_Days'], 365000)
        self.assertEqual(self.p_dict['Gender'], "VECTOR_FEMALE")
        self.assertEqual(self.p_dict['Include_Vector_State_Columns'], 1)
        self.assertEqual(self.p_dict['Report_Description'], "")
        self.assertEqual(self.p_dict['Start_Day'], 0)
        self.assertEqual(self.p_dict['Stratify_By'], "GENOME")
        self.assertEqual(self.p_dict['Combine_Similar_Genomes'], 0)

    def test_vg_custom_genome_stratification(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_report_vector_genetics(None, schema_path_file,
                                                       combine_similar_genomes=1,
                                                       stratify_by="GENOME")
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Combine_Similar_Genomes'], 1)
        self.assertEqual(self.p_dict['Stratify_By'], "GENOME")

    def test_vg_custom_specific_genome_stratification(self):
        self.tmp_reporter = add_report_vector_genetics(None, schema_path_file,
                                                       duration_days=345,
                                                       gender="VECTOR_MALE",
                                                       include_vector_state=0,
                                                       report_description="test_report",
                                                       species="Silly_Skeeter",
                                                       start_day=1234,
                                                       stratify_by="SPECIFIC_GENOME",
                                                       specific_genome_combinations_for_stratification=[["X"], ["*"]])
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Duration_Days'], 345)
        self.assertEqual(self.p_dict['Gender'], "VECTOR_MALE")
        self.assertEqual(self.p_dict['Include_Vector_State_Columns'], 0)
        self.assertEqual(self.p_dict['Report_Description'], "test_report")
        self.assertEqual(self.p_dict['Species'], "Silly_Skeeter")
        self.assertEqual(self.p_dict['Start_Day'], 1234)
        self.assertEqual(self.p_dict['Specific_Genome_Combinations_For_Stratification'], [["X"], ["*"]])
        self.assertEqual(self.p_dict['Stratify_By'], "SPECIFIC_GENOME")  # because of previous

    def test_vg_custom_specific_genome_stratification_no_combination(self):
        self.tmp_reporter = add_report_vector_genetics(None, schema_path_file,
                                                       stratify_by="ALLELE_FREQ",
                                                       duration_days=12345,
                                                       species="Silly_Skeeter",
                                                       gender="VECTOR_MALE",
                                                       include_vector_state=0,
                                                       alleles_for_stratification=["a0", "a1", "b0", "b1"],
                                                       report_description="Does some stuff",
                                                       )
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Duration_Days'], 12345)
        self.assertEqual(self.p_dict['Gender'], "VECTOR_MALE")
        self.assertEqual(self.p_dict['Include_Vector_State_Columns'], 0)
        self.assertEqual(self.p_dict['Report_Description'], "Does some stuff")
        self.assertEqual(self.p_dict['Species'], "Silly_Skeeter")
        self.assertEqual(self.p_dict['Alleles_For_Stratification'], ["a0", "a1", "b0", "b1"])
        self.assertEqual(self.p_dict['Stratify_By'], "ALLELE_FREQ")  # because of previous

    def test_vg_custom_allele_stratification(self):
        self.tmp_reporter = add_report_vector_genetics(None, schema_path_file,
                                                       gender="VECTOR_BOTH_GENDERS",
                                                       stratify_by="ALLELE",
                                                       allele_combinations_for_stratification=[["X"], ["Y"]]
                                                       )
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Gender'], "VECTOR_BOTH_GENDERS")
        self.assertEqual(self.p_dict['Allele_Combinations_For_Stratification'], [["X"], ["Y"]])
        self.assertEqual(self.p_dict["Stratify_By"], "ALLELE")
        pass

    def test_vg_custom_allele_frequency_stratification(self):
        self.tmp_reporter = add_report_vector_genetics(None, schema_path_file,
                                                       alleles_for_stratification=["a0", "a1", "b0", "b1"],
                                                       stratify_by="ALLELE_FREQ")
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Alleles_For_Stratification'], ["a0", "a1", "b0", "b1"])
        self.assertEqual(self.p_dict['Stratify_By'], "ALLELE_FREQ")
        pass

    # endregion

    # region malaria patient json report
    def test_malaria_patient_json_report_default(self):
        self.tmp_reporter = add_malaria_patient_json_report(None, schema_path_file)
        self.assertIsNotNone(self.tmp_reporter)
        pass

    # endregion

    # region MalariaSummaryReport
    def test_malaria_summary_report_default(self):
        self.tmp_reporter = add_malaria_summary_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'], "NodeSetAll")
        self.assertEqual(self.p_dict['Duration_Days'], 365000)
        self.assertEqual(self.p_dict['Age_Bins'], [])
        self.assertEqual(self.p_dict['Individual_Property_Filter'], "")
        self.assertEqual(self.p_dict['Infectiousness_Bins'], [])
        self.assertEqual(self.p_dict['Max_Number_Reports'], 100)
        self.assertEqual(self.p_dict['Parasitemia_Bins'], [])
        self.assertEqual(self.p_dict['Pretty_Format'], 0)
        self.assertEqual(self.p_dict['Report_Description'], "")
        self.assertEqual(self.p_dict['Reporting_Interval'], 1)
        self.assertEqual(self.p_dict['Start_Day'], 0)
        pass

    def test_malaria_summary_report_nodelist(self):
        node_ids = [1, 2, 3, 5, 8, 13]
        self.tmp_reporter = add_malaria_summary_report(None, schema_path_file,
                                                       nodes=node_ids)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Nodeset_Config']['Node_List'], node_ids)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'], "NodeSetNodeList")

    def test_malaria_summary_report_custom1(self):
        self.tmp_reporter = add_malaria_summary_report(None, schema_path_file,
                                                       age_bins=[1, 2, 5, 15, 25, 45, 65],
                                                       duration_days=1234)
        self.p_dict = self.tmp_reporter.parameters
        self.assertEqual(self.p_dict['Age_Bins'], [1, 2, 5, 15, 25, 45, 65])
        self.assertEqual(self.p_dict['Duration_Days'], 1234)

    def test_malaria_summary_report_custom2(self):
        self.tmp_reporter = add_malaria_summary_report(None, schema_path_file,
                                                       individual_property_filter="FavoriteCola:RC",
                                                       infectiousness_bins=[-15, -5, 0, 3, 5, 8],
                                                       max_number_reports=63,
                                                       parasitemia_bins=[100, 500, 1500, 2345])
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Individual_Property_Filter'], "FavoriteCola:RC")
        self.assertEqual(self.p_dict['Infectiousness_Bins'], [-15, -5, 0, 3, 5, 8])
        self.assertEqual(self.p_dict['Max_Number_Reports'], 63)
        self.assertEqual(self.p_dict['Parasitemia_Bins'], [100, 500, 1500, 2345])
        pass

    def test_malaria_summary_report_custom3(self):
        self.tmp_reporter = add_malaria_summary_report(None, schema_path_file,
                                                       pretty_format=1,
                                                       report_description="A pretty good report for pretty good people",
                                                       reporting_interval=15.5,
                                                       start_day=12)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Pretty_Format'], 1)
        self.assertEqual(self.p_dict['Report_Description'], "A pretty good report for pretty good people")
        self.assertEqual(self.p_dict['Reporting_Interval'], 15.5)
        self.assertEqual(self.p_dict['Start_Day'], 12)
        pass

    # endregion

    # MalariaSqlReport
    def test_malaria_sql_report_default(self):
        self.tmp_reporter = add_malaria_sql_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], 0)
        self.assertEqual(self.p_dict['End_Day'], 365000)
        self.assertEqual(self.p_dict['Include_Infection_Data_Table'], 1)
        self.assertEqual(self.p_dict['Include_Health_Table'], 1)

    def test_malaria_sql_report_custom(self):
        end_day = 77
        start_day = 7
        false = 0
        self.tmp_reporter = add_malaria_sql_report(None, schema_path_file,
                                                   end_day=end_day,
                                                   start_day=start_day,
                                                   include_infection_table=false,
                                                   include_health_table=false)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)
        self.assertEqual(self.p_dict['Include_Infection_Data_Table'], false)
        self.assertEqual(self.p_dict['Include_Health_Table'], false)

    # end region

    # start region ReportEventCounter
    def test_report_counter_default(self):
        self.tmp_reporter = add_report_event_counter(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'], "NodeSetAll")
        self.assertEqual(self.p_dict['Duration_Days'], 365000)
        self.assertEqual(self.p_dict['Event_Trigger_List'], [])
        self.assertEqual(self.p_dict['Start_Day'], 0)
        self.assertEqual(self.p_dict['Report_Description'], "")

    def test_report_counter_custom(self):
        duration = 17
        trigger_list = ["STINewInfection", "ExitedRelationship"]
        start_day = 5
        self.tmp_reporter = add_report_event_counter(None, schema_path_file,
                                                     start_day=start_day,
                                                     duration_days=duration,
                                                     event_trigger_list=trigger_list)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['Duration_Days'], duration)
        self.assertEqual(self.p_dict['Event_Trigger_List'], trigger_list)

    # end region

    # region ReportSimpleMalariaTransimissionJSON
    def test_malaria_transmission_report_default(self):
        self.tmp_reporter = add_malaria_transmission_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], 0)
        self.assertEqual(self.p_dict['Duration_Days'], 365000)
        self.assertEqual(self.p_dict['Pretty_Format'], 0)
        self.assertEqual(self.p_dict['Report_Description'], "")
        self.assertEqual(self.p_dict['Nodeset_Config']['class'], "NodeSetAll")

    def test_malaria_transmission_report_custom(self):
        duration = 17
        report_description = "Testing"
        start_day = 5
        nodes = [2342, 32, 10]
        self.tmp_reporter = add_malaria_transmission_report(None, schema_path_file,
                                                            start_day=start_day,
                                                            duration_days=duration,
                                                            nodes=nodes, pretty_format=1,
                                                            report_description=report_description)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['Duration_Days'], duration)
        self.assertEqual(self.p_dict['Pretty_Format'], 1)
        self.assertEqual(self.p_dict['Report_Description'], report_description)
        self.assertEqual(self.p_dict['Nodeset_Config']['Node_List'], nodes)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'], "NodeSetNodeList")

    # end region

    # region VectorHabitatReport
    def test_add_vector_habitat_report(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_malaria_transmission_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)

    # end region

    # MalariaImmunityReport
    def test_malaria_immunity_report_default(self):
        start_day = 0
        duration_days = 365000
        reporting_interval = 1
        max_number_reports = 365000
        age_bins = []
        pretty_format = 0
        report_description = ""
        self.tmp_reporter = add_malaria_immunity_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['Duration_Days'], duration_days)
        self.assertEqual(self.p_dict['Reporting_Interval'], reporting_interval)
        self.assertEqual(self.p_dict['Max_Number_Reports'], max_number_reports)
        self.assertEqual(self.p_dict['Age_Bins'], age_bins)
        self.assertEqual(self.p_dict['Pretty_Format'], pretty_format)
        self.assertEqual(self.p_dict['Report_Description'], report_description)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'], "NodeSetAll")

    def test_malaria_immunity_report_custom(self):
        start_day = 23
        duration_days = 58
        reporting_interval = 5
        max_number_reports = 7
        nodes = [23, 2135, 9]
        age_bins = [6, 20, 45, 90]
        pretty_format = 1
        report_description = "Testing_Test"
        self.tmp_reporter = add_malaria_immunity_report(None, schema_path_file,
                                                        start_day=start_day,
                                                        duration_days=duration_days,
                                                        reporting_interval=reporting_interval,
                                                        max_number_reports=max_number_reports,
                                                        nodes=nodes,
                                                        age_bins=age_bins,
                                                        pretty_format=pretty_format,
                                                        report_description=report_description)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['Duration_Days'], duration_days)
        self.assertEqual(self.p_dict['Reporting_Interval'], reporting_interval)
        self.assertEqual(self.p_dict['Max_Number_Reports'], max_number_reports)
        self.assertEqual(self.p_dict['Age_Bins'], age_bins)
        self.assertEqual(self.p_dict['Pretty_Format'], pretty_format)
        self.assertEqual(self.p_dict['Report_Description'], report_description)
        self.assertEqual(self.p_dict['Nodeset_Config']['Node_List'], nodes)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'], "NodeSetNodeList")

    # end region

    # MalariaSurveyJSONAnalyzer
    def test_malaria_survey_analyzer_custom(self):
        start_day = 42
        duration_days = 25
        event_trigger_list = ["HappyBirthday"]
        max_number_reports = 15
        nodes = [42, 434, 94]
        individual_property_to_collect = "Risk"
        pretty_format = 1
        reporting_interval = 234.6

        report_description = "Analyzer_Test"
        self.tmp_reporter = add_malaria_survey_analyzer(None, schema_path_file,
                                                        start_day=start_day,
                                                        duration_days=duration_days,
                                                        event_trigger_list=event_trigger_list,
                                                        max_number_reports=max_number_reports,
                                                        reporting_interval=reporting_interval,
                                                        nodes=nodes,
                                                        individual_property_to_collect=individual_property_to_collect,
                                                        pretty_format=pretty_format,
                                                        report_description=report_description)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['Duration_Days'], duration_days)
        self.assertEqual(self.p_dict['Max_Number_Reports'], max_number_reports)
        self.assertEqual(self.p_dict['Event_Trigger_List'], event_trigger_list)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], individual_property_to_collect)
        self.assertEqual(self.p_dict['Pretty_Format'], pretty_format)
        self.assertEqual(self.p_dict['Reporting_Interval'], reporting_interval)
        self.assertEqual(self.p_dict['Report_Description'], report_description)
        self.assertEqual(self.p_dict['Nodeset_Config']['Node_List'], nodes)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'], "NodeSetNodeList")

    def test_malaria_survey_analyzer_default(self):
        start_day = 0
        duration_days = 365000
        event_trigger_list = ["HappyBirthday"]
        max_number_reports = 365000
        individual_property_to_collect = ""
        pretty_format = 0
        report_description = ""
        reporting_interval = 1
        self.tmp_reporter = add_malaria_survey_analyzer(None, schema_path_file,
                                                        event_trigger_list=event_trigger_list)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['Duration_Days'], duration_days)
        self.assertEqual(self.p_dict['Max_Number_Reports'], max_number_reports)
        self.assertEqual(self.p_dict['Event_Trigger_List'], event_trigger_list)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], individual_property_to_collect)
        self.assertEqual(self.p_dict['Pretty_Format'], pretty_format)
        self.assertEqual(self.p_dict['Reporting_Interval'], reporting_interval)
        self.assertEqual(self.p_dict['Report_Description'], report_description)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'], "NodeSetAll")

    # end region

    # ReportDrugStatus
    def test_drug_status_report_custom(self):
        start_day = 45
        end_day = 85
        self.tmp_reporter = add_drug_status_report(None, schema_path_file,
                                                   start_day=start_day,
                                                   end_day=end_day)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)

    def test_drug_status_report_default(self):
        start_day = 0
        end_day = 365000
        self.tmp_reporter = add_drug_status_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)

    # end region

    # ReportHumanMigrationTracking
    def test_human_migration_tracking_custom(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_drug_status_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)

    # end region

    # ReportNodeDemographics
    def test_report_node_demographics_custom(self):
        age_bins = [3, 17, 25, 120]
        individual_property_to_collect = "Risk"
        stratify_by_gender = 0
        self.tmp_reporter = add_report_node_demographics(None, schema_path_file,
                                                         age_bins=age_bins,
                                                         individual_property_to_collect=individual_property_to_collect,
                                                         stratify_by_gender=stratify_by_gender)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], age_bins)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], individual_property_to_collect)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], stratify_by_gender)

    def test_report_node_demographics_default(self):
        age_bins = []
        individual_property_to_collect = ""
        stratify_by_gender = 1
        self.tmp_reporter = add_report_node_demographics(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], age_bins)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], individual_property_to_collect)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], stratify_by_gender)

    # end region

    # ReportNodeDemographicsMalaria
    def test_report_node_demographics_malaria_custom(self):
        age_bins = [3, 17, 25, 120]
        individual_property_to_collect = "Risk"
        stratify_by_gender = 0
        self.tmp_reporter = add_report_node_demographics_malaria(None, schema_path_file,
                                                                 age_bins=age_bins,
                                                                 individual_property_to_collect=individual_property_to_collect,
                                                                 stratify_by_gender=stratify_by_gender)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], age_bins)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], individual_property_to_collect)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], stratify_by_gender)

    def test_report_node_demographics_malaria_default(self):
        age_bins = []
        individual_property_to_collect = ""
        stratify_by_gender = 1
        self.tmp_reporter = add_report_node_demographics_malaria(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], age_bins)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], individual_property_to_collect)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], stratify_by_gender)

    # end region

    # ReportNodeDemographicsMalariaGenetics
    def test_report_node_demographics_malaria_genetics_custom(self):
        barcodes = ["AGT", "GGG"]
        drug_resistant_strings = ["G"]
        drug_resistant_statistic_type = "NUM_INFECTIONS"
        age_bins = [5, 45, 90]
        individual_property_to_collect = "Risk"
        stratify_by_gender = 0
        self.tmp_reporter = add_report_node_demographics_malaria_genetics(None, schema_path_file,
                                                                          barcodes=barcodes,
                                                                          drug_resistant_strings=drug_resistant_strings,
                                                                          drug_resistant_statistic_type=drug_resistant_statistic_type,
                                                                          age_bins=age_bins,
                                                                          individual_property_to_collect=individual_property_to_collect,
                                                                          stratify_by_gender=stratify_by_gender)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], age_bins)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], individual_property_to_collect)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], stratify_by_gender)
        self.assertEqual(self.p_dict['Barcodes'], barcodes)
        self.assertEqual(self.p_dict['Drug_Resistant_Strings'], drug_resistant_strings)
        self.assertEqual(self.p_dict['Drug_Resistant_Statistic_Type'], drug_resistant_statistic_type)

    def test_report_node_demographics_malaria_genetics_default(self):
        barcodes = []
        drug_resistant_strings = []
        drug_resistant_statistic_type = "NUM_PEOPLE_WITH_RESISTANT_INFECTION"
        age_bins = []
        individual_property_to_collect = ""
        stratify_by_gender = 1
        self.tmp_reporter = add_report_node_demographics_malaria_genetics(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], age_bins)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], individual_property_to_collect)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], stratify_by_gender)
        self.assertEqual(self.p_dict['Barcodes'], barcodes)
        self.assertEqual(self.p_dict['Drug_Resistant_Strings'], drug_resistant_strings)
        self.assertEqual(self.p_dict['Drug_Resistant_Statistic_Type'], drug_resistant_statistic_type)

    # end region

    # region ReportVectorMigration
    def test_report_vector_migration_custom(self):
        start_day = 55
        end_day = 60
        self.tmp_reporter = add_report_vector_migration(None, schema_path_file,
                                                        start_day=start_day,
                                                        end_day=end_day)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)

    def test_report_vector_migration_default(self):
        start_day = 0
        end_day = 365000
        self.tmp_reporter = add_report_vector_migration(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)

    # endregion

    # region ReportVectorStatsMalariaGenetics
    def test_report_vector_stats_malaria_genetics_custom(self):
        species_list = ["gambiae", "funestus"]
        stratify_by_species = 1
        include_wolbachia = 1
        include_gestation = 1
        barcodes = ["AAATTAGC"]
        self.tmp_reporter = add_report_vector_stats_malaria_genetics(None, schema_path_file,
                                                                     species_list=species_list,
                                                                     stratify_by_species=stratify_by_species,
                                                                     include_wolbachia=include_wolbachia,
                                                                     include_gestation=include_gestation,
                                                                     barcodes=barcodes)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Species_List'], species_list)
        self.assertEqual(self.p_dict['Stratify_By_Species'], stratify_by_species)
        self.assertEqual(self.p_dict['Include_Wolbachia_Columns'], include_wolbachia)
        self.assertEqual(self.p_dict['Include_Gestation_Columns'], include_gestation)
        self.assertEqual(self.p_dict['Barcodes'], barcodes)

    def test_report_vector_stats_malaria_genetics_default(self):
        species_list = []
        stratify_by_species = 0
        include_wolbachia = 0
        include_gestation = 0
        barcodes = []
        self.tmp_reporter = add_report_vector_stats_malaria_genetics(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Species_List'], species_list)
        self.assertEqual(self.p_dict['Stratify_By_Species'], stratify_by_species)
        self.assertEqual(self.p_dict['Include_Wolbachia_Columns'], include_wolbachia)
        self.assertEqual(self.p_dict['Include_Gestation_Columns'], include_gestation)
        self.assertEqual(self.p_dict['Barcodes'], barcodes)

    # endregion

    # region SpatialReportMalariaFiltered
    def test_spatial_report_malaria_filtered_custom(self):
        start_day = 55
        end_day = 555
        reporting_interval = 5
        nodes = [32, 1, 4]
        report_filename = "MyReport.json"
        spatial_output_channels = ["Adult_Vectors"]
        self.tmp_reporter = add_spatial_report_malaria_filtered(None, schema_path_file,
                                                                start_day=start_day,
                                                                end_day=end_day,
                                                                reporting_interval=reporting_interval,
                                                                nodes=nodes,
                                                                report_filename=report_filename,
                                                                spatial_output_channels=spatial_output_channels)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)
        self.assertEqual(self.p_dict['Reporting_Interval'], reporting_interval)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], nodes)
        self.assertEqual(self.p_dict['Report_File_Name'], report_filename)
        self.assertEqual(self.p_dict['Spatial_Output_Channels'], spatial_output_channels)

    def test_spatial_report_malaria_filtered_default(self):
        start_day = 0
        end_day = 365000
        reporting_interval = 1
        nodes = []
        report_filename = "SpatialReportMalariaFiltered"
        spatial_output_channels = ["Blood_Smear_Parasite_Prevalence",
                                   "New_Clinical_Cases",
                                   "Population"]
        self.tmp_reporter = add_spatial_report_malaria_filtered(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)
        self.assertEqual(self.p_dict['Reporting_Interval'], reporting_interval)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], nodes)
        self.assertEqual(self.p_dict['Report_File_Name'], report_filename)
        self.assertEqual(self.p_dict['Spatial_Output_Channels'], spatial_output_channels)

    # endregion

    # region ReportMalariaFiltered
    def test_report_malaria_filtered_custom(self):
        start_day = 30
        end_day = 452
        nodes = [34, 2, 1]
        report_filename = "MyTestReport.json"
        max_age = 12
        min_age = 3
        has_interventions = ["Bednet", "SpaceSpray"]
        include_average = False
        self.tmp_reporter = add_report_malaria_filtered(None, schema_path_file,
                                                        start_day=start_day,
                                                        end_day=end_day,
                                                        nodes=nodes,
                                                        report_filename=report_filename,
                                                        min_age_years=min_age,
                                                        max_age_years=max_age,
                                                        has_interventions=has_interventions,
                                                        include_30day_avg_infection_duration=include_average)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], nodes)
        self.assertEqual(self.p_dict['Report_File_Name'], report_filename)
        self.assertEqual(self.p_dict['Max_Age_Years'], max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], min_age)
        self.assertEqual(self.p_dict['Has_Interventions'], has_interventions)
        self.assertEqual(self.p_dict['Include_30Day_Avg_Infection_Duration'], 1 if include_average else 0)

    def test_report_malaria_filtered_default(self):
        start_day = 0
        end_day = 365000
        nodes = []
        report_filename = "ReportMalariaFiltered.json"
        max_age = 125
        min_age = 0
        has_interventions = []
        include_average = 1
        self.tmp_reporter = add_report_malaria_filtered(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], nodes)
        self.assertEqual(self.p_dict['Report_File_Name'], report_filename)
        self.assertEqual(self.p_dict['Max_Age_Years'], max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], min_age)
        self.assertEqual(self.p_dict['Has_Interventions'], has_interventions)
        self.assertEqual(self.p_dict['Include_30Day_Avg_Infection_Duration'], 1 if include_average else 0)

    # endregion

    # region ReportHumanMigrationTracking
    def test_human_migration_tracking_default(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_human_migration_tracking(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)

    # region end

    # region ReportIneterventionPopAvg
    def test_report_intervention_pop_avg(self):
        start_day = 83
        duration_days = 23487
        nodes = [1, 42, 23]
        report_description = "test_test"
        self.tmp_reporter = add_report_intervention_pop_avg(None, schema_path_file,
                                                            start_day=start_day,
                                                            duration_days=duration_days,
                                                            report_description=report_description,
                                                            nodes=nodes)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['Duration_Days'], duration_days)
        self.assertEqual(self.p_dict['Nodeset_Config']['Node_List'], nodes)
        self.assertEqual(self.p_dict['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(self.p_dict['Report_Description'], report_description)
    # endregion


if __name__ == '__main__':
    unittest.main()
