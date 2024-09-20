"""
This module contains functionality for bednet distribution.
"""

from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emod_api.interventions.common import ScheduledCampaignEvent, TriggeredCampaignEvent, BroadcastEvent


#schema_path = None
iv_name = "Bednet"


def BednetIntervention(schema_path,
                       blocking_eff: float = 0.9,
                       killing_eff: float = 0.6,
                       repelling_eff: float = 0,
                       usage_eff: float = 1,
                       blocking_decay_rate: float = 0,
                       blocking_predecay_duration: int = 730,
                       killing_decay_rate: float = 0,
                       killing_predecay_duration: int = 1460,
                       repelling_decay_rate: float = 0,
                       repelling_predecay_duration: int = 365,
                       usage_decay_rate: float = 0,
                       usage_predecay_duration: int = 365,
                       insecticide: str = None,
                       cost: float = 0
                       ):
    """
    To define the durability of the bednets.
    Args:
        schema_path: Path to the schema
        blocking_eff: Blocking efficacy
        killing_eff: Killing efficacy
        repelling_eff: Repelling efficacy
        usage_eff: Usage efficacy
        blocking_decay_rate: Blocking decay rate
        blocking_predecay_duration: Blocking predacy duration
        killing_decay_rate: Killing decay rate
        killing_predecay_duration: Killing Predecay
        repelling_decay_rate: Repelling decay rate
        repelling_predecay_duration: Repelling predecay duration
        usage_decay_rate: Usage decay rate
        usage_predecay_duration:Usage predecay duration
        insecticide: The name of the insecticide used in the bednet.
        cost: Cost for the intervention.

    Returns:

    """
    intervention = s2c.get_class_with_defaults("SimpleBednet", schema_path)
    blocking = utils.get_waning_from_params(schema_path, blocking_eff, blocking_predecay_duration, blocking_decay_rate)
    killing = utils.get_waning_from_params(schema_path, killing_eff, killing_predecay_duration, killing_decay_rate)
    repelling = utils.get_waning_from_params(schema_path, repelling_eff, repelling_predecay_duration,
                                             repelling_decay_rate)
    if usage_eff != 1 or usage_decay_rate != 0 or usage_predecay_duration != 365:
        usage = utils.get_waning_from_params(schema_path, usage_eff, usage_predecay_duration, usage_decay_rate)
    else: # true default
        usage = s2c.get_class_with_defaults( "WaningEffectRandomBox", schema_path )
        usage.Expected_Discard_Time=3650
        usage.Initial_Effect=1

    # Second, hook them up
    intervention.Killing_Config = killing
    intervention.Blocking_Config = blocking
    intervention.Repelling_Config = repelling
    intervention.Usage_Config = usage
    intervention.Intervention_Name = iv_name
    intervention.Cost_To_Consumer = cost
    if insecticide is None:
        intervention.pop("Insecticide_Name")  # this is not permanent
    else:
        intervention.Insecticide_Name = insecticide

    return intervention


def Bednet(schema_path,
           start_day: int = 0,
           coverage: float = 1.0,
           blocking_eff: float = 1,
           killing_eff: float = 1,
           repelling_eff: float = 1,
           usage_eff: float = 1,
           blocking_decay_rate: float = 0,
           blocking_predecay_duration: int = 365,
           killing_decay_rate: float = 0,
           killing_predecay_duration: int = 365,
           repelling_decay_rate: float = 0,
           repelling_predecay_duration: int = 365,
           usage_decay_rate: float = 0,
           usage_predecay_duration: int = 365,
           node_ids: list = None,
           insecticide: str = None
           ):
    """
    Add a simple insecticide-treated bednet intervention with configurable efficacy and usage 
    that can decay over time to your campaign. This is equivalent to 
    :doc:`emod-malaria:parameter-campaign-individual-usagedependentbednet` with exponential
    waning.

    Args:
        schema_path: path to the schema
        start_day: The day of the simulation on which the bednets are distributed. We recommend 
            aligning this with the start of the simulation.
        coverage: The proportion of the population that will receive a bednet.
        blocking_eff: The efficacy of the bednet at blocking mosquitoes from feeding.
        killing_eff: The efficacy of the bednet at killing mosquitoes that land on it.
        repelling_eff: The efficacy of the bednet at repelling mosquitoes.
        usage_eff: The proportion of time that individuals with a bednet use it. This effectively
            reduces the other efficacy measures by the amount specified; a value of 0.5 will reduce
            blocking, killing, and repelling efficacies by half.
        blocking_decay_rate: The exponential decay length, in days, where the current effect is equal 
            initial efficacy - dt/decay rate.  
        blocking_predecay_duration: The time, in days, before bednet efficacy begins to decay.
        killing_decay_rate: The exponential decay length, in days, where the current effect is equal 
            initial efficacy - dt/decay rate. 
        killing_predecay_duration: The time, in days, before bednet efficacy begins to decay.
        repelling_decay_rate: The exponential decay length, in days, where the current effect is equal 
            initial efficacy - dt/decay rate. 
        repelling_predecay_duration: The time, in days, before bednet efficacy begins to decay.
        usage_decay_rate: The exponential decay length, in days, where the current usage is equal 
            initial efficacy - dt/decay rate. 
        usage_predecay_duration: The time, in days, before bednet usage begins to decay.
        node_ids: The IDs of the nodes in which to distribute the bednets.
        insecticide: The name of the insecticide used in the bednet.

    Returns:
        The bednet intervention event.
    """
    # First, get the objects
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    coordinator.Demographic_Coverage = coverage
    coordinator.Node_Property_Restrictions = []
    coordinator.Property_Restrictions_Within_Node = []
    coordinator.Property_Restrictions = []
    event.Event_Coordinator_Config = coordinator

    intervention = BednetIntervention(
           schema_path,
           blocking_eff,
           killing_eff, 
           repelling_eff, 
           usage_eff, 
           blocking_decay_rate, 
           blocking_predecay_duration, 
           killing_decay_rate, 
           killing_predecay_duration, 
           repelling_decay_rate, 
           repelling_predecay_duration, 
           usage_decay_rate, 
           usage_predecay_duration, 
           insecticide
       )

    coordinator.Intervention_Config = intervention
    event.Start_Day = float(start_day)

    event.Nodeset_Config = utils.do_nodes(schema_path, node_ids)

    return event


def BasicBednet(camp, start_day, coverage=1.0, blocking_eff=1, killing_eff=1, repelling_eff=1, usage_eff=1,
                 insecticide=None):
    """
    Add a simpler insecticide-treated bednet intervention with constant efficacy and usage
    to your campaign. This is equivalent to :doc:`emod-malaria:parameter-campaign-individual-simplebednet`.

    Args:
        camp: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will 
            be added. 
        start_day: The day of the simulation on which the bednets are distributed. We recommend 
            aligning this with the start of the simulation.
        coverage: The proportion of the population that will receive a bednet.
        blocking_eff: The efficacy of the bednet at blocking mosquitoes from feeding.
        killing_eff: The efficacy of the bednet at killing mosquitoes that land on it.
        repelling_eff: The efficacy of the bednet at repelling mosquitoes.
        usage_eff: The proportion of individuals with a bednet who use it.
        insecticide: The insecticide used in the bednet.

    Returns:
        The bednet intervention event.
    """
    return Bednet(camp, start_day=start_day, coverage=coverage, blocking_eff=blocking_eff, killing_eff=killing_eff,
                  repelling_eff=repelling_eff, usage_eff=usage_eff, insecticide=insecticide)


def new_intervention_as_file(camp, start_day, filename=None):
    """
    Write a campaign file to disk with a single bednet event, using defaults. Useful for testing and learning.

    Args:
        camp: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will be added. 
        start_day: The day of the simulation on which the bednets are distributed. We recommend 
            aligning this with the start of the simulation.
        filename: The campaign filename; can be omitted and default will be used and returned to user.

    Returns:
        The campaign filename written to disk.
    """
    camp.add(Bednet(camp.schema_path, start_day), first=True)
    if filename is None:
        filename = "BedNet.json"
    camp.save(filename)
    return filename


def add_ITN_scheduled(camp,
                      start_day: int = 0,
                      coverage_by_ages: list = None,
                      node_ids: list = None,
                      itn_bednet: BednetIntervention = None,
                      blocking_eff: float = 0.9,
                      blocking_predecay_duration: int = 0,
                      blocking_decay_rate: float = 1/7300.,
                      killing_eff: float = 0.6,
                      killing_predecay_duration: int = 0,
                      killing_decay_rate: float = 1/7300.,
                      ind_property_restrictions: list = None,
                      repetitions: int = 1,
                      tsteps_btwn_repetitions: int = 365*3,
                      receiving_itn_event_name: str = ""
                      ):
    """
    Add a scheduled bednet intervention.

    Args:
        camp: object for building, modifying, and writing campaign configuration files.
        start_day: Start day of intervention.
        coverage_by_ages: A list of dictionaries defining the coverage per
            age group. For example, ``[{"coverage":1,"min": 1, "max": 10},
            {"coverage":1,"min": 11, "max": 50},{ "coverage":0.5, "birth":"birth",
            "duration":34}]``.
        node_ids: The list of nodes to apply this intervention to. If not provided, set value of NodeSetAll.
        itn_bednet:  An object of class Bednet to define the durability of the nets. If not
            provided, the default decay profile of a Bednet intervention is used.
        blocking_eff: Initial blocking efficacy.
        blocking_predecay_duration: How long blocking efficacy holds prior to decay.
        blocking_decay_rate: Blocking decay rate after constant period.
        killing_eff: Initial killing efficacy.
        killing_predecay_duration: How long killing efficacy holds prior to decay.
        killing_decay_rate: Killing decay rate after constant period.
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention (
            **Property_Restrictions_Within_Node** parameter). In the format ``[{
            "BitingRisk":"High"}, {"IsCool":"Yes}]``.
        repetitions: Repeat this intervention **repetions** times.
        tsteps_btwn_repetitions: Number of timesteps between repetitions.
        receiving_itn_event_name: Name of event/trigger/signal to publish when bednet is distributed.

    Returns:
        None

    """
    if not receiving_itn_event_name :
       receiving_itn_event_name = 'Received_ITN'
    receiving_itn_event = BroadcastEvent(camp=camp, Event_Trigger=receiving_itn_event_name)

    if itn_bednet is None:
        itn_bednet = BednetIntervention( camp.schema_path, blocking_eff=blocking_eff, blocking_predecay_duration=blocking_predecay_duration, blocking_decay_rate=blocking_decay_rate, killing_eff=killing_eff, killing_predecay_duration=killing_predecay_duration, killing_decay_rate=killing_decay_rate )

    for coverage_by_age in coverage_by_ages:
        sce_itn = ScheduledCampaignEvent(camp, start_day,
                                         Node_Ids=node_ids,
                                         Number_Repetitions=repetitions,
                                         Timesteps_Between_Repetitions=tsteps_btwn_repetitions,
                                         Property_Restrictions=ind_property_restrictions,
                                         Demographic_Coverage=coverage_by_age["coverage"],
                                         Intervention_List=[itn_bednet, receiving_itn_event],
                                         Target_Age_Min=coverage_by_age["min"],
                                         Target_Age_Max=coverage_by_age["max"]
                                         )
        camp.add(sce_itn)


def add_ITN_triggered(camp, start_day: int = 0, event_name: str = "", coverage_by_ages: list = None, itn_bednet: Bednet = None,
                      node_ids: list = None, insecticide: str = None, node_property_restrictions: list = None,
                      triggered_campaign_delay: int = None,
                      trigger_condition_list: list = None, listening_duration: int = -1,
                      check_eligibility_at_trigger: bool = False, repetitions: int = 1,
                      tsteps_btwn_repetitions: int = 365 * 3):

    if itn_bednet is None:
        itn_bednet = BednetIntervention(camp.schema_path)   # use defaults

    for coverage_by_age in coverage_by_ages:
        sce_itn = TriggeredCampaignEvent(camp, start_day, event_name,
                                         Triggers=trigger_condition_list,
                                         Intervention_List=[itn_bednet],
                                         Node_Ids=node_ids,
                                         Property_Restrictions=node_property_restrictions,
                                         # Demographic_Coverage=None,
                                         Number_Repetitions=repetitions,
                                         Timesteps_Between_Repetitions=tsteps_btwn_repetitions,
                                         Demographic_Coverage=coverage_by_age["coverage"],
                                         Target_Age_Min=coverage_by_age["min"],
                                         Target_Age_Max=coverage_by_age["max"],
                                         # Target_Gender=None,
                                         # Target_Residents_Only=None,
                                         Duration=listening_duration,
                                         # Blackout_Event_Trigger=None,
                                         # Blackout_Period=0,
                                         # Blackout_On_First_Occurrence=None,
                                         # Disqualifying_Properties=None,
                                         # Disqualifying_Properties=None,
                                         Delay=triggered_campaign_delay
                                         )
        camp.add(sce_itn)
    raise NotImplemented


def add_ITN(camp, start: int = 0, coverage_by_ages: list = None, itn_bednet: s2c.ReadOnlyDict = None,
            nodeIDs: list = None, insecticide: str = None, node_property_restrictions: list = None,
            ind_property_restrictions: list = None, triggered_campaign_delay: int = None,
            trigger_condition_list: list = None, listening_duration: int = -1,
            check_eligibility_at_trigger: bool = False, repetitions: int = 1, tsteps_btwn_repetitions: int = 365*3):
    """ Add an insecticide-treated net (ITN) intervention to the campaign using the **SimpleBednet** class.

    Args:
        camp: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>`
            containing the campaign configuration.
        start: The day on which to start distributing the bednets
            (**Start_Day** parameter).
        coverage_by_ages: A list of dictionaries defining the coverage per
            age group. For example, ``[{"coverage":1,"min": 1, "max": 10},
            {"coverage":1,"min": 11, "max": 50},{ "coverage":0.5, "birth":"birth",
            "duration":34}]``.
        itn_bednet: A dictionary defining the durability of the nets. If not
            provided, the default decay profile for **Killing_Config**,
            **Blocking_Config**, and **Usage_Config** are used. For example,
            to update usage duration, provide ``{"Usage_Config" : {
            "Expected_Discard_Time": 180}}``.
        cost: The per-unit cost (**Cost_To_Consumer** parameter).
        nodeIDs: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.
        insecticide: name of insecticide to use, must be in config.json Default None.
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention (
            **Property_Restrictions_Within_Node** parameter). In the format ``[{
            "BitingRisk":"High"}, {"IsCool":"Yes}]``.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention (**Node_Property_Restrictions**
            parameter). In the format ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``.
        triggered_campaign_delay: After the trigger is received, the number of
            time steps until the campaign starts. Eligibility of people or nodes
            for the campaign is evaluated on the start day, not the triggered
            day.
        trigger_condition_list: (Optional) A list of the events that will
            trigger the ITN intervention. If included, **start** is the day
            when monitoring for triggers begins. This argument cannot
            configure birth-triggered ITN (use **coverage_by_ages** instead).
        listening_duration: The number of time steps that the distributed
            event will monitor for triggers. Default is -1, which is indefinitely.
        check_eligibility_at_trigger: if triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay.

    Returns:
        None

    Example:
        camp = DTKConfigBuilder.from_defaults(sim_example)
        coverage_by_ages = [{"coverage": 1, "min": 1, "max": 10},
        {"coverage": 0.75, "min": 11, "max": 60}]
        add_ITN(camp, start=1, coverage_by_ages,
        nodeIDs=[2, 5, 7, 21],
        node_property_restrictions=[{"Place": "Urban"}],
        ind_property_restrictions=[{"Biting_Risk": "High"],
        triggered_campaign_delay=14,
        trigger_condition_list=["NewClinicalCase", "NewSevereCase"],
        listening_duration=-1)
    """

    if trigger_condition_list:
        add_ITN_triggered(camp, start, "ITN", trigger_condition_list,
                          Node_Property_Restrictions=node_property_restrictions,
                          Property_Restrictions=ind_property_restrictions,
                          coverage_by_ages=coverage_by_ages,
                          Number_Repetitions=repetitions,
                          Timesteps_Between_Repetitions=tsteps_btwn_repetitions,
                          Nodeset_Config=nodeIDs,
                          Delay=triggered_campaign_delay,
                          Duration=listening_duration
                          )

    else:
        add_ITN_scheduled(camp, start,
                          coverage_by_ages=coverage_by_ages,
                          node_ids=nodeIDs,
                          itn_bednet=itn_bednet,
                          ind_property_restrictions=node_property_restrictions,
                          repetitions=repetitions,
                          tsteps_btwn_repetitions=tsteps_btwn_repetitions
                          )

