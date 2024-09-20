from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

schema_path = None
iv_name = "IRSHousingModification"


# dupe_policy = "Replace" # or "Add" or "Abort" -- from covid branch
# Note that duration (what we call waning profile) needs to be configurable, but in an intuitive way

def add_irs_housing_modification(
        campaign,
        start_day: int = 1,
        coverage: float = 1,
        killing_initial_effect: float = 1,
        killing_box_duration_days: int = 0,
        killing_exponential_decay_constant_days: int = 90,
        repelling_initial_effect: float = 0,
        repelling_box_duration_days: int = 0,
        repelling_exponential_decay_constant_days: int = 90,
        insecticide: str = None,
        node_ids: list = None):
    """
        Adds IRSHousingModification intervention to the campaign. The IRSHousingModification intervention class
        includes Indoor Residual Spraying (IRS) in the simulation. IRS is another key vector control tool in which
        insecticide is sprayed on the interior walls of a house so that mosquitoes resting on the walls after
        consuming a blood meal will die. IRS can also have a repellent effect. Because this class is distributed
        to individuals, it can target subgroups of the population. To target all individuals in a node, use
        IndoorSpaceSpraying. Do not use IRSHousingModification and IndoorSpaceSpraying together.

    Args:
        campaign: A campaign builder that also contains schema_path parameters
        start_day: The day on which the intervention is distributed
        coverage: The fraction of individuals in the target demographic that will receive this intervention
        killing_initial_effect: Initial strength of the Killing effect. The effect decays over time.
        killing_box_duration_days: Box duration of effect in days before the decay of Killing Initial Effect.
        killing_exponential_decay_constant_days: The exponential decay length, in days of the Killing Initial Effect.
        repelling_initial_effect: Initial strength of the Killing effect. The effect decays over time.
        repelling_box_duration_days: Box duration of effect in days before the decay of Repelling Initial Effect.
        repelling_exponential_decay_constant_days: The exponential decay length, in days of the Repelling Initial Effect.
        insecticide:The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        node_ids: A list of node ids to which this intervention will be distributed. None or [] distributes
            intervention to all nodes.

    Returns:
        Nothing
    """
    schema_path = campaign.schema_path
    # First, get the objects
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    coordinator.Demographic_Coverage = coverage
    if coordinator is None:
        print("s2c.get_class_with_defaults returned None. Maybe no schema.json was provided.")
        return ""

    intervention = s2c.get_class_with_defaults("IRSHousingModification", schema_path)

    # fixme IRS with repelling is rarely modeled, so this could probably be removed.
    repelling = utils.get_waning_from_params(schema_path=schema_path,
                                             initial=repelling_initial_effect,
                                             box_duration=repelling_box_duration_days,
                                             decay_rate=1. / repelling_exponential_decay_constant_days)

    killing = utils.get_waning_from_params(schema_path=schema_path,
                                           initial=killing_initial_effect,
                                           box_duration=killing_box_duration_days,
                                           decay_rate=1. / killing_exponential_decay_constant_days)

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    intervention.Killing_Config = killing
    intervention.Repelling_Config = repelling
    event.Start_Day = float(start_day)

    intervention.Intervention_Name = iv_name
    if insecticide is None:
        intervention.pop("Insecticide_Name")  # this is not permanent
    else:
        intervention.Insecticide_Name = insecticide
    # intervention.Duplicate_Policy = dupe_policy

    event.Nodeset_Config = utils.do_nodes(schema_path, node_ids)
    campaign.add(event)


def new_intervention_as_file(campaign, start_day, filename=None):
    add_irs_housing_modification(campaign=campaign, start_day=start_day)
    if filename is None:
        filename = "IRSHousingModification.json"
    campaign.save(filename)
    return filename
