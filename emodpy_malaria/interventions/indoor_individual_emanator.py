"""
This module contains functionality for IndoorIndividualEmanator intervention for malaria campaigns
"""

from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emod_api.interventions.common import BroadcastEvent
from emodpy_malaria.interventions.common import add_campaign_event, add_triggered_campaign_delay_event


def _indoor_individual_emanator(campaign,
                                killing_initial_effect: float,
                                killing_box_duration: float,
                                killing_decay_time_constant: float,
                                repelling_initial_effect: float,
                                repelling_box_duration: float,
                                repelling_decay_time_constant: float,
                                insecticide: str = "",
                                cost: float = 0,
                                new_property_value: str = "",
                                intervention_name: str = "IndoorIndividualEmanator"):
    """
        Configures IndoorIndividualEmanator intervention.

        Note: for killing, repelling effects - depending on the parameters you set,
        different WaningEffect classes will be used:
        box_duration = -1 => WaningEffectConstant, decay_time_constant is ignored
        box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
        box_duration > 0 + decay_time_constant = 0 => WaningEffectBox
        box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential

    Args:
        campaign:
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        repelling_initial_effect: Initial strength of the Repelling effect. The effect may decay over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial_Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial_Effect.
        insecticide: The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        cost: Unit cost per IndoorIndividualEmanator
        new_property_value: New IndividualProperty value to assign to individuals receiving this intervention. Must be
            in format of "PropertyName:Value", e.g. "EmanatorUser:Yes".
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple IndoorIndividualEmanator interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        Configured IndoorIndividualEmanator intervention
    """
    schema_path = campaign.schema_path
    intervention = s2c.get_class_with_defaults("IndoorIndividualEmanator", schema_path)
    intervention.Killing_Config = utils.get_waning_from_params(schema_path,
                                                               initial=killing_initial_effect,
                                                               box_duration=killing_box_duration,
                                                               decay_time_constant=killing_decay_time_constant)
    intervention.Repelling_Config = utils.get_waning_from_params(schema_path,
                                                                 initial=repelling_initial_effect,
                                                                 box_duration=repelling_box_duration,
                                                                 decay_time_constant=repelling_decay_time_constant)
    intervention.Intervention_Name = intervention_name
    intervention.Cost_To_Consumer = cost
    intervention.New_Property_Value = new_property_value
    intervention.Insecticide_Name = insecticide

    return intervention


def add_indoor_individual_emanator_scheduled(campaign,
                                             killing_initial_effect: float,
                                             killing_box_duration: float,
                                             killing_decay_time_constant: float,
                                             repelling_initial_effect: float,
                                             repelling_box_duration: float,
                                             repelling_decay_time_constant: float,
                                             start_day: int,
                                             coverage_by_ages: list = None,
                                             demographic_coverage: float = None,
                                             target_num_individuals: int = None,
                                             node_ids: list = None,
                                             repetitions: int = 1,
                                             timesteps_between_repetitions: int = 365,
                                             ind_property_restrictions: list = None,
                                             receiving_broadcast_event: str = None,
                                             insecticide: str = "",
                                             cost: float = 0,
                                             new_property_value: str = "",
                                             intervention_name: str = "IndoorIndividualEmanator"
                                             ):
    """
        Add a scheduled IndoorIndividualEmanator intervention.

        Note: for killing, repelling effects - depending on the parameters you set,
        different WaningEffect classes will be used:
        box_duration = -1 => WaningEffectConstant, decay_time_constant is ignored
        box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
        box_duration > 0 + decay_time_constant = 0 => WaningEffectBox
        box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential

    Args:
        campaign: object for building, modifying, and writing campaign configuration files.
        start_day: Start day of intervention.
        coverage_by_ages: A list of dictionaries defining the coverage per
            age group. For example, ``[{"coverage":1,"min": 1, "max": 10},
            {"coverage":1,"min": 11, "max": 50}]``.
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
            Sets **Timesteps_Between_Repetitions**.
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**. In the format ``[{
            "BitingRisk":"High"}, {"IsCool":"Yes}]``
        receiving_broadcast_event: Optional. BroadcastEvent that's sent out when IndoorIndividualEmanator is received.
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        repelling_initial_effect: Initial strength of the Repelling effect. The effect may decay over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial_Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial_Effect.
        insecticide: The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        cost: Unit cost per IndoorIndividualEmanator
        new_property_value: New IndividualProperty value to assign to individuals receiving this intervention. Must be
            in format of "PropertyName:Value", e.g. "EmanatorUser:Yes".
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple IndoorIndividualEmanator interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        Nothing

    """
    if coverage_by_ages and (demographic_coverage or target_num_individuals):
        raise ValueError(f"When 'setting 'coverage_by_ages', do not set 'demographic_coverage' or "
                         f"'target_num_individuals'.\n")
    if target_num_individuals is None and demographic_coverage is None and coverage_by_ages is None:
        raise ValueError(f"You must set either 'target_num_individuals', 'demographic_coverage' or "
                         f"'coverage_by_ages'.\n")

    intervention = _indoor_individual_emanator(campaign,
                                               killing_initial_effect=killing_initial_effect,
                                               killing_box_duration=killing_box_duration,
                                               killing_decay_time_constant=killing_decay_time_constant,
                                               repelling_initial_effect=repelling_initial_effect,
                                               repelling_box_duration=repelling_box_duration,
                                               repelling_decay_time_constant=repelling_decay_time_constant,
                                               cost=cost,
                                               insecticide=insecticide,
                                               new_property_value=new_property_value,
                                               intervention_name=intervention_name)

    if receiving_broadcast_event:
        intervention = [intervention, BroadcastEvent(camp=campaign, Event_Trigger=receiving_broadcast_event)]

    if coverage_by_ages:
        for coverage_by_age in coverage_by_ages:
            add_campaign_event(campaign,
                               start_day=start_day,
                               demographic_coverage=coverage_by_age["coverage"],
                               target_age_min=coverage_by_age["min"],
                               target_age_max=coverage_by_age["max"],
                               node_ids=node_ids,
                               repetitions=repetitions,
                               timesteps_between_repetitions=timesteps_between_repetitions,
                               ind_property_restrictions=ind_property_restrictions,
                               individual_intervention=intervention)
    else:
        add_campaign_event(campaign,
                           start_day=start_day,
                           demographic_coverage=demographic_coverage,
                           target_num_individuals=target_num_individuals,
                           node_ids=node_ids,
                           repetitions=repetitions,
                           timesteps_between_repetitions=timesteps_between_repetitions,
                           ind_property_restrictions=ind_property_restrictions,
                           individual_intervention=intervention)


def add_indoor_individual_emanator_triggered(campaign,
                                             killing_initial_effect: float,
                                             killing_box_duration: float,
                                             killing_decay_time_constant: float,
                                             repelling_initial_effect: float,
                                             repelling_box_duration: float,
                                             repelling_decay_time_constant: float,
                                             start_day: int,
                                             trigger_condition_list: list,
                                             demographic_coverage: float = 1.0,
                                             listening_duration: int = -1,
                                             delay_period_constant: float = 0,
                                             node_ids: list = None,
                                             repetitions: int = 1,
                                             timesteps_between_repetitions: int = 365,
                                             ind_property_restrictions: list = None,
                                             receiving_broadcast_event: str = None,
                                             insecticide: str = "",
                                             cost: float = 0,
                                             new_property_value: str = "",
                                             intervention_name: str = "IndoorIndividualEmanator"
                                             ):
    """
        Adds a triggered IndoorIndividualEmanator intervention

    Args:
        campaign: object for building, modifying, and writing campaign configuration files.
        start_day: The day the intervention is given out.
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        trigger_condition_list: A list of the events that will trigger intervention distribution.
        listening_duration: The number of time steps that the distributed event will monitor for triggers.
            Default is -1, which is indefinitely.
        delay_period_constant: Optional. Delay, in days, before the intervention is given out after a trigger
            is received.
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**.
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**. In the format ``[{
            "BitingRisk":"High"}, {"IsCool":"Yes}]``
        receiving_broadcast_event: Optional. BroadcastEvent that's sent out when IndoorIndividualEmanator is received.
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        repelling_initial_effect: Initial strength of the Repelling effect. The effect may decay over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial_Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial_Effect.
        insecticide: The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        cost: Unit cost per IndoorIndividualEmanator
        new_property_value: New IndividualProperty value to assign to individuals receiving this intervention. Must be
            in format of "PropertyName:Value", e.g. "EmanatorUser:Yes".
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple IndoorIndividualEmanator interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        Nothing

    """

    intervention_list = [_indoor_individual_emanator(campaign,
                                                     killing_initial_effect=killing_initial_effect,
                                                     killing_box_duration=killing_box_duration,
                                                     killing_decay_time_constant=killing_decay_time_constant,
                                                     repelling_initial_effect=repelling_initial_effect,
                                                     repelling_box_duration=repelling_box_duration,
                                                     repelling_decay_time_constant=repelling_decay_time_constant,
                                                     insecticide=insecticide,
                                                     cost=cost,
                                                     new_property_value=new_property_value,
                                                     intervention_name=intervention_name)]

    if receiving_broadcast_event:
        intervention_list.append(BroadcastEvent(camp=campaign, Event_Trigger=receiving_broadcast_event))

    add_triggered_campaign_delay_event(campaign=campaign,
                                       start_day=start_day,
                                       demographic_coverage=demographic_coverage,
                                       trigger_condition_list=trigger_condition_list,
                                       listening_duration=listening_duration,
                                       delay_period_constant=delay_period_constant,
                                       node_ids=node_ids,
                                       repetitions=repetitions,
                                       timesteps_between_repetitions=timesteps_between_repetitions,
                                       ind_property_restrictions=ind_property_restrictions,
                                       individual_intervention=intervention_list)
