from emod_api import schema_to_class as s2c
from emod_api.interventions.common import utils


def add_community_health_worker(campaign,
                                start_day: int = 1,
                                trigger_condition_list: list = None,
                                demographic_coverage: float = 1.0,
                                node_ids: list = None,
                                ind_property_restrictions: list = None,
                                target_age_min: int = 0,
                                target_age_max: int = 1000,
                                target_gender: str = "All",
                                initial_amount: int = 6,
                                amount_in_shipment: int = 2147480000,
                                days_between_shipments: float = 7,
                                duration: float = 3.40282e+38,
                                intervention_config: any = None,
                                max_distributed_per_day: int = 2147480000,
                                max_stock: int = 2147480000,
                                waiting_period: int = 0):
    """
        Sets up a CommunityHealthWorkerEventCoordinator with the passed in intervention

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day the intervention is given out.
        trigger_condition_list: The list of individual events that are of interest to the community health worker (CHW).
            If one of these events occurs, the individual or node is put into a queue to receive the CHW's intervention.
            The CHW processes the queue when the event coordinator is updated.
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        initial_amount: Each instance will receive this constant/fixed value. Uses **Initial_Amount_Constant**
        amount_in_shipment: The number of interventions (such as vaccine doses) that a health worker or clinic receives
            in a shipment.
        days_between_shipments: The number of days to wait before a clinic or health worker receives a new shipment
            of interventions (such as vaccine doses)
        duration: The number of days for an event coordinator to be active before it expires. -1 means it never expires.
        intervention_config: A configured intervention to be distributed by the coordinator
        max_distributed_per_day: The maximum number of interventions (such as vaccine doses) that can be distributed
            by health workers or clinics in a given day
        max_stock: The maximum number of interventions (such as vaccine doses) that can be stored by a health worker
            or clinic
        waiting_period: The number of days a person or node can be in the queue waiting to get the intervention from
            the community health worker (CHW)

    Returns:
        Nothing
    """
    if not trigger_condition_list or not intervention_config:
        raise ValueError("Please define trigger_condition_list and intervention_config.\n")

    schema_path = campaign.schema_path

    # configuring the intervention itself
    coordinator = s2c.get_class_with_defaults("CommunityHealthWorkerEventCoordinator", schema_path)
    coordinator.Amount_In_Shipment = amount_in_shipment
    coordinator.Days_Between_Shipments = days_between_shipments
    coordinator.Demographic_Coverage = demographic_coverage
    coordinator.Duration = duration
    coordinator.Initial_Amount_Constant = initial_amount
    coordinator.Initial_Amount_Distribution = "CONSTANT_DISTRIBUTION"
    coordinator.Intervention_Config = intervention_config
    coordinator.Max_Distributed_Per_Day = max_distributed_per_day
    coordinator.Max_Stock = max_stock
    coordinator.Property_Restrictions_Within_Node = ind_property_restrictions if ind_property_restrictions else []
    coordinator.Trigger_Condition_List = [campaign.get_recv_trigger(trigger, old=True) for trigger in trigger_condition_list]
    coordinator.Waiting_Period = waiting_period

    if target_age_min > 0 or target_age_max < 1000:
        coordinator.Target_Age_Min = target_age_min
        coordinator.Target_Age_Max = target_age_max
    if target_gender != "All":
        coordinator.Target_Gender = target_gender
        coordinator.Target_Demographic = "ExplicitAgeRangesAndGender"

    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    event.Start_Day = start_day
    event.Nodeset_Config = utils.do_nodes(schema_path, node_ids)
    event.Event_Coordinator_Config = coordinator

    campaign.add(event)
