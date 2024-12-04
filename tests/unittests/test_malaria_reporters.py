import unittest
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from emodpy_malaria.reporters.builtin import *
import schema_path_file

empty_string = ""
empty_list = []
default_end_day = 365000
default_start_day = 0
default_min_age = 0
default_max_age = 125
test_start_day = 11
test_end_day = 2834720
test_list = [12, 23, 34, 45, 100]
test_string = "wekrjpoefn2349"
test_string1 = "skdufhwiuety"
test_string2 = "hdfw9845n"
test_min_age = 11
test_max_age = 87
test_float = 234.56
test_int = 55
test_int1 = 98
test_int2 = 21


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
        self.assertEqual(self.p_dict['Species_List'], empty_list)
        self.assertEqual(self.p_dict['Include_Wolbachia_Columns'], 0)
        self.assertEqual(self.p_dict['Include_Gestation_Columns'], 0)
        self.assertEqual(self.p_dict['Include_Death_By_State_Columns'], 0)
        self.assertEqual(self.p_dict['Include_Microsporidia_Columns'], 0)
        pass

    def test_vector_stats_custom(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_report_vector_stats(None, schema_path_file,
                                                    include_gestation=True,
                                                    include_wolbachia=True,
                                                    include_death_state=True,
                                                    species_list=["gambiae", "SillySkeeter"],
                                                    stratify_by_species=True,
                                                    include_microsporidia=True)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Stratify_By_Species'], 1)
        self.assertEqual(self.p_dict['Species_List'], ["gambiae", "SillySkeeter"])
        self.assertEqual(self.p_dict['Include_Wolbachia_Columns'], 1)
        self.assertEqual(self.p_dict['Include_Gestation_Columns'], 1)
        self.assertEqual(self.p_dict['Include_Death_By_State_Columns'], 1)
        self.assertEqual(self.p_dict['Include_Microsporidia_Columns'], 1)
        pass
    # endregion

    # region ReportVectorGenetics
    def test_vector_genetics_default(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_report_vector_genetics(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Gender'], "VECTOR_FEMALE")
        self.assertEqual(self.p_dict['Include_Vector_State_Columns'], 1)
        self.assertEqual(self.p_dict['Filename_Suffix'], empty_string)
        self.assertEqual(self.p_dict['Start_Day'], 0)
        self.assertEqual(self.p_dict['Stratify_By'], "GENOME")
        self.assertEqual(self.p_dict['Combine_Similar_Genomes'], 0)

    def test_vg_custom_genome_stratification(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_report_vector_genetics(None, schema_path_file,
                                                       combine_similar_genomes=True,
                                                       stratify_by="GENOME")
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Combine_Similar_Genomes'], 1)
        self.assertEqual(self.p_dict['Stratify_By'], "GENOME")

    def test_vg_custom_specific_genome_stratification(self):
        self.tmp_reporter = add_report_vector_genetics(None, schema_path_file,
                                                       end_day=test_end_day,
                                                       gender="VECTOR_MALE",
                                                       include_vector_state=False,
                                                       filename_suffix="test_report",
                                                       species="Silly_Skeeter",
                                                       start_day=test_start_day,
                                                       node_ids=test_list,
                                                       stratify_by="SPECIFIC_GENOME",
                                                       specific_genome_combinations_for_stratification=[["X"], ["*"]])
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], test_list)
        self.assertEqual(self.p_dict['Gender'], "VECTOR_MALE")
        self.assertEqual(self.p_dict['Include_Vector_State_Columns'], 0)
        self.assertEqual(self.p_dict['Filename_Suffix'], "test_report")
        self.assertEqual(self.p_dict['Species'], "Silly_Skeeter")
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['Specific_Genome_Combinations_For_Stratification'], [["X"], ["*"]])
        self.assertEqual(self.p_dict['Stratify_By'], "SPECIFIC_GENOME")  # because of previous

    def test_vg_custom_specific_genome_stratification_no_combination(self):
        self.tmp_reporter = add_report_vector_genetics(None, schema_path_file,
                                                       stratify_by="ALLELE_FREQ",
                                                       end_day=test_end_day,
                                                       species="Silly_Skeeter",
                                                       gender="VECTOR_MALE",
                                                       include_vector_state=False,
                                                       alleles_for_stratification=["a0", "a1", "b0", "b1"],
                                                       filename_suffix="Does some stuff",
                                                       )
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Gender'], "VECTOR_MALE")
        self.assertEqual(self.p_dict['Include_Vector_State_Columns'], 0)
        self.assertEqual(self.p_dict['Filename_Suffix'], "Does some stuff")
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

    # region ReportInfectionStatsMalaria
    def test_report_infection_stats_default(self):
        self.tmp_reporter = add_report_infection_stats_malaria(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Reporting_Interval'], 30)
        self.assertEqual(self.p_dict['Include_Column_Gametocyte'], 1)
        self.assertEqual(self.p_dict['Include_Column_Hepatocyte'], 1)
        self.assertEqual(self.p_dict['Include_Column_IRBC'], 1)
        self.assertEqual(self.p_dict['Include_Data_Threshold_Gametocytes'], 0)
        self.assertEqual(self.p_dict['Include_Data_Threshold_Hepatocytes'], 0)
        self.assertEqual(self.p_dict['Include_Data_Threshold_IRBC'], 0)

        pass

    def test_report_infection_stats_custom(self):
        self.tmp_reporter = add_report_infection_stats_malaria(None, schema_path_file,
                                                               start_day=test_start_day, end_day=test_end_day,
                                                               reporting_interval=test_int,
                                                               include_irbc=False, include_gametocyte=False,
                                                               include_hepatocyte=False, irbc_threshold=2,
                                                               hepatocyte_threshold=3802300, gametocyte_threshold=20)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Reporting_Interval'], test_int)
        self.assertEqual(self.p_dict['Include_Column_Gametocyte'], 0)
        self.assertEqual(self.p_dict['Include_Column_Hepatocyte'], 0)
        self.assertEqual(self.p_dict['Include_Column_IRBC'], 0)
        self.assertEqual(self.p_dict['Include_Data_Threshold_Gametocytes'], 20)
        self.assertEqual(self.p_dict['Include_Data_Threshold_Hepatocytes'], 3802300)
        self.assertEqual(self.p_dict['Include_Data_Threshold_IRBC'], 2)
        pass
    # endregion

    # region MalariaSummaryReport
    def test_malaria_summary_report_default(self):
        self.tmp_reporter = add_malaria_summary_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], empty_list)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Age_Bins'], empty_list)
        self.assertEqual(self.p_dict['Infectiousness_Bins'], empty_list)
        self.assertEqual(self.p_dict['Max_Number_Reports'], 100)
        self.assertEqual(self.p_dict['Parasitemia_Bins'], empty_list)
        self.assertEqual(self.p_dict['Pretty_Format'], 0)
        self.assertEqual(self.p_dict['Filename_Suffix'], empty_string)
        self.assertEqual(self.p_dict['Reporting_Interval'], 365)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], empty_string)
        self.assertEqual(self.p_dict['Use_True_Density_Vs_Threshold'], 0)
        # not in the dict beccause Use_True_Density_Vs_Threshold is false
        #self.assertEqual(self.p_dict['Detection_Threshold_True_Gametocyte_Density'], 0.0)
        pass

    def test_malaria_summary_report_nodelist(self):
        self.tmp_reporter = add_malaria_summary_report(None, schema_path_file,
                                                       node_ids=test_list,
                                                       must_have_intervention=test_string,
                                                       must_have_ip_key_value=test_string1)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], test_list)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], test_string1)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], test_string)

    def test_malaria_summary_report_custom1(self):
        self.tmp_reporter = add_malaria_summary_report(None, schema_path_file,
                                                       age_bins=test_list,
                                                       end_day=test_end_day)
        self.p_dict = self.tmp_reporter.parameters
        self.assertEqual(self.p_dict['Age_Bins'], test_list)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)

    def test_malaria_summary_report_custom2(self):
        self.tmp_reporter = add_malaria_summary_report(None, schema_path_file,
                                                       must_have_ip_key_value="FavoriteCola:RC",
                                                       use_true_density=True,
                                                       gametocyte_detection_threshold=0.77,
                                                       infectiousness_bins=[-15, -5, 0, 3, 5, 8],
                                                       max_number_reports=63,
                                                       parasitemia_bins=[100, 500, 1500, 2345],
                                                       must_have_intervention="SimpleBednet")
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], "FavoriteCola:RC")
        self.assertEqual(self.p_dict['Must_Have_Intervention'], "SimpleBednet")
        self.assertEqual(self.p_dict['Infectiousness_Bins'], [-15, -5, 0, 3, 5, 8])
        self.assertEqual(self.p_dict['Max_Number_Reports'], 63)
        self.assertEqual(self.p_dict['Parasitemia_Bins'], [100, 500, 1500, 2345])
        self.assertEqual(self.p_dict['Use_True_Density_Vs_Threshold'], 1)
        self.assertEqual(self.p_dict['Detection_Threshold_True_Gametocyte_Density'], 0.77)
        pass

    def test_malaria_summary_report_custom3(self):
        self.tmp_reporter = add_malaria_summary_report(None, schema_path_file,
                                                       pretty_format=True,
                                                       filename_suffix=test_string2,
                                                       reporting_interval=test_float,
                                                       start_day=test_start_day)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Pretty_Format'], 1)
        self.assertEqual(self.p_dict['Filename_Suffix'], test_string2)
        self.assertEqual(self.p_dict['Reporting_Interval'], test_float)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        pass
    # endregion

    # SqlReportMalaria
    def test_sql_report_malaria_default(self):
        self.tmp_reporter = add_sql_report_malaria(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Include_Infection_Data_Table'], 1)
        self.assertEqual(self.p_dict['Include_Health_Table'], 1)
        self.assertEqual(self.p_dict['Include_Drug_Status_Table'], 0)
        self.assertEqual(self.p_dict['Include_Individual_Properties'], 0)

    def test_sql_report_malaria_custom(self):
        self.tmp_reporter = add_sql_report_malaria(None, schema_path_file,
                                                   end_day=test_end_day,
                                                   start_day=test_start_day,
                                                   include_infection_table=False,
                                                   include_health_table=False,
                                                   include_drug_table=True,
                                                   include_individual_properties=True)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Include_Infection_Data_Table'], 0)
        self.assertEqual(self.p_dict['Include_Health_Table'], 0)
        self.assertEqual(self.p_dict['Include_Drug_Status_Table'], 1)
        self.assertEqual(self.p_dict['Include_Individual_Properties'], 1)
    # end region

    # SqlReportMalariaGenetics
    def test_sql_report_malaria_genetics_default(self):
        self.tmp_reporter = add_sql_report_malaria_genetics(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Include_Infection_Data_Table'], 1)
        self.assertEqual(self.p_dict['Include_Health_Table'], 1)
        self.assertEqual(self.p_dict['Include_Drug_Status_Table'], 0)
        self.assertEqual(self.p_dict['Include_Individual_Properties'], 0)

    def test_sql_report_malaria_genetics_custom(self):
        self.tmp_reporter = add_sql_report_malaria_genetics(None, schema_path_file,
                                                            end_day=test_end_day,
                                                            start_day=test_start_day,
                                                            include_infection_table=False,
                                                            include_health_table=False,
                                                            include_drug_table=True,
                                                            include_individual_properties=True)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Include_Infection_Data_Table'], 0)
        self.assertEqual(self.p_dict['Include_Health_Table'], 0)
        self.assertEqual(self.p_dict['Include_Drug_Status_Table'], 1)
        self.assertEqual(self.p_dict['Include_Individual_Properties'], 1)
    # end region

    # start region ReportEventCounter
    def test_report_counter_default(self):
        self.tmp_reporter = add_report_event_counter(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Event_Trigger_List'], empty_list)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['Filename_Suffix'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], empty_string)
        self.assertEqual(self.p_dict['Max_Age_Years'], default_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], default_min_age)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], empty_list)

    def test_report_counter_custom(self):
        trigger_list = ["STINewInfection", "ExitedRelationship"]
        self.tmp_reporter = add_report_event_counter(None, schema_path_file,
                                                     start_day=test_start_day,
                                                     end_day=test_end_day,
                                                     event_trigger_list=trigger_list,
                                                     filename_suffix=test_string2,
                                                     min_age_years=test_min_age,
                                                     max_age_years=test_max_age,
                                                     must_have_intervention=test_string,
                                                     must_have_ip_key_value=test_string1,
                                                     node_ids=test_list)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Event_Trigger_List'], trigger_list)
        self.assertEqual(self.p_dict['Filename_Suffix'], test_string2)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], test_string1)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], test_string)
        self.assertEqual(self.p_dict['Max_Age_Years'], test_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], test_min_age)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], test_list)
    # end region

    # region ReportSimpleMalariaTransimission
    def test_malaria_cotransmission_report_default(self):
        self.tmp_reporter = add_malaria_cotransmission_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertNotIn('Pretty_Format', self.p_dict)
        self.assertEqual(self.p_dict['Include_Human_To_Vector_Transmission'], 0)
        self.assertEqual(self.p_dict['Filename_Suffix'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], empty_string)
        self.assertEqual(self.p_dict['Max_Age_Years'], default_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], default_min_age)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], empty_list)

    def test_malaria_cotransmission_report_custom(self):
        self.tmp_reporter = add_malaria_cotransmission_report(None, schema_path_file,
                                                              start_day=test_start_day,
                                                              end_day=test_end_day,
                                                              node_ids=test_list,
                                                              filename_suffix=test_string2,
                                                              include_human_to_vector=1,
                                                              min_age_years=test_min_age,
                                                              max_age_years=test_max_age,
                                                              must_have_intervention=test_string,
                                                              must_have_ip_key_value=test_string1,
                                                              )
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertNotIn('Pretty_Format', self.p_dict)
        self.assertEqual(self.p_dict['Include_Human_To_Vector_Transmission'], 1)
        self.assertEqual(self.p_dict['Filename_Suffix'], test_string2)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], test_string1)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], test_string)
        self.assertEqual(self.p_dict['Max_Age_Years'], test_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], test_min_age)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], test_list)

    # end region

    # region VectorHabitatReport
    def test_add_vector_habitat_report(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_vector_habitat_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
    # end region

    # MalariaImmunityReport
    def test_malaria_immunity_report_default(self):
        self.tmp_reporter = add_malaria_immunity_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Reporting_Interval'], 1)
        self.assertEqual(self.p_dict['Max_Number_Reports'], default_end_day)
        self.assertEqual(self.p_dict['Age_Bins'], empty_list)
        self.assertEqual(self.p_dict['Pretty_Format'], 0)
        self.assertEqual(self.p_dict['Filename_Suffix'], empty_string)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], empty_list)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], empty_string)

    def test_malaria_immunity_report_custom(self):
        self.tmp_reporter = add_malaria_immunity_report(None, schema_path_file,
                                                        start_day=test_start_day,
                                                        end_day=test_end_day,
                                                        reporting_interval=test_int,
                                                        max_number_reports=test_int,
                                                        node_ids=test_list,
                                                        age_bins=test_list,
                                                        pretty_format=True,
                                                        filename_suffix=test_string2,
                                                        must_have_intervention=test_string,
                                                        must_have_ip_key_value=test_string1)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Reporting_Interval'], test_int)
        self.assertEqual(self.p_dict['Max_Number_Reports'], test_int)
        self.assertEqual(self.p_dict['Age_Bins'], test_list)
        self.assertEqual(self.p_dict['Pretty_Format'], 1)
        self.assertEqual(self.p_dict['Filename_Suffix'], test_string2)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], test_string1)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], test_string)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], test_list)
    # end region

    # MalariaSurveyJSONAnalyzer
    def test_malaria_survey_analyzer_custom(self):
        event_trigger_list = ["HappyBirthday"]
        max_number_reports = 15
        pretty_format = 1
        reporting_interval = 234.6
        filename_suffix = "Analyzer_Test"
        self.tmp_reporter = add_malaria_survey_analyzer(None, schema_path_file,
                                                        start_day=test_start_day,
                                                        end_day=test_end_day,
                                                        event_trigger_list=event_trigger_list,
                                                        max_number_reports=max_number_reports,
                                                        reporting_interval=reporting_interval,
                                                        node_ids=test_list,
                                                        ip_key_to_collect=test_string2,
                                                        pretty_format=pretty_format,
                                                        filename_suffix=filename_suffix,
                                                        must_have_intervention=test_string,
                                                        must_have_ip_key_value=test_string1
                                                        )
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Max_Number_Reports'], max_number_reports)
        self.assertEqual(self.p_dict['Event_Trigger_List'], event_trigger_list)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], test_string2)
        self.assertEqual(self.p_dict['Pretty_Format'], pretty_format)
        self.assertEqual(self.p_dict['Reporting_Interval'], reporting_interval)
        self.assertEqual(self.p_dict['Filename_Suffix'], filename_suffix)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], test_string1)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], test_string)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], test_list)

    def test_malaria_survey_analyzer_default(self):
        self.tmp_reporter = add_malaria_survey_analyzer(None, schema_path_file, event_trigger_list=test_list)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Max_Number_Reports'], default_end_day)
        self.assertEqual(self.p_dict['Event_Trigger_List'], test_list)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], empty_string)
        self.assertEqual(self.p_dict['Pretty_Format'], 0)
        self.assertEqual(self.p_dict['Reporting_Interval'], 1)
        self.assertEqual(self.p_dict['Filename_Suffix'], empty_string)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], empty_list),
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], empty_string)
    # end region

    # ReportDrugStatus
    def test_drug_status_report_custom(self):
        self.tmp_reporter = add_drug_status_report(None, schema_path_file,
                                                   start_day=test_start_day,
                                                   end_day=test_end_day)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)

    def test_drug_status_report_default(self):
        self.tmp_reporter = add_drug_status_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
    # end region

    # ReportHumanMigrationTracking
    def test_human_migration_tracking_custom(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_drug_status_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
    # end region

    # ReportSimulationStats
    def test_add_report_simulation_stats(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_drug_status_report(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
    # end region

    # ReportMicrosporidia
    def test_report_microsporidia(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_report_microsporidia(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
    # end region

    # ReportNodeDemographics
    def test_report_node_demographics_custom(self):
        self.tmp_reporter = add_report_node_demographics(None, schema_path_file,
                                                         age_bins=test_list,
                                                         ip_key_to_collect=test_string,
                                                         stratify_by_gender=False)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], test_list)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], test_string)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], 0)

    def test_report_node_demographics_default(self):
        stratify_by_gender = 1
        self.tmp_reporter = add_report_node_demographics(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], empty_list)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], empty_string)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], stratify_by_gender)
    # end region

    # ReportNodeDemographicsMalaria
    def test_report_node_demographics_malaria_custom(self):
        self.tmp_reporter = add_report_node_demographics_malaria(None, schema_path_file,
                                                                 age_bins=test_list,
                                                                 ip_key_to_collect=test_string,
                                                                 stratify_by_gender=False,
                                                                 stratify_by_clinical_symptoms=True)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], test_list)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], test_string)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], 0)
        self.assertEqual(self.p_dict['Stratify_By_Has_Clinical_Symptoms'], 1)

    def test_report_node_demographics_malaria_default(self):
        stratify_by_gender = 1
        self.tmp_reporter = add_report_node_demographics_malaria(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], empty_list)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], empty_string)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], stratify_by_gender)
        self.assertEqual(self.p_dict['Stratify_By_Has_Clinical_Symptoms'], 0)

    # end region

    # ReportNodeDemographicsMalariaGenetics
    def test_report_node_demographics_malaria_genetics_custom(self):
        barcodes = ["AGT", "GGG"]
        drug_resistant_strings = ["G"]
        drug_resistant_statistic_type = DrugResistantAndHRPStatisticType.NUM_INFECTIONS
        age_bins = [5, 45, 90]
        individual_property_to_collect = "Risk"
        self.tmp_reporter = add_report_node_demographics_malaria_genetics(None, schema_path_file,
                                                                          barcodes=barcodes,
                                                                          drug_resistant_strings=drug_resistant_strings,
                                                                          drug_resistant_and_hrp_statistic_type=drug_resistant_statistic_type,
                                                                          age_bins=age_bins,
                                                                          ip_key_to_collect=individual_property_to_collect,
                                                                          stratify_by_gender=False,
                                                                          include_identity_by_xxx=True)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], age_bins)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], individual_property_to_collect)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], 0)
        self.assertEqual(self.p_dict['Barcodes'], barcodes)
        self.assertEqual(self.p_dict['Drug_Resistant_Strings'], drug_resistant_strings)
        self.assertEqual(self.p_dict['Drug_Resistant_And_HRP_Statistic_Type'], drug_resistant_statistic_type.value)
        self.assertEqual(self.p_dict['Include_Identity_By_XXX'], 1)

    def test_report_node_demographics_malaria_genetics_default(self):
        barcodes = empty_list
        drug_resistant_strings = empty_list
        drug_resistant_statistic_type = "NUM_PEOPLE_WITH_RESISTANT_INFECTION"
        age_bins = empty_list
        individual_property_to_collect = empty_string
        stratify_by_gender = 1
        self.tmp_reporter = add_report_node_demographics_malaria_genetics(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Age_Bins'], age_bins)
        self.assertEqual(self.p_dict['IP_Key_To_Collect'], individual_property_to_collect)
        self.assertEqual(self.p_dict['Stratify_By_Gender'], stratify_by_gender)
        self.assertEqual(self.p_dict['Barcodes'], barcodes)
        self.assertEqual(self.p_dict['Drug_Resistant_Strings'], drug_resistant_strings)
        self.assertEqual(self.p_dict['Drug_Resistant_And_HRP_Statistic_Type'], drug_resistant_statistic_type)
        self.assertEqual(self.p_dict['Include_Identity_By_XXX'], 0)

    # end region

    # region ReportVectorMigration
    def test_report_vector_migration_custom(self):
        start_day = 55
        end_day = 60
        species_list = ["gambiae", "test"]
        must_be_in_state = [VectorState.STATE_MALE]
        must_be_from_node = [1, 2, 3]
        must_be_to_node = [4, 5, 6]
        include_genome_data = True
        filename_suffix = "Testing"
        self.tmp_reporter = add_report_vector_migration(None, schema_path_file,
                                                        start_day=start_day,
                                                        end_day=end_day,
                                                        species_list=species_list,
                                                        must_be_in_state=must_be_in_state,
                                                        must_be_from_node=must_be_from_node,
                                                        must_be_to_node=must_be_to_node,
                                                        include_genome_data=True,
                                                        filename_suffix=filename_suffix)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)
        self.assertEqual(self.p_dict['Species_List'], species_list)
        self.assertEqual(self.p_dict['Must_Be_In_State'], ["STATE_MALE"])
        self.assertEqual(self.p_dict['Must_Be_From_Node'], must_be_from_node)
        self.assertEqual(self.p_dict['Must_Be_To_Node'], must_be_to_node)
        self.assertEqual(self.p_dict['Include_Genome_Data'], 1)
        self.assertEqual(self.p_dict['Filename_Suffix'], filename_suffix)

    def test_report_vector_migration_default(self):
        self.tmp_reporter = add_report_vector_migration(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], 3.40282e+38)
        self.assertEqual(self.p_dict['Species_List'], [])
        self.assertEqual(self.p_dict['Must_Be_In_State'], [])
        self.assertEqual(self.p_dict['Must_Be_From_Node'], [])
        self.assertEqual(self.p_dict['Must_Be_To_Node'], [])
        self.assertEqual(self.p_dict['Include_Genome_Data'], 0)
        self.assertEqual(self.p_dict['Filename_Suffix'], "")


    # endregion

    # region ReportVectorStatsMalariaGenetics
    def test_report_vector_stats_malaria_genetics_custom(self):
        species_list = ["gambiae", "funestus"]
        barcodes = ["AAATTAGC"]
        self.tmp_reporter = add_report_vector_stats_malaria_genetics(None, schema_path_file,
                                                                     species_list=species_list,
                                                                     stratify_by_species=True,
                                                                     include_death_state=True,
                                                                     include_wolbachia=True,
                                                                     include_gestation=True,
                                                                     barcodes=barcodes,
                                                                     include_microsporidia=True)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Species_List'], species_list)
        self.assertEqual(self.p_dict['Stratify_By_Species'], 1)
        self.assertEqual(self.p_dict['Include_Wolbachia_Columns'], 1)
        self.assertEqual(self.p_dict['Include_Gestation_Columns'], 1)
        self.assertEqual(self.p_dict['Include_Death_By_State_Columns'], 1)
        self.assertEqual(self.p_dict['Barcodes'], barcodes)
        self.assertEqual(self.p_dict['Include_Microsporidia_Columns'], 1)

    def test_report_vector_stats_malaria_genetics_default(self):
        species_list = empty_list
        stratify_by_species = 0
        include_wolbachia = 0
        include_gestation = 0
        barcodes = empty_list
        include_microsporidia = 0
        self.tmp_reporter = add_report_vector_stats_malaria_genetics(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Species_List'], species_list)
        self.assertEqual(self.p_dict['Stratify_By_Species'], stratify_by_species)
        self.assertEqual(self.p_dict['Include_Wolbachia_Columns'], include_wolbachia)
        self.assertEqual(self.p_dict['Include_Gestation_Columns'], include_gestation)
        self.assertEqual(self.p_dict['Include_Death_By_State_Columns'], include_gestation)
        self.assertEqual(self.p_dict['Include_Microsporidia_Columns'], include_microsporidia)
        self.assertEqual(self.p_dict['Barcodes'], barcodes)

    # endregion

    # region SpatialReportMalariaFiltered
    def test_spatial_report_malaria_filtered_custom(self):
        start_day = 55
        end_day = 555
        reporting_interval = 5
        node_ids = [32, 1, 4]
        filename_suffix = "Testing"
        spatial_output_channels = ["Adult_Vectors"]
        self.tmp_reporter = add_spatial_report_malaria_filtered(None, schema_path_file,
                                                                start_day=start_day,
                                                                end_day=end_day,
                                                                reporting_interval=reporting_interval,
                                                                node_ids=node_ids,
                                                                filename_suffix=filename_suffix,
                                                                spatial_output_channels=spatial_output_channels,
                                                                max_age_years=test_max_age,
                                                                min_age_years=test_min_age,
                                                                must_have_ip_key_value=test_string1,
                                                                must_have_intervention=test_string)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], start_day)
        self.assertEqual(self.p_dict['End_Day'], end_day)
        self.assertEqual(self.p_dict['Reporting_Interval'], reporting_interval)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], node_ids)
        self.assertEqual(self.p_dict['Filename_Suffix'], filename_suffix)
        self.assertEqual(self.p_dict['Spatial_Output_Channels'], spatial_output_channels)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], test_string1)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], test_string)
        self.assertEqual(self.p_dict['Max_Age_Years'], test_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], test_min_age)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], node_ids)

    def test_spatial_report_malaria_filtered_default(self):
        reporting_interval = 1
        spatial_output_channels = ["Blood_Smear_Parasite_Prevalence",
                                   "New_Clinical_Cases",
                                   "Population"]
        self.tmp_reporter = add_spatial_report_malaria_filtered(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Reporting_Interval'], reporting_interval)
        self.assertEqual(self.p_dict['Spatial_Output_Channels'], spatial_output_channels)
        self.assertEqual(self.p_dict['Filename_Suffix'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], empty_string)
        self.assertEqual(self.p_dict['Max_Age_Years'], default_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], default_min_age)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], empty_list)

    # endregion

    # region ReportMalariaFiltered
    def test_report_malaria_filtered_custom(self):
        has_interventions = ["Bednet", "SpaceSpray"]
        include_average = False
        self.tmp_reporter = add_report_malaria_filtered(None, schema_path_file,
                                                        start_day=test_start_day,
                                                        end_day=test_end_day,
                                                        node_ids=test_list,
                                                        filename_suffix=test_string2,
                                                        min_age_years=test_min_age,
                                                        max_age_years=test_max_age,
                                                        has_interventions=has_interventions,
                                                        must_have_intervention=test_string,
                                                        must_have_ip_key_value=test_string1,
                                                        include_30day_avg_infection_duration=include_average)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], test_list)
        self.assertEqual(self.p_dict['Filename_Suffix'], test_string2)
        self.assertEqual(self.p_dict['Max_Age_Years'], test_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], test_min_age)
        self.assertEqual(self.p_dict['Has_Interventions'], has_interventions)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], test_string1)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], test_string)
        self.assertEqual(self.p_dict['Include_30Day_Avg_Infection_Duration'], 1 if include_average else 0)

    def test_report_malaria_filtered_default(self):
        self.tmp_reporter = add_report_malaria_filtered(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], empty_list)
        self.assertEqual(self.p_dict['Filename_Suffix'], empty_string)
        self.assertEqual(self.p_dict['Max_Age_Years'], default_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], default_min_age)
        self.assertEqual(self.p_dict['Has_Interventions'], empty_list)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], empty_string)
        self.assertEqual(self.p_dict['Include_30Day_Avg_Infection_Duration'], 1)

    # endregion

    # region ReportHumanMigrationTracking
    def test_human_migration_tracking_default(self):
        self.assertIsNone(self.tmp_reporter)
        self.tmp_reporter = add_human_migration_tracking(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)

    # region end

    # region ReportInterventionPopAvg
    def test_report_intervention_pop_avg_default(self):
        filename_suffix = "test_test"
        self.tmp_reporter = add_report_intervention_pop_avg(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Filename_Suffix'], empty_string)
        self.assertEqual(self.p_dict['Max_Age_Years'], default_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], default_min_age)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], empty_list)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], empty_string)

    def test_report_intervention_pop_avg_custom(self):
        self.tmp_reporter = add_report_intervention_pop_avg(None, schema_path_file,
                                                            start_day=test_start_day,
                                                            end_day=test_end_day,
                                                            filename_suffix=test_string2,
                                                            max_age_years=test_max_age,
                                                            min_age_years=test_min_age,
                                                            node_ids=test_list,
                                                            must_have_ip_key_value=test_string1,
                                                            must_have_intervention=test_string)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Filename_Suffix'], test_string2)
        self.assertEqual(self.p_dict['Max_Age_Years'], test_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], test_min_age)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], test_list)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], test_string1)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], test_string)

    # endregion

    # region ReportFpgOutputForObservationalModel
    def test_report_fpg_output_default(self):
        self.tmp_reporter = add_report_fpg_output(None, schema_path_file)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], default_start_day)
        self.assertEqual(self.p_dict['End_Day'], default_end_day)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], empty_list)
        self.assertEqual(self.p_dict['Max_Age_Years'], default_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], default_min_age)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], empty_string)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], empty_string)
        self.assertEqual(self.p_dict['Include_Genome_IDs'], 0)
        self.assertEqual(self.p_dict['Minimum_Parasite_Density'], 1)
        self.assertEqual(self.p_dict['Sampling_Period'], 1)

    def test_report_fpg_output_custom(self):
        self.tmp_reporter = add_report_fpg_output(None, schema_path_file,
                                                  start_day=test_start_day,
                                                  end_day=test_end_day,
                                                  node_ids=test_list,
                                                  min_age_years=test_min_age,
                                                  max_age_years=test_max_age,
                                                  must_have_intervention=test_string,
                                                  must_have_ip_key_value=test_string1,
                                                  include_genome_ids=True,
                                                  minimum_parasite_density=test_float,
                                                  sampling_period=test_int)
        self.p_dict = self.tmp_reporter.parameters
        self.assertIsNotNone(self.tmp_reporter)
        self.assertEqual(self.p_dict['Start_Day'], test_start_day)
        self.assertEqual(self.p_dict['End_Day'], test_end_day)
        self.assertEqual(self.p_dict['Node_IDs_Of_Interest'], test_list)
        self.assertEqual(self.p_dict['Max_Age_Years'], test_max_age)
        self.assertEqual(self.p_dict['Min_Age_Years'], test_min_age)
        self.assertEqual(self.p_dict['Must_Have_IP_Key_Value'], test_string1)
        self.assertEqual(self.p_dict['Must_Have_Intervention'], test_string)
        self.assertEqual(self.p_dict['Include_Genome_IDs'], 1)
        self.assertEqual(self.p_dict['Minimum_Parasite_Density'], test_float)
        self.assertEqual(self.p_dict['Sampling_Period'], test_int)
    # endregion


if __name__ == '__main__':
    unittest.main()
