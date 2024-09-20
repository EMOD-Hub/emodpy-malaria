from emod_api import schema_to_class as s2c
from emod_api.interventions import utils

iv_name = "SpaceSpraying"


def SpaceSpraying(
        campaign,
        start_day: int = 1,
        spray_coverage: float = 1.0,
        killing_effect: float = 1,
        insecticide: str = None,
        box_duration: int = 0,
        decay_rate: float = 0,
        node_ids: list = None
):
    """
        Create a new SpaceSpraying scheduled campaign intervention.
        Note: for WaningEffect, Decay_Time_Constant = 1.0/decay_rate
        box_duration = 0 + decay_rate > 0 => WaningEffectExponential
        box_duration > 0 + decay_rate = 0 => WaningEffectBox/Constant (depending on duration)
        box_duration > 0 + decay_rate > 0 => WaningEffectBoxExponential

        Args:
        campaign:
        start_day: the day to distribute the SpaceSpraying intervention
        spray_coverage: how much of each node to cover (total portion killed = killing effect * coverage)
        killing_effect: portion of vectors killed by the intervention (Initial_Effect in WaningEffect)
        insecticide: insecticide, if used
        box_duration: Box_Duration of the WaningEffect
        decay_rate: decay_rate of the WaningEffect, gets set as Decay_Time_Constant = 1.0/decay_rate
        node_ids: list of node ids to which distribute the intervention

        Returns:
        The formatted intervention ready to be added to the campaign.

    """

    schema_path = campaign.schema_path
    # First, get the objects
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    event.Start_Day = float(start_day)
    event.Nodeset_Config = utils.do_nodes(schema_path, node_ids)

    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    if coordinator is None:
        print("s2c.get_class_with_defaults returned None. Maybe no schema.json was provided.")
        return ""
    coordinator.Node_Property_Restrictions = []
    coordinator.Property_Restrictions_Within_Node = []
    coordinator.Property_Restrictions = []

    intervention = s2c.get_class_with_defaults("SpaceSpraying", schema_path)
    intervention.Intervention_Name = iv_name
    if not insecticide:
        intervention.pop("Insecticide_Name")  # this is not permanent
    else:
        intervention.Insecticide_Name = insecticide
    intervention.Spray_Coverage = spray_coverage

    killing = utils.get_waning_from_params(schema_path, killing_effect, box_duration, decay_rate)

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing

    # intervention.Duplicate_Policy = dupe_policy
    return event


def new_intervention_as_file(campaign, start_day: int = 0, filename: str = None):
    """
    Creates a file with SpaceSpray intervention
    Args:
        campaign:
        start_day: the day to distribute the SpaceSpraying intervention
        filename: name of the filename created

    Returns:
    filename of the file created
    """

    campaign.add(SpaceSpraying(campaign, start_day), first=True)
    if filename is None:
        filename = "SpaceSpraying.json"
    campaign.save(filename)
    return filename
