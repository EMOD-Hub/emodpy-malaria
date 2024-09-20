import coverage
import unittest
loader = unittest.TestLoader()
cov = coverage.Coverage(source=[
    "emodpy_malaria.demographics.MalariaDemographics"
    , "emodpy_malaria.malaria_config"
    , "emodpy_malaria.interventions.bednet"
    , "emodpy_malaria.interventions.drug"
    , "emodpy_malaria.interventions.irs"
    , "emodpy_malaria.interventions.ivermectin"
    , "emodpy_malaria.interventions.outdoorrestkill"
    , "emodpy_malaria.interventions.spacespraying"
    , "emodpy_malaria.interventions.sugartrap"
    , "emodpy_malaria.interventions.udbednet"
    , "emodpy_malaria.vector_config"
    , "emodpy_malaria.interventions.common"
    , "emodpy_malaria.interventions.community_health_worker"
    , "emodpy_malaria.interventions.diag_survey"
    , "emodpy_malaria.interventions.drug_campaign"
    , "emodpy_malaria.interventions.inputeir"
    , "emodpy_malaria.interventions.mosquitorelease"
    , "emodpy_malaria.interventions.outbreak"
    , "emodpy_malaria.interventions.treatment_seeking"
    , "emodpy_malaria.interventions.malaria_vector_species_params"
])
cov.start()

# First, load and run the unittest tests
from test_import import MalariaTestImports
from test_malaria_interventions import TestMalariaInterventions
from test_malaria_interventions_as_files import MalariaInterventionFileTest
from test_malaria_reporters import TestMalariaReport
from test_malaria_config import TestMalariaConfig
from test_treatment_seeking import TreatmentSeekingTest
from test_demog import DemoTest

test_classes_to_run = [MalariaTestImports,
                       TestMalariaInterventions,
                       MalariaInterventionFileTest,
                       TestMalariaReport,
                       TestMalariaConfig,
                       TreatmentSeekingTest,
                       DemoTest]

suites_list = []
for tc in test_classes_to_run:
    suite = loader.loadTestsFromTestCase(tc)
    suites_list.append(suite)
    pass

big_suite = unittest.TestSuite(suites_list)
runner = unittest.TextTestRunner()
results = runner.run(big_suite)

cov.stop()
cov.save()
cov.html_report()