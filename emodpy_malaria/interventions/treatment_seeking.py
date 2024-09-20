from emod_api.interventions.common import *
import emod_api.interventions.utils as utils
from emodpy_malaria.interventions.common import AntimalarialDrug


def _get_events(
        camp,
        start_day: int = 1,
        targets: list = None,
        drug: list = None,
        node_ids: list = None,
        ind_property_restrictions: list = None,
        drug_ineligibility_duration: float = 0,
        duration: int = -1,
        broadcast_event_name: str = 'ReceivedTreatment'):
    if drug is None:
        drug = ['Artemether', 'Lumefantrine']

    if not targets:
        targets = [
            {'trigger': 'NewClinicalCase', 'coverage': 0.1, 'agemin': 15, 'agemax': 70, 'seek': 0.4, 'rate': 0.3},
            {'trigger': 'NewSevereCase', 'coverage': 0.8, 'seek': 0.6, 'rate': 0.5}]

    drugs = [AntimalarialDrug(camp, Drug_Type=d) for d in drug]
    drugs.append(BroadcastEvent(camp, Event_Trigger=broadcast_event_name))
    drug_config = MultiInterventionDistributor(camp, Intervention_List=drugs)

    expire_recent_drug = None

    # cannot be used due to https://github.com/InstituteforDiseaseModeling/emod-api/issues/329
    if drug_ineligibility_duration > 0:
        expire_recent_drug = PropertyValueChanger(camp,
                                                  Target_Property_Key="DrugStatus",
                                                  Target_Property_Value="RecentDrug",
                                                  Revert=drug_ineligibility_duration)

    ret_events = list()

    for t in targets:
        if t['rate'] > 0:
            actual_config = DelayedIntervention(
                camp,
                Delay_Dict={"Delay_Period_Exponential": 1.0 / t['rate']},
                Configs=drugs)
        else:
            actual_config = drug_config

        target_age_min = 0  # age is in years
        target_age_max = 125  # setting defaults in case these are unused
        if all([k in t.keys() for k in ['agemin', 'agemax']]):
            target_age_min = t['agemin']
            target_age_max = t['agemax']

        health_seeking_event = TriggeredCampaignEvent(
            camp,
            Event_Name="Treatment_Seeking_Behaviour",
            Start_Day=start_day,
            Node_Ids=node_ids,
            Triggers=[t['trigger']],
            Duration=duration,
            Target_Age_Min=target_age_min,
            Target_Age_Max=target_age_max,
            Demographic_Coverage=t['coverage'] * t['seek'],
            Property_Restrictions=ind_property_restrictions,
            Intervention_List=[actual_config, expire_recent_drug] if expire_recent_drug else [actual_config])

        ret_events.append(health_seeking_event)

    return ret_events


def add_treatment_seeking(camp,
                          start_day: int = 1,
                          targets: list = None,
                          drug: list = None,
                          node_ids: list = None,
                          ind_property_restrictions: list = None,
                          drug_ineligibility_duration: float = 0,
                          duration: int = -1,
                          broadcast_event_name: str = 'ReceivedTreatment'):
    """
    Add an event-triggered drug-seeking behavior intervention to the campaign using
    the **NodeLevelHealthTriggeredIV**. The intervention will distribute drugs 
    to targeted individuals within the node.
        
    Args:
        camp: object for building, modifying, and writing campaign configuration files.
        start_day: Start day of intervention.
        targets: List of dictionaries defining the trigger event and coverage for and 
        properties of individuals to target with the intervention. Default is

 

            ``[{
            "trigger":"NewClinicalCase","coverage":0.8,"agemin":15,"agemax":70, 
            "seek":0.4,"rate":0.3},{"trigger":"NewSevereCase","coverage":0.8,"seek":0.6,
            "rate":0.5}]``.

 

        drug: List of drug(s) to administer. Default is ``["Artemether","Lumefantrine"]``.
        node_ids: The list of nodes to apply this intervention to (**Node_List**
        parameter). If not provided, set value of NodeSetAll.
        ind_property_restrictions: List of IndividualProperty key:value pairs that 
        individuals must have to receive the intervention. For example,

 

            ``["IndividualProperty1:PropertyValue1", "IndividualProperty2:PropertyValue2"]``.

 
        drug_ineligibility_duration: number of days for which an individual will be ineligible for more drugs
        duration: duration from start_day until people will no longer seek drugs when sick.
            Default is -1, where this never happens.
        broadcast_event_name: Event to broadcast when successful health seeking behavior. 
        Default is ReceivedTreatment.
    Returns:
        None
    
    """

    camp_events = _get_events(camp=camp, start_day=start_day, targets=targets, drug=drug, node_ids=node_ids,
                              ind_property_restrictions=ind_property_restrictions,
                              drug_ineligibility_duration=drug_ineligibility_duration, duration=duration,
                              broadcast_event_name=broadcast_event_name)
    for event in camp_events:
        camp.add(event)
