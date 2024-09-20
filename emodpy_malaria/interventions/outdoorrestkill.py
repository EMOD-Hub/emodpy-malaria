from emodpy_malaria.interventions.common import *


def add_outdoorrestkill(campaign,
                        start_day: int = 1,
                        node_ids: list = None,
                        insecticide: str = None,
                        killing_initial_effect: float = 1,
                        killing_box_duration: int = -1,
                        killing_decay_time_constant: float = 0
                        ):
    """
        Adds a node-targeted OutdoorRestKill intervention to the campaign

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: the day on which to distribute the intervention
        insecticide :The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        killing_initial_effect: **Initial_Effect** in the *Killing_Config**
        killing_box_duration: Length in days before the **Initial_Effect** starts to decay, -1 indicates forever.
        killing_decay_time_constant: The rate of decay of the *Initial_Effect**
        node_ids: List of nodes to which to distribute the intervention. None or empty list implies "all nodes".

    Returns:
        configured campaign object
    """
    schema_path = campaign.schema_path
    intervention = s2c.get_class_with_defaults("OutdoorRestKill", schema_path)
    intervention.Insecticide_Name = insecticide if insecticide else ""
    intervention.Killing_Config = utils.get_waning_from_params(schema_path,
                                                               initial=killing_initial_effect,
                                                               box_duration=killing_box_duration,
                                                               decay_time_constant=killing_decay_time_constant)

    add_campaign_event(campaign,
                       start_day=start_day,
                       node_ids=node_ids,
                       node_intervention=intervention)

    return campaign
