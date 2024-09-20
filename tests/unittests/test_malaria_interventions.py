import unittest
import json
import os, sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
import schema_path_file
import random
import pandas as pd

from emodpy_malaria.interventions.ivermectin import add_scheduled_ivermectin, add_triggered_ivermectin
from emodpy_malaria.interventions.bednet import Bednet, add_ITN_scheduled, BednetIntervention
from emodpy_malaria.interventions.outdoorrestkill import add_OutdoorRestKill
from emodpy_malaria.interventions.usage_dependent_bednet import add_scheduled_usage_dependent_bednet, \
    add_triggered_usage_dependent_bednet
from emodpy_malaria.interventions import drug_campaign
from emodpy_malaria.interventions import diag_survey
from emodpy_malaria.interventions.common import *
from emodpy_malaria.interventions.mosquitorelease import MosquitoRelease
from emodpy_malaria.interventions.inputeir import InputEIR
from emodpy_malaria.interventions.outbreak import *
from emodpy_malaria.interventions.vaccine import *
from emodpy_malaria.interventions.irs import *
from emodpy_malaria.interventions.spacespraying import SpaceSpraying
from emodpy_malaria.interventions.sugartrap import SugarTrap
from emodpy_malaria.interventions.larvicide import add_larvicide
from emodpy_malaria.interventions.community_health_worker import add_community_health_worker
from emodpy_malaria.interventions.scale_larval_habitats import add_scale_larval_habitats

import emod_api.campaign as camp
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


# Uncomment below to also run through tests with 10 Jan schema (default is latest)
# class schema_17Dec20:
#     schema_path = schema_path_file.schema_file_17Dec20

# Uncomment below to also run through tests with 10 Jan schema (default is latest)
# class schema_10Jan21:
#     schema_path = schema_path_file.schema_file_10Jan21


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
        self.schema_file = schema_path_file
        camp.schema_path = schema_path_file.schema_path
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
                         node_property_restrictions=None,
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
                                 node_property_restrictions=node_property_restrictions,
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
        self.assertIn(WaningParams.Decay_Time, self.killing_config)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 0)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        return

    def test_ivermectin_exponential_default(self):
        self.is_debugging = False
        self.ivermectin_build(killing_decay_time_constant=10)
        self.assertEqual(self.killing_config[WaningParams.Initial], 1.0)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 10)
        self.assertIn('Box_Duration', self.killing_config)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 0)
        self.assertEqual(self.killing_config['class'], WaningEffects.BoxExp)
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
        self.assertEqual(triggered_intervention['Node_Property_Restrictions'], [])
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
            drug_campaign.add_drug_campaign(camp=camp, campaign_type=campaign_type,
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
            "AntimalarialDrug")

    def test_drug_campaign_MSAT(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "MSAT"
        # self.test_drug_campaign(campaign_type)
        coverage = 0.89
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(camp=camp, campaign_type=campaign_type,
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
                        'Intervention_Name'], "AntimalarialDrug")
            else:
                self.assertTrue(False, "Unexpected intervention in campaign.")

    def test_drug_campaign_fMDA(self):
        camp.campaign_dict["Events"] = []
        campaign_type = "fMDA"
        coverage = 0.89
        drug_codes = ["AL"]
        for drug_code in drug_codes:
            drug_campaign.add_drug_campaign(camp=camp, campaign_type=campaign_type,
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
                'Intervention_Name'] == "AntimalarialDrug":
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
            drug_campaign.add_drug_campaign(camp=camp, campaign_type=campaign_type,
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
                'Intervention_Name'] == "AntimalarialDrug":
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
            drug_campaign.add_drug_campaign(camp=camp, campaign_type=campaign_type,
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
                'Intervention_Name'] == "AntimalarialDrug":
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
    def bednet_build(self
                     , start_day=1
                     , coverage=1.0
                     , blocking_eff=1.0
                     , killing_eff=1.0
                     , repelling_eff=1.0
                     , usage_eff=1.0
                     , blocking_decay_rate=0.0
                     , blocking_predecay_duration=365
                     , killing_decay_rate=0.0
                     , killing_predecay_duration=365
                     , repelling_decay_rate=0.0
                     , repelling_predecay_duration=365
                     , usage_decay_rate=0.0
                     , usage_predecay_duration=365
                     , node_ids=None
                     , insecticide=None
                     ):
        if not self.tmp_intervention:
            self.tmp_intervention = Bednet(
                schema_path=self.schema_file.schema_path
                , start_day=start_day
                , coverage=coverage
                , blocking_eff=blocking_eff
                , killing_eff=killing_eff
                , repelling_eff=repelling_eff
                , usage_eff=usage_eff
                , blocking_decay_rate=blocking_decay_rate
                , blocking_predecay_duration=blocking_predecay_duration
                , killing_decay_rate=killing_decay_rate
                , killing_predecay_duration=killing_predecay_duration
                , repelling_decay_rate=repelling_decay_rate
                , repelling_predecay_duration=repelling_predecay_duration
                , usage_decay_rate=usage_decay_rate
                , usage_predecay_duration=usage_predecay_duration
                , node_ids=node_ids
                , insecticide=insecticide
            )
        self.parse_intervention_parts()
        self.killing_config = self.intervention_config['Killing_Config']
        self.blocking_config = self.intervention_config['Blocking_Config']
        self.repelling_config = self.intervention_config['Repelling_Config']
        self.usage_config = self.intervention_config['Usage_Config']
        self.all_configs = [
            self.killing_config
            , self.blocking_config
            , self.repelling_config
            , self.usage_config
        ]
        return

    # def test_bednet_default_throws_exception(self):
    #     with self.assertRaises(TypeError) as context:
    #         Bednet(campaign=schema_path_file)
    #     self.assertIn("start_day", str(context.exception))
    #     return

    def test_bednet_needs_only_start_day(self):
        self.is_debugging = False
        specific_day = 39

        # call emodpy-malaria code directly
        self.tmp_intervention = Bednet(schema_path=schema_path_file.schema_file,
                                       start_day=specific_day)

        self.bednet_build()  # tmp_intervention already set
        # self.bednet_build(start_day=specific_day)

        self.assertEqual(self.event_coordinator['Demographic_Coverage'], 1.0)
        self.assertEqual(self.start_day, specific_day)

        self.assertEqual(self.event_coordinator["Intervention_Config"]["Killing_Config"]["Initial_Effect"], 1)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Blocking_Config"]["Initial_Effect"], 1)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Repelling_Config"]["Initial_Effect"], 1)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Usage_Config"]["Initial_Effect"], 1)

        self.assertEqual(self.event_coordinator["Intervention_Config"]["Killing_Config"]["Box_Duration"], 365)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Blocking_Config"]["Box_Duration"], 365)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Repelling_Config"]["Box_Duration"], 365)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Usage_Config"]["Expected_Discard_Time"], 3650)

        self.assertEqual(self.event_coordinator["Intervention_Config"]["Killing_Config"]["Decay_Time_Constant"], 0)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Blocking_Config"]["Decay_Time_Constant"], 0)
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Repelling_Config"]["Decay_Time_Constant"], 0)

        self.assertEqual(self.event_coordinator["Intervention_Config"]["Killing_Config"]["class"],
                         "WaningEffectBoxExponential")
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Blocking_Config"]["class"],
                         "WaningEffectBoxExponential")
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Repelling_Config"]["class"],
                         "WaningEffectBoxExponential")
        self.assertEqual(self.event_coordinator["Intervention_Config"]["Usage_Config"]["class"],
                         "WaningEffectRandomBox")

        self.assertEqual(self.event_coordinator['Individual_Selection_Type']
                         , "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        return

    def test_bednet_all_constant_waning(self):

        self.bednet_build(start_day=13
                          , blocking_predecay_duration=-1
                          , killing_predecay_duration=-1
                          , repelling_predecay_duration=-1
                          , usage_predecay_duration=-1)
        for wc in self.all_configs:
            self.assertEqual(
                wc[WaningParams.Class]
                , WaningEffects.Constant)  # class is WaningEffectConstant
        return

    def test_bednet_all_waning_effectiveness(self):
        self.is_debugging = False
        block_effect = 0.9
        kill_effect = 0.8
        repell_effect = 0.7
        usage_effect = 0.6

        self.bednet_build(blocking_eff=block_effect
                          , killing_eff=kill_effect
                          , repelling_eff=repell_effect
                          , usage_eff=usage_effect)

        self.assertEqual(self.killing_config[WaningParams.Initial], kill_effect)
        self.assertEqual(self.blocking_config[WaningParams.Initial], block_effect)
        self.assertEqual(self.repelling_config[WaningParams.Initial], repell_effect)
        self.assertEqual(self.usage_config[WaningParams.Initial], usage_effect)
        return

    def test_bednet_all_exponential_waning(self):
        self.bednet_build(blocking_decay_rate=0.2
                          , blocking_predecay_duration=0
                          , killing_decay_rate=0.1
                          , killing_predecay_duration=0
                          , usage_decay_rate=0.01
                          , usage_predecay_duration=0
                          , repelling_decay_rate=0.5
                          , repelling_predecay_duration=0)

        # All of these should have no box duration
        # All of these should be box exponential
        for wc in self.all_configs:
            self.assertEqual(wc[WaningParams.Box_Duration], 0)
            self.assertEqual(wc[WaningParams.Class], WaningEffects.BoxExp)

        # Each of the Delay_Time_Constants is the reciprocal of the decay rate
        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], 5.0)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 10.0)
        self.assertEqual(self.usage_config[WaningParams.Decay_Time], 100.0)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], 2.0)
        return

    def test_bednet_nodeset_custom(self):
        specific_ids = [1, 12, 123, 1234]
        self.bednet_build(node_ids=specific_ids
                          , blocking_eff=0.3
                          , killing_predecay_duration=730
                          , repelling_predecay_duration=0
                          , repelling_decay_rate=0.02
                          , usage_decay_rate=0.01
                          , usage_predecay_duration=50
                          )

        self.assertEqual(self.nodeset[NodesetParams.Class],
                         NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List],
                         specific_ids)
        self.assertEqual(self.blocking_config[WaningParams.Initial], 0.3)

        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 730)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 0)

        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], 0)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], 50)

        self.assertEqual(self.usage_config[WaningParams.Decay_Time], 100)
        self.assertEqual(self.usage_config[WaningParams.Box_Duration], 50)
        return

    def test_bednet_coverage_custom(self):
        specific_coverage = 0.365
        self.bednet_build(coverage=specific_coverage

                          , killing_eff=0.3

                          , repelling_predecay_duration=730

                          , usage_predecay_duration=0
                          , usage_decay_rate=0.02

                          , blocking_decay_rate=0.01
                          , blocking_predecay_duration=50
                          )

        self.assertEqual(self.nodeset[NodesetParams.Class],
                         NodesetParams.SetAll)
        self.assertEqual(self.event_coordinator['Demographic_Coverage'],
                         specific_coverage)
        self.assertEqual(self.killing_config[WaningParams.Initial], 0.3)

        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], 730)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], 0)

        self.assertEqual(self.usage_config[WaningParams.Box_Duration], 0)
        self.assertEqual(self.usage_config[WaningParams.Decay_Time], 50)

        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], 100)
        self.assertEqual(self.blocking_config[WaningParams.Box_Duration], 50)
        return

    def test_add_itn_scheduled(self):
        camp.reset()
        start_day = 100
        coverage = 0.56
        target_age_min = 0
        target_age_max = 500
        repetitions = 3
        tsteps_btwn_repetitions = 4
        node_ids = [1, 2]
        add_ITN_scheduled(camp, start_day, [{'min': target_age_min, 'max': target_age_max, 'coverage': coverage}],
                          repetitions=repetitions, tsteps_btwn_repetitions=tsteps_btwn_repetitions,
                          node_ids=node_ids)

        itn_event = camp.campaign_dict["Events"][0]
        self.assertEqual(itn_event["class"], "CampaignEvent")
        self.assertEqual(itn_event["Start_Day"], start_day)

        event_coordinator_config = itn_event["Event_Coordinator_Config"]
        self.assertEqual(event_coordinator_config["class"], "StandardInterventionDistributionEventCoordinator")
        self.assertEqual(event_coordinator_config["Demographic_Coverage"], coverage)
        self.assertEqual(event_coordinator_config["Target_Age_Max"], target_age_max)
        self.assertEqual(event_coordinator_config["Target_Age_Min"], target_age_min)
        self.assertEqual(event_coordinator_config["Number_Repetitions"], repetitions)
        self.assertEqual(event_coordinator_config["Timesteps_Between_Repetitions"], tsteps_btwn_repetitions)

        intervention_config = event_coordinator_config.get("Intervention_Config")
        self.assertIsNone(intervention_config.get("Actual_IndividualIntervention_Config"))
        self.assertEqual(intervention_config["class"], "MultiInterventionDistributor")

        intervention_list_zero = intervention_config.get("Intervention_List")[0]
        self.assertEqual(intervention_list_zero["class"], "SimpleBednet")

        blocking_config = intervention_list_zero.get("Blocking_Config")
        self.assertEqual(blocking_config["class"], "WaningEffectBoxExponential")

        killing_config = intervention_list_zero.get("Killing_Config")
        self.assertEqual(killing_config["class"], "WaningEffectBoxExponential")

        usage_config = intervention_list_zero.get("Usage_Config")
        self.assertEqual(usage_config["class"], "WaningEffectRandomBox")

        nodeset_config = itn_event["Nodeset_Config"]
        self.assertEqual(nodeset_config["class"], "NodeSetNodeList")
        self.assertEqual(nodeset_config["Node_List"], node_ids)

        camp.save("test_add_itn_scheduled.json")

    def test_add_itn_scheduled_config(self):
        camp.reset()
        start_day = 100
        coverage = 0.56
        target_age_min = 0
        target_age_max = 500
        blocking_eff = 0.12
        killing_eff = 0.34
        repelling_eff = 0.56
        usage_eff = 0.78

        bednet = BednetIntervention(camp.schema_path, blocking_eff=blocking_eff, killing_eff=killing_eff,
                                    repelling_eff=repelling_eff, usage_eff=usage_eff)
        add_ITN_scheduled(camp, start_day, [{'min': target_age_min, 'max': target_age_max, 'coverage': coverage}],
                          itn_bednet=bednet)

        itn_event = camp.campaign_dict["Events"][0]
        intervention_list_zero = itn_event["Event_Coordinator_Config"]["Intervention_Config"].get("Intervention_List")[
            0]

        blocking_config = intervention_list_zero.get("Blocking_Config")
        self.assertEqual(blocking_config["Initial_Effect"], blocking_eff)

        killing_config = intervention_list_zero.get("Killing_Config")
        self.assertEqual(killing_config["Initial_Effect"], killing_eff)

        usage_config = intervention_list_zero.get("Usage_Config")
        self.assertEqual(usage_config["Initial_Effect"], usage_eff)

        repelling_config = intervention_list_zero.get("Repelling_Config")
        self.assertEqual(repelling_config["Initial_Effect"], repelling_eff)

    # endregion

    # region OutdoorRestKill
    def test_outdoorrestkill_default(self):
        # correct setting for WaningParams are tested elsewhere here
        camp.campaign_dict["Events"] = []  # resetting
        add_OutdoorRestKill(camp)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.event_coordinator["Demographic_Coverage"], 1)
        self.assertEqual(self.start_day, 1)
        self.assertEqual(self.intervention_config["class"], "OutdoorRestKill")
        self.assertEqual(self.killing_config["class"], WaningEffects.BoxExp)
        return

    def test_outdoorrestkill_all_custom(self):
        camp.campaign_dict["Events"] = []  # resetting
        specific_start_day = 123
        specific_insecticide_name = "Vinegar"
        specific_killing_effect = 0.15
        specific_box_duration = 100
        specific_decay_rate = 0.05
        specific_nodes = [1, 2, 3, 5, 8, 13, 21, 34]
        add_OutdoorRestKill(camp,
                            start_day=specific_start_day,
                            insecticide_name=specific_insecticide_name,
                            killing_initial_effect=specific_killing_effect,
                            killing_box_duration=specific_box_duration,
                            killing_exponential_decay_rate=specific_decay_rate,
                            node_ids=specific_nodes)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config['Insecticide_Name'], specific_insecticide_name)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 1 / specific_decay_rate)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], specific_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], specific_killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], specific_nodes)
        return

        # endregion

        # region UsageDependentBednet
    def test_scheduled_usage_dependent_bednet_default(self):
        camp.campaign_dict["Events"] = []  # resetting
        start_day = 1
        demographic_coverage = 1
        target_num_individuals = None
        node_ids = None
        ind_property_restrictions = []
        node_property_restrictions = []
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
        age_dependence_times = [1, 1]
        age_dependence_values = [0, 125]
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
        self.assertEqual(self.event_coordinator['Node_Property_Restrictions'], node_property_restrictions)
        self.assertEqual(self.event_coordinator['Property_Restrictions'], ind_property_restrictions)
        self.assertEqual(self.intervention_config['Discard_Event'], 'Bednet_Discarded')
        self.assertEqual(self.intervention_config['Using_Event'], 'Bednet_Using')
        self.assertEqual(self.intervention_config['Received_Event'], 'Bednet_Got_New_One')
        self.assertEqual(self.intervention_config['Intervention_Name'], intervention_name)
        self.assertEqual(self.intervention_config['Insecticide_Name'], insecticide)
        self.assertEqual(self.intervention_config['Expiration_Period_Distribution'], "EXPONENTIAL_DISTRIBUTION")
        self.assertEqual(self.intervention_config['Expiration_Period_Exponential'], expiration_period)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], killing_decay_time_constant)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], killing_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], blocking_decay_time_constant)
        self.assertEqual(self.blocking_config[WaningParams.Box_Duration], blocking_box_duration)
        self.assertEqual(self.blocking_config[WaningParams.Initial], blocking_initial_effect)
        self.assertEqual(self.blocking_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], repelling_decay_time_constant)
        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], repelling_box_duration)
        self.assertEqual(self.repelling_config[WaningParams.Initial], repelling_initial_effect)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.BoxExp)

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
        node_property_restrictions = []
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
        self.assertEqual(node_level_triggered_intervention['Node_Property_Restrictions'], node_property_restrictions)
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
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], killing_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], blocking_decay_time_constant)
        self.assertEqual(self.blocking_config[WaningParams.Box_Duration], blocking_box_duration)
        self.assertEqual(self.blocking_config[WaningParams.Initial], blocking_initial_effect)
        self.assertEqual(self.blocking_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], repelling_decay_time_constant)
        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], repelling_box_duration)
        self.assertEqual(self.repelling_config[WaningParams.Initial], repelling_initial_effect)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.BoxExp)

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
        node_property_restrictions = [
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
                                             node_property_restrictions=node_property_restrictions,
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
        self.assertEqual(self.event_coordinator['Node_Property_Restrictions'], node_property_restrictions)
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
        node_property_restrictions = [
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
                                             node_property_restrictions=node_property_restrictions,
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
        self.assertEqual(node_level_triggered_intervention['Node_Property_Restrictions'], node_property_restrictions)
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

    def test_scheduled_usage_dependent_bednet_default(self):
        camp.campaign_dict["Events"] = []  # resetting
        start_day = 1
        demographic_coverage = 1
        ind_property_restrictions = []
        node_property_restrictions = []
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
        age_dependence = None
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
        for durability in usage_configs:
            if durability['class'] == 'WaningEffectMapLinearSeasonal':
                found_seasonal = True
                durability_map = durability['Durability_Map']
                self.assertEqual(durability_map['Times'], specific_times)
                self.assertEqual(durability_map['Values'], specific_values)
        self.assertTrue(found_seasonal)
        self.parse_intervention_parts()
        self.killing_config = self.intervention_config['Killing_Config']
        self.blocking_config = self.intervention_config['Blocking_Config']
        self.repelling_config = self.intervention_config['Repelling_Config']
        self.usage_config = self.intervention_config['Usage_Config_List']
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        self.assertEqual(self.event_coordinator['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], demographic_coverage)
        self.assertEqual(self.event_coordinator['Node_Property_Restrictions'], node_property_restrictions)
        self.assertEqual(self.event_coordinator['Property_Restrictions'], ind_property_restrictions)
        self.assertEqual(self.intervention_config['Discard_Event'], 'Bednet_Discarded')
        self.assertEqual(self.intervention_config['Using_Event'], 'Bednet_Using')
        self.assertEqual(self.intervention_config['Received_Event'], 'Bednet_Got_New_One')
        self.assertEqual(self.intervention_config['Intervention_Name'], intervention_name)
        self.assertEqual(self.intervention_config['Insecticide_Name'], insecticide)
        self.assertEqual(self.intervention_config['Expiration_Period_Distribution'], "EXPONENTIAL_DISTRIBUTION")
        self.assertEqual(self.intervention_config['Expiration_Period_Exponential'], expiration_period)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], killing_decay_time_constant)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], killing_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_initial_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.blocking_config[WaningParams.Decay_Time], blocking_decay_time_constant)
        self.assertEqual(self.blocking_config[WaningParams.Box_Duration], blocking_box_duration)
        self.assertEqual(self.blocking_config[WaningParams.Initial], blocking_initial_effect)
        self.assertEqual(self.blocking_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], repelling_decay_time_constant)
        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], repelling_box_duration)
        self.assertEqual(self.repelling_config[WaningParams.Initial], repelling_initial_effect)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.BoxExp)

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
        self.assertEqual(event_config['Node_Property_Restrictions'], [])
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
        IP_restrictions = [{"IndividualProperty1": "PropertyValue1"}, {"IndividualProperty2": "PropertyValue2"}]
        NP_restrictions = []
        disqualifying_properties = [{"IndividualProperty3": "PropertyValue2"}]
        trigger_condition_list = ["NewInfectionEvent"]
        listening_duration = 50
        triggered_campaign_delay = 0
        check_eligibility_at_trigger = False
        expire_recent_drugs = None
        self.is_debugging = False

        diag_survey.add_diagnostic_survey(camp, start_day=start_day, coverage=coverage, repetitions=repetitions,
                                          target=target,
                                          diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                                          measurement_sensitivity=measurement_sensitivity, node_ids=node_ids,
                                          positive_diagnosis_configs=positive_diagnosis_configs,
                                          negative_diagnosis_configs=negative_diagnosis_configs,
                                          received_test_event=received_test_event,
                                          IP_restrictions=IP_restrictions, NP_restrictions=NP_restrictions,
                                          disqualifying_properties=disqualifying_properties,
                                          trigger_condition_list=trigger_condition_list,
                                          listening_duration=listening_duration,
                                          triggered_campaign_delay=triggered_campaign_delay,
                                          check_eligibility_at_trigger=check_eligibility_at_trigger,
                                          expire_recent_drugs=expire_recent_drugs)

        with open("testcampaign.json", "w") as testcampaign:
            json.dump(camp.campaign_dict['Events'], testcampaign)

        self.assertEqual(len(camp.campaign_dict['Events']), 1)
        campaign_event = camp.campaign_dict['Events'][0]
        self.assertEqual(campaign_event['Start_Day'], start_day + 1)
        self.assertEqual(campaign_event['Nodeset_Config']['class'], "NodeSetNodeList")
        self.assertEqual(campaign_event['Nodeset_Config']['Node_List'], node_ids)
        event_config = campaign_event['Event_Coordinator_Config']
        self.assertEqual(event_config['Individual_Selection_Type'], "DEMOGRAPHIC_COVERAGE")
        self.assertEqual(event_config['Node_Property_Restrictions'], NP_restrictions)
        intervention_config = event_config['Intervention_Config']
        self.assertEqual(intervention_config['Property_Restrictions_Within_Node'], IP_restrictions)
        self.assertEqual(intervention_config['Demographic_Coverage'], coverage)
        self.assertEqual(intervention_config['Duration'], listening_duration)
        self.assertEqual(intervention_config['class'], "NodeLevelHealthTriggeredIV")
        self.assertEqual(intervention_config['Target_Demographic'], "ExplicitAgeRangesAndGender")
        self.assertEqual(intervention_config['Target_Age_Min'], agemin)
        self.assertEqual(intervention_config['Target_Age_Max'], agemax)
        self.assertEqual(intervention_config['Target_Gender'], gender)
        self.assertEqual(len(intervention_config['Actual_IndividualIntervention_Config']['Intervention_List']), 2)
        if intervention_config['Actual_IndividualIntervention_Config']['Intervention_List'][0][
            "class"] == "MalariaDiagnostic":
            malaria_diagnostic = intervention_config['Actual_IndividualIntervention_Config']['Intervention_List'][0]
            broadcast_event = intervention_config['Actual_IndividualIntervention_Config']['Intervention_List'][1]
        else:
            malaria_diagnostic = intervention_config['Actual_IndividualIntervention_Config']['Intervention_List'][1]
            broadcast_event = intervention_config['Actual_IndividualIntervention_Config']['Intervention_List'][0]
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

    def test_malaria_diagnostic_custom(self):
        self.is_debugging = False
        malaria_diagnostic = MalariaDiagnostic(camp, "PCR_PARASITES", 0.5, 1)
        measures = [malaria_diagnostic.Measurement_Sensitivity, malaria_diagnostic.Detection_Threshold]

        self.assertEqual(malaria_diagnostic.Detection_Threshold, 1, msg="Detection Threshold not set properly")
        self.assertEqual(malaria_diagnostic.Measurement_Sensitivity, 0.5,
                         msg="Measurement Sensitivity not set properly")
        self.assertEqual("PCR_PARASITES", malaria_diagnostic.Diagnostic_Type)

        antimalarial_drug = AntimalarialDrug(camp, "Malaria")
        self.assertEqual(antimalarial_drug.Drug_Type, "Malaria")
        self.assertEqual(antimalarial_drug.Cost_To_Consumer, 1.0)

    def test_malaria_diagnostic_default(self):
        self.is_debugging = False
        malaria_diagnostic = MalariaDiagnostic(camp)
        measures = [0.5, malaria_diagnostic.Detection_Threshold]

        self.assertFalse(any(item == 1 for item in measures), msg="Not all values are 0 when set to 0")
        self.assertEqual("BLOOD_SMEAR_PARASITES", malaria_diagnostic.Diagnostic_Type)

        antimalarial_drug = AntimalarialDrug(camp, "Malaria")
        self.assertEqual(antimalarial_drug.Drug_Type, "Malaria")
        self.assertEqual(antimalarial_drug.Cost_To_Consumer, 1.0)

    def test_malaria_diagnostic_error(self):
        with self.assertRaises(ValueError) as context:
            diag = MalariaDiagnostic(camp, "BANANA")

        with self.assertRaises(ValueError) as context:
            MalariaDiagnostic(camp, "BLOOD_SMEAR_PARASITES", -1, 0)

        with self.assertRaises(ValueError) as context:
            MalariaDiagnostic(camp, "BLOOD_SMEAR_PARASITES", 0, -1)

    def test_malaria_diagnostic_infection(self):
        self.is_debugging = False
        malaria_diagnostic = MalariaDiagnostic(camp, "TRUE_INFECTION_STATUS")

        self.assertEqual("StandardDiagnostic", malaria_diagnostic.Intervention_Name)

        with self.assertRaises(ValueError) as context:
            MalariaDiagnostic(camp, "TRUE_INFECTION_STATUS", -1, 0)
        with self.assertRaises(ValueError) as context:
            MalariaDiagnostic(camp, "TRUE_INFECTION_STATUS", 0, -1)

    def mosquitorelease_build(self
                              , start_day=1
                              , number=10_000
                              , fraction=None
                              , infectious=0.0
                              , species='arabiensis'
                              , genome=None
                              , node_ids=None):
        camp.schema_path = os.path.join(file_dir, "./old_schemas/latest_schema.json")
        if not genome:
            genome = [['X', 'X']]
        if not self.tmp_intervention:
            self.tmp_intervention = MosquitoRelease(
                campaign=self.schema_file
                , start_day=start_day
                , released_fraction=fraction
                , released_number=number
                , released_infectious=infectious
                , released_species=species
                , released_genome=genome
                , node_ids=node_ids
            )
        self.parse_intervention_parts()
        return

    # def test_mosquitorelease_only_needs_startday(self):
    #     specific_start_day = 125
    #     self.tmp_intervention = MosquitoRelease(
    #         campaign=schema_path_file
    #         , released_number=100
    #         , start_day=specific_start_day)
    #     self.mosquitorelease_build() # parse intervention parts
    #
    #     self.assertIsNotNone(self.tmp_intervention)
    #     self.assertEqual(self.start_day, specific_start_day)
    #     self.assertEqual(self.intervention_config['class'], 'MosquitoRelease')
    #     return

    def test_mosquitorelease_default(self):
        self.mosquitorelease_build()

        self.assertEqual(self.start_day, 1)
        self.assertEqual(self.nodeset[NodesetParams.Class]
                         , NodesetParams.SetAll)  # default is nodesetall
        self.assertEqual(self.intervention_config['Released_Type'],
                         'FIXED_NUMBER')
        self.assertEqual(self.intervention_config['Released_Number'],
                         10_000)
        self.assertEqual(self.intervention_config['Released_Infectious'],
                         0)
        self.assertEqual(self.intervention_config['Released_Species'],
                         'arabiensis')
        self.assertEqual(self.intervention_config['Released_Genome'],
                         [['X', 'X']])
        return

    def test_mosquitorelease_custom(self):
        specific_start_day = 13
        specific_genome = [['X', 'Y']]
        specific_fraction = 0.14
        specific_infectious_fraction = 0.28
        specific_species = 'SillySkeeter'
        specific_nodes = [3, 5, 8, 13, 21]
        self.mosquitorelease_build(
            start_day=specific_start_day
            , number=None
            , fraction=specific_fraction
            , infectious=specific_infectious_fraction
        )

    def test_inputeir_default(self):
        eir = [random.randint(0, 50) for x in range(12)]
        self.tmp_intervention = InputEIR(camp, eir)
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Monthly_EIR, eir)
        self.assertEqual(self.intervention_config.Age_Dependence, "OFF")
        self.assertEqual(self.intervention_config.Scaling_Factor, 1)
        self.assertEqual(self.start_day, 1)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        pass

    def test_inputeir(self):
        eir = [random.randint(0, 50) for x in range(12)]
        self.tmp_intervention = InputEIR(camp, monthly_eir=eir, start_day=2, node_ids=[2, 3],
                                         age_dependence='LINEAR', scaling_factor=0.24)
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Monthly_EIR, eir)
        self.assertEqual(self.intervention_config.Age_Dependence, "LINEAR")
        self.assertEqual(self.intervention_config.Scaling_Factor, 0.24)
        self.assertEqual(self.start_day, 2)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], [2, 3])

        pass

    def test_daily_inputeir(self):
        daily_eir = [random.randint(0, 50) for x in range(365)]
        self.tmp_intervention = InputEIR(camp, daily_eir=daily_eir, start_day=2, node_ids=[2, 3],
                                         age_dependence='SURFACE_AREA_DEPENDENT', scaling_factor=0.67)
        self.parse_intervention_parts()

        self.assertEqual(self.intervention_config.Daily_EIR, daily_eir)
        self.assertEqual(self.intervention_config.EIR_Type, "DAILY")
        self.assertEqual(self.intervention_config.Age_Dependence, "SURFACE_AREA_DEPENDENT")
        self.assertEqual(self.intervention_config.Scaling_Factor, 0.67)
        self.assertEqual(self.start_day, 2)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], [2, 3])

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
        node_property_restrictions = ["Planet:Mars"]
        target_age_min = 3
        target_age_max = 35
        target_gender = "Female"
        broadcast_event = "I am vaccinated!"
        vaccine_type = "TransmissionBlocking"
        vaccine_take = 0.95
        vaccine_initial_effect = 0.98
        vaccine_box_duration = 2000
        vaccine_exponential_decay_rate = 0
        efficacy_is_multiplicative = False

        add_scheduled_vaccine(camp,
                              start_day=start_day,
                              target_num_individuals=target_num_individuals,
                              node_ids=node_ids,
                              repetitions=repetitions,
                              timesteps_between_repetitions=timesteps_between_repetitions,
                              ind_property_restrictions=ind_property_restrictions,
                              node_property_restrictions=node_property_restrictions,
                              target_age_min=target_age_min,
                              target_age_max=target_age_max,
                              target_gender=target_gender,
                              broadcast_event=broadcast_event,
                              vaccine_type=vaccine_type,
                              vaccine_take=vaccine_take,
                              vaccine_initial_effect=vaccine_initial_effect,
                              vaccine_box_duration=vaccine_box_duration,
                              vaccine_exponential_decay_rate=vaccine_exponential_decay_rate,
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
        self.assertEqual(coordinator_config['Node_Property_Restrictions'], node_property_restrictions)
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
        self.assertEqual(campaign_event['Target_Demographic'], "ExplicitAgeRanges") # should be everyone, but there's a bug in emod_api.intervnetions.common
        self.assertEqual(campaign_event['Property_Restrictions'], [])
        self.assertEqual(campaign_event['Node_Property_Restrictions'], [])
        self.assertEqual(campaign_event['Number_Repetitions'], 1)
        self.assertEqual(campaign_event['Timesteps_Between_Repetitions'], 365)
        intervention_0 = campaign_event['Intervention_Config']
        #self.assertEqual(len(campaign_event['Intervention_Config']['Intervention_List']), 1)
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
        self.assertEqual(campaign_event['Intervention_Config']['Target_Demographic'], "ExplicitAgeRanges") # should be everyone, but there's a bug in emod_api.intervnetions.common
        self.assertEqual(campaign_event['Intervention_Config']['Property_Restrictions'], [])
        self.assertEqual(campaign_event['Intervention_Config']['Node_Property_Restrictions'], [])
        self.assertEqual(campaign_event['Number_Repetitions'], 1)
        self.assertEqual(campaign_event['Timesteps_Between_Repetitions'], 365)
        intervention_0 = campaign_event['Intervention_Config']['Actual_IndividualIntervention_Config']["Actual_IndividualIntervention_Configs"][0]
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
        node_property_restrictions = [{"Planet": "Mars"}]
        target_age_min = 3
        target_age_max = 35
        target_gender = "Female"
        broadcast_event = "I am vaccinated!"
        vaccine_type = "TransmissionBlocking"
        vaccine_take = 0.95
        vaccine_initial_effect = 0.98
        vaccine_box_duration = 2000
        vaccine_exponential_decay_rate = 0
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
                              node_property_restrictions=node_property_restrictions,
                              target_age_min=target_age_min,
                              target_age_max=target_age_max,
                              target_gender=target_gender,
                              broadcast_event=broadcast_event,
                              vaccine_type=vaccine_type,
                              vaccine_take=vaccine_take,
                              vaccine_initial_effect=vaccine_initial_effect,
                              vaccine_box_duration=vaccine_box_duration,
                              vaccine_exponential_decay_rate=vaccine_exponential_decay_rate,
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
        self.assertEqual(triggered_config['Node_Property_Restrictions'], node_property_restrictions)
        self.assertEqual(triggered_config['Trigger_Condition_List'], triggers)
        self.assertEqual(triggered_config['Duration'], duration)
        self.assertEqual(triggered_config['Actual_IndividualIntervention_Config']["Delay_Period_Constant"], delay)
        self.assertEqual(campaign_event['Event_Coordinator_Config']['Number_Repetitions'], repetitions)
        self.assertEqual(campaign_event['Event_Coordinator_Config']['Timesteps_Between_Repetitions'], timesteps_between_repetitions)
        intervention_1 = triggered_config['Actual_IndividualIntervention_Config']['Actual_IndividualIntervention_Configs'][1]
        intervention_0 = triggered_config['Actual_IndividualIntervention_Config']['Actual_IndividualIntervention_Configs'][0]
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

    def test_add_irs_housing_modification_custom(self):
        camp.campaign_dict["Events"] = []  # resetting
        specific_start_day = 123
        specific_insecticide_name = "Vinegar"
        specific_killing_effect = 0.15
        specific_repelling_effect = 0.93
        specific_killing_box_duration = 100
        specific_killing_exponential_decay_time = 35
        specific_repelling_box_duration = 5
        specific_repelling_exponential_decay_time = 41
        specific_nodes = [1, 2, 3, 5, 8, 13, 21, 34]
        specific_coverage = 0.78
        intervention_name = "IRSTest1"

        add_scheduled_irs_housing_modification(camp,
                                               start_day=specific_start_day,
                                               demographic_coverage=specific_coverage,
                                               insecticide=specific_insecticide_name,
                                               killing_initial_effect=specific_killing_effect,
                                               repelling_initial_effect=specific_repelling_effect,
                                               killing_box_duration=specific_killing_box_duration,
                                               killing_decay_time_constant=specific_killing_exponential_decay_time,
                                               repelling_box_duration=specific_repelling_box_duration,
                                               repelling_decay_time_constant=specific_repelling_exponential_decay_time,
                                               node_ids=specific_nodes,
                                               intervention_name=intervention_name)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], specific_coverage)
        self.assertEqual(self.intervention_config['Insecticide_Name'], specific_insecticide_name)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], specific_killing_exponential_decay_time)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], specific_killing_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], specific_killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], specific_repelling_exponential_decay_time)
        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], specific_repelling_box_duration)
        self.assertEqual(self.repelling_config[WaningParams.Initial], specific_repelling_effect)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], specific_nodes)
        self.assertEqual(self.intervention_config['Intervention_Name'], intervention_name)
        return

    def test_add_irs_housing_modification_default(self):
        camp.campaign_dict["Events"] = []  # resetting
        add_scheduled_irs_housing_modification(camp)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.event_coordinator['Demographic_Coverage'], 1)
        self.assertEqual(self.intervention_config['Insecticide_Name'], "")
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 90)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], 0)
        self.assertEqual(self.killing_config[WaningParams.Initial], 1)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], 90)
        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], 0)
        self.assertEqual(self.repelling_config[WaningParams.Initial], 0)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)

        return

    def test_add_triggered_irs_housing_modification_custom(self):
        camp.campaign_dict["Events"] = []  # resetting
        specific_start_day = 123
        specific_insecticide_name = "Vinegar"
        specific_killing_effect = 0.15
        specific_repelling_effect = 0.93
        specific_killing_box_duration = 100
        specific_killing_exponential_decay_time = 35
        specific_repelling_box_duration = 5
        specific_repelling_exponential_decay_time = 41
        specific_nodes = [1, 2, 3, 5, 8, 13, 21, 34]
        specific_coverage = 0.78
        intervention_name = "IRSTest1"
        trigger_list = ["HappyBirthday"]

        add_triggered_irs_housing_modification(camp,
                                               trigger_condition_list=trigger_list,
                                               start_day=specific_start_day,
                                               demographic_coverage=specific_coverage,
                                               insecticide=specific_insecticide_name,
                                               killing_initial_effect=specific_killing_effect,
                                               repelling_initial_effect=specific_repelling_effect,
                                               killing_box_duration=specific_killing_box_duration,
                                               killing_decay_time_constant=specific_killing_exponential_decay_time,
                                               repelling_box_duration=specific_repelling_box_duration,
                                               repelling_decay_time_constant=specific_repelling_exponential_decay_time,
                                               node_ids=specific_nodes,
                                               intervention_name=intervention_name)
        self.tmp_intervention = camp.campaign_dict['Events'][0]
        self.parse_intervention_parts()
        self.assertEqual(self.event_coordinator["Intervention_Config"]['Demographic_Coverage'], specific_coverage)
        self.assertEqual(self.intervention_config["Actual_IndividualIntervention_Config"]
                         ["Actual_IndividualIntervention_Configs"][0]['Insecticide_Name'],
                         specific_insecticide_name)
        self.killing_config = self.intervention_config["Actual_IndividualIntervention_Config"][
            "Actual_IndividualIntervention_Configs"][0]["Killing_Config"]
        self.repelling_config = self.intervention_config["Actual_IndividualIntervention_Config"][
            "Actual_IndividualIntervention_Configs"][0]["Repelling_Config"]
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], specific_killing_exponential_decay_time)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], specific_killing_box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], specific_killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.repelling_config[WaningParams.Decay_Time], specific_repelling_exponential_decay_time)
        self.assertEqual(self.repelling_config[WaningParams.Box_Duration], specific_repelling_box_duration)
        self.assertEqual(self.repelling_config[WaningParams.Initial], specific_repelling_effect)
        self.assertEqual(self.repelling_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], specific_nodes)
        self.assertEqual(
            self.intervention_config["Actual_IndividualIntervention_Config"]["Actual_IndividualIntervention_Configs"][
                0]['Intervention_Name'],
            intervention_name)
        return

    def test_default_space_spraying(self):
        start_day = 1
        spray_coverage = 1
        killing_effect = 1
        insecticide = None
        box_duration = 0
        decay_rate = 0
        self.tmp_intervention = SpaceSpraying(camp)
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Spray_Coverage, spray_coverage)
        self.assertEqual(self.start_day, start_day)
        self.assertNotIn("Insecticide_Name", self.intervention_config)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 0)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        pass

    def test_custom_space_spraying(self):
        camp.campaign_dict["Events"] = []
        start_day = 235
        spray_coverage = 0.69
        killing_effect = 0.52
        insecticide = "KillVectors"
        box_duration = 51
        decay_rate = 0.02
        node_ids = [2, 3, 6]
        self.tmp_intervention = SpaceSpraying(camp, start_day=start_day, spray_coverage=spray_coverage,
                                              killing_effect=killing_effect, insecticide=insecticide,
                                              box_duration=box_duration, decay_rate=decay_rate, node_ids=node_ids)
        self.parse_intervention_parts()
        self.assertEqual(self.intervention_config.Spray_Coverage, spray_coverage)
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.intervention_config.Insecticide_Name, insecticide)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 1 / decay_rate)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetList)
        self.assertEqual(self.nodeset[NodesetParams.Node_List], node_ids)
        pass

    def test_default_sugar_trap(self):
        start_day = 0
        killing_effect = 1
        box_duration = 100
        self.tmp_intervention = SugarTrap(camp)
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, start_day)
        self.assertNotIn("Insecticide_Name", self.intervention_config)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 0)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
        self.assertEqual(self.nodeset[NodesetParams.Class], NodesetParams.SetAll)
        pass

    def test_custom_sugar_trap(self):
        camp.campaign_dict["Events"] = []
        start_day = 235
        killing_effect = 0.52
        insecticide = "KillVectors"
        box_duration = 51
        decay_rate = 0.02
        node_ids = [2, 3, 6]
        self.tmp_intervention = SugarTrap(camp, start_day=start_day,
                                          killing_effect=killing_effect, insecticide=insecticide,
                                          box_duration=box_duration, decay_rate=decay_rate, node_ids=node_ids)
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, start_day)
        self.assertEqual(self.intervention_config.Insecticide_Name, insecticide)
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 1 / decay_rate)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
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
        self.assertEqual(self.killing_config[WaningParams.Decay_Time], 0)
        self.assertEqual(self.killing_config[WaningParams.Box_Duration], box_duration)
        self.assertEqual(self.killing_config[WaningParams.Initial], killing_effect)
        self.assertEqual(self.killing_config[WaningParams.Class], WaningEffects.BoxExp)
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
        node_property_restrictions = ["Planet:Mars"]
        target_age_min = 3
        target_age_max = 35
        target_gender = "Female"
        initial_amount = 12
        amount_in_shipment = 30
        days_between_shipments = 14
        duration = 780
        intervention_config = AntimalarialDrug(camp, "malaria_drug")
        max_distributed_per_day = 3
        max_stock = 65
        waiting_period = 2
        self.tmp_intervention = add_community_health_worker(camp, start_day=start_day,
                                                            trigger_condition_list=trigger_condition_list,
                                                            demographic_coverage=demographic_coverage,
                                                            node_ids=node_ids,
                                                            ind_property_restrictions=ind_property_restrictions,
                                                            node_property_restrictions=node_property_restrictions,
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
        self.assertEqual(coordinator_config['Node_Property_Restrictions'], node_property_restrictions)
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
        intervention_config = AntimalarialDrug(camp, "malaria_drug")
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
        self.assertEqual(coordinator_config['Node_Property_Restrictions'], [])
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
        npr = [{"Test:Testing"}, {"Test:Checking"}]
        add_scale_larval_habitats(camp, df=df,
                                  start_day=35, repetitions=3, timesteps_between_repetitions=36,
                                  node_property_restrictions=npr)
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
            self.assertEqual(event_config['Node_Property_Restrictions'], npr)
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

    def test_adherent_drug(self):
        import emodpy_malaria.interventions.adherentdrug as ad
        camp.set_schema(schema_path_file.schema_file)
        doses = [["Sulfadoxine", "Pyrimethamine", 'Amodiaquine'], ['Amodiaquine'], ['Amodiaquine'],
                 ['Pyrimethamine']]  # use doses value that is different from the default
        dose_interval = 2
        non_adherence_options = ['Stop']
        non_adherence_distribution = [1]
        values = [1, 0.6, 0.4, 0.1]
        adherent_drug = ad.adherent_drug(camp,
                                         doses=doses,
                                         dose_interval=dose_interval,
                                         non_adherence_options=non_adherence_options,
                                         non_adherence_distribution=non_adherence_distribution,
                                         adherence_values=values
                                         )
        times = [1.0, 2.0, 3.0, 4.0]
        self.assertEqual(adherent_drug["Adherence_Config"]["Durability_Map"]["Times"], times)
        self.assertEqual(adherent_drug["Adherence_Config"]["Durability_Map"]["Values"], values)
        self.assertEqual(adherent_drug["Doses"], doses)
        self.assertEqual(adherent_drug["Dose_Interval"], dose_interval)
        self.assertEqual(adherent_drug["Non_Adherence_Distribution"], non_adherence_distribution)
        self.assertEqual(adherent_drug["Non_Adherence_Options"], non_adherence_options)
        pass

    def test_adherent_drug_defaults(self):
        import emodpy_malaria.interventions.adherentdrug as ad
        camp.set_schema(schema_path_file.schema_file)
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
        pass


# Uncomment below if you would like to run test suite with different schema
# class TestMalariaInterventions_17Dec20(TestMalariaInterventions):

#     def setUp(self):
#         super(TestMalariaInterventions_17Dec20, self).setUp()
#         self.schema_file = schema_17Dec20

# class TestMalariaInterventions_10Jan21(TestMalariaInterventions):

#     def setUp(self):
#         super(TestMalariaInterventions_10Jan21, self).setUp()
#         self.schema_file = schema_10Jan21


if __name__ == '__main__':
    unittest.main()
