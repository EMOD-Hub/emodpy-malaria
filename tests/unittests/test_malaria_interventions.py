import json
import os
import sys
import unittest

import schema_path_file
import random
import pandas as pd

from emodpy_malaria.interventions.ivermectin import add_scheduled_ivermectin, add_triggered_ivermectin
from emodpy_malaria.interventions.bednet import add_itn_scheduled, add_itn_triggered
from emodpy_malaria.interventions.outdoorrestkill import add_outdoorrestkill
from emodpy_malaria.interventions.usage_dependent_bednet import add_scheduled_usage_dependent_bednet, \
    add_triggered_usage_dependent_bednet
from emodpy_malaria.interventions import drug_campaign
from emodpy_malaria.interventions import diag_survey
from emodpy_malaria.interventions.drug import _antimalarial_drug
from emodpy_malaria.interventions.common import _malaria_diagnostic
from emodpy_malaria.interventions.mosquitorelease import add_scheduled_mosquito_release
from emodpy_malaria.interventions.inputeir import add_scheduled_input_eir
from emodpy_malaria.interventions.outbreak import *
from emodpy_malaria.interventions.vaccine import *
from emodpy_malaria.interventions.irs import *
from emodpy_malaria.interventions.spacespraying import add_scheduled_space_spraying
from emodpy_malaria.interventions.sugartrap import add_scheduled_sugar_trap
from emodpy_malaria.interventions.larvicide import add_larvicide
from emodpy_malaria.interventions.community_health_worker import add_community_health_worker
from emodpy_malaria.interventions.scale_larval_habitats import add_scale_larval_habitats
from emodpy_malaria.interventions.malaria_challenge import add_challenge_trial
from emodpy_malaria.interventions.treatment_seeking import add_treatment_seeking
from emodpy_malaria.interventions.outdoor_node_emanator import add_outdoor_node_emanator_scheduled
from emodpy_malaria.interventions.indoor_individual_emanator import (add_indoor_individual_emanator_triggered,
                                                                     add_indoor_individual_emanator_scheduled)
from emod_api.utils import Distributions
import emod_api.campaign as camp

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
camp.unsafe = True

drug_codes = ["ALP", "AL", "ASA", "DP", "DPP", "PPQ", "DHA_PQ", "DHA", "PMQ", "DA", "CQ", "SP", "SPP", "SPA"]


class WaningEffects:
    Box = "WaningEffectBox"
    Constant = "WaningEffectConstant"
    Exp = "WaningEffectExponential"
    BoxExp = "WaningEffectBoxExponential"


class WaningParams:
    Box_Duration = "Box_Duration"
    Decay_Time = "Decay_Time_Constant"
    Initial = "Initial_Effect"
    Class = "class"


class NodesetParams:
    Class = "class"
    SetAll = "NodeSetAll"
    SetList = "NodeSetNodeList"
    Node_List = "Node_List"


class TestMalariaInterventions(unittest.TestCase):
    # region helper methods
    def setUp(self) -> None:
        self.is_debugging = False
        self.tmp_intervention = None
        self.nodeset = None
        self.start_day = None
        self.event_coordinator = None
        self.intervention_config = None
        self.killing_config = None
        self.blocking_config = None
        self.repelling_config = None
        self.usage_config = None
        self.schema_file = schema_path_file.schema_file
        camp.set_schema(self.schema_file)
        return

    def write_debug_files(self):
        with open(f'DEBUG_{self._testMethodName}.json', 'w') as outfile:
            json.dump(self.tmp_intervention, outfile, indent=4, sort_keys=True)
        return

    def parse_intervention_parts(self):
        self.nodeset = self.tmp_intervention['Nodeset_Config']
        self.start_day = self.tmp_intervention['Start_Day']
        self.event_coordinator = self.tmp_intervention['Event_Coordinator_Config']
        self.intervention_config = self.event_coordinator['Intervention_Config']
        if "Intervention_List" in self.intervention_config:
            self.intervention_config = self.intervention_config["Intervention_List"][0]
        if "Killing_Config" in self.intervention_config:
            self.killing_config = self.intervention_config["Killing_Config"]
        if "Larval_Killing_Config" in self.intervention_config:
            self.killing_config = self.intervention_config["Larval_Killing_Config"]
        if "Blocking_Config" in self.intervention_config:
            self.blocking_config = self.intervention_config["Blocking_Config"]
        if "Repelling_Config" in self.intervention_config:
            self.repelling_config = self.intervention_config["Repelling_Config"]
        if "Usage_Config" in self.intervention_config:
            self.usage_config = self.intervention_config["Usage_Config"]

    def tearDown(self) -> None:
        camp.reset()
        if self.is_debugging:
            self.write_debug_files()
        return

    # endregion

    # region Ivermectin

    def ivermectin_build(self,
                         start_day=0,
                         target_coverage=1.0,
                         target_num_individuals=None,
                         node_ids=None,
                         ind_property_restrictions=None,
                         killing_initial_effect=1.0,
                         killing_duration_box=0,
                         killing_decay_time_constant=0.0,
                         insecticide="",
                         cost=1,
                         intervention_name="Ivermectin"):
        camp.campaign_dict["Events"] = []  # resetting
        add_scheduled_ivermectin(campaign=camp,
                                 start_day=start_day,
                                 demographic_coverage=target_coverage,
                                 target_num_individuals=target_num_individuals,
                                 node_ids=node_ids,
                                 ind_property_restrictions=ind_property_restrictions,
                                 killing_initial_effect=killing_initial_effect,
                                 killing_box_duration=killing_duration_box,
                                 killing_decay_time_constant=killing_decay_time_constant,
                                 insecticide=insecticide,
                                 cost=cost,
                                 intervention_name=intervention_name
                                 )
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.killing_config = self.intervention_config['Killing_Config']
        return

    def test_ivermectin_box_default(self):
        self.is_debugging = False
        self.assertIsNone(self.tmp_intervention)
        self.ivermectin_build(killing_duration_box=3)
        self.assertIsNotNone(self.tmp_intervention)
        self.assertEqual(self.start_day, 0)
        self.assertEqual(self.event_coordinator['Demographic_Coverage'],
                         1.0)
        self.assertEqual(self.killing_config[WaningParams.Initial], 1.0)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.Box)
        return

    def test_ivermectin_exponential_default(self):
        self.is_debugging = False
        self.ivermectin_build(killing_decay_time_constant=10)
        self.assertEqual(self.killing_config[WaningParams.Initial], 1.0)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 10)
        self.assertEqual(self.killing_config['class'], WaningEffects.Exp)
        pass

    def test_ivermectin_boxexponential_default(self):
        self.is_debugging = False
        self.ivermectin_build(killing_decay_time_constant=4,
                              killing_duration_box=3,
                              killing_initial_effect=0.8)
        self.assertEqual(self.killing_config[WaningParams.Initial], 0.8)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 4)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 3)
        pass

    def test_ivermectin_custom_everything(self):
        self.ivermectin_build(
            start_day=123,
            target_coverage=0.87,
            killing_initial_effect=0.76,
            killing_duration_box=12,
            killing_decay_time_constant=5
        )
        self.assertEqual(self.start_day, 123)
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], 0.87)
        self.assertEqual(self.killing_config[WaningParams.Initial], 0.76)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 12)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 5)
        self.assertEqual(self.killing_config['class'], WaningEffects.BoxExp)
        pass

    def test_ivermectin_num_individuals(self):
        self.is_debugging = False
        self.ivermectin_build(target_num_individuals=354,
                              killing_duration_box=3,
                              insecticide="testtest",
                              cost=234,
                              )
        self.assertEqual(self.event_coordinator['Target_Num_Individuals'], 354)
        self.assertIn('Individual_Selection_Type', self.event_coordinator)
        self.assertEqual(self.event_coordinator['Individual_Selection_Type'], 'TARGET_NUM_INDIVIDUALS')
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 3)
        # self.assertNotIn('Demographic_Coverage', self.event_coordinator)
        # TODO: uncomment that assertion later
        pass

    def test_triggered_ivermectin(self):
        camp.campaign_dict["Events"] = []
        start_day = 21
        triggers = ["Testing", "123"]
        duration = 34
        delay = 5
        demog_cov = 0.75
        ind_prop = ["Risk:High"]
        init_eff = 0.88
        box = 33
        decay = 55
        name = "Yuppers"
        insecticide = "BugSpray"
        cost = 1.5
        nodes = [23, 12, 3]
        add_triggered_ivermectin(campaign=camp, start_day=start_day,
                                 trigger_condition_list=triggers,
                                 listening_duration=duration, delay_period_constant=delay,
                                 demographic_coverage=demog_cov, node_ids=nodes,
                                 ind_property_restrictions=ind_prop, killing_initial_effect=init_eff,
                                 killing_box_duration=box, killing_decay_time_constant=decay,
                                 intervention_name=name,
                                 insecticide=insecticide, cost=cost)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], nodes)
        triggered_intervention = campaign_event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(triggered_intervention['Demographic_Coverage'], demog_cov)
        self.assertEqual(triggered_intervention['Duration'], duration)
        self.assertEqual(triggered_intervention['Trigger_Condition_List'], triggers)
        self.assertEqual(triggered_intervention['Property_Restrictions'], ind_prop)
        delayed_intervention = triggered_intervention["Actual_IndividualIntervention_Config"]
        self.assertEqual(delayed_intervention['Delay_Period_Constant'], delay)
        self.assertEqual(delayed_intervention['Delay_Period_Distribution'], "CONSTANT_DISTRIBUTION")
        ivermectin = delayed_intervention["Actual_IndividualIntervention_Configs"][0]
        self.assertEqual(ivermectin['Insecticide_Name'], insecticide)
        self.assertEqual(ivermectin['Intervention_Name'], name)
        self.assertEqual(ivermectin['Cost_To_Consumer'], cost)
        self.killing_config = ivermectin['Killing_Config']
        self.assertEqual(self.killing_config[WaningParams.Initial], init_eff)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], box)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], decay)

    # endregion

    # region drug_campaign

    def test_drug_campaign_MDA(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "MDA"
        coverage = 0.78
        # self.test_drug_campaign(campaign_type)
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(campaign=camp, campaign_type=campaign_type,
                                            drug_code=drug_code, repetitions=3, tsteps_btwn_repetitions=100,
                                            coverage=coverage)
        # camp.save("campaign_mda.json") # can be used for debugging, writes out a file
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Number_Repetitions'], 3)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Timesteps_Between_Repetitions'],
                         100)
        self.assertEqual(camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Demographic_Coverage'], coverage)
        self.assertEqual(
            camp.campaign_dict['Events'][0]['Event_Coordinator_Config']['Intervention_Config']['Intervention_List'][0][
                'Intervention_Name'],
            "AntimalarialDrug_Artemether")

    def test_drug_campaign_MSAT(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "MSAT"
        # self.test_drug_campaign(campaign_type)
        coverage = 0.89
        drug_codes = ["AL"]

        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(campaign=camp, campaign_type=campaign_type,
                                            drug_code=drug_code, repetitions=3, tsteps_btwn_repetitions=100,
                                            coverage=coverage)

        # camp.save("campaign_msat.json") # can be used for debugging, writes out a file
        self.assertEqual(len(camp.campaign_dict['Events']), 2)
        for event in camp.campaign_dict['Events']:
            if event['Event_Coordinator_Config']['Intervention_Config']['Intervention_Name'] == "MalariaDiagnostic":
                self.assertEqual(event['Event_Coordinator_Config']['Number_Repetitions'], 3)
                self.assertEqual(event['Event_Coordinator_Config']['Timesteps_Between_Repetitions'], 100)
                self.assertEqual(event['Event_Coordinator_Config']['Demographic_Coverage'], coverage)
            elif event['Event_Coordinator_Config']['Intervention_Config'][
                'Intervention_Name'] == "NodeLevelHealthTriggeredIV":
                self.assertEqual(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_Name'], "AntimalarialDrug_Artemether")
            else:
                self.assertTrue(False, "Unexpected intervention in campaign.")

    def test_drug_campaign_fMDA(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "fMDA"
        coverage = 0.89
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(campaign=camp, campaign_type=campaign_type,
                                            drug_code=drug_code,
                                            coverage=coverage)

        # camp.save("campaign_fmda.json")  # can be used for debugging, writes out a file
        self.assertEqual(len(camp.campaign_dict['Events']), 3)
        for event in camp.campaign_dict['Events']:
            if event['Event_Coordinator_Config']['Intervention_Config']['Intervention_Name'] == "MalariaDiagnostic":
                self.assertEqual(len(event['Event_Coordinator_Config']['Intervention_Config']['Intervention_List']), 2)
            elif event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                'Intervention_Name'] == "BroadcastEventToOtherNodes":
                self.assertEqual(len(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_List']), 2)
            elif event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                'Intervention_Name'] == "AntimalarialDrug_Artemether":
                self.assertEqual(len(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_List']), 3)
            else:
                self.assertTrue(False, "Unexpected intervention in campaign.")

    def test_drug_campaign_rfMDA(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "rfMDA"
        coverage = 0.89
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(campaign=camp, campaign_type=campaign_type,
                                            drug_code=drug_code, fmda_radius=6,
                                            coverage=coverage)

        camp.save("campaign_rfmda.json")  # can be used for debugging, writes out a file
        self.assertEqual(len(camp.campaign_dict['Events']), 2)
        for event in camp.campaign_dict['Events']:
            if 'Actual_IndividualIntervention_Configs' in event['Event_Coordinator_Config']['Intervention_Config'][
                'Actual_IndividualIntervention_Config']:
                self.assertEqual(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Actual_IndividualIntervention_Configs'][0]['class'], "BroadcastEventToOtherNodes")
                self.assertEqual(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Actual_IndividualIntervention_Configs'][0]['Max_Distance_To_Other_Nodes_Km'], 6)
            elif event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                'Intervention_Name'] == "AntimalarialDrug_Artemether":
                self.assertEqual(len(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_List']), 3)
            else:
                self.assertTrue(False, "Unexpected intervention in campaign.")

    def test_drug_campaign_rfMSAT(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "rfMSAT"
        coverage = 0.89
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(campaign=camp, campaign_type=campaign_type,
                                            drug_code=drug_code, fmda_radius=6,
                                            coverage=coverage)

        camp.save("campaign_rfmsat.json")  # can be used for debugging, writes out a file
        self.assertEqual(len(camp.campaign_dict['Events']), 3)
        for event in camp.campaign_dict['Events']:
            if 'Actual_IndividualIntervention_Configs' in event['Event_Coordinator_Config']['Intervention_Config'][
                'Actual_IndividualIntervention_Config']:
                self.assertEqual(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Actual_IndividualIntervention_Configs'][0]['class'], "BroadcastEventToOtherNodes")
                self.assertEqual(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Actual_IndividualIntervention_Configs'][0]['Max_Distance_To_Other_Nodes_Km'], 6)
            elif event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                'Intervention_Name'] == "AntimalarialDrug_Artemether":
                self.assertEqual(len(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_List']), 3)
            elif event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                'Intervention_Name'] == "MalariaDiagnostic":
                self.assertEqual(len(
                    event['Event_Coordinator_Config']['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        'Intervention_List']), 2)
            else:
                self.assertTrue(False, "Unexpected intervention in campaign.")

    # end region

    # region bednet
    def test_bednet_default(self):
        camp.campaign_dict["Events"] = []
        self.is_debugging = False
        add_itn_scheduled(campaign=camp)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], 1.0)
        self.assertEqual(self.start_day, 0)

        self.assertEqual(self.event_coordinator["Intervention_Config"]["Killing_Config"]["Initial_Effect"], 0.6)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Blocking_Config"]["Initial_Effect"], 0.9)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Repelling_Config"]["Initial_Effect"], 0)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Usage_Config"]["Initial_Effect"], 1)
        self.assertAlmostEqual(self.event_coordinator["Intervention_Config"]["Killing_Config"]["Decay_Time_Constant"],
                               7300)
        self.assertAlmostEqual(self.event_coordinator["Intervention_Config"]["Blocking_Config"]["Decay_Time_Constant"],
                               7300)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Killing_Config"]["class"],
                         "WaningEffectExponential")
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Blocking_Config"]["class"],
                         "WaningEffectExponential")
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Repelling_Config"]["class"],
                         "WaningEffectConstant")
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Usage_Config"]["class"],
                         "WaningEffectConstant")
        self.assertEqual(self.event_coordinator['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        return

    def test_bednet_custom(self):
        camp.campaign_dict["Events"] = []
        self.is_debugging = False
        start_day = 11
        coverage_by_ages = [{"coverage": 0.55, "min": 1, "max": 10},
                            {"coverage": 0.33, "min": 11, "max": 50}]
        demographic_coverage = 0.4
        node_ids = [3, 45, 3453453]
        repetitions = 3
        timesteps_between_repetitions = 700
        ind_property_restrictions = [{"Book": "Smart", "Hi": "There"}, {"Mellow": "Yellow"}]
        receiving_itn_broadcast_event = "GotMeANet"
        blocking_initial_effect = 0.11
        blocking_box_duration = 12
        blocking_decay_time_constant = 13
        killing_initial_effect = 0.22
        killing_box_duration = 23
        killing_decay_time_constant = 24
        repelling_initial_effect = 0.33
        repelling_box_duration = 34
        repelling_decay_time_constant = 35
        usage_initial_effect = 0.44
        usage_box_duration = 45
        usage_decay_time_constant = 46
        insecticide = "NoMoreBugs"
        cost = 1.23
        intervention_name = "TestingBednet"

        add_itn_scheduled(campaign=camp,
                          start_day=start_day,
                          coverage_by_ages=coverage_by_ages,
                          demographic_coverage=demographic_coverage,
                          node_ids=node_ids,
                          repetitions=repetitions,
                          timesteps_between_repetitions=timesteps_between_repetitions,
                          ind_property_restrictions=ind_property_restrictions,
                          receiving_itn_broadcast_event=receiving_itn_broadcast_event,
                          blocking_initial_effect=blocking_initial_effect,
                          blocking_box_duration=blocking_box_duration,
                          blocking_decay_time_constant=blocking_decay_time_constant,
                          killing_initial_effect=killing_initial_effect,
                          killing_box_duration=killing_box_duration,
                          killing_decay_time_constant=killing_decay_time_constant,
                          repelling_initial_effect=repelling_initial_effect,
                          repelling_box_duration=repelling_box_duration,
                          repelling_decay_time_constant=repelling_decay_time_constant,
                          usage_initial_effect=usage_initial_effect,
                          usage_box_duration=usage_box_duration,
                          usage_decay_time_constant=usage_decay_time_constant,
                          insecticide=insecticide,
                          cost=cost,
                          intervention_name=intervention_name)
        for event in camp.campaign_dict["Events"]:
            self.tmp_intervention = event
            self.parse_intervention_parts()
            self.assertEqual(event["Start_Day"], start_day)
            intervention_list = self.tmp_intervention["Event_Coordinator_Config"]["Intervention_Config"][
                "Intervention_List"]
            if intervention_list[0]["class"] == "SimpleBednet":
                broadcast_intervention = intervention_list[1]
                self.intervention_config = intervention_list[0]
            else:
                self.intervention_config = intervention_list[1]
                broadcast_intervention = intervention_list[0]
            self.killing_config = self.intervention_config['Killing_Config']
            self.blocking_config = self.intervention_config['Blocking_Config']
            self.repelling_config = self.intervention_config['Repelling_Config']
            self.killing_config = self.intervention_config['Killing_Config']
            self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
            self.assertEqual(self.killing_config[WaningParams.Box_Duration], killing_box_duration)
            self.assertEqual(self.killing_config[WaningParams.Decay_Time], killing_decay_time_constant)
            self.assertEqual(self.blocking_config[WaningParams.Initial], blocking_initial_effect)
            self.assertEqual(self.blocking_config[WaningParams.Box_Duration], blocking_box_duration)
            self.assertEqual(self.blocking_config[WaningParams.Decay_Time], blocking_decay_time_constant)
            self.assertEqual(self.repelling_config[WaningParams.Initial], repelling_initial_effect)
            self.assertEqual(self.repelling_config[WaningParams.Box_Duration], repelling_box_duration)
            self.assertEqual(self.repelling_config[WaningParams.Decay_Time], repelling_decay_time_constant)
            self.assertEqual(self.usage_config[WaningParams.Initial], usage_initial_effect)
            self.assertEqual(self.usage_config[WaningParams.Box_Duration], usage_box_duration)
            self.assertEqual(self.usage_config[WaningParams.Decay_Time], usage_decay_time_constant)
            self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
            self.assertEqual(self.nodeset[NodesetParams.Node_List], node_ids)
            self.assertEqual(self.event_coordinator['Number_Repetitions'], repetitions)
            self.assertEqual(self.event_coordinator['Property_Restrictions_Within_Node'], ind_property_restrictions)
            self.assertEqual(self.event_coordinator['Timesteps_Between_Repetitions'], timesteps_between_repetitions)
            self.assertEqual(self.intervention_config['Intervention_Name'], intervention_name)
            self.assertEqual(self.intervention_config['Insecticide_Name'], insecticide)
            self.assertEqual(self.intervention_config['Cost_To_Consumer'], cost)
            self.assertEqual(broadcast_intervention['Broadcast_Event'], receiving_itn_broadcast_event)
            if self.event_coordinator['Target_Age_Min'] == 1:
                self.assertEqual(self.event_coordinator['Target_Age_Max'], 10)
                self.assertEqual(self.event_coordinator['Demographic_Coverage'], 0.55)
            else:
                self.assertEqual(self.event_coordinator['Target_Age_Max'], 50)
                self.assertEqual(self.event_coordinator['Target_Age_Min'], 11)
                self.assertEqual(self.event_coordinator['Demographic_Coverage'], 0.33)
        return

    def test_bednet_triggered_custom(self):
        camp.campaign_dict["Events"] = []
        self.is_debugging = False
        start_day = 11
        triggers = ["HappyBirthday", "oops"]
        delay = 88
        duration = 444
        demographic_coverage = 0.4
        node_ids = [3, 45, 3453453]
        repetitions = 3
        timesteps_between_repetitions = 700
        receiving_itn_broadcast_event = "GotMeANet"
        blocking_initial_effect = 0.11
        blocking_box_duration = 12
        blocking_decay_time_constant = 13
        killing_initial_effect = 0.22
        killing_box_duration = 23
        killing_decay_time_constant = 24
        repelling_initial_effect = 0.33
        repelling_box_duration = 34
        repelling_decay_time_constant = 35
        usage_initial_effect = 0.44
        usage_box_duration = 45
        usage_decay_time_constant = 46
        insecticide = "NoMoreBugs"
        cost = 1.23
        intervention_name = "TestingBednet"

        add_itn_triggered(campaign=camp,
                          start_day=start_day,
                          trigger_condition_list=triggers,
                          delay_period_constant=delay,
                          listening_duration=duration,
                          demographic_coverage=demographic_coverage,
                          node_ids=node_ids,
                          repetitions=repetitions,
                          timesteps_between_repetitions=timesteps_between_repetitions,
                          receiving_itn_broadcast_event=receiving_itn_broadcast_event,
                          blocking_initial_effect=blocking_initial_effect,
                          blocking_box_duration=blocking_box_duration,
                          blocking_decay_time_constant=blocking_decay_time_constant,
                          killing_initial_effect=killing_initial_effect,
                          killing_box_duration=killing_box_duration,
                          killing_decay_time_constant=killing_decay_time_constant,
                          repelling_initial_effect=repelling_initial_effect,
                          repelling_box_duration=repelling_box_duration,
                          repelling_decay_time_constant=repelling_decay_time_constant,
                          usage_initial_effect=usage_initial_effect,
                          usage_box_duration=usage_box_duration,
                          usage_decay_time_constant=usage_decay_time_constant,
                          insecticide=insecticide,
                          cost=cost,
                          intervention_name=intervention_name)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.tmp_intervention["Start_Day"], start_day)
        intervention_list = self.tmp_intervention["Event_Coordinator_Config"]["Intervention_Config"][
            "Actual_IndividualIntervention_Config"]["Actual_IndividualIntervention_Configs"]
        if intervention_list[0]["class"] == "SimpleBednet":
            broadcast_intervention = intervention_list[1]
            self.intervention_config = intervention_list[0]
        else:
            self.intervention_config = intervention_list[1]
            broadcast_intervention = intervention_list[0]
        self.killing_config = self.intervention_config['Killing_Config']
        self.blocking_config = self.intervention_config['Blocking_Config']
        self.repelling_config = self.intervention_config['Repelling_Config']
        self.usage_config = self.intervention_config['Usage_Config']
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], killing_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], killing_decay_time_constant)
        self.assertEqual(self.blocking_config[WaningParams.Initial], blocking_initial_effect)
        self.assertEqual(self.blocking_config[WaningParams.Box_Duration], blocking_box_duration)
        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], blocking_decay_time_constant)
        self.assertEqual(self.repelling_config[WaningParams.Initial], repelling_initial_effect)
        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], repelling_box_duration)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], repelling_decay_time_constant)
        self.assertEqual(self.usage_config[WaningParams.Initial], usage_initial_effect)
        self.assertEqual(self.usage_config[WaningParams.Box_Duration], usage_box_duration)
        self.assertEqual(self.usage_config[WaningParams.Decay_Time], usage_decay_time_constant)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], node_ids)
        self.assertEqual(self.event_coordinator['Number_Repetitions'], repetitions)
        self.assertEqual(self.event_coordinator['Timesteps_Between_Repetitions'], timesteps_between_repetitions)
        self.assertEqual(self.intervention_config['Intervention_Name'], intervention_name)
        self.assertEqual(self.intervention_config['Insecticide_Name'], insecticide)
        self.assertEqual(self.intervention_config['Cost_To_Consumer'], cost)
        self.assertEqual(
            self.tmp_intervention["Event_Coordinator_Config"]["Intervention_Config"]["Demographic_Coverage"],
            demographic_coverage)
        self.assertEqual(broadcast_intervention['Broadcast_Event'], receiving_itn_broadcast_event)
        return

    # endregion

    # region OutdoorRestKill
    def test_outdoorrestkill_default(self):
        # correct setting for WaningParams are tested elsewhere here
        camp.campaign_dict["Events"] = []  # resetting
        add_outdoorrestkill(campaign=camp)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, 1)
        self.assertEqual(self.intervention_config["class"], "OutdoorRestKill")
        self.assertEqual(self.killing_config["class"], WaningEffects.Constant)

        camp.campaign_dict["Events"] = []  # resetting
        return

    def test_outdoorrestkill_all_custom(self):
        camp.campaign_dict["Events"] = []  # resetting
        specific_start_day = 123
        specific_insecticide_name = "Vinegar"
        specific_killing_effect = 0.15
        specific_box_duration = 100
        specific_decay_time = 145
        specific_nodes = [1, 2, 3, 5, 8, 13, 21, 34]
        add_outdoorrestkill(camp,
                            start_day=specific_start_day,
                            insecticide=specific_insecticide_name,
                            killing_initial_effect=specific_killing_effect,
                            killing_box_duration=specific_box_duration,
                            killing_decay_time_constant=specific_decay_time,
                            node_ids=specific_nodes)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config['Insecticide_Name'], specific_insecticide_name)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], specific_decay_time)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], specific_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], specific_killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], specific_nodes)
        camp.campaign_dict["Events"] = []  # resetting
        return

        # endregion

        # region UsageDependentBednet

    def test_scheduled_usage_dependent_bednet_default(self):
        camp.campaign_dict["Events"] = []  # resetting
        start_day = 1
        demographic_coverage = 1
        ind_property_restrictions = []
        intervention_name = "UsageDependentBednet"
        expiration_period = 10 * 365
        insecticide = ""
        repelling_initial_effect = 0
        repelling_box_duration = 0
        repelling_decay_time_constant = 1460
        blocking_initial_effect = 0.9
        blocking_decay_time_constant = 730
        killing_initial_effect = 0
        killing_decay_time_constant = 1460
        age_dependence_times = [0, 125]
        age_dependence_values = [1, 1]
        specific_times = [0, 90, 180, 270]
        specific_values = [10, 50, 15, 75]
        specific_seasonality = {
            'Times': specific_times,
            'Values': specific_values
        }
        add_scheduled_usage_dependent_bednet(campaign=camp, seasonal_dependence=specific_seasonality)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config['Discard_Event'], 'Bednet_Discarded')
        self.assertEqual(self.intervention_config['Using_Event'], 'Bednet_Using')
        self.assertEqual(self.intervention_config['Received_Event'], 'Bednet_Got_New_One')
        usage_configs = self.intervention_config['Usage_Config_List']
        found_seasonal = False
        found_age = False
        for durability in usage_configs:
            if durability['class'] == 'WaningEffectMapLinearSeasonal':
                found_seasonal = True
                durability_map = durability['Durability_Map']
                self.assertEqual(durability_map['Times'], specific_times)
                self.assertEqual(durability_map['Values'], specific_values)
            elif durability['class'] == "WaningEffectMapLinearAge":
                found_age = True
                durability_map = durability['Durability_Map']
                self.assertEqual(durability_map['Times'], age_dependence_times)
                self.assertEqual(durability_map['Values'], age_dependence_values)
            else:
                self.assertTrue(False, "There shouldn't be a third option for WaningEffectMap.\n")
        self.assertTrue(found_age)
        self.assertTrue(found_seasonal)
        self.killing_config = self.intervention_config['Killing_Config']
        self.blocking_config = self.intervention_config['Blocking_Config']
        self.repelling_config = self.intervention_config['Repelling_Config']
        self.usage_config = self.intervention_config['Usage_Config_List']
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        self.assertEqual(self.event_coordinator['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], demographic_coverage)
        self.assertEqual(self.event_coordinator['Property_Restrictions'], ind_property_restrictions)
        self.assertEqual(self.intervention_config['Discard_Event'], 'Bednet_Discarded')
        self.assertEqual(self.intervention_config['Using_Event'], 'Bednet_Using')
        self.assertEqual(self.intervention_config['Received_Event'], 'Bednet_Got_New_One')
        self.assertEqual(self.intervention_config['Intervention_Name'], intervention_name)
        self.assertEqual(self.intervention_config['Insecticide_Name'], insecticide)
        self.assertEqual(self.intervention_config['Expiration_Period_Distribution'], "EXPONENTIAL_DISTRIBUTION")
        self.assertEqual(self.intervention_config['Expiration_Period_Exponential'], expiration_period)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], killing_decay_time_constant)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.Exp)
        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], blocking_decay_time_constant)
        self.assertEqual(self.blocking_config[WaningParams.Initial], blocking_initial_effect)
        self.assertEqual(self.blocking_config[WaningParams.Class], WaningEffects.Exp)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], repelling_decay_time_constant)
        self.assertEqual(self.repelling_config[WaningParams.Initial], repelling_initial_effect)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.Exp)

        # checking that this is finalized appropriately
        camp.save("test_campaign.json")
        with open('test_campaign.json') as file:
            campaign = json.load(file)
        self.assertTrue('schema' not in campaign, msg="UDBednet contains bits of schema in it")
        os.remove("test_campaign.json")
        camp.campaign_dict["Events"] = []  # resetting
        return

    def test_triggered_usage_dependent_bednet_default(self):
        camp.campaign_dict["Events"] = []  # resetting
        start_day = 1
        demographic_coverage = 1
        duration = -1
        delay = 0
        triggers = ["HappyBirthday"]
        ind_property_restrictions = []
        intervention_name = "UsageDependentBednet"
        expiration_period = 10 * 365
        discard_config = {"Expiration_Period_Exponential": expiration_period}
        insecticide = ""
        repelling_initial_effect = 0
        repelling_box_duration = 0
        repelling_decay_time_constant = 1460
        blocking_initial_effect = 0.9
        blocking_box_duration = 0
        blocking_decay_time_constant = 730
        killing_initial_effect = 0
        killing_box_duration = 0
        killing_decay_time_constant = 1460
        age_dependence_times = [0, 125]
        age_dependence_values = [1, 1]
        specific_times = [0, 90, 180, 270]
        specific_values = [10, 50, 15, 75]
        specific_seasonality = {
            'Times': specific_times,
            'Values': specific_values
        }
        add_triggered_usage_dependent_bednet(campaign=camp, trigger_condition_list=triggers,
                                             seasonal_dependence=specific_seasonality)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        node_level_triggered_intervention = self.intervention_config
        self.intervention_config = self.tmp_intervention["Event_Coordinator_Config"]["Intervention_Config"][
            "Actual_IndividualIntervention_Config"]
        usage_configs = self.intervention_config['Usage_Config_List']
        found_seasonal = False
        found_age = False
        for durability in usage_configs:
            if durability['class'] == 'WaningEffectMapLinearSeasonal':
                found_seasonal = True
                durability_map = durability['Durability_Map']
                self.assertEqual(durability_map['Times'], specific_times)
                self.assertEqual(durability_map['Values'], specific_values)
            elif durability['class'] == "WaningEffectMapLinearAge":
                found_age = True
                durability_map = durability['Durability_Map']
                self.assertEqual(durability_map['Times'], age_dependence_times)
                self.assertEqual(durability_map['Values'], age_dependence_values)
            else:
                self.assertTrue(False, "There shouldn't be a third option for WaningEffectMap.\n")
        self.assertTrue(found_age)
        self.assertTrue(found_seasonal)
        self.killing_config = self.intervention_config['Killing_Config']
        self.blocking_config = self.intervention_config['Blocking_Config']
        self.repelling_config = self.intervention_config['Repelling_Config']
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        self.assertEqual(node_level_triggered_intervention['Demographic_Coverage'], demographic_coverage)
        self.assertEqual(node_level_triggered_intervention['Property_Restrictions'], ind_property_restrictions)
        self.assertEqual(node_level_triggered_intervention['Trigger_Condition_List'], triggers)
        self.assertEqual(node_level_triggered_intervention['Duration'], duration)
        self.assertEqual(self.intervention_config['Discard_Event'], 'Bednet_Discarded')
        self.assertEqual(self.intervention_config['Using_Event'], 'Bednet_Using')
        self.assertEqual(self.intervention_config['Received_Event'], 'Bednet_Got_New_One')
        self.assertEqual(self.intervention_config['Intervention_Name'], intervention_name)
        self.assertEqual(self.intervention_config['Insecticide_Name'], insecticide)
        self.assertEqual(self.intervention_config['Expiration_Period_Distribution'], "EXPONENTIAL_DISTRIBUTION")
        self.assertEqual(self.intervention_config['Expiration_Period_Exponential'], expiration_period)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], killing_decay_time_constant)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.Exp)
        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], blocking_decay_time_constant)
        self.assertEqual(self.blocking_config[WaningParams.Initial], blocking_initial_effect)
        self.assertEqual(self.blocking_config[WaningParams.Class], WaningEffects.Exp)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], repelling_decay_time_constant)
        self.assertEqual(self.repelling_config[WaningParams.Initial], repelling_initial_effect)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.Exp)

        # checking that this is finalized appropriately
        camp.save("test_campaign.json")
        with open('test_campaign.json') as file:
            campaign = json.load(file)
        self.assertTrue('schema' not in campaign, msg="UDBednet contains bits of schema in it")
        os.remove("test_campaign.json")
        camp.campaign_dict["Events"] = []  # resetting
        return

    def test_scheduled_usage_dependent_bednet_custom(self):
        camp.campaign_dict["Events"] = []  # resetting
        start_day = 1
        demographic_coverage = 1
        target_num_individuals = 33
        node_ids = [2, 435]
        ind_property_restrictions = [
            {
                "Place": "URBAN",
                "Risk": "MED"
            },
            {
                "Place": "RURAL",
                "Risk": "LOW"
            }
        ]
        intervention_name = "TestingName"
        gaussian = "GAUSSIAN_DISTRIBUTION"
        g_mean = 22
        g_dev = 44
        discard_config = {"Expiration_Period_Distribution": gaussian,
                          "Expiration_Period_Gaussian_Mean": g_mean,
                          "Expiration_Period_Gaussian_Std_Dev": g_dev}
        insecticide = "SpraySpray"
        repelling_initial_effect = 0.11
        repelling_box_duration = -1
        repelling_decay_time_constant = 0
        blocking_initial_effect = 0.34
        blocking_box_duration = 8527
        blocking_decay_time_constant = 200
        killing_initial_effect = 0.51
        killing_box_duration = 55
        killing_decay_time_constant = 250
        age_dependence_times = [0, 2.9, 12.9, 13]
        age_dependence_values = [1, 1, 0.7, 0.7, 1]
        age_dependence = {"Times": age_dependence_times, "Values": age_dependence_values}
        specific_min_val = 0.1
        specific_max_day = 73  # March 14 in non leap years
        seasonal_dependence = {
            'min_cov': specific_min_val,
            'max_day': specific_max_day
        }
        add_scheduled_usage_dependent_bednet(camp,
                                             start_day=start_day,
                                             demographic_coverage=demographic_coverage,
                                             target_num_individuals=target_num_individuals,
                                             node_ids=node_ids,
                                             ind_property_restrictions=ind_property_restrictions,
                                             intervention_name=intervention_name,
                                             discard_config=discard_config,
                                             insecticide=insecticide,
                                             repelling_initial_effect=repelling_initial_effect,
                                             repelling_box_duration=repelling_box_duration,
                                             repelling_decay_time_constant=repelling_decay_time_constant,
                                             blocking_initial_effect=blocking_initial_effect,
                                             blocking_box_duration=blocking_box_duration,
                                             blocking_decay_time_constant=blocking_decay_time_constant,
                                             killing_initial_effect=killing_initial_effect,
                                             killing_box_duration=killing_box_duration,
                                             killing_decay_time_constant=killing_decay_time_constant,
                                             age_dependence=age_dependence,
                                             seasonal_dependence=seasonal_dependence
                                             )
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.killing_config = self.intervention_config['Killing_Config']
        self.blocking_config = self.intervention_config['Blocking_Config']
        self.repelling_config = self.intervention_config['Repelling_Config']
        self.usage_config = self.intervention_config['Usage_Config_List']
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], node_ids)
        self.assertEqual(self.event_coordinator['Individual_Selection_Type'], "TARGET_NUM_INDIVIDUALS")
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], demographic_coverage)
        self.assertEqual(self.event_coordinator['Target_Num_Individuals'], target_num_individuals)
        self.assertEqual(self.event_coordinator['Property_Restrictions_Within_Node'], ind_property_restrictions)
        self.assertEqual(self.intervention_config['Discard_Event'], 'Bednet_Discarded')
        self.assertEqual(self.intervention_config['Using_Event'], 'Bednet_Using')
        self.assertEqual(self.intervention_config['Received_Event'], 'Bednet_Got_New_One')
        self.assertEqual(self.intervention_config['Intervention_Name'], intervention_name)
        self.assertEqual(self.intervention_config['Insecticide_Name'], insecticide)
        self.assertEqual(self.intervention_config['Expiration_Period_Distribution'], gaussian)
        self.assertEqual(self.intervention_config['Expiration_Period_Gaussian_Mean'], g_mean)
        self.assertEqual(self.intervention_config['Expiration_Period_Gaussian_Std_Dev'], g_dev)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], killing_decay_time_constant)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], blocking_decay_time_constant)
        self.assertEqual(self.blocking_config[WaningParams.Initial], blocking_initial_effect)
        self.assertEqual(self.blocking_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.repelling_config[WaningParams.Initial], repelling_initial_effect)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.Constant)
        found_seasonal = False
        found_age = False
        for durability in self.usage_config:
            if durability['class'] == 'WaningEffectMapLinearSeasonal':
                found_seasonal = True
                durability_map = durability['Durability_Map']
                actual_min = min(durability_map['Values'])
                actual_min_diff = abs(actual_min - specific_min_val)
                self.assertLessEqual(actual_min_diff, 0.02)
                target_index = -1
                next_index = target_index + 1  # Find out the index that contains the max_day
                while durability_map['Times'][next_index] < specific_max_day:  # So until the next index is too high...
                    target_index += 1
                    next_index += 1
                actual_max_index = durability_map['Values'].index(
                    max(durability_map['Values']))  # Get the index of the actually highest day
                self.assertEqual(target_index, actual_max_index,
                                 msg=f"Expected value in bucket {target_index}"
                                     f": {durability_map['Values'][target_index]} to be max, "
                                     f"but index {actual_max_index}: {durability_map['Values'][actual_max_index]} "
                                     f"was higher.")
            elif durability['class'] == "WaningEffectMapLinearAge":
                found_age = True
                durability_map = durability['Durability_Map']
                self.assertEqual(durability_map['Times'], age_dependence_times)
                self.assertEqual(durability_map['Values'], age_dependence_values)
            else:
                self.assertTrue(False, "There shouldn't be a third option for WaningEffectMap.\n")

        self.assertTrue(found_seasonal)
        self.assertTrue(found_age)
        # checking that this is finalized appropriately
        camp.save("test_campaign.json")
        with open('test_campaign.json') as file:
            campaign = json.load(file)
        self.assertTrue('schema' not in campaign, msg="UDBednet contains bits of schema in it")
        os.remove("test_campaign.json")
        camp.campaign_dict["Events"] = []  # resetting
        return

    def test_triggered_usage_dependent_bednet_custom(self):
        camp.campaign_dict["Events"] = []  # resetting
        triggers = ["HappyBirthday"]
        delay = 55
        duration = 123
        start_day = 1
        demographic_coverage = 1
        node_ids = [2, 435]
        ind_property_restrictions = [
            {
                "Place": "URBAN",
                "Risk": "MED"
            },
            {
                "Place": "RURAL",
                "Risk": "LOW"
            }
        ]
        intervention_name = "TestingName"
        gaussian = "GAUSSIAN_DISTRIBUTION"
        g_mean = 22
        g_dev = 44
        discard_config = {"Expiration_Period_Distribution": gaussian,
                          "Expiration_Period_Gaussian_Mean": g_mean,
                          "Expiration_Period_Gaussian_Std_Dev": g_dev}
        insecticide = "SpraySpray"
        repelling_initial_effect = 0.11
        repelling_box_duration = -1
        repelling_decay_time_constant = 0
        blocking_initial_effect = 0.34
        blocking_box_duration = 8527
        blocking_decay_time_constant = 200
        killing_initial_effect = 0.51
        killing_box_duration = 55
        killing_decay_time_constant = 250
        age_dependence_times = [0, 2.9, 3, 12.9, 13]
        age_dependence_values = [1, 1, 0.7, 0.7, 1]
        age_dependence = {"youth_cov": 0.7, "youth_min_age": 3, "youth_max_age": 13}
        specific_min_val = 0.1
        specific_max_day = 73  # March 14 in non leap years
        seasonal_dependence = {
            'min_cov': specific_min_val,
            'max_day': specific_max_day
        }
        add_triggered_usage_dependent_bednet(camp,
                                             start_day=start_day,
                                             trigger_condition_list=triggers,
                                             triggered_campaign_delay=delay,
                                             listening_duration=duration,
                                             demographic_coverage=demographic_coverage,
                                             node_ids=node_ids,
                                             ind_property_restrictions=ind_property_restrictions,
                                             intervention_name=intervention_name,
                                             discard_config=discard_config,
                                             insecticide=insecticide,
                                             repelling_initial_effect=repelling_initial_effect,
                                             repelling_box_duration=repelling_box_duration,
                                             repelling_decay_time_constant=repelling_decay_time_constant,
                                             blocking_initial_effect=blocking_initial_effect,
                                             blocking_box_duration=blocking_box_duration,
                                             blocking_decay_time_constant=blocking_decay_time_constant,
                                             killing_initial_effect=killing_initial_effect,
                                             killing_box_duration=killing_box_duration,
                                             killing_decay_time_constant=killing_decay_time_constant,
                                             age_dependence=age_dependence,
                                             seasonal_dependence=seasonal_dependence
                                             )
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        node_level_triggered_intervention = self.intervention_config
        self.intervention_config = self.tmp_intervention["Event_Coordinator_Config"]["Intervention_Config"][
            "Actual_IndividualIntervention_Config"]["Actual_IndividualIntervention_Configs"][0]
        self.killing_config = self.intervention_config['Killing_Config']
        self.blocking_config = self.intervention_config['Blocking_Config']
        self.repelling_config = self.intervention_config['Repelling_Config']
        self.usage_config = self.intervention_config['Usage_Config_List']
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], node_ids)
        self.assertEqual(node_level_triggered_intervention['Demographic_Coverage'], demographic_coverage)
        self.assertEqual(node_level_triggered_intervention['Property_Restrictions_Within_Node'],
                         ind_property_restrictions)
        self.assertEqual(node_level_triggered_intervention['Trigger_Condition_List'], triggers)
        self.assertEqual(node_level_triggered_intervention['Duration'], duration)
        self.assertEqual(
            node_level_triggered_intervention["Actual_IndividualIntervention_Config"]["Delay_Period_Constant"], delay)
        self.assertEqual(self.intervention_config['Discard_Event'], 'Bednet_Discarded')
        self.assertEqual(self.intervention_config['Using_Event'], 'Bednet_Using')
        self.assertEqual(self.intervention_config['Received_Event'], 'Bednet_Got_New_One')
        self.assertEqual(self.intervention_config['Intervention_Name'], intervention_name)
        self.assertEqual(self.intervention_config['Insecticide_Name'], insecticide)
        self.assertEqual(self.intervention_config['Expiration_Period_Distribution'], gaussian)
        self.assertEqual(self.intervention_config['Expiration_Period_Gaussian_Mean'], g_mean)
        self.assertEqual(self.intervention_config['Expiration_Period_Gaussian_Std_Dev'], g_dev)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], killing_decay_time_constant)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], killing_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], blocking_decay_time_constant)
        self.assertEqual(self.blocking_config[WaningParams.Box_Duration], blocking_box_duration)
        self.assertEqual(self.blocking_config[WaningParams.Initial], blocking_initial_effect)
        self.assertEqual(self.blocking_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.repelling_config[WaningParams.Initial], repelling_initial_effect)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.Constant)
        found_seasonal = False
        found_age = False
        for durability in self.usage_config:
            if durability['class'] == 'WaningEffectMapLinearSeasonal':
                found_seasonal = True
                durability_map = durability['Durability_Map']
                actual_min = min(durability_map['Values'])
                actual_min_diff = abs(actual_min - specific_min_val)
                self.assertLessEqual(actual_min_diff, 0.02)
                target_index = -1
                next_index = target_index + 1  # Find out the index that contains the max_day
                while durability_map['Times'][next_index] < specific_max_day:  # So until the next index is too high...
                    target_index += 1
                    next_index += 1
                actual_max_index = durability_map['Values'].index(
                    max(durability_map['Values']))  # Get the index of the actually highest day
                self.assertEqual(target_index, actual_max_index,
                                 msg=f"Expected value in bucket {target_index}"
                                     f": {durability_map['Values'][target_index]} to be max, "
                                     f"but index {actual_max_index}: {durability_map['Values'][actual_max_index]} "
                                     f"was higher.")
            elif durability['class'] == "WaningEffectMapLinearAge":
                found_age = True
                durability_map = durability['Durability_Map']
                self.assertEqual(durability_map['Times'], age_dependence_times)
                self.assertEqual(durability_map['Values'], age_dependence_values)
            else:
                self.assertTrue(False, "There shouldn't be a third option for WaningEffectMap.\n")
        self.assertTrue(found_age)
        self.assertTrue(found_seasonal)

        # checking that this is finalized appropriately
        camp.save("test_campaign.json")
        with open('test_campaign.json') as file:
            campaign = json.load(file)
        self.assertTrue('schema' not in campaign, msg="UDBednet contains bits of schema in it")
        os.remove("test_campaign.json")
        camp.campaign_dict["Events"] = []  # resetting
        return

    # endregion

    def test_diagnostic_survey_default(self):
        camp.campaign_dict["Events"] = []
        coverage = 1
        repetitions = 1
        tsteps_btwn_repetitions = 365
        target = 'Everyone'
        start_day = 1
        diagnostic_type = 'BLOOD_SMEAR_PARASITES'
        diagnostic_threshold = 40
        measurement_sensitivity = 0.1
        received_test_event = 'Received_Test'
        self.is_debugging = False
        diag_survey.add_diagnostic_survey(camp)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day + 1)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetAll")
        event_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(event_config['Demographic_Coverage'], coverage)
        self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(event_config['Timesteps_Between_Repetitions'], tsteps_btwn_repetitions)
        self.assertEqual(event_config['Number_Repetitions'], repetitions)
        self.assertEqual(event_config['Target_Demographic'], target)
        self.assertEqual(event_config['Property_Restrictions'], [])
        intervention_config = event_config['Intervention_Config']
        self.assertEqual(intervention_config['class'], "MultiInterventionDistributor")
        self.assertEqual(len(intervention_config['Intervention_List']), 2)
        if intervention_config['Intervention_List'][0]["class"] == "MalariaDiagnostic":
            malaria_diagnostic = intervention_config['Intervention_List'][0]
            broadcast_event = intervention_config['Intervention_List'][1]
        else:
            malaria_diagnostic = intervention_config['Intervention_List'][1]
            broadcast_event = intervention_config['Intervention_List'][0]
        self.assertEqual(malaria_diagnostic['Diagnostic_Type'], diagnostic_type)
        self.assertEqual(malaria_diagnostic['Detection_Threshold'], diagnostic_threshold)
        self.assertEqual(malaria_diagnostic['Measurement_Sensitivity'], measurement_sensitivity)
        self.assertEqual(malaria_diagnostic['Disqualifying_Properties'], [])
        self.assertEqual(len(malaria_diagnostic['Negative_Diagnosis_Config']['Intervention_List']), 2)
        self.assertIn(malaria_diagnostic['Negative_Diagnosis_Config']['Intervention_List'][0]['Broadcast_Event'],
                      "TestedNegative")
        self.assertIn(malaria_diagnostic['Positive_Diagnosis_Config']['Intervention_List'][0]['Broadcast_Event'],
                      "TestedPositive")
        self.assertEqual(broadcast_event['Broadcast_Event'], received_test_event)

    def test_diagnostic_survey_custom(self):
        camp.campaign_dict["Events"] = []

        coverage = 0.65
        repetitions = 1
        agemin = 5
        agemax = 10
        gender = "Female"
        target = {"agemin": agemin, "agemax": agemax, "gender": gender}
        start_day = 6
        diagnostic_type = 'PCR_PARASITES'
        diagnostic_threshold = 12
        measurement_sensitivity = 0.2
        event_name = "Diagnostic Survey"
        node_ids = [23, 49, 50]
        positive_diagnosis_configs = None
        negative_diagnosis_configs = None
        received_test_event = 'Received_Test_Test'
        ind_property_restrictions = [{"IndividualProperty1": "PropertyValue1"},
                                     {"IndividualProperty2": "PropertyValue2"}]
        disqualifying_properties = [{"IndividualProperty3": "PropertyValue2"}]
        trigger_condition_list = ["NewInfectionEvent"]
        listening_duration = 50
        triggered_campaign_delay = 3
        check_eligibility_at_trigger = False
        expire_recent_drugs = True
        self.is_debugging = False

        diag_survey.add_diagnostic_survey(camp, start_day=start_day, coverage=coverage, repetitions=repetitions,
                                          target=target,
                                          diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                                          measurement_sensitivity=measurement_sensitivity, node_ids=node_ids,
                                          positive_diagnosis_configs=positive_diagnosis_configs,
                                          negative_diagnosis_configs=negative_diagnosis_configs,
                                          received_test_event=received_test_event,
                                          ind_property_restrictions=ind_property_restrictions,
                                          disqualifying_properties=disqualifying_properties,
                                          trigger_condition_list=trigger_condition_list,
                                          listening_duration=listening_duration,
                                          triggered_campaign_delay=triggered_campaign_delay,
                                          check_eligibility_at_trigger=check_eligibility_at_trigger,
                                          expire_recent_drugs=expire_recent_drugs)

        with open("testcampaign.json", "w") as testcampaign:
            json.dump(camp.campaign_dict['Events'], testcampaign)
        all_found = 0
        custom_trigger_broadcast = ''
        custom_trigger_listen = ''
        self.assertEqual(len(camp.campaign_dict['Events']), 2)
        for campaign_event in camp.campaign_dict['Events']:
            actual_config = campaign_event['Event_Coordinator_Config']['Intervention_Config'][
                'Actual_IndividualIntervention_Config']
            if actual_config["class"] == "MultiInterventionDistributor":
                self.assertEqual(campaign_event['Start_Day'], start_day + 1)
                self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
                self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], node_ids)
                event_config = campaign_event['Event_Coordinator_Config']
                self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
                intervention_config = event_config['Intervention_Config']
                custom_trigger_listen = intervention_config["Trigger_Condition_List"][0]
                # self.assertEqual(intervention_config['Property_Restrictions_Within_Node'], ind_property_restrictions)
                self.assertEqual(intervention_config['Demographic_Coverage'], 0.65)
                self.assertEqual(intervention_config['Duration'], listening_duration)
                self.assertEqual(intervention_config['class'], "NodeLevelHealthTriggeredIV")
                self.assertEqual(intervention_config['Target_Demographic'], "ExplicitAgeRangesAndGender")
                self.assertEqual(intervention_config['Target_Age_Min'], agemin)
                self.assertEqual(intervention_config['Target_Age_Max'], agemax)
                self.assertEqual(intervention_config['Target_Gender'], gender)
                self.assertEqual(len(intervention_config['Actual_IndividualIntervention_Config']['Intervention_List']),
                                 2)
                if intervention_config['Actual_IndividualIntervention_Config']['Intervention_List'][0][
                    "class"] == "MalariaDiagnostic":
                    all_found += 1
                    malaria_diagnostic = \
                        intervention_config['Actual_IndividualIntervention_Config']['Intervention_List'][0]
                    broadcast_event = intervention_config['Actual_IndividualIntervention_Config']['Intervention_List'][
                        1]
                else:
                    all_found += 1
                    malaria_diagnostic = \
                        intervention_config['Actual_IndividualIntervention_Config']['Intervention_List'][1]
                    broadcast_event = intervention_config['Actual_IndividualIntervention_Config']['Intervention_List'][
                        0]
                self.assertEqual(malaria_diagnostic['Diagnostic_Type'], diagnostic_type)
                self.assertEqual(malaria_diagnostic['Detection_Threshold'], diagnostic_threshold)
                self.assertEqual(malaria_diagnostic['Measurement_Sensitivity'], measurement_sensitivity)
                self.assertEqual(malaria_diagnostic['Disqualifying_Properties'], [])
                self.assertEqual(len(malaria_diagnostic['Negative_Diagnosis_Config']['Intervention_List']), 2)
                self.assertIn(
                    malaria_diagnostic['Negative_Diagnosis_Config']['Intervention_List'][0]['Broadcast_Event'],
                    "TestedNegative")
                self.assertIn(
                    malaria_diagnostic['Positive_Diagnosis_Config']['Intervention_List'][0]['Broadcast_Event'],
                    "TestedPositive")
                self.assertEqual(broadcast_event['Broadcast_Event'], received_test_event)
            else:
                self.assertEqual(actual_config["class"], "DelayedIntervention")
                self.assertEqual(actual_config["Delay_Period_Constant"], 3)
                custom_trigger_broadcast = actual_config["Actual_IndividualIntervention_Configs"][0]["Broadcast_Event"]
                self.assertEqual(
                    campaign_event['Event_Coordinator_Config']['Intervention_Config']["Trigger_Condition_List"],
                    ["NewInfectionEvent"])
                all_found += 1
        self.assertEqual(custom_trigger_broadcast, custom_trigger_listen)
        self.assertEqual(all_found, 2)

    def test_malaria_diagnostic_custom(self):
        self.is_debugging = False
        malaria_diagnostic = _malaria_diagnostic(camp, "PCR_PARASITES", 0.5, 1)
        measures = [malaria_diagnostic.Measurement_Sensitivity, malaria_diagnostic.Detection_Threshold]

        self.assertEqual(malaria_diagnostic.Detection_Threshold, 1, msg="Detection Threshold not set properly")
        self.assertEqual(malaria_diagnostic.Measurement_Sensitivity, 0.5,
                         msg="Measurement Sensitivity not set properly")
        self.assertEqual("PCR_PARASITES", malaria_diagnostic.Diagnostic_Type)

        antimalarial_drug = _antimalarial_drug(camp, "Malaria")
        self.assertEqual(antimalarial_drug.Drug_Type, "Malaria")
        self.assertEqual(antimalarial_drug.Cost_To_Consumer, 0)
        self.assertEqual(antimalarial_drug.Intervention_Name, "AntimalarialDrug_Malaria")

    def test_malaria_diagnostic_default(self):
        self.is_debugging = False
        malaria_diagnostic = _malaria_diagnostic(camp)
        measures = [0.5, malaria_diagnostic.Detection_Threshold]

        self.assertFalse(any(item == 1 for item in measures), msg="Not all values are 0 when set to 0")
        self.assertEqual("BLOOD_SMEAR_PARASITES", malaria_diagnostic.Diagnostic_Type)

        antimalarial_drug = _antimalarial_drug(camp, "Malaria")
        self.assertEqual(antimalarial_drug.Drug_Type, "Malaria")
        self.assertEqual(antimalarial_drug.Cost_To_Consumer, 0)
        self.assertEqual(antimalarial_drug.Intervention_Name, "AntimalarialDrug_Malaria")

    def test_malaria_diagnostic_error(self):
        with self.assertRaises(ValueError) as context:
            diag = _malaria_diagnostic(camp, "BANANA")

        with self.assertRaises(ValueError) as context:
            _malaria_diagnostic(camp, "BLOOD_SMEAR_PARASITES", -1, 0)

        with self.assertRaises(ValueError) as context:
            _malaria_diagnostic(camp, "BLOOD_SMEAR_PARASITES", 0, -1)

    def test_malaria_diagnostic_infection(self):
        self.is_debugging = False
        malaria_diagnostic = _malaria_diagnostic(camp, "TRUE_INFECTION_STATUS")

        self.assertEqual("StandardDiagnostic", malaria_diagnostic.Intervention_Name)

        with self.assertRaises(ValueError) as context:
            _malaria_diagnostic(camp, "TRUE_INFECTION_STATUS", -1, 0)
        with self.assertRaises(ValueError) as context:
            _malaria_diagnostic(camp, "TRUE_INFECTION_STATUS", 0, -1)

    def test_inputeir_default(self):
        camp.campaign_dict["Events"] = []
        eir = [random.randint(0, 50) for x in range(12)]
        add_scheduled_input_eir(campaign=camp, monthly_eir=eir)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Monthly_EIR, eir)
        self.assertEqual(self.intervention_config.Age_Dependence, "OFF")
        self.assertEqual(self.intervention_config.Scaling_Factor, 1)
        self.assertEqual(self.start_day, 1)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        pass

    def test_inputeir(self):
        camp.campaign_dict["Events"] = []
        eir = [random.randint(0, 50) for x in range(12)]
        add_scheduled_input_eir(camp, monthly_eir=eir, start_day=2, node_ids=[2, 3],
                                age_dependence='LINEAR', scaling_factor=0.24)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Monthly_EIR, eir)
        self.assertEqual(self.intervention_config.Age_Dependence, "LINEAR")
        self.assertEqual(self.intervention_config.Scaling_Factor, 0.24)
        self.assertEqual(self.start_day, 2)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], [2, 3])
        pass

    def test_daily_inputeir(self):
        camp.campaign_dict["Events"] = []
        daily_eir = [random.randint(0, 50) for x in range(365)]
        add_scheduled_input_eir(camp, daily_eir=daily_eir, start_day=2, node_ids=[2, 3],
                                age_dependence='SURFACE_AREA_DEPENDENT', scaling_factor=0.67)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Daily_EIR, daily_eir)
        self.assertEqual(self.intervention_config.EIR_Type, "DAILY")
        self.assertEqual(self.intervention_config.Age_Dependence, "SURFACE_AREA_DEPENDENT")
        self.assertEqual(self.intervention_config.Scaling_Factor, 0.67)
        self.assertEqual(self.start_day, 2)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], [2, 3])
        pass

    def test_default_scheduled_mosquito_release(self):
        camp.campaign_dict["Events"] = []
        start_day = 0
        repetitions = 1
        timesteps_between_repetitions = 365
        intervention_name = "MosquitoRelease"
        released_number = 203847
        released_ratio = None
        released_infectious = 0
        released_microsporidia_strain = ''
        released_species = "arabiensis"
        released_genome = [["X", "X"]]
        add_scheduled_mosquito_release(campaign=camp, released_number=203847)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.intervention_config["Intervention_Name"], intervention_name)
        self.assertEqual(self.intervention_config["Released_Type"], "FIXED_NUMBER")
        self.assertEqual(self.intervention_config["Released_Number"], released_number)
        self.assertEqual(self.intervention_config["Released_Infectious"], released_infectious)
        self.assertEqual(self.intervention_config["Released_Species"], released_species)
        self.assertEqual(self.intervention_config["Released_Genome"], released_genome)
        self.assertEqual(self.intervention_config["Released_Mate_Genome"], [])
        self.assertEqual(self.intervention_config["Released_Microsporidia_Strain"], released_microsporidia_strain)
        self.assertEqual(self.event_coordinator["Number_Repetitions"], repetitions)
        self.assertEqual(self.event_coordinator["Timesteps_Between_Repetitions"], timesteps_between_repetitions)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        pass

    def test_custom_scheduled_mosquito_release(self):
        camp.campaign_dict["Events"] = []
        start_day = 2098
        repetitions = 978
        timesteps_between_repetitions = 41
        intervention_name = "MosquitoReleaseTesting"
        released_ratio = 1.88
        released_infectious = True
        released_microsporidia_strain = 'tEst_strain'
        released_species = "funestus"
        released_genome = [["s", "S"]]
        released_mate_genome = [["m", "M"]]
        node_ids = [234, 4356, 54]
        add_scheduled_mosquito_release(campaign=camp, start_day=start_day, repetitions=repetitions,
                                       timesteps_between_repetitions=timesteps_between_repetitions,
                                       node_ids=node_ids,
                                       intervention_name=intervention_name,
                                       released_ratio=released_ratio,
                                       released_infectious=released_infectious,
                                       released_species=released_species,
                                       released_genome=released_genome,
                                       released_mate_genome=released_mate_genome,
                                       released_microsporidia=released_microsporidia_strain)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.intervention_config["Intervention_Name"], intervention_name)
        self.assertEqual(self.intervention_config["Released_Type"], "RATIO")
        self.assertEqual(self.intervention_config["Released_Ratio"], released_ratio)
        self.assertEqual(self.intervention_config["Released_Infectious"], 1)
        self.assertEqual(self.intervention_config["Released_Species"], released_species)
        self.assertEqual(self.intervention_config["Released_Genome"], released_genome)
        self.assertEqual(self.intervention_config["Released_Mate_Genome"], released_mate_genome)
        self.assertEqual(self.intervention_config["Released_Microsporidia_Strain"], released_microsporidia_strain)
        self.assertEqual(self.event_coordinator["Number_Repetitions"], repetitions)
        self.assertEqual(self.event_coordinator["Timesteps_Between_Repetitions"], timesteps_between_repetitions)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], node_ids)
        pass

    def test_default_add_outbreak_individual(self):
        # resetting campaign
        camp.campaign_dict["Events"] = []
        add_outbreak_individual(camp)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], 1)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetAll")
        event_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(event_config['Number_Repetitions'], 1)
        self.assertEqual(event_config['Timesteps_Between_Repetitions'], 365)
        self.assertEqual(event_config['Demographic_Coverage'], 1)
        self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(event_config['Target_Gender'], "All")
        self.assertEqual(event_config['Property_Restrictions'], [])
        self.assertEqual(event_config['Intervention_Config']['class'], "OutbreakIndividual")
        self.assertEqual(event_config['Intervention_Config']['Antigen'], 0)
        self.assertEqual(event_config['Intervention_Config']['Genome'], 0)
        self.assertEqual(event_config['Intervention_Config']['Ignore_Immunity'], 1)
        self.assertEqual(event_config['Intervention_Config']['Incubation_Period_Override'], -1)

        pass

    def test_custom_add_outbreak_individual(self):
        camp.campaign_dict["Events"] = []
        add_outbreak_individual(camp, start_day=3, target_num_individuals=7, repetitions=5,
                                timesteps_between_repetitions=9, node_ids=[45, 89], target_gender="Female",
                                target_age_min=23, target_age_max=34,
                                antigen=2, genome=4, ignore_immunity=False, incubation_period_override=2,
                                ind_property_restrictions=[{"Risk": "High"}], broadcast_event="Testing!")
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], 3)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], [45, 89])
        event_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(event_config['Number_Repetitions'], 5)
        self.assertEqual(event_config['Timesteps_Between_Repetitions'], 9)
        self.assertEqual(event_config['Target_Num_Individuals'], 7)
        self.assertEqual(event_config['Individual_Selection_Type'], "TARGET_NUM_INDIVIDUALS")
        self.assertEqual(event_config['Target_Gender'], "Female")
        self.assertEqual(event_config['Property_Restrictions_Within_Node'], [{"Risk": "High"}])
        self.assertEqual(event_config['Target_Age_Min'], 23)
        self.assertEqual(event_config['Target_Age_Max'], 34)
        self.assertEqual(event_config['Target_Demographic'], "ExplicitAgeRangesAndGender")
        self.assertEqual(len(event_config['Intervention_Config']['Intervention_List']), 2)
        intervention_1 = event_config['Intervention_Config']['Intervention_List'][1]
        intervention_0 = event_config['Intervention_Config']['Intervention_List'][0]
        if intervention_0['class'] == "BroadcastEvent":
            self.assertEqual(intervention_0["Broadcast_Event"], "Testing!")
            self.assertEqual(intervention_1['class'], "OutbreakIndividual")
            self.assertEqual(intervention_1['Antigen'], 2)
            self.assertEqual(intervention_1['Genome'], 4)
            self.assertEqual(intervention_1['Ignore_Immunity'], 0)
            self.assertEqual(intervention_1['Incubation_Period_Override'], 2)
        else:  # just in case this happens the other way around
            self.assertEqual(intervention_0['class'], "OutbreakIndividual")
            self.assertEqual(intervention_0['Antigen'], 2)
            self.assertEqual(intervention_0['Genome'], 4)
            self.assertEqual(intervention_0['Ignore_Immunity'], 0)
            self.assertEqual(intervention_0['Incubation_Period_Override'], 2)
        pass

    def test_1_custom_add_outbreak_malaria_genetics(self):
        camp.campaign_dict["Events"] = []
        allele_frequencies = [[1.00, 0.00, 0.00, 0.00], [0.00, 1.00, 0.00, 0.00], [0.00, 0.00, 1.00, 0.00],
                              [0.00, 0.00, 0.00, 1.00], [0.50, 0.50, 0.00, 0.00], [0.00, 0.50, 0.50, 0.00],
                              [0.00, 0.00, 0.50, 0.50], [0.25, 0.25, 0.25, 0.25], [0.10, 0.20, 0.30, 0.40],
                              [0.40, 0.30, 0.20, 0.10], [1.00, 0.00, 0.00, 0.00], [0.00, 1.00, 0.00, 0.00],
                              [0.00, 0.00, 1.00, 0.00], [0.00, 0.00, 0.00, 1.00], [0.50, 0.50, 0.00, 0.00],
                              [0.00, 0.50, 0.50, 0.00], [0.00, 0.00, 0.50, 0.50], [0.25, 0.25, 0.25, 0.25],
                              [0.10, 0.20, 0.30, 0.40], [0.40, 0.30, 0.20, 0.10], [1.00, 0.00, 0.00, 0.00],
                              [0.10, 0.20, 0.30, 0.40], [0.40, 0.30, 0.20, 0.10], [1.00, 0.00, 0.00, 0.00]
                              ]

        start_day = 4
        target_num_individuals = 25
        create_nucleotide_sequence_from = "ALLELE_FREQUENCIES"
        drug_resistant_allele_frequencies_per_genome_location = [[0.7, 0.3, 0, 0]]
        node_ids = [83, 235]

        add_outbreak_malaria_genetics(camp, start_day=start_day,
                                      target_num_individuals=target_num_individuals,
                                      create_nucleotide_sequence_from=create_nucleotide_sequence_from,
                                      barcode_allele_frequencies_per_genome_location=allele_frequencies,
                                      drug_resistant_allele_frequencies_per_genome_location=drug_resistant_allele_frequencies_per_genome_location,
                                      node_ids=node_ids)

        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], node_ids)
        event_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(event_config['Target_Num_Individuals'], target_num_individuals)
        self.assertEqual(event_config['Individual_Selection_Type'], "TARGET_NUM_INDIVIDUALS")
        intervention_config = event_config['Intervention_Config']
        self.assertEqual(intervention_config['class'], "OutbreakIndividualMalariaGenetics")
        self.assertEqual(intervention_config['Barcode_Allele_Frequencies_Per_Genome_Location'], allele_frequencies)
        self.assertEqual(intervention_config['Drug_Resistant_Allele_Frequencies_Per_Genome_Location'],
                         drug_resistant_allele_frequencies_per_genome_location)
        self.assertEqual(intervention_config['Create_Nucleotide_Sequence_From'], create_nucleotide_sequence_from)

        pass

    def test_2_custom_add_outbreak_malaria_genetics(self):
        camp.campaign_dict["Events"] = []
        barcode_string = "AAAAAAAAAAAAAAAAAAAA"
        create_nucleotide_sequence_from = "BARCODE_STRING"
        drug_resistant_string = "CC"

        add_outbreak_malaria_genetics(camp,
                                      barcode_string=barcode_string,
                                      drug_resistant_string=drug_resistant_string)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], 1)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetAll")
        event_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(event_config['Demographic_Coverage'], 1)
        self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        intervention_config = event_config['Intervention_Config']
        self.assertEqual(intervention_config['class'], "OutbreakIndividualMalariaGenetics")
        self.assertEqual(intervention_config['Barcode_String'], barcode_string)
        self.assertEqual(intervention_config['Drug_Resistant_String'], drug_resistant_string)
        self.assertEqual(intervention_config['Create_Nucleotide_Sequence_From'], create_nucleotide_sequence_from)
        self.assertEqual(intervention_config['Incubation_Period_Override'], -1)
        self.assertEqual(intervention_config['Ignore_Immunity'], 1)

        pass

    def test_3_custom_add_outbreak_malaria_genetics(self):
        camp.campaign_dict["Events"] = []
        barcode_string = "AAAAAAAAAAAAAAAAAAAA"
        start_day = 8
        demographic_coverage = 0.25
        create_nucleotide_sequence_from = "NUCLEOTIDE_SEQUENCE"
        drug_resistant_string = "CC"
        msp_variant_value = 460
        pfemp1_variants_values = [x for x in range(200, 250)]

        add_outbreak_malaria_genetics(camp, start_day=start_day,
                                      demographic_coverage=demographic_coverage,
                                      create_nucleotide_sequence_from=create_nucleotide_sequence_from,
                                      drug_resistant_string=drug_resistant_string,
                                      msp_variant_value=msp_variant_value,
                                      pfemp1_variants_values=pfemp1_variants_values)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetAll")
        event_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(event_config['Demographic_Coverage'], demographic_coverage)
        self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        intervention_config = event_config['Intervention_Config']
        self.assertEqual(intervention_config['class'], "OutbreakIndividualMalariaGenetics")
        self.assertEqual(intervention_config['Drug_Resistant_String'], drug_resistant_string)
        self.assertEqual(intervention_config['Create_Nucleotide_Sequence_From'], create_nucleotide_sequence_from)
        self.assertEqual(intervention_config['PfEMP1_Variants_Values'], pfemp1_variants_values)
        self.assertEqual(intervention_config['MSP_Variant_Value'], msp_variant_value)

        pass

    def test_1_custom_add_outbreak_malaria_var_genes(self):
        camp.campaign_dict["Events"] = []
        start_day = 8
        demographic_coverage = 0.25
        msp_type = 2
        irbc_type = [
            2, 75, 148, 221, 294, 367, 440, 513, 586, 659, 732, 805, 878, 951, 24, 97, 170,
            243, 316, 389, 462, 535, 608, 681, 754, 827, 900, 973, 46, 119, 192, 265, 338,
            411, 484, 557, 630, 703, 776, 849, 922, 995, 68, 141, 214, 287, 360, 433, 506, 579
        ]
        minor_epitope_type = [
            2, 0, 3, 3, 1, 2, 3, 3, 0, 1, 3, 2, 1, 3, 0, 1, 1, 2, 4, 0, 1, 1, 0, 4, 0, 1, 1, 4, 4, 0, 2, 0, 4, 1, 2, 1,
            1, 0, 1, 3, 3, 1, 2, 4, 2, 4, 4, 3, 2, 4
        ]

        add_outbreak_malaria_var_genes(camp, start_day=start_day,
                                       demographic_coverage=demographic_coverage,
                                       msp_type=msp_type, irbc_type=irbc_type, minor_epitope_type=minor_epitope_type)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetAll")
        event_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(event_config['Demographic_Coverage'], demographic_coverage)
        self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        intervention_config = event_config['Intervention_Config']
        self.assertEqual(intervention_config['class'], "OutbreakIndividualMalariaVarGenes")
        self.assertEqual(intervention_config['IRBC_Type'], irbc_type)
        self.assertEqual(intervention_config['Minor_Epitope_Type'], minor_epitope_type)
        self.assertEqual(intervention_config['MSP_Type'], msp_type)

        pass

    def test_2_custom_add_outbreak_malaria_var_genes(self):
        camp.campaign_dict["Events"] = []
        start_day = 8
        target_num_individuals = 17
        node_ids = [90, 33]
        msp_type = 2
        irbc_type = [
            2, 75, 148, 221, 294, 367, 440, 513, 586, 659, 732, 805, 878, 951, 24, 97, 170,
            243, 316, 389, 462, 535, 608, 681, 754, 827, 900, 973, 46, 119, 192, 265, 338,
            411, 484, 557, 630, 703, 776, 849, 922, 995, 68, 141, 214, 287, 360, 433, 506, 579
        ]
        minor_epitope_type = [
            2, 0, 3, 3, 1, 2, 3, 3, 0, 1, 3, 2, 1, 3, 0, 1, 1, 2, 4, 0, 1, 1, 0, 4, 0, 1, 1, 4, 4, 0, 2, 0, 4, 1, 2, 1,
            1, 0, 1, 3, 3, 1, 2, 4, 2, 4, 4, 3, 2, 4
        ]

        add_outbreak_malaria_var_genes(camp, start_day=start_day,
                                       target_num_individuals=target_num_individuals,
                                       node_ids=node_ids,
                                       msp_type=msp_type, irbc_type=irbc_type, minor_epitope_type=minor_epitope_type)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], node_ids)
        event_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(event_config['Target_Num_Individuals'], target_num_individuals)
        self.assertEqual(event_config['Individual_Selection_Type'], "TARGET_NUM_INDIVIDUALS")
        intervention_config = event_config['Intervention_Config']
        self.assertEqual(intervention_config['class'], "OutbreakIndividualMalariaVarGenes")
        self.assertEqual(intervention_config['IRBC_Type'], irbc_type)
        self.assertEqual(intervention_config['Minor_Epitope_Type'], minor_epitope_type)
        self.assertEqual(intervention_config['MSP_Type'], msp_type)

        pass

    def test_vaccine_custom(self):
        camp.campaign_dict["Events"] = []
        start_day = 12
        target_num_individuals = 78
        node_ids = [12, 234, 3]
        repetitions = 5
        timesteps_between_repetitions = 30
        ind_property_restrictions = [{"Risk": "High", "Location": "Rural"}, {"Risk": "Medium", "Location": "Urban"}]
        target_age_min = 3
        target_age_max = 35
        target_gender = "Female"
        broadcast_event = "I am vaccinated!"
        vaccine_type = "TransmissionBlocking"
        vaccine_take = 0.95
        vaccine_initial_effect = 0.98
        vaccine_box_duration = 2000
        vaccine_decay_time_constant = 135
        efficacy_is_multiplicative = False

        add_scheduled_vaccine(camp,
                              start_day=start_day,
                              target_num_individuals=target_num_individuals,
                              node_ids=node_ids,
                              repetitions=repetitions,
                              timesteps_between_repetitions=timesteps_between_repetitions,
                              ind_property_restrictions=ind_property_restrictions,
                              target_age_min=target_age_min,
                              target_age_max=target_age_max,
                              target_gender=target_gender,
                              broadcast_event=broadcast_event,
                              vaccine_type=vaccine_type,
                              vaccine_take=vaccine_take,
                              vaccine_initial_effect=vaccine_initial_effect,
                              vaccine_box_duration=vaccine_box_duration,
                              vaccine_decay_time_constant=vaccine_decay_time_constant,
                              efficacy_is_multiplicative=efficacy_is_multiplicative)

        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], node_ids)
        coordinator_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(coordinator_config['Target_Num_Individuals'], target_num_individuals)
        self.assertEqual(coordinator_config['Individual_Selection_Type'], "TARGET_NUM_INDIVIDUALS")
        self.assertEqual(coordinator_config['Target_Age_Max'], target_age_max)
        self.assertEqual(coordinator_config['Target_Age_Min'], target_age_min)
        self.assertEqual(coordinator_config['Target_Gender'], target_gender)
        self.assertEqual(coordinator_config['Target_Demographic'], "ExplicitAgeRangesAndGender")
        self.assertEqual(coordinator_config['Property_Restrictions_Within_Node'], ind_property_restrictions)
        self.assertEqual(coordinator_config['Number_Repetitions'], repetitions)
        self.assertEqual(coordinator_config['Timesteps_Between_Repetitions'], timesteps_between_repetitions)
        self.assertEqual(len(coordinator_config['Intervention_Config']['Intervention_List']), 2)
        intervention_1 = coordinator_config['Intervention_Config']['Intervention_List'][1]
        intervention_0 = coordinator_config['Intervention_Config']['Intervention_List'][0]
        if intervention_0['class'] == "BroadcastEvent":
            self.assertEqual(intervention_0["Broadcast_Event"], broadcast_event)
            self.assertEqual(intervention_1['class'], "SimpleVaccine")
            self.assertEqual(intervention_1['Efficacy_Is_Multiplicative'], 0)
            self.assertEqual(intervention_1['Vaccine_Take'], vaccine_take)
            self.assertEqual(intervention_1['Vaccine_Type'], vaccine_type)
            self.assertEqual(intervention_1['Waning_Config']["Box_Duration"], vaccine_box_duration)
            self.assertEqual(intervention_1['Waning_Config']["Initial_Effect"], vaccine_initial_effect)
            self.assertEqual(intervention_1['Waning_Config']["class"], "WaningEffectBoxExponential")
        else:  # just in case this happens the other way around
            self.assertEqual(intervention_0['class'], "SimpleVaccine")
            self.assertEqual(intervention_0['Efficacy_Is_Multiplicative'], 0)
            self.assertEqual(intervention_0['Vaccine_Take'], vaccine_take)
            self.assertEqual(intervention_0['Vaccine_Type'], vaccine_type)
            self.assertEqual(intervention_0['Waning_Config']["Box_Duration"], vaccine_box_duration)
            self.assertEqual(intervention_0['Waning_Config']["Initial_Effect"], vaccine_initial_effect)
            self.assertEqual(intervention_0['Waning_Config']["class"], "WaningEffectBoxExponential")
            self.assertEqual(intervention_1["Broadcast_Event"], broadcast_event)
        pass

    def test_vaccine_default(self):
        camp.campaign_dict["Events"] = []
        add_scheduled_vaccine(camp)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]['Event_Coordinator_Config']
        self.assertEqual(camp.campaign_dict['Events'][0]['Start_Day'], 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetAll")
        self.assertEqual(campaign_event['Demographic_Coverage'], 1)
        self.assertEqual(campaign_event['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(campaign_event['Target_Gender'], "All")
        self.assertEqual(campaign_event['Target_Demographic'],
                         "ExplicitAgeRanges")  # should be everyone, but there's a bug in emod_api.intervnetions.common
        self.assertEqual(campaign_event['Property_Restrictions'], [])
        self.assertEqual(campaign_event['Number_Repetitions'], 1)
        self.assertEqual(campaign_event['Timesteps_Between_Repetitions'], 365)
        intervention_0 = campaign_event['Intervention_Config']
        self.assertEqual(intervention_0['class'], "SimpleVaccine")
        self.assertEqual(intervention_0['Efficacy_Is_Multiplicative'], 1)
        self.assertEqual(intervention_0['Vaccine_Take'], 1)
        self.assertEqual(intervention_0['Vaccine_Type'], "AcquisitionBlocking")
        self.assertEqual(intervention_0['Waning_Config']["Box_Duration"], 365)
        self.assertEqual(intervention_0['Waning_Config']["Initial_Effect"], 1)
        self.assertEqual(intervention_0['Waning_Config']["class"], "WaningEffectBoxExponential")

    def test_triggered_vaccine_default(self):
        camp.campaign_dict["Events"] = []
        add_triggered_vaccine(camp, trigger_condition_list=["HappyBirthday"])
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]['Event_Coordinator_Config']
        self.assertEqual(camp.campaign_dict['Events'][0]['Start_Day'], 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetAll")
        self.assertEqual(campaign_event['Demographic_Coverage'], 1)
        self.assertEqual(campaign_event['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(campaign_event['Target_Gender'], "All")
        self.assertEqual(campaign_event['Intervention_Config']['Target_Demographic'],
                         "ExplicitAgeRanges")  # should be everyone, but there's a bug in emod_api.intervnetions.common
        self.assertEqual(campaign_event['Intervention_Config']['Property_Restrictions'], [])
        self.assertEqual(campaign_event['Number_Repetitions'], 1)
        self.assertEqual(campaign_event['Timesteps_Between_Repetitions'], 365)
        intervention_0 = campaign_event['Intervention_Config']['Actual_IndividualIntervention_Config']
        self.assertEqual(intervention_0['class'], "SimpleVaccine")
        self.assertEqual(intervention_0['Efficacy_Is_Multiplicative'], 1)
        self.assertEqual(intervention_0['Vaccine_Take'], 1)
        self.assertEqual(intervention_0['Vaccine_Type'], "AcquisitionBlocking")
        self.assertEqual(intervention_0['Waning_Config']["Box_Duration"], 365)
        self.assertEqual(intervention_0['Waning_Config']["Initial_Effect"], 1)
        self.assertEqual(intervention_0['Waning_Config']["class"], "WaningEffectBoxExponential")

    def test_triggered_vaccine_custom(self):
        camp.campaign_dict["Events"] = []
        start_day = 12
        triggers = ["Births", "HappyBirthday"]
        delay = 234
        duration = 324
        demographic_coverage = 0.374
        node_ids = [12, 234, 3]
        repetitions = 5
        timesteps_between_repetitions = 30
        ind_property_restrictions = [{"Risk": "High", "Location": "Rural"}, {"Risk": "Medium", "Location": "Urban"}]
        target_age_min = 3
        target_age_max = 35
        target_gender = "Female"
        broadcast_event = "I am vaccinated!"
        vaccine_type = "TransmissionBlocking"
        vaccine_take = 0.95
        vaccine_initial_effect = 0.98
        vaccine_box_duration = 2000
        vaccine_decay_time_constant = 549
        efficacy_is_multiplicative = False

        add_triggered_vaccine(camp,
                              start_day=start_day,
                              demographic_coverage=demographic_coverage,
                              trigger_condition_list=triggers,
                              delay_period_constant=delay,
                              listening_duration=duration,
                              node_ids=node_ids,
                              repetitions=repetitions,
                              timesteps_between_repetitions=timesteps_between_repetitions,
                              ind_property_restrictions=ind_property_restrictions,
                              target_age_min=target_age_min,
                              target_age_max=target_age_max,
                              target_gender=target_gender,
                              broadcast_event=broadcast_event,
                              vaccine_type=vaccine_type,
                              vaccine_take=vaccine_take,
                              vaccine_initial_effect=vaccine_initial_effect,
                              vaccine_box_duration=vaccine_box_duration,
                              vaccine_decay_time_constant=vaccine_decay_time_constant,
                              efficacy_is_multiplicative=efficacy_is_multiplicative)

        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], node_ids)
        triggered_config = campaign_event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(triggered_config['Target_Age_Max'], target_age_max)
        self.assertEqual(triggered_config['Target_Age_Min'], target_age_min)
        self.assertEqual(triggered_config['Target_Gender'], target_gender)
        self.assertEqual(triggered_config['Target_Demographic'], "ExplicitAgeRangesAndGender")
        self.assertEqual(triggered_config['Property_Restrictions_Within_Node'], ind_property_restrictions)
        self.assertEqual(triggered_config['Trigger_Condition_List'], triggers)
        self.assertEqual(triggered_config['Duration'], duration)
        self.assertEqual(triggered_config['Actual_IndividualIntervention_Config']["Delay_Period_Constant"], delay)
        self.assertEqual(campaign_event['Event_Coordinator_Config']['Number_Repetitions'], repetitions)
        self.assertEqual(campaign_event['Event_Coordinator_Config']['Timesteps_Between_Repetitions'],
                         timesteps_between_repetitions)
        intervention_1 = \
            triggered_config['Actual_IndividualIntervention_Config']['Actual_IndividualIntervention_Configs'][1]
        intervention_0 = \
            triggered_config['Actual_IndividualIntervention_Config']['Actual_IndividualIntervention_Configs'][0]
        if intervention_0['class'] == "BroadcastEvent":
            self.assertEqual(intervention_0["Broadcast_Event"], broadcast_event)
            self.assertEqual(intervention_1['class'], "SimpleVaccine")
            self.assertEqual(intervention_1['Efficacy_Is_Multiplicative'], 0)
            self.assertEqual(intervention_1['Vaccine_Take'], vaccine_take)
            self.assertEqual(intervention_1['Vaccine_Type'], vaccine_type)
            self.assertEqual(intervention_1['Waning_Config']["Box_Duration"], vaccine_box_duration)
            self.assertEqual(intervention_1['Waning_Config']["Initial_Effect"], vaccine_initial_effect)
            self.assertEqual(intervention_1['Waning_Config']["class"], "WaningEffectBoxExponential")
        else:  # just in case this happens the other way around
            self.assertEqual(intervention_0['class'], "SimpleVaccine")
            self.assertEqual(intervention_0['Efficacy_Is_Multiplicative'], 0)
            self.assertEqual(intervention_0['Vaccine_Take'], vaccine_take)
            self.assertEqual(intervention_0['Vaccine_Type'], vaccine_type)
            self.assertEqual(intervention_0['Waning_Config']["Box_Duration"], vaccine_box_duration)
            self.assertEqual(intervention_0['Waning_Config']["Initial_Effect"], vaccine_initial_effect)
            self.assertEqual(intervention_0['Waning_Config']["class"], "WaningEffectBoxExponential")
            self.assertEqual(intervention_1["Broadcast_Event"], broadcast_event)

        # test IRSHousindModification

    def test_scheduled_irs_custom(self):
        camp.campaign_dict["Events"] = []
        start_day = 12
        target_num_individuals = 78
        node_ids = [12, 234, 3]
        repetitions = 5
        timesteps_between_repetitions = 30
        ind_property_restrictions = [{"Risk": "High", "Location": "Rural"}, {"Risk": "Medium", "Location": "Urban"}]
        target_age_min = 3
        target_age_max = 35
        target_gender = "Female"
        broadcast_event = "IRS!"
        target_residents_only = True
        killing_initial_effect = 0.99
        killing_box_duration = 27
        killing_decay_time_constant = 904
        repelling_initial_effect = 0.21
        repelling_box_duration = 33
        repelling_decay_time_constant = 0
        insecticide = "TheBestInsecticide"
        intervention_name = "IRSTEST"

        add_scheduled_irs_housing_modification(camp,
                                               start_day=start_day,
                                               target_num_individuals=target_num_individuals,
                                               node_ids=node_ids,
                                               repetitions=repetitions,
                                               timesteps_between_repetitions=timesteps_between_repetitions,
                                               ind_property_restrictions=ind_property_restrictions,
                                               target_age_min=target_age_min,
                                               target_age_max=target_age_max,
                                               target_gender=target_gender,
                                               broadcast_event=broadcast_event,
                                               target_residents_only=target_residents_only,
                                               killing_initial_effect=killing_initial_effect,
                                               killing_box_duration=killing_box_duration,
                                               killing_decay_time_constant=killing_decay_time_constant,
                                               repelling_initial_effect=repelling_initial_effect,
                                               repelling_box_duration=repelling_box_duration,
                                               repelling_decay_time_constant=repelling_decay_time_constant,
                                               insecticide=insecticide,
                                               intervention_name=intervention_name)

        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], node_ids)
        coordinator_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(coordinator_config['Target_Num_Individuals'], target_num_individuals)
        self.assertEqual(coordinator_config['Individual_Selection_Type'], "TARGET_NUM_INDIVIDUALS")
        self.assertEqual(coordinator_config['Target_Age_Max'], target_age_max)
        self.assertEqual(coordinator_config['Target_Age_Min'], target_age_min)
        self.assertEqual(coordinator_config['Target_Gender'], target_gender)
        self.assertEqual(coordinator_config['Target_Residents_Only'], 1)
        self.assertEqual(coordinator_config['Target_Demographic'], "ExplicitAgeRangesAndGender")
        self.assertEqual(coordinator_config['Property_Restrictions_Within_Node'], ind_property_restrictions)
        self.assertEqual(coordinator_config['Number_Repetitions'], repetitions)
        self.assertEqual(coordinator_config['Timesteps_Between_Repetitions'], timesteps_between_repetitions)
        self.assertEqual(len(coordinator_config['Intervention_Config']['Intervention_List']), 2)
        intervention_1 = coordinator_config['Intervention_Config']['Intervention_List'][1]
        intervention_0 = coordinator_config['Intervention_Config']['Intervention_List'][0]
        if intervention_0['class'] == "BroadcastEvent":
            self.assertEqual(intervention_0["Broadcast_Event"], broadcast_event)
            self.assertEqual(intervention_1['class'], "IRSHousingModification")
            self.assertEqual(intervention_1['Insecticide_Name'], insecticide)
            self.assertEqual(intervention_1["Intervention_Name"], intervention_name)
            self.assertEqual(intervention_1['Killing_Config']["Box_Duration"], killing_box_duration)
            self.assertEqual(intervention_1['Killing_Config']["Initial_Effect"], killing_initial_effect)
            self.assertEqual(intervention_1["Killing_Config"]["Decay_Time_Constant"], killing_decay_time_constant)
            self.assertEqual(intervention_1['Killing_Config']["class"], "WaningEffectBoxExponential")
            self.assertEqual(intervention_1['Repelling_Config']["Box_Duration"], repelling_box_duration)
            self.assertEqual(intervention_1['Repelling_Config']["Initial_Effect"], repelling_initial_effect)
            self.assertEqual(intervention_1['Repelling_Config']["class"], "WaningEffectBox")
        else:  # just in case this happens the other way around
            self.assertEqual(intervention_1["Broadcast_Event"], broadcast_event)
            self.assertEqual(intervention_0['class'], "IRSHousingModification")
            self.assertEqual(intervention_0['Insecticide_Name'], insecticide)
            self.assertEqual(intervention_0["Intervention_Name"], intervention_name)
            self.assertEqual(intervention_0['Killing_Config']["Box_Duration"], killing_box_duration)
            self.assertEqual(intervention_0['Killing_Config']["Initial_Effect"], killing_initial_effect)
            self.assertEqual(intervention_0["Killing_Config"]["Decay_Time_Constant"], killing_decay_time_constant)
            self.assertEqual(intervention_0['Killing_Config']["class"], "WaningEffectBoxExponential")
            self.assertEqual(intervention_0['Repelling_Config']["Box_Duration"], repelling_box_duration)
            self.assertEqual(intervention_0['Repelling_Config']["Initial_Effect"], repelling_initial_effect)
            self.assertEqual(intervention_0['Repelling_Config']["class"], "WaningEffectBox")
        pass

    def test_scheduled_irs_default_no_broadcast(self):
        camp.campaign_dict["Events"] = []
        target_residents_only = 0
        killing_initial_effect = 1
        killing_decay_time_constant = 90
        repelling_initial_effect = 0
        repelling_decay_time_constant = 90
        insecticide = ""
        intervention_name = "IRSHousingModification"
        add_scheduled_irs_housing_modification(camp, broadcast_event="")
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]['Event_Coordinator_Config']
        self.assertEqual(camp.campaign_dict['Events'][0]['Start_Day'], 1)
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetAll")
        self.assertEqual(campaign_event['Demographic_Coverage'], 1)
        self.assertEqual(campaign_event['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(campaign_event['Target_Gender'], "All")
        self.assertEqual(campaign_event['Target_Demographic'],
                         "ExplicitAgeRanges")  # should be everyone, but there's a bug in emod_api.intervnetions.common
        self.assertEqual(campaign_event['Target_Residents_Only'], target_residents_only)
        self.assertEqual(campaign_event['Property_Restrictions'], [])
        self.assertEqual(campaign_event['Number_Repetitions'], 1)
        self.assertEqual(campaign_event['Timesteps_Between_Repetitions'], 365)
        intervention_0 = campaign_event['Intervention_Config']
        self.assertEqual(intervention_0['Insecticide_Name'], insecticide)
        self.assertEqual(intervention_0["Intervention_Name"], intervention_name)
        self.assertEqual(intervention_0['Killing_Config']["Initial_Effect"], killing_initial_effect)
        self.assertEqual(intervention_0["Killing_Config"]["Decay_Time_Constant"], killing_decay_time_constant)
        self.assertEqual(intervention_0['Killing_Config']["class"], WaningEffects.Exp)
        self.assertEqual(intervention_0['Repelling_Config']["Initial_Effect"], repelling_initial_effect)
        self.assertEqual(intervention_0["Repelling_Config"]["Decay_Time_Constant"], repelling_decay_time_constant)
        self.assertEqual(intervention_0['Repelling_Config']["class"], WaningEffects.Exp)

    def test_scheduled_irs_default(self):
        camp.campaign_dict["Events"] = []
        start_day = 1
        repetitions = 1
        timesteps_between_repetitions = 365
        target_age_min = 0
        target_age_max = 125
        target_gender = "All"
        broadcast_event = "Received_IRS"
        target_residents_only = 0
        killing_initial_effect = 1
        killing_box_duration = 0
        killing_decay_time_constant = 90
        repelling_initial_effect = 0
        repelling_decay_time_constant = 90
        insecticide = ""
        intervention_name = "IRSHousingModification"

        add_scheduled_irs_housing_modification(camp)

        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetAll")
        coordinator_config = campaign_event['Event_Coordinator_Config']
        self.assertNotIn("Target_Num_Individuals", coordinator_config)
        self.assertEqual(coordinator_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(coordinator_config['Target_Age_Max'], target_age_max)
        self.assertEqual(coordinator_config['Target_Age_Min'], target_age_min)
        self.assertEqual(coordinator_config['Target_Gender'], target_gender)
        self.assertEqual(coordinator_config['Target_Residents_Only'], target_residents_only)
        self.assertEqual(coordinator_config['Target_Demographic'], "ExplicitAgeRanges")
        self.assertNotIn('Property_Restrictions_Within_Node', coordinator_config)
        self.assertEqual(coordinator_config['Number_Repetitions'], repetitions)
        self.assertEqual(coordinator_config['Timesteps_Between_Repetitions'], timesteps_between_repetitions)
        self.assertEqual(len(coordinator_config['Intervention_Config']['Intervention_List']), 2)
        intervention_1 = coordinator_config['Intervention_Config']['Intervention_List'][1]
        intervention_0 = coordinator_config['Intervention_Config']['Intervention_List'][0]
        if intervention_0['class'] == "BroadcastEvent":
            self.assertEqual(intervention_0["Broadcast_Event"], broadcast_event)
            self.assertEqual(intervention_1['class'], "IRSHousingModification")
            self.assertEqual(intervention_1['Insecticide_Name'], insecticide)
            self.assertEqual(intervention_1["Intervention_Name"], intervention_name)
            self.assertEqual(intervention_1['Killing_Config']["Initial_Effect"], killing_initial_effect)
            self.assertEqual(intervention_1["Killing_Config"]["Decay_Time_Constant"], killing_decay_time_constant)
            self.assertEqual(intervention_1['Killing_Config']["class"], WaningEffects.Exp)
            self.assertEqual(intervention_1['Repelling_Config']["Initial_Effect"], repelling_initial_effect)
            self.assertEqual(intervention_1["Repelling_Config"]["Decay_Time_Constant"], repelling_decay_time_constant)
            self.assertEqual(intervention_1['Repelling_Config']["class"], WaningEffects.Exp)
        else:  # just in case this happens the other way around
            self.assertEqual(intervention_1["Broadcast_Event"], broadcast_event)
            self.assertEqual(intervention_0['class'], "IRSHousingModification")
            self.assertEqual(intervention_0['Insecticide_Name'], insecticide)
            self.assertEqual(intervention_0["Intervention_Name"], intervention_name)
            self.assertEqual(intervention_0['Killing_Config']["Initial_Effect"], killing_initial_effect)
            self.assertEqual(intervention_0["Killing_Config"]["Decay_Time_Constant"], killing_decay_time_constant)
            self.assertEqual(intervention_0['Killing_Config']["class"], WaningEffects.Exp)
            self.assertEqual(intervention_0['Repelling_Config']["Initial_Effect"], repelling_initial_effect)
            self.assertEqual(intervention_0["Repelling_Config"]["Decay_Time_Constant"], repelling_decay_time_constant)
            self.assertEqual(intervention_0['Repelling_Config']["class"], WaningEffects.Exp)
        pass

    def test_triggered_irs_custom(self):
        camp.campaign_dict["Events"] = []
        start_day = 12
        triggers = ["Births", "HappyBirthday"]
        delay = 234
        duration = 324
        demographic_coverage = 0.374
        node_ids = [12, 234, 3]
        repetitions = 5
        timesteps_between_repetitions = 30
        ind_property_restrictions = [{"Risk": "High", "Location": "Rural"}, {"Risk": "Medium", "Location": "Urban"}]
        target_age_min = 3
        target_age_max = 35
        target_gender = "Female"
        broadcast_event = "IRS!"
        target_residents_only = True
        killing_initial_effect = 0.99
        killing_box_duration = 27
        killing_decay_time_constant = 904
        repelling_initial_effect = 0.21
        repelling_box_duration = 33
        repelling_decay_time_constant = 0
        insecticide = "TheBestInsecticide"
        intervention_name = "IRSTEST"

        add_triggered_irs_housing_modification(camp,
                                               start_day=start_day,
                                               demographic_coverage=demographic_coverage,
                                               trigger_condition_list=triggers,
                                               delay_period_constant=delay,
                                               listening_duration=duration,
                                               node_ids=node_ids,
                                               repetitions=repetitions,
                                               timesteps_between_repetitions=timesteps_between_repetitions,
                                               ind_property_restrictions=ind_property_restrictions,
                                               target_age_min=target_age_min,
                                               target_age_max=target_age_max,
                                               target_gender=target_gender,
                                               target_residents_only=target_residents_only,
                                               broadcast_event=broadcast_event,
                                               killing_initial_effect=killing_initial_effect,
                                               killing_box_duration=killing_box_duration,
                                               killing_decay_time_constant=killing_decay_time_constant,
                                               repelling_initial_effect=repelling_initial_effect,
                                               repelling_box_duration=repelling_box_duration,
                                               repelling_decay_time_constant=repelling_decay_time_constant,
                                               insecticide=insecticide,
                                               intervention_name=intervention_name)

        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], node_ids)
        triggered_config = campaign_event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(triggered_config['Target_Age_Max'], target_age_max)
        self.assertEqual(triggered_config['Target_Age_Min'], target_age_min)
        self.assertEqual(triggered_config['Target_Gender'], target_gender)
        self.assertEqual(triggered_config['Target_Demographic'], "ExplicitAgeRangesAndGender")
        self.assertEqual(triggered_config['Property_Restrictions_Within_Node'], ind_property_restrictions)
        self.assertEqual(triggered_config['Trigger_Condition_List'], triggers)
        self.assertEqual(triggered_config['Duration'], duration)
        self.assertEqual(triggered_config['Actual_IndividualIntervention_Config']["Delay_Period_Constant"], delay)
        self.assertEqual(campaign_event['Event_Coordinator_Config']['Number_Repetitions'], repetitions)
        self.assertEqual(campaign_event['Event_Coordinator_Config']['Timesteps_Between_Repetitions'],
                         timesteps_between_repetitions)
        intervention_1 = \
            triggered_config['Actual_IndividualIntervention_Config']['Actual_IndividualIntervention_Configs'][1]
        intervention_0 = \
            triggered_config['Actual_IndividualIntervention_Config']['Actual_IndividualIntervention_Configs'][0]
        if intervention_0['class'] == "BroadcastEvent":
            self.assertEqual(intervention_0["Broadcast_Event"], broadcast_event)
            self.assertEqual(intervention_1['class'], "IRSHousingModification")
            self.assertEqual(intervention_1['Insecticide_Name'], insecticide)
            self.assertEqual(intervention_1["Intervention_Name"], intervention_name)
            self.assertEqual(intervention_1['Killing_Config']["Box_Duration"], killing_box_duration)
            self.assertEqual(intervention_1['Killing_Config']["Initial_Effect"], killing_initial_effect)
            self.assertEqual(intervention_1["Killing_Config"]["Decay_Time_Constant"], killing_decay_time_constant)
            self.assertEqual(intervention_1['Killing_Config']["class"], "WaningEffectBoxExponential")
            self.assertEqual(intervention_1['Repelling_Config']["Box_Duration"], repelling_box_duration)
            self.assertEqual(intervention_1['Repelling_Config']["Initial_Effect"], repelling_initial_effect)
            self.assertEqual(intervention_1['Repelling_Config']["class"], WaningEffects.Box)
        else:  # just in case this happens the other way around
            self.assertEqual(intervention_1["Broadcast_Event"], broadcast_event)
            self.assertEqual(intervention_0['class'], "IRSHousingModification")
            self.assertEqual(intervention_0['Insecticide_Name'], insecticide)
            self.assertEqual(intervention_0["Intervention_Name"], intervention_name)
            self.assertEqual(intervention_0['Killing_Config']["Box_Duration"], killing_box_duration)
            self.assertEqual(intervention_0['Killing_Config']["Initial_Effect"], killing_initial_effect)
            self.assertEqual(intervention_0["Killing_Config"]["Decay_Time_Constant"], killing_decay_time_constant)
            self.assertEqual(intervention_0['Killing_Config']["class"], "WaningEffectBoxExponential")
            self.assertEqual(intervention_0['Repelling_Config']["Box_Duration"], repelling_box_duration)
            self.assertEqual(intervention_0['Repelling_Config']["Initial_Effect"], repelling_initial_effect)
            self.assertEqual(intervention_0['Repelling_Config']["class"], WaningEffects.Box)

    def test_triggered_irs_default(self):
        camp.campaign_dict["Events"] = []
        triggers = ["Births"]
        start_day = 1
        repetitions = 1
        timesteps_between_repetitions = 365
        ind_property_restrictions = []
        target_age_min = 0
        target_age_max = 125
        target_gender = "All"
        broadcast_event = "Received_IRS"
        killing_initial_effect = 1
        killing_box_duration = 0
        killing_decay_time_constant = 90
        repelling_initial_effect = 0
        repelling_box_duration = 0
        repelling_decay_time_constant = 90
        insecticide = ""
        intervention_name = "IRSHousingModification"

        add_triggered_irs_housing_modification(camp, trigger_condition_list=triggers)

        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(camp.campaign_dict['Events'][0]['Nodeset_Config']['class'], "NodeSetAll")
        triggered_config = campaign_event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(triggered_config['Target_Age_Max'], target_age_max)
        self.assertEqual(triggered_config['Target_Age_Min'], target_age_min)
        self.assertEqual(triggered_config['Target_Gender'], target_gender)
        self.assertEqual(triggered_config['Target_Demographic'], "ExplicitAgeRanges")
        self.assertNotIn('Property_Restrictions_Within_Node', triggered_config)
        self.assertEqual(triggered_config['Trigger_Condition_List'], triggers)
        self.assertEqual(triggered_config['Duration'], -1)
        self.assertEqual(triggered_config['Actual_IndividualIntervention_Config']["class"],
                         "MultiInterventionDistributor")
        self.assertEqual(campaign_event['Event_Coordinator_Config']['Number_Repetitions'], repetitions)
        self.assertEqual(campaign_event['Event_Coordinator_Config']['Timesteps_Between_Repetitions'],
                         timesteps_between_repetitions)
        intervention_1 = \
            triggered_config['Actual_IndividualIntervention_Config']['Intervention_List'][1]
        intervention_0 = \
            triggered_config['Actual_IndividualIntervention_Config']['Intervention_List'][0]
        if intervention_0['class'] == "BroadcastEvent":
            self.assertEqual(intervention_0["Broadcast_Event"], broadcast_event)
            self.assertEqual(intervention_1['class'], "IRSHousingModification")
            self.assertNotIn('Insecticide', intervention_1)
            self.assertEqual(intervention_1["Intervention_Name"], intervention_name)
            self.assertEqual(intervention_1['Killing_Config']["Initial_Effect"], killing_initial_effect)
            self.assertEqual(intervention_1["Killing_Config"]["Decay_Time_Constant"], killing_decay_time_constant)
            self.assertEqual(intervention_1['Killing_Config']["class"], WaningEffects.Exp)
            self.assertEqual(intervention_1['Repelling_Config']["Initial_Effect"], repelling_initial_effect)
            self.assertEqual(intervention_1["Repelling_Config"]["Decay_Time_Constant"], repelling_decay_time_constant)
            self.assertEqual(intervention_1['Repelling_Config']["class"], WaningEffects.Exp)
        else:  # just in case this happens the other way around
            self.assertEqual(intervention_1["Broadcast_Event"], broadcast_event)
            self.assertEqual(intervention_0['class'], "IRSHousingModification")
            self.assertNotIn('Insecticide', intervention_0)
            self.assertEqual(intervention_0["Intervention_Name"], intervention_name)
            self.assertEqual(intervention_0['Killing_Config']["Initial_Effect"], killing_initial_effect)
            self.assertEqual(intervention_0["Killing_Config"]["Decay_Time_Constant"], killing_decay_time_constant)
            self.assertEqual(intervention_0['Killing_Config']["class"], WaningEffects.Exp)
            self.assertEqual(intervention_0['Repelling_Config']["Initial_Effect"], repelling_initial_effect)
            self.assertEqual(intervention_0["Repelling_Config"]["Decay_Time_Constant"], repelling_decay_time_constant)
            self.assertEqual(intervention_0['Repelling_Config']["class"], WaningEffects.Exp)

    def test_default_space_spraying(self):
        camp.campaign_dict["Events"] = []
        start_day = 1
        spray_coverage = 1
        killing_effect = 1
        add_scheduled_space_spraying(campaign=camp)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Spray_Coverage, spray_coverage)
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.Constant)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        pass

    def test_custom_space_spraying(self):
        camp.campaign_dict["Events"] = []
        start_day = 235
        spray_coverage = 0.69
        killing_effect = 0.52
        insecticide = "KillVectors"
        box_duration = 51
        decay_constant = 2324
        repetitions = 3
        intervention_name = "TestingSpaceSpraying"
        timesteps_between_repetitions = 32
        node_ids = [2, 3, 6]
        cost = 22
        add_scheduled_space_spraying(campaign=camp, start_day=start_day,
                                     node_ids=node_ids, repetitions=repetitions,
                                     timesteps_between_repetitions=timesteps_between_repetitions,
                                     spray_coverage=spray_coverage,
                                     insecticide=insecticide,
                                     intervention_name=intervention_name,
                                     killing_initial_effect=killing_effect,
                                     killing_box_duration=box_duration,
                                     killing_decay_time_constant=decay_constant,
                                     cost_to_consumer=cost)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.event_coordinator.Number_Repetitions, repetitions)
        self.assertEqual(self.event_coordinator.Timesteps_Between_Repetitions, timesteps_between_repetitions)
        self.assertEqual(self.intervention_config.Spray_Coverage, spray_coverage)
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.intervention_config.Insecticide_Name, insecticide)
        self.assertEqual(self.intervention_config.Intervention_Name, intervention_name)
        self.assertEqual(self.intervention_config.Cost_To_Consumer, cost)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], decay_constant)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], node_ids)
        pass

    def test_default_malaria_challenge(self):
        camp.campaign_dict["Events"] = []
        start_day = 0
        coverage = 1
        bites = 5
        challenge_type = "InfectiousBites"
        add_challenge_trial(campaign=camp)
        intervention_name = "MalariaChallenge"
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Coverage, coverage)
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        self.assertEqual(self.intervention_config.Challenge_Type, challenge_type)
        self.assertEqual(self.intervention_config.Infectious_Bite_Count, bites)
        self.assertEqual(self.intervention_config.Intervention_Name, intervention_name)
        pass

    def test_custom_malaria_challenge(self):
        camp.campaign_dict["Events"] = []
        start_day = 235
        coverage = 0.69
        intervention_name = "TestingMalariaChallenge"
        node_ids = [2, 3, 6]
        bites = 1
        sporozoites = 32
        challenge_type = "Sporozoites"
        add_challenge_trial(campaign=camp, start_day=start_day,
                            node_ids=node_ids,
                            demographic_coverage=coverage,
                            sporozoites=sporozoites,
                            infectious_bites=0,
                            intervention_name=intervention_name)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Coverage, coverage)
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.intervention_config.Challenge_Type, challenge_type)
        self.assertEqual(self.intervention_config.Infectious_Bite_Count, bites)
        self.assertEqual(self.intervention_config.Sporozoite_Count, sporozoites)
        self.assertEqual(self.intervention_config.Intervention_Name, intervention_name)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], node_ids)
        pass

    def test_malaria_challenge_exceptions(self):
        with self.assertRaisesRegex(Exception,
                                    "Please enter a positive value for either 'infectious_bites' or 'sporozoites', "
                                    "but not both.\n"):
            add_challenge_trial(campaign=camp, sporozoites=3, infectious_bites=4)
        with self.assertRaisesRegex(Exception,
                                    "Please enter a positive value for either 'infectious_bites' or 'sporozoites', "
                                    "but not both.\n"):
            add_challenge_trial(campaign=camp, sporozoites=0, infectious_bites=0)

    def test_default_scheduled_sugar_trap(self):
        camp.campaign_dict["Events"] = []
        start_day = 0
        repetitions = 1
        timesteps_between_repetitions = 365
        cost_to_consumer = 0
        expiration_constant = 30
        insecticide = ""
        intervention_name = "SugarTrap"
        killing_initial_effect = 1
        add_scheduled_sugar_trap(campaign=camp)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.intervention_config["Expiration_Period_Constant"], expiration_constant)
        self.assertEqual(self.intervention_config["Expiration_Period_Distribution"], "CONSTANT_DISTRIBUTION")
        self.assertEqual(self.intervention_config["Cost_To_Consumer"], cost_to_consumer)
        self.assertEqual(self.intervention_config["Insecticide_Name"], insecticide)
        self.assertEqual(self.intervention_config["Intervention_Name"], intervention_name)
        self.assertEqual(self.event_coordinator["Number_Repetitions"], repetitions)
        self.assertEqual(self.event_coordinator["Timesteps_Between_Repetitions"], timesteps_between_repetitions)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.Constant)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        pass

    def test_custom_scheduled_sugar_trap(self):
        camp.campaign_dict["Events"] = []
        start_day = 345
        node_ids = [234, 11, 42]
        repetitions = 8
        timesteps_between_repetitions = 3
        cost_to_consumer = 1.15
        expiration_config = {"Expiration_Period_Distribution": "GAUSSIAN_DISTRIBUTION",
                             "Expiration_Period_Gaussian_Mean": 20,
                             "Expiration_Period_Gaussian_Std_Dev": 10}
        expiration_constant = 33
        insecticide = "EatMe"
        intervention_name = "SugarTrapEatMe"
        killing_initial_effect = 0.89
        killing_box_duration = 256
        killing_decay_time_constant = 500
        add_scheduled_sugar_trap(campaign=camp, start_day=start_day,
                                 node_ids=node_ids, repetitions=repetitions,
                                 timesteps_between_repetitions=timesteps_between_repetitions,
                                 cost_to_consumer=cost_to_consumer, expiration_config=expiration_config,
                                 expiration_constant=expiration_constant, insecticide=insecticide,
                                 intervention_name=intervention_name, killing_initial_effect=killing_initial_effect,
                                 killing_box_duration=killing_box_duration,
                                 killing_decay_time_constant=killing_decay_time_constant)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.tmp_intervention["Start_Day"], start_day)
        self.assertEqual(self.intervention_config["Expiration_Period_Gaussian_Mean"], 20)
        self.assertEqual(self.intervention_config["Expiration_Period_Distribution"], "GAUSSIAN_DISTRIBUTION")
        self.assertEqual(self.intervention_config["Expiration_Period_Gaussian_Std_Dev"], 10)
        self.assertEqual(self.intervention_config["Cost_To_Consumer"], cost_to_consumer)
        self.assertEqual(self.intervention_config["Insecticide_Name"], insecticide)
        self.assertEqual(self.intervention_config["Intervention_Name"], intervention_name)
        self.assertEqual(self.event_coordinator["Number_Repetitions"], repetitions)
        self.assertEqual(self.event_coordinator["Timesteps_Between_Repetitions"], timesteps_between_repetitions)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], killing_decay_time_constant)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], killing_box_duration)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], node_ids)
        pass

    def test_default_larvicide(self):
        start_day = 1  # TBD: these should all really be loaded from schema.
        killing_effect = 1
        box_duration = 100
        camp.campaign_dict["Events"] = []
        add_larvicide(camp)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, start_day)
        self.assertNotIn("Insecticide_Name", self.intervention_config)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.Box)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        pass

    def test_custom_larvicide(self):
        camp.campaign_dict["Events"] = []
        start_day = 235
        killing_effect = 0.52
        insecticide = "KillVectors"
        spray_coverage = 0.44
        box_duration = 51
        decay_rate = 0.02
        node_ids = [2, 3, 6]
        camp.campaign_dict["Events"] = []
        add_larvicide(camp, start_day=start_day, spray_coverage=spray_coverage,
                      killing_effect=killing_effect, insecticide=insecticide,
                      box_duration=box_duration, decay_time_constant=1 / decay_rate,
                      node_ids=node_ids)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.intervention_config.Insecticide_Name, insecticide)
        self.assertEqual(self.intervention_config.Spray_Coverage, spray_coverage)
        self.assertIsNotNone(self.killing_config)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 1 / decay_rate)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], node_ids)
        pass

    def test_custom_add_community_health_worker(self):
        camp.campaign_dict["Events"] = []
        start_day = 123
        trigger_condition_list = ["Sick", "SoSick"]
        demographic_coverage = 0.63
        node_ids = [4, 6, 33]
        ind_property_restrictions = [{"Risk": "High", "Location": "Rural"}, {"Risk": "Medium", "Location": "Urban"}]
        target_age_min = 3
        target_age_max = 35
        target_gender = "Female"
        initial_amount = 12
        amount_in_shipment = 30
        days_between_shipments = 14
        duration = 780
        drug_type = "malaria_drug"
        intervention_name = "fancy_new_drug"
        intervention_config = _antimalarial_drug(camp, drug_type=drug_type, intervention_name=intervention_name)
        max_distributed_per_day = 3
        max_stock = 65
        waiting_period = 2
        self.tmp_intervention = add_community_health_worker(camp, start_day=start_day,
                                                            trigger_condition_list=trigger_condition_list,
                                                            demographic_coverage=demographic_coverage,
                                                            node_ids=node_ids,
                                                            ind_property_restrictions=ind_property_restrictions,
                                                            target_age_min=target_age_min,
                                                            target_age_max=target_age_max,
                                                            target_gender=target_gender,
                                                            initial_amount=initial_amount,
                                                            amount_in_shipment=amount_in_shipment,
                                                            days_between_shipments=days_between_shipments,
                                                            duration=duration,
                                                            intervention_config=intervention_config,
                                                            max_distributed_per_day=max_distributed_per_day,
                                                            max_stock=max_stock,
                                                            waiting_period=waiting_period)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], node_ids)
        coordinator_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(coordinator_config['Target_Age_Max'], target_age_max)
        self.assertEqual(coordinator_config['Target_Age_Min'], target_age_min)
        self.assertEqual(coordinator_config['Target_Gender'], target_gender)
        self.assertEqual(coordinator_config['Target_Demographic'], "ExplicitAgeRangesAndGender")
        self.assertEqual(coordinator_config['Property_Restrictions_Within_Node'], ind_property_restrictions)
        self.assertEqual(coordinator_config['Demographic_Coverage'], demographic_coverage)
        self.assertEqual(coordinator_config['class'], "CommunityHealthWorkerEventCoordinator")
        self.assertEqual(coordinator_config['Amount_In_Shipment'], amount_in_shipment)
        self.assertEqual(coordinator_config['Days_Between_Shipments'], days_between_shipments)
        self.assertEqual(coordinator_config['Max_Distributed_Per_Day'], max_distributed_per_day)
        self.assertEqual(coordinator_config['Max_Stock'], max_stock)
        self.assertEqual(coordinator_config['Duration'], duration)
        self.assertEqual(coordinator_config['Trigger_Condition_List'], trigger_condition_list)
        self.assertEqual(coordinator_config['Waiting_Period'], waiting_period)
        self.assertEqual(coordinator_config['Initial_Amount_Constant'], initial_amount)
        self.assertEqual(coordinator_config['Initial_Amount_Distribution'], "CONSTANT_DISTRIBUTION")
        intervention_config = coordinator_config['Intervention_Config']
        self.assertEqual(intervention_config['class'], "AntimalarialDrug")
        self.assertEqual(intervention_config['Intervention_Name'], intervention_name)
        self.assertEqual(intervention_config['Drug_Type'], drug_type)

        pass

    def test_default_add_community_health_worker(self):
        camp.campaign_dict["Events"] = []
        start_day = 1
        trigger_condition_list = ["Sick", "SoSick"]
        demographic_coverage = 1.0
        initial_amount = 6
        amount_in_shipment = 2147480000
        days_between_shipments = 7
        duration = 3.40282e+38
        drug_type = "malaria_drug"
        intervention_config = _antimalarial_drug(camp, drug_type=drug_type)
        max_distributed_per_day = 2147480000
        max_stock = 2147480000
        waiting_period = 0
        self.tmp_intervention = add_community_health_worker(camp, trigger_condition_list=trigger_condition_list,
                                                            intervention_config=intervention_config)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetAll")
        coordinator_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(coordinator_config['Target_Demographic'], "Everyone")
        self.assertEqual(coordinator_config['Property_Restrictions_Within_Node'], [])
        self.assertEqual(coordinator_config['Demographic_Coverage'], demographic_coverage)
        self.assertEqual(coordinator_config['class'], "CommunityHealthWorkerEventCoordinator")
        self.assertEqual(coordinator_config['Amount_In_Shipment'], amount_in_shipment)
        self.assertEqual(coordinator_config['Days_Between_Shipments'], days_between_shipments)
        self.assertEqual(coordinator_config['Max_Distributed_Per_Day'], max_distributed_per_day)
        self.assertEqual(coordinator_config['Max_Stock'], max_stock)
        self.assertEqual(coordinator_config['Duration'], duration)
        self.assertEqual(coordinator_config['Trigger_Condition_List'], trigger_condition_list)
        self.assertEqual(coordinator_config['Waiting_Period'], waiting_period)
        self.assertEqual(coordinator_config['Initial_Amount_Constant'], initial_amount)
        self.assertEqual(coordinator_config['Initial_Amount_Distribution'], "CONSTANT_DISTRIBUTION")
        intervention_config = coordinator_config['Intervention_Config']
        self.assertEqual(intervention_config['class'], "AntimalarialDrug")
        self.assertEqual(intervention_config['Intervention_Name'], "AntimalarialDrug_malaria_drug")
        self.assertEqual(intervention_config['Drug_Type'], drug_type)
        pass

    def test_scale_larval_habitat(self):
        # resetting campaign
        camp.campaign_dict["Events"] = []
        df = pd.DataFrame({'NodeID': [1, 2, 3, 4, 5],
                           'CONSTANT.arabiensis': [1, 0, 1, 1, 1],
                           'TEMPORARY_RAINFALL.arabiensis': [1, 1, 0, 1, 0],
                           'CONSTANT.funestus': [1, 0, 1, 1, 1],
                           'WATER_VEGETATION': [1, 1, 0, 1, 0]
                           })
        add_scale_larval_habitats(camp, df=df,
                                  start_day=35, repetitions=3, timesteps_between_repetitions=36)
        self.assertEqual(len(camp.campaign_dict['Events']), 3)
        for campaign_event in camp.campaign_dict['Events']:
            self.assertEqual(campaign_event['Start_Day'], 35)
            self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
            event_config = campaign_event['Event_Coordinator_Config']
            self.assertEqual(event_config['Number_Repetitions'], 3)
            self.assertEqual(event_config['Timesteps_Between_Repetitions'], 36)
            self.assertEqual(event_config['Demographic_Coverage'], 1)
            self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
            self.assertEqual(event_config['Target_Gender'], "All")
            self.assertEqual(event_config['Intervention_Config']['class'], "ScaleLarvalHabitat")
            if campaign_event['Nodeset_Config']['Node_List'] == [1, 4]:
                with open('14.json', 'w') as f:
                    json.dump(event_config['Intervention_Config']['Larval_Habitat_Multiplier'], f)
                self.assertIn({"Habitat": "WATER_VEGETATION", "Species": "ALL_SPECIES", "Factor": 1},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
                self.assertIn({"Habitat": "CONSTANT", "Species": "arabiensis", "Factor": 1},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
                self.assertIn({"Habitat": "CONSTANT", "Species": "funestus", "Factor": 1},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
                self.assertIn({"Habitat": "TEMPORARY_RAINFALL", "Species": "arabiensis", "Factor": 1},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
            elif campaign_event['Nodeset_Config']['Node_List'] == [3, 5]:
                with open('35.json', 'w') as f:
                    json.dump(event_config['Intervention_Config']['Larval_Habitat_Multiplier'], f)
                self.assertIn({"Habitat": "WATER_VEGETATION", "Species": "ALL_SPECIES", "Factor": 0},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
                self.assertIn({"Habitat": "CONSTANT", "Species": "arabiensis", "Factor": 1},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
                self.assertIn({"Habitat": "CONSTANT", "Species": "funestus", "Factor": 1},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
                self.assertIn({"Habitat": "TEMPORARY_RAINFALL", "Species": "arabiensis", "Factor": 0},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
            elif campaign_event['Nodeset_Config']['Node_List'] == [2]:
                with open('2.json', 'w') as f:
                    json.dump(event_config['Intervention_Config']['Larval_Habitat_Multiplier'], f)
                self.assertIn({"Habitat": "TEMPORARY_RAINFALL", "Species": "arabiensis", "Factor": 1},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
                self.assertIn({"Habitat": "WATER_VEGETATION", "Species": "ALL_SPECIES", "Factor": 1},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
                self.assertIn({"Habitat": "CONSTANT", "Species": "arabiensis", "Factor": 0},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
                self.assertIn({"Habitat": "CONSTANT", "Species": "funestus", "Factor": 0},
                              event_config['Intervention_Config']['Larval_Habitat_Multiplier'])
            else:
                self.assertTrue(True, "Could not find the correct node combination.")
        pass

    def test_scale_larval_habitat1(self):
        # resetting campaign
        camp.campaign_dict["Events"] = []
        df = pd.DataFrame({'TEMPORARY_RAINFALL': [3]})
        add_scale_larval_habitats(camp, df=df,
                                  start_day=35, repetitions=3, timesteps_between_repetitions=36)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        for campaign_event in camp.campaign_dict['Events']:  # there's only one
            self.assertEqual(campaign_event['Start_Day'], 35)
            self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetAll")
            event_config = campaign_event['Event_Coordinator_Config']
            self.assertEqual(event_config['Number_Repetitions'], 3)
            self.assertEqual(event_config['Timesteps_Between_Repetitions'], 36)
            self.assertEqual(event_config['Demographic_Coverage'], 1)
            self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
            self.assertEqual(event_config['Target_Gender'], "All")
            self.assertEqual(event_config['Intervention_Config']['class'], "ScaleLarvalHabitat")
            self.assertEqual(event_config['Intervention_Config']['Larval_Habitat_Multiplier'][0]["Habitat"],
                             "TEMPORARY_RAINFALL")
            self.assertEqual(event_config['Intervention_Config']['Larval_Habitat_Multiplier'][0]["Species"],
                             "ALL_SPECIES")
            self.assertEqual(event_config['Intervention_Config']['Larval_Habitat_Multiplier'][0]["Factor"],
                             3)
        pass

    def test_scale_larval_habitat2(self):
        # resetting campaign
        camp.campaign_dict["Events"] = []
        df = pd.DataFrame({'TEMPORARY_RAINFALL.arabiensis': [3]})
        add_scale_larval_habitats(camp, df=df,
                                  start_day=35, repetitions=3, timesteps_between_repetitions=36)
        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        for campaign_event in camp.campaign_dict['Events']:  # there's only one
            self.assertEqual(campaign_event['Start_Day'], 35)
            self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetAll")
            event_config = campaign_event['Event_Coordinator_Config']
            self.assertEqual(event_config['Number_Repetitions'], 3)
            self.assertEqual(event_config['Timesteps_Between_Repetitions'], 36)
            self.assertEqual(event_config['Demographic_Coverage'], 1)
            self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
            self.assertEqual(event_config['Target_Gender'], "All")
            self.assertEqual(event_config['Intervention_Config']['class'], "ScaleLarvalHabitat")
            self.assertEqual(event_config['Intervention_Config']['Larval_Habitat_Multiplier'][0]["Habitat"],
                             "TEMPORARY_RAINFALL")
            self.assertEqual(event_config['Intervention_Config']['Larval_Habitat_Multiplier'][0]["Species"],
                             "arabiensis")
            self.assertEqual(event_config['Intervention_Config']['Larval_Habitat_Multiplier'][0]["Factor"],
                             3)
        pass

    def test_scale_larval_habitat3(self):
        # resetting campaign
        camp.campaign_dict["Events"] = []
        df = pd.DataFrame({'NodeID': [0, 1, 2, 3, 4],
                           'CONSTANT': [1, 0, 1, 1, 1],
                           'TEMPORARY_RAINFALL': [1, 1, 0, 1, 0]})
        add_scale_larval_habitats(camp, df=df,
                                  start_day=35, repetitions=3, timesteps_between_repetitions=36)
        self.assertEqual(len(camp.campaign_dict['Events']), 3)
        all_found = 0
        for campaign_event in camp.campaign_dict['Events']:
            self.assertEqual(campaign_event['Start_Day'], 35)
            self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
            event_config = campaign_event['Event_Coordinator_Config']
            self.assertEqual(event_config['Number_Repetitions'], 3)
            self.assertEqual(event_config['Timesteps_Between_Repetitions'], 36)
            self.assertEqual(event_config['Demographic_Coverage'], 1)
            self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
            self.assertEqual(event_config['Target_Gender'], "All")
            if campaign_event['Nodeset_Config']['Node_List'] == [0, 3]:
                self.assertEqual(event_config['Intervention_Config']['class'], "ScaleLarvalHabitat")
                for habitat_multiplier in event_config['Intervention_Config']['Larval_Habitat_Multiplier']:
                    if habitat_multiplier["Habitat"] == "TEMPORARY_RAINFALL":
                        all_found += 1
                        self.assertEqual(habitat_multiplier["Species"], "ALL_SPECIES")
                        self.assertEqual(habitat_multiplier["Factor"], 1)
                    elif habitat_multiplier["Habitat"] == "CONSTANT":
                        all_found += 1
                        self.assertEqual(habitat_multiplier["Species"], "ALL_SPECIES")
                        self.assertEqual(habitat_multiplier["Factor"], 1)
            elif campaign_event['Nodeset_Config']['Node_List'] == [2, 4]:
                self.assertEqual(event_config['Intervention_Config']['class'], "ScaleLarvalHabitat")
                for habitat_multiplier in event_config['Intervention_Config']['Larval_Habitat_Multiplier']:
                    if habitat_multiplier["Habitat"] == "TEMPORARY_RAINFALL":
                        all_found += 1
                        self.assertEqual(habitat_multiplier["Species"], "ALL_SPECIES")
                        self.assertEqual(habitat_multiplier["Factor"], 0)
                    elif habitat_multiplier["Habitat"] == "CONSTANT":
                        all_found += 1
                        self.assertEqual(habitat_multiplier["Species"], "ALL_SPECIES")
                        self.assertEqual(habitat_multiplier["Factor"], 1)
            elif campaign_event['Nodeset_Config']['Node_List'] == [1]:
                self.assertEqual(event_config['Intervention_Config']['class'], "ScaleLarvalHabitat")
                for habitat_multiplier in event_config['Intervention_Config']['Larval_Habitat_Multiplier']:
                    if habitat_multiplier["Habitat"] == "TEMPORARY_RAINFALL":
                        all_found += 1
                        self.assertEqual(habitat_multiplier["Species"], "ALL_SPECIES")
                        self.assertEqual(habitat_multiplier["Factor"], 1)
                    elif habitat_multiplier["Habitat"] == "CONSTANT":
                        all_found += 1
                        self.assertEqual(habitat_multiplier["Species"], "ALL_SPECIES")
                        self.assertEqual(habitat_multiplier["Factor"], 0)
        self.assertEqual(all_found, 6)
        pass

    def test_adherent_drug(self):
        import emodpy_malaria.interventions.adherentdrug as ad
        doses = [["Sulfadoxine", "Pyrimethamine", 'Amodiaquine'], ['Amodiaquine'], ['Amodiaquine'],
                 ['Pyrimethamine']]  # use doses value that is different from the default
        dose_interval = 2
        non_adherence_options = ['Stop']
        non_adherence_distribution = [1]
        values = [1, 0.6, 0.4, 0.1]
        custom_intervention_name = "TryingNewDrugs"
        adherent_drug = ad.adherent_drug(camp,
                                         doses=doses,
                                         dose_interval=dose_interval,
                                         non_adherence_options=non_adherence_options,
                                         non_adherence_distribution=non_adherence_distribution,
                                         adherence_values=values,
                                         intervention_name=custom_intervention_name
                                         )
        times = [1.0, 2.0, 3.0, 4.0]
        self.assertEqual(adherent_drug["Adherence_Config"]["Durability_Map"]["Times"], times)
        self.assertEqual(adherent_drug["Adherence_Config"]["Durability_Map"]["Values"], values)
        self.assertEqual(adherent_drug["Doses"], doses)
        self.assertEqual(adherent_drug["Dose_Interval"], dose_interval)
        self.assertEqual(adherent_drug["Non_Adherence_Distribution"], non_adherence_distribution)
        self.assertEqual(adherent_drug["Non_Adherence_Options"], non_adherence_options)
        self.assertEqual(adherent_drug["Intervention_Name"], custom_intervention_name)
        pass

    def test_adherent_drug_defaults(self):
        import emodpy_malaria.interventions.adherentdrug as ad
        adherent_drug = ad.adherent_drug(camp
                                         # doses=doses,
                                         # dose_interval=dose_interval,
                                         # non_adherence_options=non_adherence_options,
                                         ##non_adherence_distribution=non_adherence_distribution,
                                         # adherence_values=values
                                         )
        default_doses = [["Sulfadoxine", "Pyrimethamine", 'Amodiaquine'], ['Amodiaquine'], ['Amodiaquine']]
        default_dose_interval = 1
        default_non_adherence_options = ['NEXT_UPDATE']
        default_non_adherence_distribution = [1]
        default_values = [1, 1, 1]  # we just happen to know this
        default_times = [1.0, 2.0, 3.0]
        self.assertEqual(adherent_drug["Adherence_Config"]["Durability_Map"]["Times"], default_times)
        self.assertEqual(adherent_drug["Adherence_Config"]["Durability_Map"]["Values"], default_values)
        self.assertEqual(adherent_drug["Doses"], default_doses)
        self.assertEqual(adherent_drug["Dose_Interval"], default_dose_interval)
        self.assertEqual(adherent_drug["Non_Adherence_Distribution"], default_non_adherence_distribution)
        self.assertEqual(adherent_drug["Non_Adherence_Options"], default_non_adherence_options)
        self.assertEqual(adherent_drug["Intervention_Name"], "AdherentDrug_Amodiaquine_Pyrimethamine_Sulfadoxine")
        pass

    def test_drug_campaign_exceptions(self):
        import emodpy_malaria.interventions.adherentdrug as ad
        with self.assertRaisesRegex(Exception,
                                    r"You have to pass in  drug_code\(AL, DP, etc; allowable "
                                    r"types defined in malaria_drugs.py\) or"
                                    "a list of adherent_drug_configs, which can be generated "
                                    "with adherent_drug.py/configure_"
                                    "adherent_drug.\n"):
            drug_campaign.add_drug_campaign(camp)
        doses = [["Sulfadoxine", "Pyrimethamine", 'Amodiaquine'], ['Amodiaquine'], ['Amodiaquine'],
                 ['Pyrimethamine']]  # use doses value that is different from the default
        dose_interval = 2
        non_adherence_options = ['Stop']
        non_adherence_distribution = [1]
        values = [1, 0.6, 0.4, 0.1]
        custom_intervention_name = "TryingNewDrugs"
        adherent_drug = ad.adherent_drug(camp,
                                         doses=doses,
                                         dose_interval=dose_interval,
                                         non_adherence_options=non_adherence_options,
                                         non_adherence_distribution=non_adherence_distribution,
                                         adherence_values=values,
                                         intervention_name=custom_intervention_name
                                         )
        with self.assertRaisesRegex(Exception, "You passed in a drug_code AND a list of adherent_drug_configs."
                                               " Please pick one.\n"):
            drug_campaign.add_drug_campaign(camp, drug_code="AL", adherent_drug_configs=[adherent_drug])
        with self.assertRaisesRegex(ValueError, '"treatment_delay" parameter is not used in MDA or SMC'):
            drug_campaign.add_drug_campaign(camp, campaign_type="MDA", drug_code="AL", treatment_delay=2)
        with self.assertRaisesRegex(Exception, 'Warning: unrecognized campaign type\n'):
            drug_campaign.add_drug_campaign(camp, campaign_type="YMCA", drug_code="AL", treatment_delay=2)
        with self.assertRaisesRegex(Exception, r"Please pass in a \(valid\) drug_code.\n"
                                               "Available drug codes:\n"
                                               "\"ALP\": Artemether, Lumefantrine, Primaquine.\n"
                                               "\"AL\": Artemether, Lumefantrine. \n"
                                               "\"ASAQ\": Artesunate, Amodiaquine.\n"
                                               "\"DP\": DHA, Piperaquine.\n"
                                               "\"DPP\": DHA, Piperaquine, Primaquine.\n"
                                               "\"PPQ\": Piperaquine.\n"
                                               "\"DHA_PQ\": DHA, Primaquine.\n"
                                               "\"DHA\": DHA.\n"
                                               "\"PMQ\": Primaquine.\n"
                                               "\"DA\": DHA, Abstract.\n"
                                               "\"CQ\": Chloroquine.\n"
                                               "\"SP\": Sulfadoxine, Pyrimethamine.\n"
                                               "\"SPP\": Sulfadoxine, Pyrimethamine, Primaquine.\n"
                                               "\"SPA\": Sulfadoxine, Pyrimethamine, Amodiaquine.\n"
                                               "\"Vehicle\": Vehicle.\n"):
            drug_campaign.drug_configs_from_code(camp, drug_code=None)
        with self.assertRaisesRegex(Exception,
                                    r"You have to pass in drug_configs \(list of drug configurations\) that "
                                    r"can be generated with "
                                    "malaria.interventions.malaria_drugs import drug_configs_from_code.\n"):
            drug_campaign.add_MSAT(camp, drug_configs=None)
        with self.assertRaisesRegex(Exception,
                                    r"You have to pass in drug_configs \(list of drug configurations\) that "
                                    r"can be generated with \n"
                                    "malaria.interventions.malaria_drugs import drug_configs_from_code.\n"):
            drug_campaign.add_fMDA(camp, drug_configs=None)
        with self.assertRaisesRegex(Exception,
                                    r"You have to pass in drug_configs \(list of drug configurations\) "
                                    r"that can be generated with "
                                    "malaria.interventions.malaria_drugs import drug_configs_from_code.\n"):
            drug_campaign.add_rfMSAT(camp, drug_configs=None)
        with self.assertRaisesRegex(Exception,
                                    r"You have to pass in drug_configs \(list of drug configurations\) "
                                    r"that can be generated with "
                                    "malaria.interventions.malaria_drugs import drug_configs_from_code.\n"):
            drug_campaign.add_rfMDA(camp, drug_configs=None)

    def test_health_seeking_defaults(self):
        camp.campaign_dict["Events"] = []
        targets = [{"trigger": "NewClinicalCase", "coverage": 0.8, "agemin": 15, "agemax": 70, "rate": 0.25}]
        add_treatment_seeking(camp, targets=targets)
        campaign_event = camp.campaign_dict["Events"][0]
        self.assertEqual(campaign_event['Start_Day'], 1)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetAll")
        event_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(event_config['Number_Repetitions'], 1)
        self.assertEqual(event_config['Timesteps_Between_Repetitions'], -1)
        self.assertEqual(event_config['Intervention_Config']['Demographic_Coverage'], 0.8)
        self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(event_config['Intervention_Config']['Target_Gender'], "All")
        self.assertEqual(event_config['Intervention_Config']['Target_Age_Min'], 15)
        self.assertEqual(event_config['Intervention_Config']['Target_Age_Max'], 70)
        self.assertEqual(event_config['Intervention_Config']['class'], "NodeLevelHealthTriggeredIV")
        self.assertEqual(event_config['Intervention_Config']['Trigger_Condition_List'], ["NewClinicalCase"])
        self.assertEqual(event_config['Intervention_Config']['Actual_IndividualIntervention_Config']['class'],
                         "DelayedIntervention")
        delayed_intervention = event_config['Intervention_Config']['Actual_IndividualIntervention_Config']
        self.assertEqual(delayed_intervention['Delay_Period_Distribution'], "EXPONENTIAL_DISTRIBUTION")
        self.assertEqual(delayed_intervention['Delay_Period_Exponential'], 4)
        self.assertEqual(len(delayed_intervention['Actual_IndividualIntervention_Configs']), 3)
        artemether_found = False
        lumefantrine_found = False
        for intervention in delayed_intervention['Actual_IndividualIntervention_Configs']:
            if intervention["class"] == "AntimalarialDrug":
                if intervention["Drug_Type"] == "Artemether":
                    self.assertEqual(intervention['Intervention_Name'], "AntimalarialDrug_Artemether")
                    artemether_found = True
                elif intervention["Drug_Type"] == "Lumefantrine":
                    self.assertEqual(intervention['Intervention_Name'], "AntimalarialDrug_Lumefantrine")
                    lumefantrine_found = True
            else:
                self.assertEqual(intervention["class"], "BroadcastEvent")
                self.assertEqual(intervention["Broadcast_Event"], "Received_Treatment")
        self.assertTrue(artemether_found and lumefantrine_found)
        pass

    def test_health_seeking_custom(self):
        camp.campaign_dict["Events"] = []
        targets = [{"trigger": "NewClinicalCase", "coverage": 0.8, "agemin": 15, "agemax": 70, "rate": 0.25},
                   {"trigger": "HappyBirthday", "agemax": 30}]
        drugs = ["TestDrug", "TestDrug2"]
        start_day = 235
        node_ids = [2, 3, 6]
        ind_property_restrictions = [{"Risk": "High", "Location": "Rural"}, {"Risk": "Medium", "Location": "Urban"}]
        drug_ineligibility = 7
        duration = 63
        broadcast = "TestingTesting"
        add_treatment_seeking(camp,
                              start_day=start_day,
                              targets=targets,
                              drug=drugs,
                              node_ids=node_ids,
                              ind_property_restrictions=ind_property_restrictions,
                              drug_ineligibility_duration=drug_ineligibility,
                              duration=duration,
                              broadcast_event_name=broadcast)
        self.assertEqual(len(camp.campaign_dict["Events"]), 2)
        target1_found = False
        target2_found = False
        for campaign_event in camp.campaign_dict["Events"]:
            if campaign_event["Event_Coordinator_Config"]['Intervention_Config']['Trigger_Condition_List'][
                0] == "NewClinicalCase":
                self.assertEqual(campaign_event['Start_Day'], start_day)
                self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
                self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], node_ids)
                event_config = campaign_event['Event_Coordinator_Config']
                if event_config['Intervention_Config']['Target_Age_Max'] == 70:
                    target1_found = True
                    self.assertEqual(event_config['Number_Repetitions'], 1)
                    self.assertEqual(event_config['Timesteps_Between_Repetitions'], -1)
                    self.assertEqual(event_config['Intervention_Config']['Demographic_Coverage'], 0.8)
                    self.assertEqual(event_config['Intervention_Config']['Target_Gender'], "All")
                    self.assertEqual(event_config['Intervention_Config']['Target_Age_Min'], 15)
                    self.assertEqual(event_config['Intervention_Config']['Target_Age_Max'], 70)
                    self.assertEqual(event_config['Intervention_Config']['class'], "NodeLevelHealthTriggeredIV")
                    self.assertEqual(event_config['Intervention_Config']['Trigger_Condition_List'], ["NewClinicalCase"])
                    self.assertEqual(event_config['Intervention_Config']['Property_Restrictions_Within_Node'],
                                     ind_property_restrictions)
                    self.assertEqual(event_config['Intervention_Config']['Duration'], duration)
                    self.assertEqual(
                        event_config['Intervention_Config']['Actual_IndividualIntervention_Config']['class'],
                        "DelayedIntervention")
                    self.assertEqual(len(
                        event_config['Intervention_Config']['Actual_IndividualIntervention_Config'][
                            "Actual_IndividualIntervention_Configs"]), 4)
                    self.assertEqual(
                        event_config['Intervention_Config']['Actual_IndividualIntervention_Config']["class"],
                        "DelayedIntervention")
                    self.assertEqual(event_config['Intervention_Config']['Actual_IndividualIntervention_Config'][
                                         "Delay_Period_Exponential"], 4)
                    testdrug_found = False
                    testdrug2_found = False
                    broadcast_found = False
                    property_changer_found = False
                    for intervention in event_config['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        "Actual_IndividualIntervention_Configs"]:
                        if intervention["class"] == "AntimalarialDrug":
                            if intervention["Drug_Type"] == "TestDrug":
                                self.assertEqual(intervention['Intervention_Name'],
                                                 "AntimalarialDrug_TestDrug")
                                testdrug_found = True
                            else:
                                self.assertEqual(intervention["Drug_Type"], "TestDrug2")
                                self.assertEqual(intervention['Intervention_Name'],
                                                 "AntimalarialDrug_TestDrug2")
                                testdrug2_found = True
                        elif intervention["class"] == "BroadcastEvent":
                            broadcast_found = True
                            self.assertEqual(intervention["Broadcast_Event"], broadcast)
                        else:
                            self.assertEqual(intervention["class"], "PropertyValueChanger")
                            property_changer_found = True
                            self.assertEqual(intervention["Daily_Probability"], 1)
                            self.assertEqual(intervention["Revert"], drug_ineligibility)
                            self.assertEqual(intervention["Target_Property_Key"], "DrugStatus")
                            self.assertEqual(intervention["Target_Property_Value"], "RecentDrug")
                    self.assertTrue(testdrug_found and testdrug2_found and broadcast_found and property_changer_found)
            elif campaign_event["Event_Coordinator_Config"]['Intervention_Config']['Trigger_Condition_List'][
                0] == "HappyBirthday":
                target2_found = True
                event_config = campaign_event['Event_Coordinator_Config']
                self.assertEqual(event_config['Number_Repetitions'], 1)
                self.assertEqual(event_config['Timesteps_Between_Repetitions'], -1)
                self.assertEqual(event_config['Intervention_Config']['Demographic_Coverage'], 1)
                self.assertEqual(event_config['Intervention_Config']['Target_Gender'], "All")
                self.assertEqual(event_config['Intervention_Config']['Target_Age_Max'], 30)
                self.assertEqual(event_config['Intervention_Config']['Target_Age_Min'], 0)
                self.assertEqual(event_config['Intervention_Config']['class'], "NodeLevelHealthTriggeredIV")
                self.assertEqual(event_config['Intervention_Config']['Trigger_Condition_List'], ["HappyBirthday"])
                self.assertEqual(event_config['Intervention_Config']['Property_Restrictions_Within_Node'],
                                 ind_property_restrictions)
                self.assertEqual(event_config['Intervention_Config']['Duration'], duration)
                self.assertEqual(
                    event_config['Intervention_Config']['Actual_IndividualIntervention_Config']['class'],
                    "MultiInterventionDistributor")
                self.assertEqual(len(
                    event_config['Intervention_Config']['Actual_IndividualIntervention_Config'][
                        "Intervention_List"]),
                    4)
                testdrug_found = False
                testdrug2_found = False
                broadcast_found = False
                property_changer_found = False
                for intervention in event_config['Intervention_Config']['Actual_IndividualIntervention_Config'][
                    "Intervention_List"]:
                    if intervention["class"] == "AntimalarialDrug":
                        if intervention["Drug_Type"] == "TestDrug":
                            self.assertEqual(intervention['Intervention_Name'],
                                             "AntimalarialDrug_TestDrug")
                            testdrug_found = True
                        else:
                            self.assertEqual(intervention["Drug_Type"], "TestDrug2")
                            self.assertEqual(intervention['Intervention_Name'],
                                             "AntimalarialDrug_TestDrug2")
                            testdrug2_found = True
                    elif intervention["class"] == "BroadcastEvent":
                        broadcast_found = True
                        self.assertEqual(intervention["Broadcast_Event"], broadcast)
                    else:
                        self.assertEqual(intervention["class"], "PropertyValueChanger")
                        property_changer_found = True
                        self.assertEqual(intervention["Daily_Probability"], 1)
                        self.assertEqual(intervention["Revert"], drug_ineligibility)
                        self.assertEqual(intervention["Target_Property_Key"], "DrugStatus")
                        self.assertEqual(intervention["Target_Property_Value"], "RecentDrug")
                self.assertTrue(testdrug_found and testdrug2_found and broadcast_found and property_changer_found)
        self.assertTrue(target1_found and target2_found)
        pass

    def test_treatment_seeking_exceptions(self):
        import emodpy_malaria.interventions.adherentdrug as ad
        with self.assertRaisesRegex(ValueError,
                                    "Please define targets for treatment seeking. It is a list of dictionaries:\n"
                                    " ex: \[\{\"trigger\":\"NewClinicalCase\", \"coverage\":0.8, \"agemin\":15, \"agemax\":70, \"rate\":0.3\}\]\n"):
            add_treatment_seeking(camp)
        bad_target = [{"age_max": 30}]
        with self.assertRaisesRegex(ValueError, "Please define \"trigger\" for each target dictionary. \n"
                                                "ex: \[\{\"trigger\":\"NewClinicalCase\", \"coverage\":0.7, \"agemax\":3 \}\]"):
            add_treatment_seeking(camp, targets=bad_target)
        seek_target = [{"trigger": "NewClinicalCase", "coverage": 0.7, "agemax": 3, "seek": 0.5}]
        with self.assertRaisesRegex(ValueError,
                                    "Notice: \"seek\" parameter has been removed. Please remove it from your \"targets\""
                                    " dictionary."
                                    " Please modify the \"coverage\" parameter "
                                    "directly to attain a different coverage for the intervention. Previously, "
                                    "\"Demographic_Coverage\" was \"coverage\"x\"seek\". It is now just \"coverage\".\n"):
            add_treatment_seeking(camp, targets=seek_target)

    def test_vector_surveillance_defaults(self):
        from emodpy_malaria.interventions.vector_surveillance import (add_vector_surveillance_event_coordinator,
                                                                      VectorGender, CountType)
        start_triggers = ["testing"]
        update_period = 4
        sample_size_distribution = Distributions.poisson(update_period)
        species = "gambiae"
        gender = VectorGender.VECTOR_BOTH_GENDERS
        count_type = CountType.ALLELE_FREQ
        coord_name = "TESsdfashodfuasy"
        add_vector_surveillance_event_coordinator(campaign=camp, start_trigger_condition_list=start_triggers,
                                                  update_period=update_period,
                                                  sample_size=sample_size_distribution, coordinator_name=coord_name,
                                                  species=species, gender=gender, count_type=count_type)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], 0)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetAll")
        coordinator_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(coordinator_config['class'], "VectorSurveillanceEventCoordinator")
        self.assertEqual(coordinator_config['Duration'], -1)
        self.assertEqual(coordinator_config['Coordinator_Name'], coord_name)
        self.assertEqual(coordinator_config['Start_Trigger_Condition_List'], start_triggers)
        self.assertEqual(coordinator_config['Stop_Trigger_Condition_List'], [])
        vector_counter = coordinator_config['Counter']
        self.assertEqual(vector_counter['Count_Type'], count_type.name)
        self.assertEqual(vector_counter['Gender'], gender.name)
        self.assertEqual(vector_counter['Sample_Size_Distribution'], "POISSON_DISTRIBUTION")
        self.assertEqual(vector_counter['Sample_Size_Poisson_Mean'], update_period)
        self.assertEqual(vector_counter['Species'], species)
        self.assertEqual(vector_counter['Update_Period'], update_period)
        self.assertEqual(coordinator_config['Responder']['Survey_Completed_Event'], "")

    def test_vector_surveillance_custom(self):
        from emodpy_malaria.interventions.vector_surveillance import (add_vector_surveillance_event_coordinator,
                                                                      VectorGender, CountType)

        start_triggers = ["testing"]
        stop_triggers = ["stop", "staaahp"]
        update_period = 4
        sample_size_distribution = Distributions.poisson(update_period)
        species = "gambiae"
        gender = VectorGender.VECTOR_BOTH_GENDERS
        start = 33
        nodelist = [23, 2323, 22]
        count_type = CountType.GENOME_FRACTION
        coord_name = "TESsdfashodfuasy"
        add_vector_surveillance_event_coordinator(campaign=camp, start_trigger_condition_list=start_triggers,
                                                  update_period=update_period, start_day=start,
                                                  stop_trigger_condition_list=stop_triggers,
                                                  coordinator_name=coord_name,
                                                  sample_size=sample_size_distribution, count_type=count_type,
                                                  species=species, gender=gender, node_ids=nodelist,
                                                  survey_completed_event=coord_name)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], nodelist)
        coordinator_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(coordinator_config['class'], "VectorSurveillanceEventCoordinator")
        self.assertEqual(coordinator_config['Duration'], -1)
        self.assertEqual(coordinator_config['Start_Trigger_Condition_List'], start_triggers)
        self.assertEqual(coordinator_config['Stop_Trigger_Condition_List'], stop_triggers)
        vector_counter = coordinator_config['Counter']
        self.assertEqual(vector_counter['Count_Type'], count_type.name)  # not optional to set for
        self.assertEqual(vector_counter['Gender'], gender.name)
        self.assertEqual(vector_counter['Sample_Size_Distribution'], "POISSON_DISTRIBUTION")
        self.assertEqual(vector_counter['Sample_Size_Poisson_Mean'], update_period)
        self.assertEqual(vector_counter['Species'], species)
        self.assertEqual(vector_counter['Update_Period'], update_period)
        self.assertEqual(coordinator_config['Responder']['Survey_Completed_Event'], coord_name)

    def test_indoor_individual_emanator(self):
        start_day = 10
        killing_effect = 1
        box_duration = 100
        deca_time = 14
        repelling_effect = 0.3
        box_duration2 = 10
        decay_time=5
        camp.campaign_dict["Events"] = []
        add_indoor_individual_emanator_scheduled(camp, killing_initial_effect=killing_effect,
                                                 killing_box_duration=box_duration,
                                                 killing_decay_time_constant=deca_time,
                                                 repelling_decay_time_constant=decay_time,
                                                 repelling_initial_effect=repelling_effect,
                                                 repelling_box_duration=box_duration2,
                                                 start_day=start_day, demographic_coverage=0.7)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.intervention_config['class'], "IndoorIndividualEmanator")
        self.assertEqual(self.intervention_config['Killing_Config']['Box_Duration'], box_duration)
        self.assertEqual(self.intervention_config['Killing_Config']['Decay_Time_Constant'], deca_time)
        self.assertEqual(self.intervention_config['Killing_Config']['Initial_Effect'], killing_effect)
        self.assertEqual(self.intervention_config['Repelling_Config']['Box_Duration'], box_duration2)
        self.assertEqual(self.intervention_config['Repelling_Config']['Decay_Time_Constant'], decay_time)
        self.assertEqual(self.intervention_config['Repelling_Config']['Initial_Effect'], repelling_effect)

    def test_triggered_indoor_individual_emanator(self):
        start_day = 10
        killing_effect = 1
        box_duration = 100
        deca_time = 14
        repelling_effect = 0.3
        box_duration2 = 10
        decay_time = 5
        camp.campaign_dict["Events"] = []
        add_indoor_individual_emanator_triggered(camp, killing_initial_effect=killing_effect,
                                                 killing_box_duration=box_duration,
                                                 killing_decay_time_constant=deca_time,
                                                 repelling_decay_time_constant=decay_time,
                                                 repelling_initial_effect=repelling_effect,
                                                 repelling_box_duration=box_duration2,
                                                 start_day=start_day, trigger_condition_list=["HappyBirthday"])
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.tmp_intervention["Trigger_Condition_List"], ["HappyBirthday"])
        self.assertEqual(self.intervention_config['class'], "IndoorIndividualEmanator")
        self.assertEqual(self.intervention_config['Killing_Config']['Box_Duration'], box_duration)
        self.assertEqual(self.intervention_config['Killing_Config']['Decay_Time_Constant'], deca_time)
        self.assertEqual(self.intervention_config['Killing_Config']['Initial_Effect'], killing_effect)
        self.assertEqual(self.intervention_config['Repelling_Config']['Box_Duration'], box_duration2)
        self.assertEqual(self.intervention_config['Repelling_Config']['Decay_Time_Constant'], decay_time)
        self.assertEqual(self.intervention_config['Repelling_Config']['Initial_Effect'], repelling_effect)

    def test_triggered_indoor_individual_emanator(self):
        start_day = 10
        killing_effect = 1
        box_duration = 100
        deca_time = 14
        repelling_effect = 0.3
        box_duration2 = 10
        decay_time = 5
        camp.campaign_dict["Events"] = []
        add_outdoor_node_emanator_scheduled(camp, killing_initial_effect=killing_effect,
                                                 killing_box_duration=box_duration,
                                                 killing_decay_time_constant=deca_time,
                                                 repelling_decay_time_constant=decay_time,
                                                 repelling_initial_effect=repelling_effect,
                                                 repelling_box_duration=box_duration2,
                                                 start_day=start_day,)
        self.tmp_intervention = camp.campaign_dict["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.intervention_config['class'], "OutdoorNodeEmanator")
        self.assertEqual(self.intervention_config['Killing_Config']['Box_Duration'], box_duration)
        self.assertEqual(self.intervention_config['Killing_Config']['Decay_Time_Constant'], deca_time)
        self.assertEqual(self.intervention_config['Killing_Config']['Initial_Effect'], killing_effect)
        self.assertEqual(self.intervention_config['Repelling_Config']['Box_Duration'], box_duration2)
        self.assertEqual(self.intervention_config['Repelling_Config']['Decay_Time_Constant'], decay_time)
        self.assertEqual(self.intervention_config['Repelling_Config']['Initial_Effect'], repelling_effect)

        pass

if __name__ == '__main__':
    unittest.main()
