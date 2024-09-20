#!/usr/bin/env python
import unittest
import sys
from pathlib import Path
import json
import shutil
from enum import Enum

import emod_api.campaign as camp
from emod_api.interventions.common import *
from emodpy_malaria.interventions.common import AntimalarialDrug
import emodpy_malaria.interventions.treatment_seeking as ts

parent = Path(__file__).resolve().parent
sys.path.append(parent)
import schema_path_file
import json

class TreatmentSeekingTest(unittest.TestCase):
    runInComps = False
    debug = False
    schema_path = schema_path_file.schema_path

    def __init__(self, *args, **kwargs):
        super(TreatmentSeekingTest, self).__init__(*args, **kwargs)

    # region unittest setup and teardown method
    @classmethod
    def setUpClass(cls):
        if cls.runInComps:
            # todo: setup comps connection
            pass
        camp.schema_path = cls.schema_path

    def setUp(self):
        print(f"running {self._testMethodName}:")
        pass

    def tearDown(self):
        print("end of test\n")
        pass

    # endregion

    # region unittests
    def test_custom(self):
        """
        Asserts non default values with _get_events.
        """
        start_day = 10
        drug = ['drug_1', 'drug_2', 'drug_3', 'drug4']
        targets = [
            {'trigger': 'NewInfection', 'coverage': 0.7, 'seek': 0.9, 'rate': 0.9},
            {'trigger': 'Births', 'coverage': 0.3, 'seek': 0.2, 'rate': 1.6}
        ]
        broadcast_event_name = 'Test_event'
        node_ids = [1, 2]
        ind_property_restrictions = [{"IndividualProperty1": "PropertyValue1"},
                                     {"IndividualProperty2": "PropertyValue2"}]
        # ind_property_restrictions = ["IndividualProperty1:PropertyValue1", "IndividualProperty2:PropertyValue2"]
        drug_ineligibility_duration = 5
        duration = 15

        camp.campaign_dict['Events'] = []
        ts.add_treatment_seeking(camp, start_day=start_day, drug=drug, targets=targets,
                                 node_ids=copy.deepcopy(node_ids),
                                 ind_property_restrictions=copy.deepcopy(ind_property_restrictions),
                                 duration=duration, drug_ineligibility_duration=drug_ineligibility_duration,
                                 broadcast_event_name=broadcast_event_name)

        self.assertEqual(len(camp.campaign_dict['Events']), len(targets))
        for event in camp.campaign_dict["Events"]:
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']['class'],
                             'NodeLevelHealthTriggeredIV')
            self.assertEqual(event['Start_Day'], 10)
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['class'], 'MultiInterventionDistributor')
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Property_Restrictions_Within_Node"], ind_property_restrictions)
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Duration"], duration)
            for intervention in event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['Intervention_List']:
                if intervention["class"] == "DelayedIntervention":
                    anti_malaria_drugs = intervention['Actual_IndividualIntervention_Configs'][0:4]
                    self.assertListEqual(drug, [d['Drug_Type'] for d in anti_malaria_drugs])

                    broadcast_event = intervention['Actual_IndividualIntervention_Configs'][4]
                    self.assertEqual(broadcast_event_name, broadcast_event['Broadcast_Event'])

                elif intervention["class"] == "PropertyValueChanger":
                    self.assertEqual(intervention["Revert"], drug_ineligibility_duration)
                else:
                    self.assertTrue(False, msg="Wrong event in intervention.")

            if event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"] == ["NewInfection"]:
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Demographic_Coverage"], 0.7 * 0.9)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Min"], 0)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Max"], 125)
                self.assertAlmostEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['Intervention_List'][0]["Delay_Period_Exponential"], 1/0.9)
            elif event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"] == ["Births"]:
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Demographic_Coverage"], 0.3 * 0.2)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Min"], 0)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Max"], 125)
                self.assertAlmostEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['Intervention_List'][0]["Delay_Period_Exponential"], 1/1.6)
            elif event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"] == ["Births"]:
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Demographic_Coverage"], 0.3 * 0.2)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Min"], 0)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Max"], 125)
                self.assertAlmostEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']["Delay_Period_Exponential"], 1/1.6)



    def test_default(self):
        """
        Asserts default values with _get_events.
        """
        camp.campaign_dict['Events'] = []
        ts.add_treatment_seeking(camp)

        drug = ['Artemether', 'Lumefantrine']
        targets = [
            {'trigger': 'NewClinicalCase', 'coverage': 0.1, 'agemin': 15, 'agemax': 70, 'seek': 0.4, 'rate': 0.3},
            {'trigger': 'NewSevereCase', 'coverage': 0.8, 'seek': 0.6, 'rate': 0.5}]
        broadcast_event_name = 'Received_Treatment'

        self.assertEqual(len(camp.campaign_dict['Events']), len(targets))
        for event in camp.campaign_dict["Events"]:
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']['class'],
                             'NodeLevelHealthTriggeredIV')
            self.assertEqual(event['Start_Day'], 1)
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['class'], 'DelayedIntervention')
            for intervention in event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['Actual_IndividualIntervention_Configs']:
                if intervention["class"] == "BroadcastEvent":
                    self.assertEqual(intervention["Broadcast_Event"], broadcast_event_name)
                else:
                    self.assertEqual(intervention["class"], "AntimalarialDrug")
                    self.assertIn(intervention["Drug_Type"], drug)

            if event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"] == ["NewClinicalCase"]:
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Demographic_Coverage"], 0.1 * 0.4)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Min"], 15)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Max"], 70)
                self.assertAlmostEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']["Delay_Period_Exponential"], 3.3333333)
            elif event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"] == ["NewSevereCase"]:
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Demographic_Coverage"], 0.8 * 0.6)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Min"], 0)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Max"], 125)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']["Delay_Period_Exponential"], 2)




    def validate_campaign(self, broadcast_event_name, campaign, drug, targets, drug_ineligibility_duration=0,
                          duration=-1, ind_property_restrictions=None, node_ids=None, start_day=1):
        if not ind_property_restrictions:
            ind_property_restrictions = []

        events = camp.campaign_dict['Events']
        self.assertEqual(len(events), len(targets))

        intervention_list = [AntimalarialDrug(camp, Drug_Type=d) for d in drug]
        intervention_list.append(BroadcastEvent(camp, Event_Trigger=broadcast_event_name))
        for i in range(len(events)):
            event = events[i]
            # test start day
            self.assertEqual(start_day, event['Start_Day'])
            # test 3rd class == NodeLevelHealthTriggeredIV
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']['class'],
                             'NodeLevelHealthTriggeredIV')
            # test 4th class == MultiInterventionDistributor
            print(event['Event_Coordinator_Config']['Intervention_Config'][
                      'Actual_IndividualIntervention_Config'])
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['class'], 'MultiInterventionDistributor')

            # test rate
            if targets[i]['rate'] > 0:  # delayed intervention, code may be changed later
                delayed_intervention = event['Event_Coordinator_Config']['Intervention_Config'][
                    'Actual_IndividualIntervention_Config']['Intervention_List'][0]
                actual_config = delayed_intervention['Actual_IndividualIntervention_Configs']
                self.assertEqual(delayed_intervention['class'], 'DelayedIntervention')
                self.assertEqual(delayed_intervention['Delay_Period_Exponential'], 1 / targets[i]['rate'])
            else:
                actual_config = event['Event_Coordinator_Config']['Intervention_Config'][
                    'Actual_IndividualIntervention_Config']['Intervention_List'][0][
                    'Intervention_List']
            # test actual intervention list
            self.assertEqual(len(actual_config), len(intervention_list))

            # test coverage and seek
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']['Demographic_Coverage'],
                             targets[i]['coverage'] * targets[i]['seek'])

            # test Nodeset_Config
            expected_nodeset_config = {
                "Node_List": node_ids,
                "class": "NodeSetNodeList"
            } if node_ids else {"class": "NodeSetAll"}
            self.assertEqual(expected_nodeset_config, event['Nodeset_Config'])

            property_restrictions_param = "Property_Restrictions"
            if ind_property_restrictions:
                if isinstance(ind_property_restrictions[0], dict):
                    property_restrictions_param = "Property_Restrictions_Within_Node"
            # test ind_property_restrictions
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']
                             [property_restrictions_param],  # Property_Restrictions_Within_Node
                             ind_property_restrictions)

            # test duration
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']['Duration'],
                             duration)


    # endregion


if __name__ == '__main__':
    unittest.main()
