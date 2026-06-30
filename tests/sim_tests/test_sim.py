from functools import partial
import os
import time
import unittest
import pytest
import sys
import json
import pathlib
import pandas as pd
from idmtools.core import ItemType
from idmtools.builders import SimulationBuilder
from idmtools.entities.experiment import Experiment
from idmtools.core.platform_factory import Platform

import emodpy.emod_task as emod_task
from emodpy.emod_task import logger

from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
import emodpy_malaria.campaign.individual_intervention as ind
import emodpy_malaria.campaign.node_intervention as node_iv
import emodpy_malaria.campaign.common as common
import emodpy_malaria.campaign.distributor as distribute
import emodpy_malaria.campaign.waning_config as waning
import emodpy_malaria.campaign.event_coordinator as ec
import emodpy_malaria.malaria_config as malaria_config
import emodpy_malaria.vector_config as vector_config
from emodpy_malaria.utils.emod_enum import (
    DiagnosticType, NonAdherenceOption,
    HabitatType, ArtificialDietTarget,
    VectorCountType, VectorGender, VaccineType,
)
from emodpy_malaria.utils.distributions import (
    ConstantDistribution, UniformDistribution, ExponentialDistribution,
)
from emodpy_malaria.utils.targeting_config import HasIP, HasIntervention, IsPregnant
from emodpy_malaria.reporters.reporters import (
    ReportEventRecorder, ReportNodeEventRecorder, ReportCoordinatorEventRecorder,
)

manifest_directory = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest
import helpers

class BaseSimTest(unittest.TestCase):

    def setUp(self) -> None:
        self.task: emod_task.EMODTask = None
        self.schema_path = manifest.schema_path
        self.eradication_path = manifest.eradication_path
        self.original_working_dir = os.getcwd()
        self.case_name = self._testMethodName
        print(f"\n{self.case_name}")
        helpers.create_failed_tests_folder()
        self.test_folder = os.path.join(manifest.failed_tests, f"{self.case_name}")
        if os.path.exists(self.test_folder):
            helpers.delete_existing_folder(self.test_folder)
        os.makedirs(self.test_folder, exist_ok=True)
        os.chdir(self.test_folder)
        self.output_path = pathlib.Path(self.test_folder).resolve()
        # sym_link=False: idmtools defaults to symlinks, but Windows requires Developer Mode
        # to create them. Using file copies instead works on all Windows configurations.
        self.platform = Platform(manifest.container_platform_name, job_directory="container_jobs",
                                 docker_image=manifest.plat_image, sym_link=False)

    def tearDown(self) -> None:
        helpers.close_idmtools_logger(logger.parent)
        if os.name == "nt":
            time.sleep(1)
        os.chdir(self.original_working_dir)

        test_failed = False
        try:
            if hasattr(self._outcome, 'errors'):
                test_failed = any(error[1] for error in self._outcome.errors)
            elif hasattr(self._outcome, 'result'):
                result = self._outcome.result
                if hasattr(result, 'errors') and hasattr(result, 'failures'):
                    test_failed = len(result.errors) > 0 or len(result.failures) > 0
        except (AttributeError, TypeError):
            test_failed = False

        delete_if_empty = test_failed
        helpers.delete_existing_folder(self.test_folder, must_be_empty=delete_if_empty)


EXAMPLES_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "examples" / "most_interventions"


def _load_example_module():
    """Import the most_interventions example module.

    Since the tests/ manifest is already loaded as sys.modules["manifest"],
    the example will use the test manifest (which has schema_file, schema_path,
    eradication_path pointing to tests/stash/).
    """
    example_str = str(EXAMPLES_DIR)
    if example_str not in sys.path:
        sys.path.insert(0, example_str)
    import importlib
    if "example" in sys.modules:
        importlib.reload(sys.modules["example"])
        return sys.modules["example"]
    return importlib.import_module("example")


def _build_most_interventions_campaign(campaign):
    """Build the comprehensive campaign from the most_interventions example."""
    mod = _load_example_module()
    return mod.build_campaign(campaign)


def _build_most_interventions_config(config):
    """Build config from the most_interventions example."""
    mod = _load_example_module()
    return mod.build_config(config)


def _build_most_interventions_demographics():
    """Build demographics from the most_interventions example."""
    mod = _load_example_module()
    return mod.build_demographics()


def _build_most_interventions_reports(reporters):
    """Build reports with event recorders only (skip DemographicsReport to avoid age bin issues)."""
    reporters.add(ReportEventRecorder(reporters, event_list=[
        "Births", "OutbreakIndividual", "AntimalarialDrug", "AdherentDrug", "MultiPackComboDrug",
        "MalariaDiagnostic", "SimpleBednet", "UsageDependentBednet",
        "MultiInsecticideUsageDependentBednet", "ScreeningHousingModification",
        "SpatialRepellentHousingModification", "SimpleIndividualRepellent",
        "IndoorIndividualEmanator", "HumanHostSeekingTrap", "Ivermectin",
        "BitingRisk", "SimpleHealthSeekingBehavior",
        "SimpleVaccine", "ControlledVaccine", "PropertyValueChanger",
        "DelayedIntervention", "StandardDiagnostic",
        "TriggeredAntimalarialDrug", "CHW_AntimalarialDrug",
        "TestedPositive", "TestedNegative", "StandardTestPositive", "StandardTestNegative",
        "TookDose", "ReceivedBednet", "UsingBednet", "DiscardedBednet",
        "ReceivedMultiBednet", "SoughtCare", "DelayedAction",
    ]))
    reporters.add(ReportNodeEventRecorder(reporters, event_list=[
        "SpaceSpraying", "IndoorSpaceSpraying",
        "MultiInsecticideSpaceSpraying", "MultiInsecticideIndoorSpaceSpraying",
        "Larvicides", "LarvalMicrosporidiaIntervention",
        "InputEIR", "MalariaChallenge", "MosquitoRelease",
        "ScaleLarvalHabitat", "OutdoorRestKill", "OutdoorNodeEmanator",
        "SugarTrap", "SpatialRepellent",
        "AnimalFeedKill", "ArtificialDiet",
        "Outbreak", "NodePropertyValueChanger",
    ]))
    reporters.add(ReportCoordinatorEventRecorder(reporters, event_list=[
        "StartVectorSurveillance", "VectorSurveyDone",
    ]))
    return reporters


@pytest.mark.container
class TestMostInterventions(BaseSimTest):

    INDIVIDUAL_BROADCAST_EVENTS = [
        "OutbreakIndividual", "AntimalarialDrug", "AdherentDrug", "MultiPackComboDrug",
        "MalariaDiagnostic", "SimpleBednet", "UsageDependentBednet",
        "MultiInsecticideUsageDependentBednet", "ScreeningHousingModification",
        "SpatialRepellentHousingModification", "SimpleIndividualRepellent",
        "IndoorIndividualEmanator", "HumanHostSeekingTrap", "Ivermectin",
        "BitingRisk", "SimpleHealthSeekingBehavior",
        "SimpleVaccine", "ControlledVaccine", "PropertyValueChanger",
        "DelayedIntervention", "StandardDiagnostic",
    ]

    NODE_BROADCAST_EVENTS = [
        "SpaceSpraying", "IndoorSpaceSpraying",
        "MultiInsecticideSpaceSpraying", "MultiInsecticideIndoorSpaceSpraying",
        "Larvicides", "LarvalMicrosporidiaIntervention",
        "InputEIR", "MalariaChallenge", "MosquitoRelease",
        "ScaleLarvalHabitat", "OutdoorRestKill", "OutdoorNodeEmanator",
        "SugarTrap", "SpatialRepellent",
        "AnimalFeedKill", "ArtificialDiet",
        "Outbreak", "NodePropertyValueChanger",
    ]

    def update_sim_random_seed(self, simulation, value):
        simulation.task.config.parameters.Run_Number = value
        return {"Run_Number": value}

    def test_most_interventions_sim_succeeds(self):
        """Run the most_interventions example as a simulation and verify it succeeds."""
        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            schema_path=str(self.schema_path),
            config_builder=_build_most_interventions_config,
            campaign_builder=_build_most_interventions_campaign,
            demographics_builder=_build_most_interventions_demographics,
            report_builder=_build_most_interventions_reports,
            embedded_python_scripts_path=str(EXAMPLES_DIR / "dtk_vector_surveillance.py"),
        )

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="Malaria_most_interventions_sim_test")
        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")
        print(f"Experiment {experiment.uid} succeeded.")

    def test_individual_interventions_distributed(self):
        """Verify that individual-level interventions are distributed by checking ReportEventRecorder."""
        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            schema_path=str(self.schema_path),
            config_builder=_build_most_interventions_config,
            campaign_builder=_build_most_interventions_campaign,
            demographics_builder=_build_most_interventions_demographics,
            report_builder=_build_most_interventions_reports,
            embedded_python_scripts_path=str(EXAMPLES_DIR / "dtk_vector_surveillance.py"),
        )

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="Malaria_individual_interventions_test")
        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        filenames = ["output/ReportEventRecorder.csv"]
        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file(), msg=f"ReportEventRecorder.csv not found for sim {simulation.uid}")

            report_df = pd.read_csv(file_path)
            events_found = set(report_df['Event_Name'].unique())

            for event in self.INDIVIDUAL_BROADCAST_EVENTS:
                event_count = len(report_df[report_df['Event_Name'] == event])
                self.assertGreater(event_count, 0,
                                   msg=f"Individual intervention '{event}' was never distributed "
                                       f"(0 events in ReportEventRecorder). Events found: {sorted(events_found)}")

    def test_node_interventions_distributed(self):
        """Verify that node-level interventions are distributed by checking ReportNodeEventRecorder."""
        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            schema_path=str(self.schema_path),
            config_builder=_build_most_interventions_config,
            campaign_builder=_build_most_interventions_campaign,
            demographics_builder=_build_most_interventions_demographics,
            report_builder=_build_most_interventions_reports,
            embedded_python_scripts_path=str(EXAMPLES_DIR / "dtk_vector_surveillance.py"),
        )

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="Malaria_node_interventions_test")
        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        filenames = ["output/ReportNodeEventRecorder.csv"]
        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportNodeEventRecorder.csv'
            self.assertTrue(file_path.is_file(), msg=f"ReportNodeEventRecorder.csv not found for sim {simulation.uid}")

            report_df = pd.read_csv(file_path)
            events_found = set(report_df['NodeEventName'].unique())

            for event in self.NODE_BROADCAST_EVENTS:
                event_count = len(report_df[report_df['NodeEventName'] == event])
                self.assertGreater(event_count, 0,
                                   msg=f"Node intervention '{event}' was never distributed "
                                       f"(0 events in ReportNodeEventRecorder). Events found: {sorted(events_found)}")


@pytest.mark.container
class TestBasicMalariaSimulation(BaseSimTest):
    """Basic malaria simulation tests for outbreak seeding and simple interventions."""

    def update_sim_random_seed(self, simulation, value):
        simulation.task.config.parameters.Run_Number = value
        return {"Run_Number": value}

    def build_demog(self):
        return MalariaDemographics.from_template_node(pop=1000)

    @staticmethod
    def set_param_fn(config, duration):
        config = malaria_config.set_team_defaults(config, manifest)
        malaria_config.add_species(config, manifest, ["arabiensis"])
        config.parameters.Simulation_Duration = duration
        config.parameters.Run_Number = 1
        config.parameters.Enable_Default_Reporting = 1
        return config

    def test_outbreak_and_demographics(self):
        """Verify outbreak seeds infection in a basic malaria sim."""
        start_day = 5

        def build_camp(campaign, timestep):
            ob = ind.OutbreakIndividual(campaign)
            distribute.add_intervention_scheduled(
                campaign,
                intervention_list=[ob],
                start_day=timestep,
                target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=1.0),
            )
            return campaign

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            schema_path=str(self.schema_path),
            campaign_builder=partial(build_camp, timestep=start_day),
            config_builder=partial(self.set_param_fn, duration=60),
            demographics_builder=self.build_demog,
        )

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="Malaria_outbreak_demographics_test")
        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        filenames = ["output/InsetChart.json"]
        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'InsetChart.json'
            self.assertTrue(file_path.is_file())

            with file_path.open(mode='r') as json_file:
                inset_chart = json.load(json_file)

            new_infection = inset_chart['Channels']['New Infections']['Data']
            self.assertEqual(sum(new_infection[:start_day]), 0,
                             msg='Expected no new infections before outbreak start day.')
            self.assertGreater(new_infection[start_day], 0,
                               msg='Expected new infections on the day after outbreak.')

            total_pop = inset_chart['Channels']['Statistical Population']['Data'][0]
            self.assertEqual(total_pop, 1000,
                             msg=f"Expected 1000 population, got {total_pop}.")

    def test_bednet_distribution(self):
        """Verify bednets are distributed at the expected coverage."""
        start_day = 5
        coverage = 0.6

        def build_camp(campaign):
            ob = ind.OutbreakIndividual(campaign)
            distribute.add_intervention_scheduled(
                campaign,
                intervention_list=[ob],
                start_day=1,
                target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.1),
            )
            bednet = ind.SimpleBednet(
                campaign,
                blocking_config=waning.Constant(0.9),
                killing_config=waning.Exponential(initial_effect=0.6, decay_time_constant=730),
                repelling_config=waning.Constant(0.0),
            )
            broadcast = ind.BroadcastEvent(campaign, broadcast_event="GotBednet")
            distribute.add_intervention_scheduled(
                campaign,
                intervention_list=[bednet, broadcast],
                start_day=start_day,
                target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=coverage),
            )
            return campaign

        def build_reports(reporters):
            reporters.add(ReportEventRecorder(reporters, event_list=["GotBednet"]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            schema_path=str(self.schema_path),
            campaign_builder=build_camp,
            config_builder=partial(self.set_param_fn, duration=30),
            demographics_builder=self.build_demog,
            report_builder=build_reports,
        )

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="Malaria_bednet_distribution_test")
        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        filenames = ["output/ReportEventRecorder.csv"]
        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())

            report_df = pd.read_csv(file_path)
            bednet_count = len(report_df[report_df['Event_Name'] == 'GotBednet'])
            self.assertAlmostEqual(bednet_count, 1000 * coverage, delta=50,
                                   msg=f'Expected ~{1000 * coverage} bednets distributed, got {bednet_count}.')

    def test_drug_treatment(self):
        """Verify antimalarial drug is distributed on positive test result."""
        diag_day = 20

        def build_camp(campaign):
            ob = ind.OutbreakIndividual(campaign)
            distribute.add_intervention_scheduled(
                campaign,
                intervention_list=[ob],
                start_day=1,
                target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=0.8),
            )
            diag = ind.MalariaDiagnostic(
                campaign,
                diagnostic_type=DiagnosticType.BLOOD_SMEAR_PARASITES,
                positive_diagnosis="TestedPositive",
                negative_diagnosis="TestedNegative",
            )
            distribute.add_intervention_scheduled(
                campaign,
                intervention_list=[diag],
                start_day=diag_day,
                target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=1.0),
            )
            drug = ind.AntimalarialDrug(campaign, drug_type="Chloroquine")
            drug_broadcast = ind.BroadcastEvent(campaign, broadcast_event="GotDrug")
            distribute.add_intervention_triggered(
                campaign,
                intervention_list=[drug, drug_broadcast],
                triggers_list=["TestedPositive"],
                start_day=1,
                target_demographics_config=common.TargetDemographicsConfig(demographic_coverage=1.0),
            )
            return campaign

        def build_reports(reporters):
            reporters.add(ReportEventRecorder(reporters,
                                              event_list=["TestedPositive", "TestedNegative", "GotDrug"]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            schema_path=str(self.schema_path),
            campaign_builder=build_camp,
            config_builder=partial(self.set_param_fn, duration=60),
            demographics_builder=self.build_demog,
            report_builder=build_reports,
        )

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="Malaria_drug_treatment_test")
        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        filenames = ["output/ReportEventRecorder.csv"]
        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())

            report_df = pd.read_csv(file_path)

            positive_count = len(report_df[report_df['Event_Name'] == 'TestedPositive'])
            drug_count = len(report_df[report_df['Event_Name'] == 'GotDrug'])
            self.assertGreater(positive_count, 0, msg='Expected some positive test results.')
            self.assertEqual(drug_count, positive_count,
                             msg=f'Expected drug count ({drug_count}) to match positive test count ({positive_count}).')


if __name__ == '__main__':
    unittest.main()
