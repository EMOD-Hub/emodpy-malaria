
from emod_api.interventions.common import BroadcastEvent
from emod_api import schema_to_class as s2c
import emod_api.interventions.utils as utils
from emodpy_malaria.interventions.common import add_campaign_event, add_triggered_campaign_delay_event, MAX_AGE_YEARS

default_name = "IRSHousingModification"


def add_scheduled_irs_housing_modification(
        campaign,
        start_day: int = 1,
        demographic_coverage: float = 1.0,
        target_num_individuals: int = None,
        node_ids: list = None,
        repetitions: int = 1,
        timesteps_between_repetitions: int = 365,
        ind_property_restrictions: list = None,
        target_age_min: int = 0,
        target_age_max: int = MAX_AGE_YEARS,
        target_gender: str = "All",
        target_residents_only: bool = False,
        broadcast_event: str = "Received_IRS",
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
        broadcast_event: "The name of the event to be broadcast. This event must be set in the
            **Custom_Coordinator_Events** configuration parameter. When None or "", nothing is broadcast.
            Default: "Received_IRS"
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        repelling_initial_effect: Initial strength of the Killing effect. The effect decays over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial Effect.
        insecticide: The name of the insecticide defined in config.Insecticides for this intervention.
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
    if broadcast_event:
        intervention = [intervention, BroadcastEvent(campaign, broadcast_event)]

    add_campaign_event(campaign=campaign,
                       start_day=start_day,
                       demographic_coverage=demographic_coverage,
                       target_num_individuals=target_num_individuals,
                       node_ids=node_ids,
                       repetitions=repetitions,
                       timesteps_between_repetitions=timesteps_between_repetitions,
                       ind_property_restrictions=ind_property_restrictions,
                       target_age_min=target_age_min,
                       target_age_max=target_age_max,
                       target_gender=target_gender,
                       target_residents_only=target_residents_only,
                       individual_intervention=intervention)


def add_triggered_irs_housing_modification(
        campaign,
        start_day: int = 1,
        trigger_condition_list: list = None,
        listening_duration: int = -1,
        delay_period_constant: float = 0,
        demographic_coverage: float = 1.0,
        node_ids: list = None,
        repetitions: int = 1,
        timesteps_between_repetitions: int = 365,
        ind_property_restrictions: list = None,
        target_age_min: float = 0,
        target_age_max: float = MAX_AGE_YEARS,
        target_gender: str = "All",
        target_residents_only: bool = False,
        broadcast_event: str = "Received_IRS",
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
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        target_residents_only: When set to True, the intervention is only distributed to individuals that began
            the simulation in the node (i.e. those that claim the node as their residence)
        broadcast_event: "The name of the event to be broadcast. This event must be set in the
            **Custom_Coordinator_Events** configuration parameter. When None or "", nothing is broadcast.
            Default: "Received_IRS"
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        repelling_initial_effect: Initial strength of the Killing effect. The effect decays over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial Effect.
        insecticide: The name of the insecticide defined in config.Insecticides for this intervention.
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
    if broadcast_event:
        intervention = [intervention, BroadcastEvent(campaign, broadcast_event)]

    add_triggered_campaign_delay_event(campaign=campaign,
                                       start_day=start_day,
                                       trigger_condition_list=trigger_condition_list,
                                       listening_duration=listening_duration,
                                       delay_period_constant=delay_period_constant,
                                       demographic_coverage=demographic_coverage,
                                       node_ids=node_ids,
                                       repetitions=repetitions,
                                       timesteps_between_repetitions=timesteps_between_repetitions,
                                       ind_property_restrictions=ind_property_restrictions,
                                       target_age_min=target_age_min,
                                       target_age_max=target_age_max,
                                       target_gender=target_gender,
                                       target_residents_only=target_residents_only,
                                       individual_intervention=intervention)


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
        insecticide: The name of the insecticide defined in config.Insecticides for this intervention.
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
                                             decay_time_constant=repelling_decay_time_constant)
    killing = utils.get_waning_from_params(schema_path=schema_path,
                                           initial=killing_initial_effect,
                                           box_duration=killing_box_duration,
                                           decay_time_constant=killing_decay_time_constant)
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
