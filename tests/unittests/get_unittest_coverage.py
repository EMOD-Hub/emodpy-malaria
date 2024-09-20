import coverage
import unittest
import xmlrunner
from pathlib import Path
import os
import tarfile
import argparse
import json
from test_import import MalariaTestImports
from test_malaria_interventions import TestMalariaInterventions
from test_malaria_interventions_as_files import MalariaInterventionFileTest
from test_malaria_reporters import TestMalariaReport
from test_malaria_config import TestMalariaConfig
from test_treatment_seeking import TreatmentSeekingTest
from test_demog import DemoTest
from weather.test_e2e import WeatherE2ETests
from weather.test_e2e_comps import WeatherE2ECompsTests
from weather.test_weather_data import WeatherDataTests
from weather.test_weather_metadata import WeatherMetadataTests
from weather.test_weather_request import WeatherRequestTests
from weather.test_weather_scenarios import WeatherScenariosTests
from weather.test_weather_set import WeatherSetTests


run_examples = False

covered_classes = [
                    "emodpy_malaria.interventions.adherentdrug",
                    "emodpy_malaria.interventions.bednet",
                    "emodpy_malaria.interventions.common",
                    "emodpy_malaria.interventions.community_health_worker",
                    "emodpy_malaria.interventions.diag_survey",
                    "emodpy_malaria.interventions.drug",
                    "emodpy_malaria.interventions.drug_campaign",
                    "emodpy_malaria.interventions.inputeir",
                    "emodpy_malaria.interventions.irs",
                    "emodpy_malaria.interventions.ivermectin",
                    "emodpy_malaria.interventions.larvicide",
                    "emodpy_malaria.interventions.mosquitorelease",
                    "emodpy_malaria.interventions.outbreak",
                    "emodpy_malaria.interventions.outdoorrestkill",
                    "emodpy_malaria.interventions.scale_larval_habitats",
                    "emodpy_malaria.interventions.spacespraying",
                    "emodpy_malaria.interventions.sugartrap",
                    "emodpy_malaria.interventions.treatment_seeking",
                    "emodpy_malaria.interventions.usage_dependent_bednet",
                    "emodpy_malaria.interventions.vaccine",
                    "emodpy_malaria.interventions.malaria_challenge",
                    "emodpy_malaria.demographics.MalariaDemographics",
                    "emodpy_malaria.malaria_config",
                    "emodpy_malaria.vector_config",
                    "emodpy_malaria.reporters.builtin",
                    "emodpy_malaria.weather.weather_data",
                    "emodpy_malaria.weather.weather_metadata",
                    "emodpy_malaria.weather.weather_request",
                    "emodpy_malaria.weather.weather_set",
                    "emodpy_malaria.weather.weather_utils",
                    "emodpy_malaria.weather.weather_variable",
                ]
examples_to_run = [
                    "add_reports",
                    "burnin_create",
                    "burnin_create_and_use_sweep_larval_habitat",
                    "burnin_create_infections",
                    "burnin_create_parasite_genetics",
                    "burnin_use",
                    "campaign_sweep",
                    "create_demographics",
                    "demographics_sweep",
                    "diagnostic_survey",
                    "download_files",
                    "drug_campaign",
                    "embedded_python_post_processing",
                    "fpg_example",
                    "inputEIR",
                    "irs",
                    "ivermectin",
                    "jonr_1",
                    "male_vector_fertility_test",
                    "microsporidia",
                    "migration_spatial_malaria_sim",
                    "migration_spatial_vector_sim",
                    "outdoor_rest_kill_male_mosquitoes",
                    "rcd_elimination_emodpy",
                    "run_with_unobserved_importation",
                    "scale_larval_habitats",
                    "serialization_remove_infections",
                    "serialization_replace_genomes",
                    "start_here",
                    "vector_basic",
                    "vector_genetics_insecticide_resistance",
                    "vector_genetics_vector_sim",
                    "weather"
                ]

class Coverage:
    def __init__(self):
        """
        Initialize to not replace existing results
        """
        self.set_baseline = False
        self.cov = None
        pass

    def get_baseline_bool(self):
        """
        Sets user input for saving coverage results json
        """
        parser = argparse.ArgumentParser(description="Settings for coverage logging")
        parser.add_argument(
            "--set_baseline",
            action="store_true",
            default=False,
            help="Use this flag to save the current coverage json as the baseline in coverage_data/.",
        )

        self.set_baseline = parser.parse_args().set_baseline

        pass

    def run_tests(self):
        self.cov = coverage.Coverage(source=covered_classes)
        self.cov.start()

        # First, load and run the unittest tests
        test_suite = unittest.TestLoader().discover(start_dir='.', pattern='test_*.py')
        runner = xmlrunner.XMLTestRunner(output='test_reports')
        results = runner.run(test_suite)

        return results

    def run_examples(self):
        """
        Adds examples to test coverage and runs all
        """
        examples_dir = Path.cwd().parent.parent.joinpath('examples')

        def run_example(name):
            exec_path = examples_dir.joinpath(name, "example.py")
            os.system(f'python {exec_path}')

        for example in examples_to_run:
            run_example(example)

    def save_results(self):
        """
        Saves new results and optionally baseline results, 
        and print coverage by module
        """
        coverage_data = self.cov.get_data()
        measured_files = coverage_data.measured_files()

        # Getting the percentage coverage from the Coverage object
        def count_lines_in_file(file_path):
            try:
                with open(file_path, "r", encoding='utf-8') as file:
                    line = sum([1 for line in file])
                return line
            except FileNotFoundError:
                print(f"File not found: {file_path}")
                return None

        total_statements = 0
        total_covered_statements = 0 
        coverage_results = {}
        for filename in measured_files:
            num_statements = count_lines_in_file(filename)
            covered_statements = len(coverage_data.lines(filename))

            total_statements += num_statements
            total_covered_statements += covered_statements

            coverage_percentage = round((covered_statements / num_statements) * 100, 2)
            coverage_results[filename] = coverage_percentage

        total_coverage_percentage = round((total_covered_statements / total_statements) * 100, 2)
        coverage_results["total_coverage"] = total_coverage_percentage

        # Formatting results to print out
        # Saving new results to /coverage_data
        new_results_path = Path.cwd() / 'coverage_data' / 'new_results.json'
        old_results_path = Path.cwd() / 'coverage_data' / 'baseline_results.json'
        with open(new_results_path, "w", encoding='utf-8') as outfile:
            json.dump(coverage_results, outfile)

        if not os.path.exists(old_results_path):
            with open(old_results_path, "w", encoding='utf-8') as outfile:
                json.dump(coverage_results, outfile)

        # Access baseline results
        with open(old_results_path, "r", encoding='utf-8') as file:
            old_coverage_results = json.load(file)

        # Printing all results by module
        # Skipping until we can  show off differences in a reasonable way
        # print("============================")
        # print(f"Total coverage: {coverage_percentage:.2f}%")
        # print("============================")
        # print("Coverage by file")
        # print("----------------------------")

        # # Formatting results by file for printing
        # max_filename_width = int(max(len(item) for item in old_coverage_results) / 2)
        # file_differences = {}
        # module_name = ""
        # for file_path, _ in sorted(old_coverage_results.items()):
        #     path_obj = Path(file_path)
        #     temp_module_name = path_obj.parent.name
        #     file_path_trunc = path_obj.name
        #     if module_name != temp_module_name:
        #         print(temp_module_name)
        #         module_name = temp_module_name
            
        #     old_value = old_coverage_results[file_path]
        #     new_value = coverage_results[file_path]
        #     print(f"--{file_path_trunc.ljust(max_filename_width)} {new_value}%")

        #     # Saving differences between new and baseline
        #     if old_value != new_value:
        #         diff = new_value - old_value
        #         file_differences[(module_name, file_path_trunc)] = diff
        #         if diff > 0:
        #             file_differences[(module_name, file_path_trunc)] = f"+{diff}"
        
        # # Printing differences between baseline and new results file
        # print("============================")
        # print("Differences")
        # print("----------------------------")
        # if len(file_differences) == 0:
        #     print("No differences")
        # else:
        #     module_name = ""
        #     for changed_file in file_differences:
        #         temp_module_name = changed_file[0]
        #         if temp_module_name != module_name:
        #             print(temp_module_name)
        #             module_name = temp_module_name
        #         print(f"--{changed_file[1].ljust(max_filename_width)} {file_differences[changed_file]}%")

        # if self.set_baseline:
        #     print("Saving new baseline to: {old_results_path}")
        #     with open(old_results_path, "w") as outfile:
        #         json.dump(coverage_results, outfile)
        self.cov.save()
        self.cov.html_report()

        # Packaging as.tar.gz for jenkins
        print("Saving coverage file as: coverage.tar.gz")
        with tarfile.open("coverage.tar.gz", "w:gz") as tar:
            tar.add("htmlcov", arcname="coverage_app")  # Within coverage.tar.gz is coverage_app/files
    
    def run(self):
        self.get_baseline_bool()
        self.run_tests()
        if run_examples:
            self.run_examples()
        self.cov.stop()
        self.save_results()



if __name__ == "__main__":
    coverage_class = Coverage()
    coverage_class.run()
