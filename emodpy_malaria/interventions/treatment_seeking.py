from emod_api.interventions.common import *
from emodpy_malaria.interventions.drug import _antimalarial_drug
from emodpy_malaria.interventions.common import add_triggered_campaign_delay_event
import random


def _get_events(
        campaign,
        start_day: int = 1,
        targets: list = None,
        drug: list = None,
        node_ids: list = None,
        ind_property_restrictions: list = None,
        drug_ineligibility_duration: float = 0,
        duration: int = -1,
        broadcast_event_name: str = 'Received_Treatment'):
    if not drug:
        drug = ['Artemether', 'Lumefantrine']

    if not targets:
        raise ValueError("Please define targets for treatment seeking. It is a list of dictionaries:\n "
                         "ex: [{\"trigger\":\"NewClinicalCase\", \"coverage\":0.8, \"agemin\":15, \"agemax\":70, \"rate\":0.3}]\n")
    for target in targets:
        if "trigger" not in target:
            raise ValueError("Please define \"trigger\" for each target dictionary. \n"
                             "ex: [{\"trigger\":\"NewClinicalCase\", \"coverage\":0.7, \"agemax\":3 }]")
        if "seek" in target:
            raise ValueError("Notice: \"seek\" parameter has been removed. Please remove it from your \"targets\""
                             " dictionary."
                             " Please modify the \"coverage\" parameter "
                             "directly to attain a different coverage for the intervention. Previously, "
                             "\"Demographic_Coverage\" was \"coverage\"x\"seek\". It is now just \"coverage\".\n")

    drugs = [_antimalarial_drug(campaign, drug_type=d) for d in drug]
    drugs.append(BroadcastEvent(campaign, Event_Trigger=broadcast_event_name))

    if drug_ineligibility_duration > 0:
        drug_ineligibility = PropertyValueChanger(campaign,
                                                  Target_Property_Key="DrugStatus",
                                                  Target_Property_Value="RecentDrug",
                                                  Revert=drug_ineligibility_duration)
        drugs.append(drug_ineligibility)

    drug_config = MultiInterventionDistributor(campaign, Intervention_List=drugs)
    ret_events = list()
    for target in targets:
        if 'rate' in target and target['rate'] > 0:
            actual_config = DelayedIntervention(
                campaign,
                Delay_Dict={"Delay_Period_Exponential": 1.0 / target['rate']},
                Configs=drugs)
        else:
            actual_config = drug_config

        target_age_min = 0  # age is in years
        target_age_max = 1000  # setting defaults in case these are unused
        coverage = 1
        if 'agemin' in target:
            target_age_min = target['agemin']
        if 'agemax' in target:
            target_age_max = target['agemax']
        if 'coverage' in target:
            coverage = target['coverage']

        treatment_seeking_event = TriggeredCampaignEvent(
            campaign,
            Event_Name="Treatment_Seeking_Behavior",
            Start_Day=start_day,
            Node_Ids=node_ids,
            Triggers=[target['trigger']],
            Duration=duration,
            Target_Age_Min=target_age_min,
            Target_Age_Max=target_age_max,
            Demographic_Coverage=coverage,
            Property_Restrictions=ind_property_restrictions,
            Intervention_List=[actual_config])

        ret_events.append(treatment_seeking_event)

    return ret_events


def add_treatment_seeking(campaign,
                          start_day: int = 1,
                          targets: list = None,
                          drug: list = None,
                          node_ids: list = None,
                          ind_property_restrictions: list = None,
                          drug_ineligibility_duration: float = 0,
                          duration: int = -1,
                          broadcast_event_name: str = 'Received_Treatment'):
    """
    Add an event-triggered drug-seeking behavior intervention to the campaign using
    the **NodeLevelHealthTriggeredIV**. The intervention will distribute drugs 
    to targeted individuals within the node.

    targets is a list of dictionaries defining the trigger event and coverage for and
    properties of individuals to target with the intervention with all possible options being:
    [{"trigger":"NewClinicalCase","coverage":0.8,"agemin":15,"agemax":70, "rate":0.3}]
    "rate" is the inverse of the average delay in time to treatment seeking from an exponential distribution
    "trigger" must be defined, but everything else has defaults:
    coverage = 1, affects all
    agemin/agemax = 0/1000, affects all
    rate = 0, no delay, seek treatment immediately

    Args:
        campaign: object for building, modifying, and writing campaign configuration files.
        start_day: Start day of intervention.
        targets: List of dictionaries defining the trigger event and coverage for and 
            properties of individuals to target with the intervention. "trigger" must be defined, other defaults are as
            follows - "coverage":1,"agemin":0,"agemax":1000, "rate":0 (no delay)

            Example::

                [{"trigger":"NewClinicalCase","coverage":0.8,"agemin":15,"agemax":70, "rate":0.3}]


        drug: List of drug(s) to administer from the drugs defined in config.
            Default is ``["Artemether","Lumefantrine"]``
        node_ids: The list of nodes to apply this intervention to (**Node_List**
        parameter). If not provided, set value of NodeSetAll.
        ind_property_restrictions: List of IndividualProperty key:value pairs that 
        individuals must have to receive the intervention. For example,

 

            ``["IndividualProperty1:PropertyValue1", "IndividualProperty2:PropertyValue2"]``.

 
        drug_ineligibility_duration: number of days for which an individual will be ineligible for more drugs
        duration: duration from start_day until people will no longer seek drugs when sick.
            Default is -1, meaning they will always seek drugs when sick
        broadcast_event_name: Event to broadcast when successful health seeking behavior.
            Default is "Received_Treatment".

    Returns:
        None
    
    """

    camp_events = _get_events(campaign=campaign, start_day=start_day, targets=targets, drug=drug, node_ids=node_ids,
                              ind_property_restrictions=ind_property_restrictions,
                              drug_ineligibility_duration=drug_ineligibility_duration, duration=duration,
                              broadcast_event_name=broadcast_event_name)
    for event in camp_events:
        campaign.add(event)
