#!/usr/bin/env python
import unittest
from emodpy_malaria.interventions.common import add_campaign_event
import emod_api.campaign as campaign

from pathlib import Path
import sys

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))
import schema_path_file

campaign.set_schema(schema_path_file.schema_path)
schema_path = schema_path_file.schema_path


class CommonInterventionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_scheduled_campaign_event(self):
        campaign.campaign_dict["Events"] = []
        target_num_individuals = 123
        campaign.schema_path = schema_path_file.schema_file
        add_campaign_event(campaign,
                           start_day=30,
                           node_ids=[1, 2],
                           target_num_individuals=target_num_individuals,
                           individual_intervention=["some_intervention"]
                           )
        event = campaign.campaign_dict["Events"][0]
        self.assertEqual(event.Event_Coordinator_Config.Target_Num_Individuals, target_num_individuals)
