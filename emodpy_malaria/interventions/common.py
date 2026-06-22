from emod_api import schema_to_class as s2c
from emod_api.interventions import common, utils
from emodpy_malaria.utils import MAX_AGE_YEARS


def _malaria_diagnostic(
        campaign,
        diagnostic_type: str = "BLOOD_SMEAR_PARASITES",
        measurement_sensitivity: float = 0,
        detection_threshold: float = 0):
    """
    Configures individual-targeted **MalariaDiagnostic** intervention

    Args:
        campaign (emodpy.campaign.emod_campaign.EMODCampaign): The `emod_api.campaign` object to which the intervention
            will be added.
        diagnostic_type (str): The setting for **Diagnostic_Type** in
            [MalariaDiagnostic](https://emod.idmod.org/emodpy-malaria/emod/parameter-campaign-individual-malariadiagnostic/).
            In addition to the accepted values listed there, you may also set
            TRUE_INFECTION_STATUS, which calls
            [StandardDiagnostic](https://emod.idmod.org/emodpy-malaria/emod/parameter-campaign-individual-standarddiagnostic/)
            instead.
        measurement_sensitivity (float): The setting for **Measurement_Sensitivity**
            in [MalariaDiagnostic](https://emod.idmod.org/emodpy-malaria/emod/parameter-campaign-individual-malariadiagnostic/).
        detection_threshold (float): The setting for **Detection_Threshold** in
            [MalariaDiagnostic](https://emod.idmod.org/emodpy-malaria/emod/parameter-campaign-individual-malariadiagnostic/).

    Returns:
    Configured individual-targeted **MalariaDiagnostic** intervention
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
                                       target_age_max: float = MAX_AGE_YEARS,
                                       target_gender: str = "All",
                                       target_residents_only: bool = False,
                                       blackout_event_trigger: str = None,
                                       blackout_period: float = 0,
                                       blackout_on_first_occurrence: bool = 0,
                                       individual_intervention: any = None):
    """
    Create and add campaign event that responds to a trigger after an optional delay with an intervention.

    Args:
        campaign (emodpy.campaign.emod_campaign.EMODCampaign): campaign object to which the intervention will be added, and schema_path container
        start_day (int): The day the intervention is given out.
        trigger_condition_list (list): A list of the events that will trigger intervention distribution.
        listening_duration (int): The number of time steps that the distributed event will monitor for triggers.
            Default is -1, which is indefinitely.
        delay_period_constant (float): Optional. Delay, in days, before the intervention is given out after a trigger
            is received.
        demographic_coverage (float): This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        node_ids (list): List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions (int): The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions (int): The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        ind_property_restrictions (list): A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        disqualifying_properties (list): A list of IndividualProperty key:value pairs that cause an intervention to be aborted.
            Generally used to control the flow of health care access. For example, to prevent the same individual from
            accessing health care via two different routes at the same time.
        target_age_min (float): The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max (float): The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender (str): The gender targeted for an intervention: All, Male, or Female.
        target_residents_only (bool): When set to True, the intervention is only distributed to individuals that began
            the simulation in the node (i.e. those that claim the node as their residence)
        blackout_event_trigger (str): The event to broadcast if an intervention cannot be distributed due to the
            **Blackout_Period**.
        blackout_period (float): After the initial intervention distribution, the time, in days, to wait before distributing
            the intervention again. If it cannot distribute due to the blackout period, it will broadcast the
            user-defined **Blackout_Event_Trigger**.
        blackout_on_first_occurrence (bool): If set to true (1), individuals will enter the blackout period after the first
            occurrence of an event in the **Trigger_Condition_List**.
        individual_intervention (IndividualIntervention or list): Individual intervention or a list of individual interventions to be distributed
            by this event
    """
    if not trigger_condition_list:
        raise ValueError("Please define trigger_condition_list.\n")

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
                       target_age_max: float = MAX_AGE_YEARS,
                       target_gender: str = "All",
                       target_residents_only: bool = False,
                       individual_intervention: any = None,
                       node_intervention: any = None,
                       node_property_restrictions: list = None):
    """
    Adds a campaign event to the campaign with a passed in intervention.

    Args:
        campaign (emodpy.campaign.emod_campaign.EMODCampaign): campaign object to which the intervention will be added, and schema_path container
        start_day (int): The day the intervention is given out.
        demographic_coverage (float): This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        target_num_individuals (int): The exact number of people to select out of the targeted group. If this value is set,
            demographic_coverage parameter is ignored
        node_ids (list): List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions (int): The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions (int): The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        ind_property_restrictions (list): A list of dictionaries of IndividualProperties, which are required for the
            individual to receive the intervention. Sets the **Property_Restrictions_Within_Node**.
        target_age_min (float): The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max (float): The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender (str): The gender targeted for an intervention: All, Male, or Female.
        target_residents_only (bool): When set to True, the intervention is only distributed to individuals that began
            the simulation in the node (i.e. those that claim the node as their residence)
        individual_intervention (IndividualIntervention or list): Individual intervention or a list of individual interventions to be distributed
            by this event
        node_intervention (NodeIntervention or list): Node intervention or a list of node interventions to be distributed
            by this event
        node_property_restrictions (list): A list of dictionaries of NodeProperties, which are required for the node
            to receive the intervention. Sets the **Node_Property_Restrictions**
    """
    if individual_intervention and node_intervention:
        raise ValueError("You cannot define both individual_intervention and node_intervention, only one.\n")
    elif not individual_intervention and not node_intervention:
        raise ValueError("Please pass in either individual_intervention or node_intervention.\n")

    if individual_intervention:
        if node_property_restrictions:
            raise ValueError("node_property_restrictions are not available when using individual_intervention.\n")
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
        coordinator.Number_Repetitions = repetitions
        coordinator.Timesteps_Between_Repetitions = timesteps_between_repetitions
        coordinator.Node_Property_Restrictions = node_property_restrictions

        event.Event_Coordinator_Config = coordinator
        coordinator.Intervention_Config = intervention

        campaign.add(event)
