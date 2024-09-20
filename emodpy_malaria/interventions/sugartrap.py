from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

schema_path = None
iv_name = "SugarTrap"


# dupe_policy = "Replace" # or "Add" or "Abort" -- from covid branch
# Note that duration (what we call waning profile) needs to be configurable, but in an intuitive way


def SugarTrap(
        campaign,
        start_day: int = 0,
        killing_effect: float = 1,
        insecticide: str = None,
        box_duration: int = 100,
        decay_rate: float = 0,
        expiration_constant: int = 100,
        node_ids=None
):
    """
    Create a new SugarTrap scheduled campaign intervention.
    Note: for WaningEffect, Decay_Time_Constant = 1.0/decay_rate.
    box_duration = 0 + decay_rate > 0 => WaningEffectExponential
    box_duration > 0 + decay_rate = 0 => WaningEffectBox/Constant (depending on duration)
    box_duration > 0 + decay_rate > 0 => WaningEffectBoxExponential

    Args:
        campaign: campaign builder.
        start_day: the day to distribute the SpaceSpraying intervention
        killing_effect: portion of vectors killed by the intervention (Initial_Effect in WaningEffect)
        insecticide: insecticide, if used
        box_duration: Box_Duration of the WaningEffect
        decay_rate: decay_rate of the WaningEffect, gets set as Decay_Time_Constant = 1.0/decay_rate
        node_ids: list of node ids to which distribute the intervention
        expiration_constant: how long after distribution of intervention it gets discarded
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

    intervention = s2c.get_class_with_defaults("SugarTrap", schema_path)
    intervention.Intervention_Name = iv_name
    intervention.Expiration_Constant = expiration_constant
    if insecticide is None:
        intervention.pop("Insecticide_Name")  # this is not permanent
    else:
        intervention.Insecticide_Name = insecticide

    killing_config = utils.get_waning_from_params(schema_path, killing_effect, box_duration, decay_rate)  # constant

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing_config

    return event


def new_intervention_as_file(campaign, start_day: int = 0, filename: str = None):
    """
    Create new campaign file with a single event which distributes a SugarTrap 
    intervention mostly with defaults. Useful for sanity testing and first time users.
    Args:
        campaign: campaign builder.
        start_day: the day to distribute the SpaceSpraying intervention
        filename: name of the filename created

    Returns:
	Filename of the file created.
    """

    campaign.add(SugarTrap(campaign, start_day), first=True)
    if filename is None:
        filename = "SugarTrap.json"
    campaign.save(filename)
    return filename
