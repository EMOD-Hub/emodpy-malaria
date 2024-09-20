from emod_api import schema_to_class as s2c


def Ivermectin(schema_path_container,
               start_day=1,
               killing_initial_effect: float = 1,
               demographic_coverage: float = 1.0,
               target_num_individuals: int = None,
               killing_box_duration: int = 0,
               killing_exponential_decay_rate: float = 0
               ):
    """
        Create a scheduled Ivermectin CampaignEvent which can then be added to a campaign.

    Args:
        schema_path_container: schema path container? a way to pass the schema to the python script
        start_day: day to give out this intervention
        demographic_coverage: probability of choosing an individual, is ignored if "target_num_individuals" is set
        target_num_individuals: number of individuals to receive ivermectin, demographic_coverage will be ignored
            if this is set
        killing_initial_effect: initial parasite killing effect
        killing_box_duration: box duration for killing effect
        killing_exponential_decay_rate: rate at which killing effect decays per day. Use 0 for box duration only.

    Returns:
        CampaignEvent which then can be added to the campaign file

    """

    schema_path = schema_path_container.schema_path

    # First, get the objects and configure
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    intervention = s2c.get_class_with_defaults("Ivermectin", schema_path)
    killing = s2c.get_class_with_defaults("WaningEffectBoxExponential", schema_path)

    # configuring the main event
    event.Start_Day = start_day

    # configuring the coordinator
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    if target_num_individuals is not None:
        coordinator.Target_Num_Individuals = target_num_individuals
    else:
        coordinator.Demographic_Coverage = demographic_coverage

    # configuring the Killing_Config
    if killing_exponential_decay_rate > 0:
        killing_duration_exponential = 1 / killing_exponential_decay_rate
        killing.Decay_Time_Constant = killing_duration_exponential
    else:
        killing.Decay_Time_Constant = 0
    killing.Box_Duration = killing_box_duration
    killing.Initial_Effect = killing_initial_effect

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing

    return event
