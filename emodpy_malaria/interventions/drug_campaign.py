"""
This module contains functionality for malaria intervention distribution
via a cascade of care that may contain diagnostics and drug treatments.
"""

from copy import deepcopy, copy
import random

from emod_api.interventions.common import *
from emodpy_malaria.interventions.drug import _antimalarial_drug
from emodpy_malaria.interventions.diag_survey import add_diagnostic_survey
from emodpy_malaria.interventions.common import add_campaign_event

# Different configurations of regimens and drugs
drug_cfg = {
    "ALP": ["Artemether", "Lumefantrine", "Primaquine"],
    "AL": ["Artemether", "Lumefantrine"],
    "ASA": ["Artesunate", "Amodiaquine"],
    "DP": ["DHA", "Piperaquine"],
    "DPP": ["DHA", "Piperaquine", "Primaquine"],
    "PPQ": ["Piperaquine"],
    "DHA_PQ": ["DHA", "Primaquine"],
    "DHA": ["DHA"],
    "PMQ": ["Primaquine"],
    "DA": ["DHA", "Abstract"],
    "CQ": ["Chloroquine"],
    "SP": ["Sulfadoxine", "Pyrimethamine"],
    "SPP": ["Sulfadoxine", "Pyrimethamine", 'Primaquine'],
    "SPA": ["Sulfadoxine", "Pyrimethamine", 'Amodiaquine'],
    "Vehicle": ["Vehicle"]
}


def drug_configs_from_code(campaign, drug_code: str = None):
    """  
    Add a single or multiple drug regimen to the configuration file based
    on its code and add the corresponding 
    :doc:`emod-malaria:parameter-campaign-individual-antimalarialdrug`
    intervention to the return dictionary. For example, passing the ``ALP`` drug
    code will add the drug configuration for artemether, lumefantrine, and
    primaquine to the configuration file and will return a dictionary containing a
    full treatment course for those three drugs. For more information, see
    **Malaria_Drug_Params** in :doc:`emod-malaria:parameter-configuration-drugs`.
      
    Args:
        campaign: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention
            will be added. 
        drug_code: The code of the drug regimen. This must be listed in the ``drug_cfg`` 
            dictionary.

    Returns:
          A dictionary containing the intervention for the given drug regimen.
    """
    if not drug_code or drug_code not in drug_cfg:
        raise Exception("Please pass in a (valid) drug_code.\n"
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
                        "\"Vehicle\": Vehicle.\n")
    drug_array = drug_cfg[drug_code]

    drug_configs = []
    for drug in drug_array:
        drug_intervention = _antimalarial_drug(campaign, drug_type=drug, cost_to_consumer=1.5)
        drug_configs.append(drug_intervention)
    return drug_configs


def add_drug_campaign(campaign,
                      campaign_type: str = 'MDA',
                      drug_code: str = None,
                      start_days: list = None,
                      coverage: float = 1.0,
                      repetitions: int = 1,
                      tsteps_btwn_repetitions: int = 60,
                      diagnostic_type: str = 'BLOOD_SMEAR_PARASITES',
                      diagnostic_threshold: float = 40,
                      measurement_sensitivity: float = 0.1,
                      fmda_radius: int = 0,
                      node_selection_type: str = 'DISTANCE_ONLY',
                      trigger_coverage: float = 1.0,
                      snowballs: int = 0,
                      treatment_delay: int = 0,
                      triggered_campaign_delay: int = 0,
                      node_ids: list = None,
                      target_group: any = 'Everyone',
                      drug_ineligibility_duration: int = 0,
                      ind_property_restrictions: list = None,
                      disqualifying_properties: list = None,
                      trigger_condition_list: list = None,
                      listening_duration: int = -1,
                      adherent_drug_configs: list = None,
                      target_residents_only: int = 1,
                      check_eligibility_at_trigger: bool = False,
                      receiving_drugs_event_name='Received_Campaign_Drugs'):
    """ 
    Add a drug intervention campaign from a list of malaria campaign types.
    This intervention uses the
    :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic` class
    to create either a scheduled or a triggered event to the campaign and the
    :doc:`emod-malaria:parameter-campaign-individual-antimalarialdrug` class
    to configure drug interventions. You can also specify a delay period for a
    triggered event that broadcasts afterwards.  If the campaign is repeated
    or triggered, separate 
    :doc:`emod-malaria:parameter-campaign-node-nodelevelhealthtriggerediv`
    interventions are created with a delay that sends an event to distribute
    drugs.




    Args:
        campaign: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will
            be added. 
        campaign_type: The type of drug campaign. Available options are:

            MDA 
                Add a mass drug administration intervention.
            MSAT 
                Add a  mass screening and treatment intervention.
            SMC 
                Add a seasonal malaria chemoprevention intervention.
            fMDA
                Add a focal mass drug administration intervention based on 
                results from a diagnostic survey, which is either scheduled or
                triggered (when **trigger_condition_list** is present).
            MTAT 
                Add a mass testing and treatment intervention.
            rfMSAT 
                Add a reactive focal mass screening and treatment intervention.
                Detecting malaria triggers diagnostic surveys to run on
                neighboring nodes and so on, up to the number of triggered interventions
                defined in the **snowballs** parameter.
            rfMDA 
                Add a reactive focal mass drug administration intervention. This triggers
                :doc:`emod-malaria:parameter-campaign-individual-broadcasteventtoothernodes`
                to broadcast a "Give_Drugs_rfMDA" event, which triggers
                :doc:`emod-malaria:parameter-campaign-individual-multiinterventiondistributor`
                to distribute drugs and a "ReceivedTreatment" event followed by
                a delayed "Give_Drugs_rfMDA" event to neighboring nodes, which
                will trigger another drug distribution. 

        drug_code: The code of the drug regimen to distribute. This must be 
            listed in the ``drug_cfg`` dictionary.
        start_days: List of start days (integers) when the drug regimen will
            be distributed. Due to diagnostic/treatment configuration,
            the earliest start day is 1. When **trigger_condition_list** is used,
            the first entry of **start_days** is the day to start listening
            for the trigger(s).
        coverage: The demographic coverage of the distribution (the fraction of
            people at home during the campaign).
        repetitions: The number of repetitions.
        tsteps_btwn_repetitions: The timesteps between the repetitions.
        diagnostic_type: The setting for **Diagnostic_Type** in 
            :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`.
            In addition to the accepted values listed there, you may also set
            TRUE_INFECTION_STATUS, which calls 
            :doc:`emod-malaria:parameter-campaign-individual-standarddiagnostic`
            instead.
        diagnostic_threshold: The setting for **Diagnostic_Threshold** in 
            :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`. 
        measurement_sensitivity: The setting for **Measurement_Sensitivity**
            in :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`.
        detection_threshold: The setting for **Detection_Threshold** in 
            :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`. 
        fmda_radius: Radius (in km) of focal response upon finding infection. 
            Used in simulations with many small nodes to simulate 
            community health workers distributing drugs to surrounding houses.
            Used when **campaign_type** is set to fMDA.
        node_selection_type: The setting for **Node_Selection_Type** in
          :doc:`emod-malaria:parameter-campaign-individual-broadcasteventtoothernodes`.
        trigger_coverage: The fraction of trigger events that will trigger reactive
            case detection (RCD). Used when **campaign_type** is set to rfMSAT or rfMDA. 
            To set the fraction of individuals reached during RCD response, use **coverage**.
        snowballs: The number of times each triggered intervention will be distributed
            to surrounding nodes. For example, one snowball gives drugs to nodes
            neighboring the first node and two snowballs gives drugs to the nodes 
            neighboring those nodes. Used when **campaign_type** is set to rfMSAT.
        treatment_delay: For **campaign_type** set to MSAT or fMDA, the length of time 
            between administering a diagnostic and giving drugs; for values of rfMSAT 
            or rfMDA, the length of time between treating the index case and triggering 
            an RCD response.
        triggered_campaign_delay: When using **trigger_condition_list**, this
            indicates the delay period between receiving the trigger event
            and running the triggered campaign intervention.
        node_ids: The setting for **Node_List** in :ref:`emod-malaria:campaign-nodeset-config`. 
        target_group: A dictionary of ``{'agemin': x, 'agemax': y}`` to
            target MDA, SMC, MSAT, fMDA to individuals between x and y years
            of age. Default is Everyone.
        drug_ineligibility_duration: The number of days to set the **DrugStatus** 
            individual property to **RecentDrug**, after which the property value
            is reverted. This property value prevents people from receiving drugs too
            frequently, but they can still receive diagnostics during this period.
            For more information, see :doc:`emod-malaria:model-targeted-interventions`.
        ind_property_restrictions: The setting for **Property_Restrictions_Within_Node**
            in :doc:`emod-malaria:parameter-campaign-event-triggeredeventcoordinator`
            that individuals must have to receive the diagnostic intervention.
        disqualifying_properties: The setting for **Disqualifying_Properties**
            in :doc:`emod-malaria:parameter-campaign-individual-antimalarialdrug` or
            in :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`.
        trigger_condition_list: The setting for **Start_Trigger_Condition_List** in
            :doc:`emod-malaria:parameter-campaign-event-triggeredeventcoordinator`.
        listening_duration: The setting for **Duration** in
            :doc:`emod-malaria:parameter-campaign-event-triggeredeventcoordinator`.
        adherent_drug_configs: List of adherent drug configurations, which are
            dictionaries from configure_adherent_drug.
        target_residents_only: The setting for **Target_Residents_Only** in
            :doc:`emod-malaria:parameter-campaign-event-triggeredeventcoordinator`.
        check_eligibility_at_trigger: Set to True to check the individual or node's 
            eligibility at the initial trigger; set to False to check eligibility
            when the event is actually distributed after a delay.
        receiving_drugs_event_name: The event to broadcast when a person receives drugs.

    Returns:
        A dictionary with drug campaign parameters.
    """

    if not drug_code and not adherent_drug_configs:
        raise Exception("You have to pass in  drug_code(AL, DP, etc; allowable types defined in malaria_drugs.py) or"
                        "a list of adherent_drug_configs, which can be generated with adherent_drug.py/configure_"
                        "adherent_drug.\n")
    elif drug_code and adherent_drug_configs:
        raise Exception("You passed in a drug_code AND a list of adherent_drug_configs. Please pick one.\n")
    if adherent_drug_configs:
        drug_configs = adherent_drug_configs
    else:
        drug_configs = drug_configs_from_code(campaign, drug_code=drug_code)
    if not ind_property_restrictions:
        ind_property_restrictions = []
    if not disqualifying_properties:
        disqualifying_properties = []

    # set up events to broadcast when receiving campaign drug
    receiving_drugs_event = BroadcastEvent(campaign, Event_Trigger=receiving_drugs_event_name)
    if campaign_type[0] == 'r':  # if reactive campaign
        receiving_drugs_event.Broadcast_Event = 'Received_RCD_Drugs'
    if drug_code and 'Vehicle' in drug_code:  # if distributing Vehicle drug
        receiving_drugs_event.Broadcast_Event = "Received_Vehicle"

    expire_recent_drugs = None
    if drug_ineligibility_duration > 0:
        expire_recent_drugs = PropertyValueChanger(
            Target_Property_Key="DrugStatus",
            Target_Property_Value="RecentDrug",
            Revert=drug_ineligibility_duration)

    if start_days is None:
        start_days = [1]
    # set up drug campaign
    if campaign_type == 'MDA' or campaign_type == 'SMC':
        if treatment_delay:
            raise ValueError('"treatment_delay" parameter is not used in MDA or SMC')
        add_MDA(campaign, start_days=start_days, coverage=coverage, drug_configs=drug_configs,
                receiving_drugs_event=receiving_drugs_event, repetitions=repetitions,
                tsteps_btwn_repetitions=tsteps_btwn_repetitions, node_ids=node_ids,
                expire_recent_drugs=expire_recent_drugs,
                ind_property_restrictions=ind_property_restrictions, disqualifying_properties=disqualifying_properties,
                target_group=target_group, trigger_condition_list=trigger_condition_list,
                listening_duration=listening_duration, triggered_campaign_delay=triggered_campaign_delay,
                target_residents_only=target_residents_only, check_eligibility_at_trigger=check_eligibility_at_trigger)

    elif campaign_type == 'MSAT' or campaign_type == 'MTAT':
        add_MSAT(campaign, start_days=start_days, coverage=coverage, drug_configs=drug_configs,
                 receiving_drugs_event=receiving_drugs_event, repetitions=repetitions,
                 tsteps_btwn_repetitions=tsteps_btwn_repetitions, treatment_delay=treatment_delay,
                 diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                 measurement_sensitivity=measurement_sensitivity,
                 node_ids=node_ids,
                 expire_recent_drugs=expire_recent_drugs,
                 ind_property_restrictions=ind_property_restrictions, disqualifying_properties=disqualifying_properties,
                 target_group=target_group, trigger_condition_list=trigger_condition_list,
                 triggered_campaign_delay=triggered_campaign_delay, listening_duration=listening_duration,
                 check_eligibility_at_trigger=check_eligibility_at_trigger)

    elif campaign_type == 'fMDA':
        add_fMDA(campaign, start_days=start_days, trigger_coverage=trigger_coverage, coverage=coverage,
                 drug_configs=drug_configs, receiving_drugs_event=receiving_drugs_event, repetitions=repetitions,
                 tsteps_btwn_repetitions=tsteps_btwn_repetitions, treatment_delay=treatment_delay,
                 diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                 measurement_sensitivity=measurement_sensitivity,
                 fmda_radius=fmda_radius,
                 node_selection_type=node_selection_type, node_ids=node_ids, expire_recent_drugs=expire_recent_drugs,
                 ind_property_restrictions=ind_property_restrictions,
                 disqualifying_properties=disqualifying_properties, target_group=target_group,
                 trigger_condition_list=trigger_condition_list, listening_duration=listening_duration,
                 triggered_campaign_delay=triggered_campaign_delay,
                 check_eligibility_at_trigger=check_eligibility_at_trigger)

    # not a triggerable campaign
    elif campaign_type == 'rfMSAT':
        add_rfMSAT(campaign, start_day=start_days[0], coverage=coverage, drug_configs=drug_configs,
                   receiving_drugs_event=receiving_drugs_event, listening_duration=listening_duration,
                   treatment_delay=treatment_delay, trigger_coverage=trigger_coverage, diagnostic_type=diagnostic_type,
                   diagnostic_threshold=diagnostic_threshold,
                   measurement_sensitivity=measurement_sensitivity,
                   fmda_radius=fmda_radius,
                   node_selection_type=node_selection_type, snowballs=snowballs, node_ids=node_ids,
                   expire_recent_drugs=expire_recent_drugs,
                   ind_property_restrictions=ind_property_restrictions,
                   disqualifying_properties=disqualifying_properties)

    # not a triggerable campaign
    elif campaign_type == 'rfMDA':
        add_rfMDA(campaign, start_day=start_days[0], coverage=coverage, drug_configs=drug_configs,
                  receiving_drugs_event=receiving_drugs_event, listening_duration=listening_duration,
                  treatment_delay=treatment_delay, trigger_coverage=trigger_coverage, fmda_radius=fmda_radius,
                  node_selection_type=node_selection_type, node_ids=node_ids, expire_recent_drugs=expire_recent_drugs,
                  ind_property_restrictions=ind_property_restrictions,
                  disqualifying_properties=disqualifying_properties)

    else:
        raise Exception('Warning: unrecognized campaign type\n')
        pass

    return {'drug_campaign.type': campaign_type,
            'drug_campaign.drugs': drug_code,
            'drug_campaign.trigger_coverage': trigger_coverage,
            'drug_campaign.coverage': coverage
            }


def add_MDA(campaign, start_days: list = None, coverage: float = 1.0, drug_configs: list = None,
            receiving_drugs_event: BroadcastEvent = None, repetitions: int = 1, tsteps_btwn_repetitions: int = 60,
            node_ids: list = None, expire_recent_drugs: PropertyValueChanger = None,
            ind_property_restrictions: list = None, disqualifying_properties: list = None,
            target_group: any = 'Everyone',
            trigger_condition_list: list = None, listening_duration: int = -1, triggered_campaign_delay: int = 0,
            target_residents_only: int = 1, check_eligibility_at_trigger: bool = False):
    """
    Add an MDA (mass drug administration) drug intervention to your campaign. 
    See :py:func:`add_drug_campaign` for more information about each
    argument.

    Returns:
        None
    """

    if start_days is None:
        start_days = [1]
    if drug_configs is None:
        raise Exception("You have to pass in drug_configs (list of drug configurations) that can be generated with "
                        "malaria.interventions.malaria_drugs import drug_configs_from_code.\n")
    if disqualifying_properties is None:
        disqualifying_properties = []

    interventions = drug_configs
    if receiving_drugs_event:
        interventions.append(receiving_drugs_event)
    if expire_recent_drugs:
        interventions.append(expire_recent_drugs)

    target_sex = "All"
    target_age_min = 0
    target_age_max = 9.3228e+35
    if "agemin" in target_group:
        target_age_min = target_group["agemin"]
    if "agemax" in target_group:
        target_age_max = target_group["agemax"]
    if "gender" in target_group:
        target_sex = target_group["gender"]
       
    """
        raise KeyError("Unknown target_group parameter. Please pass in 'Everyone' or a dictionary of "
                       "{'agemin' : x, 'agemax' : y, 'gender': 'Female'} to target  to individuals between x and "
                       "y years of age, and (optional) gender.\n")
    """

    if trigger_condition_list:
        # if once triggered, you want the diagnostic survey to repeat or if there is a delay (or both)
        # this creates a series of broadcast events that once triggered send out broadcast_event
        # at pre-determined intervals
        if repetitions > 1 or triggered_campaign_delay > 0:
            # create a trigger for each of the delays.
            broadcast_event = "MDA_Now_{}".format(random.randint(1, 10000))
            trigger_ind_property_restrictions = []
            if check_eligibility_at_trigger:
                trigger_ind_property_restrictions = ind_property_restrictions
                ind_property_restrictions = []
            for x in range(repetitions):
                tcde = TriggeredCampaignEvent(
                    campaign,
                    Start_Day=start_days[0] + 1,
                    Event_Name="MDA_Delayed",
                    Node_Ids=node_ids,
                    Triggers=trigger_condition_list,
                    Duration=listening_duration,
                    Intervention_List=[BroadcastEvent(campaign, broadcast_event)],
                    Property_Restrictions=trigger_ind_property_restrictions,
                    Delay=triggered_campaign_delay + (x * tsteps_btwn_repetitions))
                campaign.add(tcde)
            trigger_condition_list = [broadcast_event]

        drug_event = TriggeredCampaignEvent(
            campaign,
            Start_Day=start_days[0],
            Event_Name="MDA_Now",
            Node_Ids=node_ids,
            Target_Age_Min=target_age_min,
            Target_Age_Max=target_age_max,
            Target_Gender=target_sex,
            Property_Restrictions=ind_property_restrictions,
            Demographic_Coverage=coverage,
            Disqualifying_Properties=disqualifying_properties,
            Triggers=trigger_condition_list,
            Duration=listening_duration,
            Target_Residents_Only=target_residents_only,
            Intervention_List=interventions)
        campaign.add(drug_event)

    else:
        for start_day in start_days:
            add_campaign_event(
                campaign=campaign,
                start_day=start_day,
                node_ids=node_ids,
                target_age_min=target_age_min,
                target_age_max=target_age_max,
                target_gender=target_sex,
                ind_property_restrictions=ind_property_restrictions,
                demographic_coverage=coverage,
                individual_intervention=interventions,
                repetitions=repetitions,
                timesteps_between_repetitions=tsteps_btwn_repetitions)


def add_MSAT(campaign, start_days: list = None, coverage: float = 1.0, drug_configs: list = None,
             receiving_drugs_event: BroadcastEvent = None, repetitions: int = 1, tsteps_btwn_repetitions: int = 60,
             treatment_delay: int = 0, diagnostic_type: str = 'BLOOD_SMEAR_PARASITES',
             diagnostic_threshold: float = 40, measurement_sensitivity: float = 0.1, node_ids: list = None,
             expire_recent_drugs: PropertyValueChanger = None, ind_property_restrictions: list = None,
             disqualifying_properties: list = None, target_group: any = 'Everyone', trigger_condition_list: list = None,
             triggered_campaign_delay: int = 0, listening_duration: int = -1,
             check_eligibility_at_trigger: bool = False):
    """
    Add an MSAT (mass screening and treatment) drug intervention to your
    campaign. See :py:func:`add_drug_campaign` for more information about each
    argument. 

    Returns:
        None
    """

    if not start_days:
        start_days = [1]
    if drug_configs is None:
        raise Exception("You have to pass in drug_configs (list of drug configurations) that can be generated with "
                        "malaria.interventions.malaria_drugs import drug_configs_from_code.\n")
    if disqualifying_properties is None:
        disqualifying_properties = []

    event_config = drug_configs
    if receiving_drugs_event:
        event_config.append(receiving_drugs_event)
    if expire_recent_drugs:
        event_config.append(expire_recent_drugs)

    if treatment_delay == 0:
        msat_cfg = event_config
    else:
        msat_cfg = [DelayedIntervention(
            campaign,
            Delay_Dict={ "Delay_Period_Constant":treatment_delay },
            Configs=event_config)]

    # MSAT controlled by MalariaDiagnostic campaign event rather than New_Diagnostic_Sensitivity
    if trigger_condition_list:
        add_diagnostic_survey(campaign, coverage=coverage, repetitions=repetitions,
                              tsteps_btwn_repetitions=tsteps_btwn_repetitions,
                              target=target_group, start_day=start_days[0],
                              diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                              measurement_sensitivity=measurement_sensitivity,
                              node_ids=node_ids, positive_diagnosis_configs=msat_cfg,
                              ind_property_restrictions=ind_property_restrictions,
                              disqualifying_properties=disqualifying_properties,
                              trigger_condition_list=trigger_condition_list,
                              listening_duration=listening_duration, triggered_campaign_delay=triggered_campaign_delay,
                              check_eligibility_at_trigger=check_eligibility_at_trigger,
                              expire_recent_drugs=expire_recent_drugs)
    else:
        for start_day in start_days:
            add_diagnostic_survey(campaign, coverage=coverage, repetitions=repetitions,
                                  tsteps_btwn_repetitions=tsteps_btwn_repetitions,
                                  target=target_group, start_day=start_day,
                                  diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                                  measurement_sensitivity=measurement_sensitivity,
                                  node_ids=node_ids, positive_diagnosis_configs=msat_cfg,
                                  listening_duration=listening_duration,
                                  ind_property_restrictions=ind_property_restrictions,
                                  disqualifying_properties=disqualifying_properties,
                                  expire_recent_drugs=expire_recent_drugs)


def add_fMDA(
        campaign,
        start_days: list = None,
        trigger_coverage: float = 1,
        coverage: float = 1,
        drug_configs: list = None,
        receiving_drugs_event: BroadcastEvent = None,
        repetitions: int = 1,
        tsteps_btwn_repetitions: int = 365,
        treatment_delay: int = 0,
        diagnostic_type: str = 'BLOOD_SMEAR_PARASITES',
        diagnostic_threshold: float = 40,
        measurement_sensitivity: float = 0.1,
        fmda_radius: int = 0, node_selection_type: str = 'DISTANCE_ONLY', node_ids: list = None,
        expire_recent_drugs: PropertyValueChanger = None,
        ind_property_restrictions: list = None,
        disqualifying_properties: list = None, target_group: any = 'Everyone', trigger_condition_list: list = None,
        listening_duration: int = -1, triggered_campaign_delay: int = 0,
        check_eligibility_at_trigger: bool = False):
    """
    Add an fMDA (focal mass drug administration) drug intervention to your
    campaign. See :py:func:`add_drug_campaign` for more information about each
    argument.

    Returns:
        None
    """

    if not start_days:
        start_days = [1]
    if drug_configs is None:
        raise Exception("You have to pass in drug_configs (list of drug configurations) that can be generated with \n"
                        "malaria.interventions.malaria_drugs import drug_configs_from_code.\n")

    # rewritten to give out a unique trigger for the fmda
    fmda_trigger_tether = "Give_Drugs_fMDA_{}".format(random.randint(1, 10000))
    fmda_trigger_event = BroadcastEvent(campaign, Event_Trigger="Give_Drugs_fMDA")
    fmda_setup = [fmda_cfg(campaign, fmda_radius, node_selection_type, event_trigger=fmda_trigger_tether),
                  fmda_trigger_event]

    interventions = drug_configs
    if receiving_drugs_event:
        interventions.append(receiving_drugs_event)
    if expire_recent_drugs:
        interventions.append(expire_recent_drugs)

    if treatment_delay > 0:
        fmda_setup = [DelayedIntervention(
            campaign,
            Delay_Dict={"Delay_Period_Constant": treatment_delay},
            Configs=fmda_setup)]

    if trigger_condition_list:
        add_diagnostic_survey(campaign, coverage=trigger_coverage, repetitions=repetitions,
                              tsteps_btwn_repetitions=tsteps_btwn_repetitions,
                              target=target_group, start_day=start_days[0] + 1,
                              diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                              measurement_sensitivity=measurement_sensitivity,
                              node_ids=node_ids, positive_diagnosis_configs=fmda_setup,
                              ind_property_restrictions=ind_property_restrictions,
                              trigger_condition_list=trigger_condition_list,
                              listening_duration=listening_duration, triggered_campaign_delay=triggered_campaign_delay,
                              check_eligibility_at_trigger=check_eligibility_at_trigger,
                              expire_recent_drugs=expire_recent_drugs)

        fmda_distribute_drugs = TriggeredCampaignEvent(
            campaign,
            Event_Name="Distribute fMDA",
            Start_Day=start_days[0],
            Node_Ids=node_ids,
            Demographic_Coverage=coverage,
            Blackout_Event_Trigger="fMDA_Blackout_Event_Trigger",
            Blackout_Period=1,
            Blackout_On_First_Occurrence=1,
            Target_Residents_Only=1,
            Property_Restrictions=ind_property_restrictions,
            Disqualifying_Properties=disqualifying_properties,
            Duration=listening_duration,
            Triggers=[fmda_trigger_tether],
            Intervention_List=interventions)

        campaign.add(fmda_distribute_drugs)

    else:
        for start_day in start_days:
            # separate event for each repetition, otherwise RCD and fMDA can get entangled.
            for rep in range(repetitions):
                add_diagnostic_survey(campaign, coverage=trigger_coverage, repetitions=1,
                                      tsteps_btwn_repetitions=tsteps_btwn_repetitions,
                                      target=target_group, start_day=start_day + 1 + tsteps_btwn_repetitions * rep,
                                      diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                                      measurement_sensitivity=measurement_sensitivity,
                                      node_ids=node_ids, positive_diagnosis_configs=fmda_setup,
                                      ind_property_restrictions=ind_property_restrictions,
                                      disqualifying_properties=disqualifying_properties,
                                      expire_recent_drugs=expire_recent_drugs)

        fmda_distribute_drugs = TriggeredCampaignEvent(
            campaign,
            Event_Name="Distribute fMDA (2)",
            Start_Day=start_days[0],
            Node_Ids=node_ids,
            Demographic_Coverage=coverage,
            Blackout_Event_Trigger="fMDA_Blackout_Event_Trigger",
            Blackout_Period=1,
            Blackout_On_First_Occurrence=1,
            Target_Residents_Only=1,
            Property_Restrictions=ind_property_restrictions,
            Disqualifying_Properties=disqualifying_properties,
            Triggers=[fmda_trigger_tether],
            Intervention_List=interventions)

        campaign.add(fmda_distribute_drugs)


def add_rfMSAT(campaign, start_day: int = 0, coverage: float = 1, drug_configs: list = None,
               receiving_drugs_event: BroadcastEvent = None, listening_duration: int = -1, treatment_delay: int = 0,
               trigger_coverage: float = 1, diagnostic_type: str = 'BLOOD_SMEAR_PARASITES',
               diagnostic_threshold: float = 40,
               measurement_sensitivity: float = 0.1,
               fmda_radius: int = 0, node_selection_type: str = 'DISTANCE_ONLY', snowballs: int = 0,
               node_ids: list = None,
               expire_recent_drugs: PropertyValueChanger = None,
               ind_property_restrictions: list = None, disqualifying_properties: list = None):
    """
    Add a rfMSAT (reactive focal mass screening and treatment) drug intervention to your
    campaign. See :py:func:`add_drug_campaign` for more information about each
    argument. 

    Returns:
        None
    """

    if drug_configs is None:
        raise Exception("You have to pass in drug_configs (list of drug configurations) that can be generated with "
                        "malaria.interventions.malaria_drugs import drug_configs_from_code.\n")

    if disqualifying_properties is None:
        disqualifying_properties = []

    fmda_setup = fmda_cfg(campaign, fmda_radius, node_selection_type)  # default trigger used
    snowball_setup = [deepcopy(fmda_setup) for x in range(snowballs + 1)]
    snowball_trigger = 'Diagnostic_Survey_'
    snowball_setup[0].Event_Trigger = snowball_trigger + "0"

    rcd_event = TriggeredCampaignEvent(
        campaign,
        Event_Name="Trigger RCD MSAT",
        Start_Day=start_day,
        Node_Ids=node_ids,
        Demographic_Coverage=trigger_coverage,
        Duration=listening_duration,
        Triggers=["ReceivedTreatment"],
        Intervention_List=[DelayedIntervention(
            campaign,
            Delay_Dict={"Delay_Period_Constant": treatment_delay},
            Configs=[snowball_setup[0]])]
    )

    campaign.add(rcd_event)

    event_config = drug_configs
    if receiving_drugs_event:
        event_config.append(receiving_drugs_event)
    if expire_recent_drugs:
        event_config.append(expire_recent_drugs)

    add_diagnostic_survey(campaign, coverage=coverage, start_day=start_day,
                          diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                          measurement_sensitivity=measurement_sensitivity,
                          node_ids=node_ids,
                          trigger_condition_list=[snowball_setup[0].Event_Trigger],
                          event_name='Reactive MSAT level 0',
                          positive_diagnosis_configs=event_config,
                          listening_duration=listening_duration,
                          ind_property_restrictions=ind_property_restrictions,
                          disqualifying_properties=disqualifying_properties, expire_recent_drugs=expire_recent_drugs)

    for snowball in range(snowballs):
        snowball_setup[snowball + 1].Event_Trigger = snowball_trigger + str(snowball + 1)
        event_config = [snowball_setup[snowball + 1], receiving_drugs_event] + drug_configs
        curr_trigger = snowball_trigger + str(snowball)
        add_diagnostic_survey(campaign, coverage=coverage, start_day=start_day,
                              diagnostic_type=diagnostic_type, diagnostic_threshold=diagnostic_threshold,
                              measurement_sensitivity=measurement_sensitivity,
                              node_ids=node_ids,
                              trigger_condition_list=[curr_trigger],
                              event_name='Snowball level ' + str(snowball),
                              positive_diagnosis_configs=event_config,
                              listening_duration=listening_duration,
                              ind_property_restrictions=ind_property_restrictions,
                              disqualifying_properties=disqualifying_properties,
                              expire_recent_drugs=expire_recent_drugs)


def add_rfMDA(campaign, start_day: int = 0, coverage: float = 1, drug_configs: list = None,
              receiving_drugs_event: BroadcastEvent = None, listening_duration: int = -1, treatment_delay: int = 0,
              trigger_coverage: float = 1, fmda_radius: int = 0, node_selection_type: str = 'DISTANCE_ONLY',
              node_ids: list = None, expire_recent_drugs: PropertyValueChanger = None,
              ind_property_restrictions: list = None, disqualifying_properties: list = None):
    """
    Add an rfMDA (reactive focal mass drug administration) drug intervention
    to your campaign. See :py:func:`add_drug_campaign` for more information
    about each argument.

    Returns:
        None
    """

    if drug_configs is None:
        raise Exception("You have to pass in drug_configs (list of drug configurations) that can be generated with "
                        "malaria.interventions.malaria_drugs import drug_configs_from_code.\n")
    interventions = drug_configs
    if receiving_drugs_event:
        interventions.append(receiving_drugs_event)

    if disqualifying_properties is None:
        disqualifying_properties = []

    rfmda_trigger = "Give_Drugs_rfMDA"
    fmda_setup = fmda_cfg(campaign, fmda_radius, node_selection_type, event_trigger=rfmda_trigger)

    rcd_event = TriggeredCampaignEvent(
        campaign,
        Event_Name="Trigger RCD MDA",
        Start_Day=start_day,
        Node_Ids=node_ids,
        Demographic_Coverage=trigger_coverage,
        Property_Restrictions=ind_property_restrictions,
        Triggers=["ReceivedTreatment"],
        Duration=listening_duration,
        Intervention_List=[
            DelayedIntervention(
                campaign,
                Delay_Dict={"Delay_Period_Constant": treatment_delay},
                Configs=[fmda_setup])
        ]
    )

    if expire_recent_drugs:
        interventions = interventions + [expire_recent_drugs]

    # distributes drugs to individuals broadcasting "Give_Drugs_rfMDA"
    # who is broadcasting is determined by other events
    # if campaign drugs change (less effective, different cocktail), then this event should have an expiration date.
    fmda_distribute_drugs = TriggeredCampaignEvent(
        campaign,
        Event_Name="Distribute fMDA",
        Start_Day=start_day,
        Node_Ids=node_ids,
        Demographic_Coverage=coverage,
        Property_Restrictions=ind_property_restrictions,
        Disqualifying_Properties=disqualifying_properties,
        Duration=listening_duration,
        Triggers=[rfmda_trigger],
        Intervention_List=interventions)

    campaign.add(rcd_event)
    campaign.add(fmda_distribute_drugs)


def fmda_cfg(campaign, fmda_type: any = 0, node_selection_type: str = 'DISTANCE_ONLY', event_trigger: str = 'Give_Drugs'):
    """
    Create an fMDA (focal mass drug administration) configuration.

    Args:
        fmda_type: The setting for **Max_Distance_To_Other_Nodes_Km** in
          :doc:`emod-malaria:parameter-campaign-individual-broadcasteventtoothernodes`.
        node_selection_type: The setting for **Node_Selection_Type** in
          :doc:`emod-malaria:parameter-campaign-individual-broadcasteventtoothernodes`.
        event_trigger: The setting for **Event_Trigger** in
          :doc:`emod-malaria:parameter-campaign-individual-broadcasteventtoothernodes`.

    Returns:
        Configured :doc:`emod-malaria:parameter-campaign-individual-broadcasteventtoothernodes`
        intervention.
    """
    if isinstance(fmda_type, str):
        fmda_type = 0

    return BroadcastEventToOtherNodes(
        campaign,
        Event_Trigger=event_trigger,
        Include_My_Node=1,
        Node_Selection_Type=node_selection_type,
        Max_Distance_To_Other_Nodes_Km=fmda_type)
