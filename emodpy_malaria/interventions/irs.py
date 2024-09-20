
from emod_api.interventions.common import TriggeredCampaignEvent, ScheduledCampaignEvent
from emod_api import schema_to_class as s2c
import emod_api.interventions.utils as utils

default_name = "IRSHousingModification"


def add_scheduled_irs_housing_modification(
        campaign,
        start_day: int = 1,
        demographic_coverage: float = 1,
        node_ids: list = None,
        killing_initial_effect: float = 1,
        killing_box_duration: int = 0,
        killing_decay_time_constant: int = 90,
        repelling_initial_effect: float = 0,
        repelling_box_duration: int = 0,
        repelling_decay_time_constant: int = 90,
        insecticide: str = "",
        intervention_name: str = default_name
):
    """
        Adds scheduled IRSHousingModification intervention to the campaign. The IRSHousingModification intervention class
        includes Indoor Residual Spraying (IRS) in the simulation. IRS is another key vector control tool in which
        insecticide is sprayed on the interior walls of a house so that mosquitoes resting on the walls after
        consuming a blood meal will die. IRS can also have a repellent effect. Because this class is distributed
        to individuals, it can target subgroups of the population. To target all individuals in a node, use
        IndoorSpaceSpraying. Do not use IRSHousingModification and IndoorSpaceSpraying together.

    Args:
        campaign: A campaign builder that also contains schema_path parameters
        start_day: The day on which the intervention is distributed
        demographic_coverage: The fraction of individuals in the target demographic that will receive this intervention
        node_ids: A list of node ids to which this intervention will be distributed. None or [] distributes
            intervention to all nodes
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        repelling_initial_effect: Initial strength of the Killing effect. The effect decays over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial Effect.
        insecticide:The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple IRSHousingModification interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        Nothing
    """

    intervention = irs_configuration(campaign,
                                     killing_initial_effect=killing_initial_effect,
                                     killing_box_duration=killing_box_duration,
                                     killing_decay_time_constant=killing_decay_time_constant,
                                     repelling_box_duration=repelling_box_duration,
                                     repelling_initial_effect=repelling_initial_effect,
                                     repelling_decay_time_constant=repelling_decay_time_constant,
                                     insecticide=insecticide,
                                     intervention_name=intervention_name)

    campaign.add(ScheduledCampaignEvent(campaign, Start_Day=start_day, Node_Ids=node_ids,
                                        Demographic_Coverage=demographic_coverage, Intervention_List=[intervention]))


def add_triggered_irs_housing_modification(
        campaign,
        start_day: int = 1,
        demographic_coverage: float = 1,
        node_ids: list = None,
        trigger_condition_list: list = None,
        listening_duration: int = -1,
        delay_period_constant: float = 0,
        killing_initial_effect: float = 1,
        killing_box_duration: int = 0,
        killing_decay_time_constant: int = 90,
        repelling_initial_effect: float = 0,
        repelling_box_duration: int = 0,
        repelling_decay_time_constant: int = 90,
        insecticide: str = "",
        intervention_name: str = default_name
):
    """
        Adds triggered IRSHousingModification intervention to the campaign. The IRSHousingModification intervention class
        includes Indoor Residual Spraying (IRS) in the simulation. IRS is another key vector control tool in which
        insecticide is sprayed on the interior walls of a house so that mosquitoes resting on the walls after
        consuming a blood meal will die. IRS can also have a repellent effect. Because this class is distributed
        to individuals, it can target subgroups of the population. To target all individuals in a node, use
        IndoorSpaceSpraying. Do not use IRSHousingModification and IndoorSpaceSpraying together.

    Args:
        campaign: A campaign builder that also contains schema_path parameters
        start_day: The day on which the intervention is distributed
        demographic_coverage: The fraction of individuals in the target demographic that will receive this intervention
        node_ids: A list of node ids to which this intervention will be distributed. None or [] distributes
            intervention to all nodes
        trigger_condition_list: A list of the events that will trigger intervention distribution.
        listening_duration: The number of time steps that the distributed event will monitor for triggers.
            Default is -1, which is indefinitely.
        delay_period_constant: Optional. Delay, in days, before the intervention is given out after a trigger
            is received.
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        repelling_initial_effect: Initial strength of the Killing effect. The effect decays over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial Effect.
        insecticide:The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple IRSHousingModification interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        Nothing
    """
    intervention = irs_configuration(campaign,
                                     killing_initial_effect=killing_initial_effect,
                                     killing_box_duration=killing_box_duration,
                                     killing_decay_time_constant=killing_decay_time_constant,
                                     repelling_box_duration=repelling_box_duration,
                                     repelling_initial_effect=repelling_initial_effect,
                                     repelling_decay_time_constant=repelling_decay_time_constant,
                                     insecticide=insecticide,
                                     intervention_name=intervention_name)

    campaign.add(TriggeredCampaignEvent(camp=campaign,
                                        Start_Day=start_day,
                                        Event_Name="IRSHousingInterventionEvent",
                                        Triggers=trigger_condition_list,
                                        Intervention_List=[intervention],
                                        Demographic_Coverage=demographic_coverage,
                                        Duration=listening_duration,
                                        Node_Ids=node_ids,
                                        Delay=delay_period_constant))


def irs_configuration(campaign,
                      killing_initial_effect: float = 1,
                      killing_box_duration: int = 0,
                      killing_decay_time_constant: int = 90,
                      repelling_initial_effect: float = 0,
                      repelling_box_duration: int = 0,
                      repelling_decay_time_constant: int = 90,
                      insecticide: str = "",
                      intervention_name: str = default_name):
    """
        Configures and returns IRSHousingModification intervention. The IRSHousingModification intervention class
        includes Indoor Residual Spraying (IRS) in the simulation. IRS is another key vector control tool in which
        insecticide is sprayed on the interior walls of a house so that mosquitoes resting on the walls after
        consuming a blood meal will die. IRS can also have a repellent effect. Because this class is distributed
        to individuals, it can target subgroups of the population. To target all individuals in a node, use
        IndoorSpaceSpraying. Do not use IRSHousingModification and IndoorSpaceSpraying together.

    Args:
        campaign: A campaign builder that also contains schema_path parameters
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        repelling_initial_effect: Initial strength of the Killing effect. The effect decays over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial Effect.
        insecticide:The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple IRSHousingModification interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        Configured IRSHousingModification intervention
    """

    schema_path = campaign.schema_path
    intervention = s2c.get_class_with_defaults("IRSHousingModification", schema_path)
    repelling = utils.get_waning_from_params(schema_path=schema_path,
                                             initial=repelling_initial_effect,
                                             box_duration=repelling_box_duration,
                                             decay_rate=1.0 / repelling_decay_time_constant if repelling_decay_time_constant else 0)


    killing = utils.get_waning_from_params(schema_path=schema_path,
                                           initial=killing_initial_effect,
                                           box_duration=killing_box_duration,
                                           decay_rate=1.0 / killing_decay_time_constant if killing_decay_time_constant else 0)


    intervention.Killing_Config = killing
    intervention.Repelling_Config = repelling
    intervention.Intervention_Name = intervention_name
    intervention.Insecticide_Name = insecticide

    return intervention


def new_intervention_as_file(campaign, start_day, filename=None):
    add_scheduled_irs_housing_modification(campaign=campaign, start_day=start_day)
    if filename is None:
        filename = "IRSHousingModification.json"
    campaign.save(filename)
    return filename
