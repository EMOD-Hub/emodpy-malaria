from functools import partial
import unittest
import sys
from pathlib import Path
import pandas as pd

from idmtools.core import ItemType
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy.utils import EradicationBambooBuilds
import emod_api.campaign as camp
import emodpy_malaria.interventions.treatment_seeking as ts
from emodpy_malaria.interventions.outbreak import add_outbreak_individual
parent = Path(__file__).resolve().parent
sys.path.append(parent)

import config_support


class TestHealthSeeking(unittest.TestCase):

    def setUp(self):
        self.platform = Platform("SLURMStage")
        self.plan = EradicationBambooBuilds.MALARIA_LINUX
        self.schema_path = parent / 'inputs' / 'bin' / 'schema.json'
        self.eradication = parent / 'inputs' / 'bin' / 'Eradication'
        self.manifest = self.dotdict({"schema_file": str(self.schema_path), "eradication_file": str(self.eradication)})

    def update_sim_random_seed(self, simulation, value):
        simulation.task.config.parameters.Run_Number = value
        return {"Run_Number": value}

    def build_demog(self):
        import emodpy_malaria.demographics.MalariaDemographics as Demographics
        demog = Demographics.from_template_node(lat=0, lon=0, pop=1000, name=1, forced_id=1)
        return demog

    def build_camp_1(self, targets):
        camp.schema_path = str(self.schema_path)
        ts.add_treatment_seeking(camp, targets=targets)
        add_outbreak_individual(campaign=camp)
        return camp

    def build_camp_2(self, start_day, drug, targets):
        camp.schema_path = str(self.schema_path)
        ret_events = ts._get_events(camp, start_day=start_day, drug=drug, targets=targets)
        first = True
        for ret_event in ret_events:
            camp.add(ret_event, first=first)
            if first:
                first = False
        add_outbreak_individual(campaign=camp)

        return camp

    class dotdict(dict):
        # Allows dot notation to attributes
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__

    def test_delayed_health_seeking(self):
        coverage = 0.9
        seek = 0.9
        targets = [
            {'trigger': 'NewClinicalCase', 'coverage': coverage, 'seek': seek, 'rate': 0.1}
        ]

        task = emod_task.EMODTask.from_default2(
            config_path="default_config.json",
            eradication_path=str(self.eradication),
            campaign_builder=partial(self.build_camp_1, targets),
            schema_path=str(self.schema_path),
            param_custom_cb=partial(config_support.set_param_fn, manifest=self.manifest,
                                    set_config_fn=config_support.set_config, duration=365),
            ep4_custom_cb=None,
            demog_builder=self.build_demog,
            plugin_report=None
        )

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="Delayed Health Seeking Test")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)
        output_path = Path(parent, "inputs")
        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=output_path)
            # validate files exist
            local_path = output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            event_df = pd.read_csv(file_path)
            event_count = event_df['Event_Name'].value_counts()
            new_clinical_count = event_count['NewClinicalCase']
            treatment_count = event_count['Received_Treatment']
            self.assertGreater(coverage * seek, treatment_count / new_clinical_count,
                               msg=f'Test failed: expected treatment fraction should be less than {coverage * seek}, '
                                   f'got {treatment_count / new_clinical_count}')

    def test_health_seeking(self):
        start_day = 10
        coverage = 0.7
        seek = 0.9
        drug = ['Abstract', 'Amodiaquine', 'DHA']
        targets = [
            {'trigger': 'NewInfectionEvent', 'coverage': coverage, 'seek': seek, 'rate': 0}
        ]

        task = emod_task.EMODTask.from_default2(
            config_path="default_config.json",
            eradication_path=str(self.eradication),
            campaign_builder=partial(self.build_camp_2, start_day, drug, targets),
            schema_path=str(self.schema_path),
            param_custom_cb=partial(config_support.set_param_fn, manifest=self.manifest,
                                    set_config_fn=config_support.set_config),
            ep4_custom_cb=None,
            demog_builder=self.build_demog,
            plugin_report=None
        )

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="Health Seeking Test")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")

        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)
        output_path = Path(parent, "inputs")
        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=output_path)
            # validate files exist
            local_path = output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            event_df = pd.read_csv(file_path)
            event_df = event_df[event_df['Time'] > start_day]
            event_count = event_df['Event_Name'].value_counts()
            new_infection_count = event_count['NewInfectionEvent']
            treatment_count = event_count['Received_Treatment']
            self.assertAlmostEqual(treatment_count/new_infection_count, coverage * seek, delta=0.01,
                                   msg=f'Test failed: expected treatment fraction is {coverage * seek}, got '
                                       f'{treatment_count/new_infection_count}')


if __name__ == '__main__':
    unittest.main()
