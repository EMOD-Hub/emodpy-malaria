from emod_api.interventions.common import *
from emodpy_malaria.interventions.common import *
from emodpy_malaria.interventions.outbreak import add_campaign_event


def add_OutdoorRestKill(campaign,
                        start_day: int = 1,
                        insecticide_name: str = None,
                        killing_initial_effect: float = 1,
                        killing_box_duration: int = 365,
                        killing_exponential_decay_rate: float = 0,
                        node_ids: list = None):
    """
        Adds an OutdoorRestKill intervention to the campaign

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: the day on which to distribute the intervention
        insecticide_name: Name of the insecticide
        killing_initial_effect: **Initial_Effect** in the *Killing_Config**
        killing_box_duration: Length in days before the **Initial_Effect** starts to decay
        killing_exponential_decay_rate: The rate of decay of the *Initial_Effect**
        node_ids: List of nodes to which to distribute the intervention. None or empty list implies "all nodes".

    Returns:
        configured campaign object
    """
    schema_path = campaign.schema_path
    intervention = s2c.get_class_with_defaults("OutdoorRestKill", schema_path)
    intervention.Insecticide_Name = insecticide_name if insecticide_name else ""
    intervention.Killing_Config = utils.get_waning_from_params(schema_path, killing_initial_effect,
                                                               killing_box_duration,
                                                               killing_exponential_decay_rate)

    add_campaign_event(campaign=campaign, start_day=start_day, node_ids=node_ids, intervention=intervention)

    return campaign
