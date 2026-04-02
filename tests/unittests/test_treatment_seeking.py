#!/usr/bin/env python
import unittest
import sys
from pathlib import Path
import json
import shutil
from enum import Enum

import emod_api.campaign as camp
from emod_api.interventions.common import *
from emodpy_malaria.interventions.drug import _antimalarial_drug
import emodpy_malaria.interventions.treatment_seeking as ts

parent = Path(__file__).resolve().parent
sys.path.append(parent)
from . import schema_path_file
import json

DEFAULT_MAX_AGE = 1000

class TreatmentSeekingTest(unittest.TestCase):
    runInComps = False
    debug = False
    schema_path = schema_path_file.schema_file

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
        drug = ['drug_1', 'drug_2', 'drug_3', 'drug_4']
        targets = [
            {'trigger': 'NewInfectionEvent', 'coverage': 0.7,  'rate': 0.9},
            {'trigger': 'Births', 'coverage': 0.3, 'rate': 1.6}
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
                                 'Actual_IndividualIntervention_Config']['class'], 'DelayedIntervention')
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Property_Restrictions_Within_Node"], ind_property_restrictions)
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Duration"], duration)
            testdrug_found = False
            testdrug2_found = False
            testdrug3_found = False
            testdrug4_found = False
            broadcast_found = False
            property_changer_found = False
            for intervention in event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['Actual_IndividualIntervention_Configs']:
                if intervention["class"] == "AntimalarialDrug":
                    if intervention["Drug_Type"] == "drug_1":
                        self.assertEqual(intervention['Intervention_Name'],
                                         "AntimalarialDrug_drug_1")
                        testdrug_found = True
                    elif intervention["Drug_Type"] == "drug_2":
                        self.assertEqual(intervention["Drug_Type"], "drug_2")
                        self.assertEqual(intervention['Intervention_Name'],
                                         "AntimalarialDrug_drug_2")
                        testdrug2_found = True
                    elif intervention["Drug_Type"] == "drug_3":
                        self.assertEqual(intervention['Intervention_Name'],
                                         "AntimalarialDrug_drug_3")
                        testdrug3_found = True
                    else:
                        self.assertEqual(intervention["Drug_Type"], "drug_4")
                        self.assertEqual(intervention['Intervention_Name'],
                                         "AntimalarialDrug_drug_4")
                        testdrug4_found = True
                elif intervention["class"] == "BroadcastEvent":
                    broadcast_found = True
                    self.assertEqual(intervention["Broadcast_Event"], broadcast_event_name)
                else:
                    self.assertEqual(intervention["class"], "PropertyValueChanger")
                    property_changer_found = True
                    self.assertEqual(intervention["Daily_Probability"], 1)
                    self.assertEqual(intervention["Revert"], drug_ineligibility_duration)
                    self.assertEqual(intervention["Target_Property_Key"], "DrugStatus")
                    self.assertEqual(intervention["Target_Property_Value"], "RecentDrug")
            self.assertTrue(testdrug_found and testdrug2_found and broadcast_found and property_changer_found and testdrug3_found and testdrug4_found)

            if event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"] == ["NewInfectionEvent"]:
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Demographic_Coverage"], 0.7 )
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Min"], 0)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Max"], DEFAULT_MAX_AGE)
                self.assertAlmostEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']["Delay_Period_Exponential"], 1/0.9)
            elif event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"] == ["Births"]:
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Demographic_Coverage"], 0.3 )
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Min"], 0)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Max"], DEFAULT_MAX_AGE)
                self.assertAlmostEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']["Delay_Period_Exponential"], 1/1.6)
            elif event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"] == ["Births"]:
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Demographic_Coverage"], 0.3 )
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Min"], 0)
                self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Max"], DEFAULT_MAX_AGE)
                self.assertAlmostEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']["Delay_Period_Exponential"], 1/1.6)



    def test_default(self):
        """
        Asserts default values with _get_events.
        """
        camp.campaign_dict['Events'] = []
        ts.add_treatment_seeking(camp, targets=[{"trigger": "HappyBirthday"}])

        drug = ['Artemether', 'Lumefantrine']
        broadcast_event_name = 'Received_Treatment'
        for event in camp.campaign_dict["Events"]:
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']['class'],
                             'NodeLevelHealthTriggeredIV')
            self.assertEqual(event['Start_Day'], 1)
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['class'], 'MultiInterventionDistributor')
            for intervention in event['Event_Coordinator_Config']['Intervention_Config'][
                                 'Actual_IndividualIntervention_Config']['Intervention_List']:
                if intervention["class"] == "BroadcastEvent":
                    self.assertEqual(intervention["Broadcast_Event"], broadcast_event_name)
                else:
                    self.assertEqual(intervention["class"], "AntimalarialDrug")
                    self.assertIn(intervention["Drug_Type"], drug)
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"], ["HappyBirthday"])
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Demographic_Coverage"], 1)
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Min"], 0)
            self.assertEqual(event['Event_Coordinator_Config']['Intervention_Config']["Target_Age_Max"], DEFAULT_MAX_AGE)






    def validate_campaign(self, broadcast_event_name, campaign, drug, targets, drug_ineligibility_duration=0,
                          duration=-1, ind_property_restrictions=None, node_ids=None, start_day=1):
        if not ind_property_restrictions:
            ind_property_restrictions = []

        events = camp.campaign_dict['Events']
        self.assertEqual(len(events), len(targets))

        intervention_list = [_antimalarial_drug(camp, drug_type=d) for d in drug]
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
