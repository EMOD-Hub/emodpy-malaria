
from typing import List
from emod_api import schema_to_class as s2c
from emod_api.interventions import common, utils


def _malaria_diagnostic(
        campaign,
        diagnostic_type: str = "BLOOD_SMEAR_PARASITES",
        measurement_sensitivity: float = 0,
        detection_threshold: float = 0):
    """
        Configures individual-targeted MalariaDiagnostic intervention

    Args:
        campaign: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention
            will be added.
        diagnostic_type: The setting for **Diagnostic_Type** in
            :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`.
            In addition to the accepted values listed there, you may also set
            TRUE_INFECTION_STATUS, which calls
            :doc:`emod-malaria:parameter-campaign-individual-standarddiagnostic`
            instead.
        measurement_sensitivity: The setting for **Measurement_Sensitivity**
            in :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`.
        detection_threshold: The setting for **Detection_Threshold** in
            :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`.

    Returns:
      Configured individual-targeted MalariaDiagnostic intervention
    """
    # Shares lots of code with Standard. Not obvious if code minimization maximizes readability.
    import emod_api.interventions.common as emodapi_com
    schema_path = campaign.schema_path
    # First, get the objects

    if diagnostic_type == "TRUE_INFECTION_STATUS":
        if measurement_sensitivity or detection_threshold:
            raise ValueError("MalariaDiagnostic invoked with 'TRUE_INFECTION_STATUS' and values "
                             "of either measurement_sensitivity or detection_threshold params (or both). "
                             "Those parameters are not used for TRUE_INFECTION_STATUS.")
        intervention = emodapi_com.StandardDiagnostic(campaign)
    else:
        intervention = s2c.get_class_with_defaults("MalariaDiagnostic", schema_path)
        intervention.Measurement_Sensitivity = measurement_sensitivity
        intervention.Detection_Threshold = detection_threshold
        intervention.Diagnostic_Type = diagnostic_type

    return intervention


def add_triggered_campaign_delay_event(campaign,
                                       start_day: int = 1,
                                       trigger_condition_list: list = None,
                                       listening_duration: int = -1,
                                       delay_period_constant: float = 0,
                                       demographic_coverage: float = 1.0,
                                       node_ids: list = None,
                                       repetitions: int = 1,
                                       timesteps_between_repetitions: int = 365,
                                       ind_property_restrictions: list = None,
                                       disqualifying_properties: list = None,
                                       target_age_min: float = 0,
                                       target_age_max: float = 125,
                                       target_gender: str = "All",
                                       target_residents_only: bool = False,
                                       blackout_event_trigger: str = None,
                                       blackout_period: float = 0,
                                       blackout_on_first_occurrence: bool = 0,
                                       individual_intervention: any = None):
    """
        Create and add campaign event that responds to a trigger after an optional delay with an intervention.

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day the intervention is given out.
        trigger_condition_list: A list of the events that will trigger intervention distribution.
        listening_duration: The number of time steps that the distributed event will monitor for triggers.
            Default is -1, which is indefinitely.
        delay_period_constant: Optional. Delay, in days, before the intervention is given out after a trigger
            is received.
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        disqualifying_properties: A list of IndividualProperty key:value pairs that cause an intervention to be aborted.
            Generally used to control the flow of health care access. For example, to prevent the same individual from
            accessing health care via two different routes at the same time.
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        target_residents_only: When set to True, the intervention is only distributed to individuals that began
            the simulation in the node (i.e. those that claim the node as their residence)
        blackout_event_trigger: The event to broadcast if an intervention cannot be distributed due to the
            **Blackout_Period**.
        blackout_period: After the initial intervention distribution, the time, in days, to wait before distributing
            the intervention again. If it cannot distribute due to the blackout period, it will broadcast the
            user-defined **Blackout_Event_Trigger**.
        blackout_on_first_occurrence: If set to true (1), individuals will enter the blackout period after the first
            occurrence of an event in the **Trigger_Condition_List***.
        individual_intervention: Individual intervention or a list of individual interventions to be distributed
            by this event

    Returns:
        Nothing

    """
    if not trigger_condition_list:
        raise ValueError(f"Please define trigger_condition_list.\n")

    event = common.TriggeredCampaignEvent(camp=campaign,
                                          Start_Day=start_day,
                                          Event_Name="TriggeredEvent",
                                          Triggers=trigger_condition_list,
                                          Intervention_List=individual_intervention if isinstance(
                                              individual_intervention, list) else [individual_intervention],
                                          Node_Ids=node_ids,
                                          Timesteps_Between_Repetitions=timesteps_between_repetitions,
                                          Number_Repetitions=repetitions,
                                          Target_Gender=target_gender,
                                          Target_Age_Max=target_age_max,
                                          Target_Age_Min=target_age_min,
                                          Target_Residents_Only=1 if target_residents_only else 0,
                                          Duration=listening_duration,
                                          Demographic_Coverage=demographic_coverage,
                                          Delay=delay_period_constant,
                                          Disqualifying_Properties=disqualifying_properties,
                                          Blackout_Period=blackout_period,
                                          Blackout_Event_Trigger=blackout_event_trigger,
                                          Blackout_On_First_Occurrence=blackout_on_first_occurrence
                                          )
    triggered_event = event.Event_Coordinator_Config.Intervention_Config
    individual_restrictions = utils._convert_prs(ind_property_restrictions)
    if len(individual_restrictions) > 0 and type(individual_restrictions[0]) is dict:
        triggered_event["Property_Restrictions_Within_Node"] = individual_restrictions
    else:
        triggered_event.Property_Restrictions = individual_restrictions
    campaign.add(event)


def add_campaign_event(campaign,
                       start_day: int = 1,
                       demographic_coverage: float = 1.0,
                       target_num_individuals: int = None,
                       node_ids: list = None,
                       repetitions: int = 1,
                       timesteps_between_repetitions: int = 365,
                       ind_property_restrictions: list = None,
                       target_age_min: float = 0,
                       target_age_max: float = 125,
                       target_gender: str = "All",
                       target_residents_only: bool = False,
                       individual_intervention: any = None,
                       node_intervention: any = None):
    """
        Adds a campaign event to the campaign with a passed in intervention.

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day the intervention is given out.
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        target_num_individuals: The exact number of people to select out of the targeted group. If this value is set,
            demographic_coverage parameter is ignored
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        target_residents_only: When set to True, the intervention is only distributed to individuals that began
            the simulation in the node (i.e. those that claim the node as their residence)
        individual_intervention: Individual intervention or a list of individual interventions to be distributed
            by this event
        node_intervention: Node intervention or a list of node interventions to be distributed
            by this event
    Returns:
        Nothing
    """
    if individual_intervention and node_intervention:
        raise ValueError(f"You cannot define both individual_intervention and node_intervention, only one.\n")
    elif not individual_intervention and not node_intervention:
        raise ValueError(f"Please pass in either individual_intervention or node_intervention.\n")

    if individual_intervention:
        event = common.ScheduledCampaignEvent(camp=campaign,
                                              Start_Day=start_day,
                                              Node_Ids=node_ids,
                                              Number_Repetitions=repetitions,
                                              Timesteps_Between_Repetitions=timesteps_between_repetitions,
                                              Event_Name="ScheduledCampaignEvent",
                                              Demographic_Coverage=demographic_coverage,
                                              Property_Restrictions=ind_property_restrictions,
                                              Target_Age_Min=target_age_min,
                                              Target_Age_Max=target_age_max,
                                              Target_Gender=target_gender,
                                              Target_Residents_Only=target_residents_only,
                                              Intervention_List=individual_intervention if isinstance(
                                                  individual_intervention,
                                                  list) else [
                                                  individual_intervention])
        event.Event_Coordinator_Config.Target_Num_Individuals = target_num_individuals
        campaign.add(event)
    else:
        schema_path = campaign.schema_path
        event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
        event.Start_Day = start_day
        event.Nodeset_Config = utils.do_nodes(schema_path, node_ids)
        if isinstance(node_intervention, list):
            multi_intervention_distributor = s2c.get_class_with_defaults("MultiNodeInterventionDistributor",
                                                                         schema_path)
            multi_intervention_distributor.Node_Intervention_List = node_intervention
            intervention = multi_intervention_distributor
        else:
            intervention = node_intervention

        # configuring the coordinator
        coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
        if target_num_individuals is not None:
            coordinator.Target_Num_Individuals = target_num_individuals
        else:
            coordinator.Demographic_Coverage = demographic_coverage
        coordinator.Number_Repetitions = repetitions
        coordinator.Timesteps_Between_Repetitions = timesteps_between_repetitions
        coordinator.Property_Restrictions_Within_Node = ind_property_restrictions if ind_property_restrictions else []
        coordinator.Property_Restrictions = []  # not using; Property_Restrictions_Within_Node are more flexible

        if target_age_min > 0 or target_age_max < 125:
            coordinator.Target_Age_Min = target_age_min
            coordinator.Target_Age_Max = target_age_max
        if target_gender != "All":
            coordinator.Target_Gender = target_gender
            coordinator.Target_Demographic = "ExplicitAgeRangesAndGender"

        event.Event_Coordinator_Config = coordinator
        coordinator.Intervention_Config = intervention

        campaign.add(event)
