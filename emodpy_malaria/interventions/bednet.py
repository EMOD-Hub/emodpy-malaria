"""
This module contains functionality for bednet distribution.
"""

from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emod_api.interventions.common import BroadcastEvent
from emodpy_malaria.interventions.common import add_campaign_event, add_triggered_campaign_delay_event


def _simple_bednet(campaign,
                   killing_initial_effect: float = 1,
                   killing_box_duration: float = 0,
                   killing_decay_time_constant: float = 0,
                   blocking_initial_effect: float = 1,
                   blocking_box_duration: float = 0,
                   blocking_decay_time_constant: float = 0,
                   repelling_initial_effect: float = 1,
                   repelling_box_duration: float = 0,
                   repelling_decay_time_constant: float = 0,
                   usage_initial_effect: float = 1,
                   usage_box_duration: float = 0,
                   usage_decay_time_constant: float = 0,
                   insecticide: str = "",
                   cost: float = 0,
                   intervention_name: str = "SimpleBednet"):
    """
        Configures SimpleBednet intervention.
        Note: for WaningEffect,
        box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
        box_duration > 0 + decay_time_constant = 0 => WaningEffectBox/Constant (depending on duration)
        box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential

todo: how to describe usage_ effects? how to make usage default WaningEffectConstant

    Args:
        campaign:
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        blocking_initial_effect: Initial strength of the Blocking effect. The effect may decay over time.
        blocking_box_duration: Box duration of effect in days before the decay of Blocking Initial_Effect.
        blocking_decay_time_constant: The exponential decay length, in days of the Blocking Initial_Effect.
        repelling_initial_effect: Initial strength of the Repelling effect. The effect may decay over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial_Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial_Effect.
        usage_initial_effect: Determines when and if an individual is using a bed net.
        usage_box_duration: ?
        usage_decay_time_constant: ?
        insecticide:The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        cost: Unit cost per bednet
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple SimpleBednet interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        Configured SimpleBednet intervention
    """
    schema_path = campaign.schema_path
    intervention = s2c.get_class_with_defaults("SimpleBednet", schema_path)
    intervention.Blocking_Config = utils.get_waning_from_params(schema_path,
                                                                initial=blocking_initial_effect,
                                                                box_duration=blocking_box_duration,
                                                                decay_time_constant=blocking_decay_time_constant)
    intervention.Killing_Config = utils.get_waning_from_params(schema_path,
                                                               initial=killing_initial_effect,
                                                               box_duration=killing_box_duration,
                                                               decay_time_constant=killing_decay_time_constant)
    intervention.Repelling_Config = utils.get_waning_from_params(schema_path,
                                                                 initial=repelling_initial_effect,
                                                                 box_duration=repelling_box_duration,
                                                                 decay_time_constant=repelling_decay_time_constant)
    intervention.Usage_Config = utils.get_waning_from_params(schema_path,
                                                             initial=usage_initial_effect,
                                                             box_duration=usage_box_duration,
                                                             decay_time_constant=usage_decay_time_constant)

    intervention.Intervention_Name = intervention_name
    intervention.Cost_To_Consumer = cost
    intervention.Insecticide_Name = insecticide

    return intervention


def new_intervention_as_file(campaign, start_day, filename=None):
    """
    Write a campaign file to disk with a single bednet event, using defaults. Useful for testing and learning.

    Args:
        campaign: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will be added.
        start_day: The day of the simulation on which the bednets are distributed. We recommend 
            aligning this with the start of the simulation.
        filename: The campaign filename; can be omitted and default will be used and returned to user.

    Returns:
        The campaign filename written to disk.
    """
    add_itn_scheduled(campaign=campaign, start_day=start_day)
    if filename is None:
        filename = "BedNet.json"
    campaign.save(filename)
    return filename


def add_itn_scheduled(campaign,
                      start_day: int = 0,
                      coverage_by_ages: list = None,
                      demographic_coverage: float = 1.0,
                      target_num_individuals: int = None,
                      node_ids: list = None,
                      repetitions: int = 1,
                      timesteps_between_repetitions: int = 365,
                      ind_property_restrictions: list = None,
                      node_property_restrictions: list = None,
                      receiving_itn_broadcast_event: str = None,
                      blocking_initial_effect: float = 0.9,
                      blocking_box_duration: float = 0,
                      blocking_decay_time_constant: float = 7300,
                      killing_initial_effect: float = 0.6,
                      killing_box_duration: int = 0,
                      killing_decay_time_constant: float = 7300,
                      repelling_initial_effect: float = 0,
                      repelling_box_duration: float = 0,
                      repelling_decay_time_constant: float = 0,
                      usage_initial_effect: float = 1,
                      usage_box_duration: float = 0,
                      usage_decay_time_constant: float = 0,
                      insecticide: str = "",
                      cost: float = 0,
                      intervention_name: str = "SimpleBednet"
                      ):
    """
        Add a scheduled SimpleBednet intervention.

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
        node_property_restrictions: A list of the NodeProperty key:value pairs, as defined in the demographics file,
            that nodes must have to receive the intervention. Sets **Node_Property_Restrictions**
        receiving_itn_broadcast_event: Optional. BroadcastEvent that's sent out when bednet is received.
            Default is to send out 'Received_ITN' event. To not send out event set to None.
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        blocking_initial_effect: Initial strength of the Blocking effect. The effect may decay over time.
        blocking_box_duration: Box duration of effect in days before the decay of Blocking Initial_Effect.
        blocking_decay_time_constant: The exponential decay length, in days of the Blocking Initial_Effect.
        repelling_initial_effect: Initial strength of the Repelling effect. The effect may decay over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial_Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial_Effect.
        usage_initial_effect: Determines when and if an individual is using a bed net.
        usage_box_duration: ?
        usage_decay_time_constant: ?
        insecticide:The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        cost: Unit cost per bednet
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple SimpleBednet interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        Nothing

    """
    if target_num_individuals and coverage_by_ages:
        raise ValueError(f"You cannot use both - 'target_num_individuals' and 'coverage_by_ages'.\n")

    intervention = _simple_bednet(campaign,
                                  killing_initial_effect=killing_initial_effect,
                                  killing_box_duration=killing_box_duration,
                                  killing_decay_time_constant=killing_decay_time_constant,
                                  blocking_initial_effect=blocking_initial_effect,
                                  blocking_box_duration=blocking_box_duration,
                                  blocking_decay_time_constant=blocking_decay_time_constant,
                                  repelling_initial_effect=repelling_initial_effect,
                                  repelling_box_duration=repelling_box_duration,
                                  repelling_decay_time_constant=repelling_decay_time_constant,
                                  usage_initial_effect=usage_initial_effect,
                                  usage_box_duration=usage_box_duration,
                                  usage_decay_time_constant=usage_decay_time_constant,
                                  insecticide=insecticide,
                                  cost=cost,
                                  intervention_name=intervention_name)

    if receiving_itn_broadcast_event:
        intervention = [intervention, BroadcastEvent(camp=campaign, Event_Trigger=receiving_itn_broadcast_event)]

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
                               node_property_restrictions=node_property_restrictions,
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
                           node_property_restrictions=node_property_restrictions,
                           individual_intervention=intervention)


def add_itn_triggered(campaign,
                      start_day: int = 0,
                      demographic_coverage: float = 1.0,
                      trigger_condition_list: list = None,
                      listening_duration: int = -1,
                      delay_period_constant: float = 0,
                      node_ids: list = None,
                      repetitions: int = 1,
                      timesteps_between_repetitions: int = 365,
                      ind_property_restrictions: list = None,
                      node_property_restrictions: list = None,
                      receiving_itn_broadcast_event: str = None,
                      blocking_initial_effect: float = 0.9,
                      blocking_box_duration: float = 0,
                      blocking_decay_time_constant: float = 7300,
                      killing_initial_effect: float = 0.6,
                      killing_box_duration: int = 0,
                      killing_decay_time_constant: float = 7300,
                      repelling_initial_effect: float = 0,
                      repelling_box_duration: float = 0,
                      repelling_decay_time_constant: float = 0,
                      usage_initial_effect: float = 1,
                      usage_box_duration: float = 0,
                      usage_decay_time_constant: float = 0,
                      insecticide: str = "",
                      cost: float = 0,
                      intervention_name: str = "SimpleBednet"
                      ):
    """
        Adds a triggered SimpleBednet intervention

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
        node_property_restrictions: A list of the NodeProperty key:value pairs, as defined in the demographics file,
            that nodes must have to receive the intervention. Sets **Node_Property_Restrictions**
        receiving_itn_broadcast_event: Optional. BroadcastEvent that's sent out when bednet is received.
            Default is to send out 'Received_ITN' event. To not send out event set to None.
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        blocking_initial_effect: Initial strength of the Blocking effect. The effect may decay over time.
        blocking_box_duration: Box duration of effect in days before the decay of Blocking Initial_Effect.
        blocking_decay_time_constant: The exponential decay length, in days of the Blocking Initial_Effect.
        repelling_initial_effect: Initial strength of the Repelling effect. The effect may decay over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial_Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial_Effect.
        usage_initial_effect: Determines when and if an individual is using a bed net.
        usage_box_duration: ?
        usage_decay_time_constant: ?
        insecticide:The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        cost: Unit cost per bednet
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple SimpleBednet interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        Nothing

    """

    intervention_list = [_simple_bednet(campaign,
                                        killing_initial_effect=killing_initial_effect,
                                        killing_box_duration=killing_box_duration,
                                        killing_decay_time_constant=killing_decay_time_constant,
                                        blocking_initial_effect=blocking_initial_effect,
                                        blocking_box_duration=blocking_box_duration,
                                        blocking_decay_time_constant=blocking_decay_time_constant,
                                        repelling_initial_effect=repelling_initial_effect,
                                        repelling_box_duration=repelling_box_duration,
                                        repelling_decay_time_constant=repelling_decay_time_constant,
                                        usage_initial_effect=usage_initial_effect,
                                        usage_box_duration=usage_box_duration,
                                        usage_decay_time_constant=usage_decay_time_constant,
                                        insecticide=insecticide,
                                        cost=cost,
                                        intervention_name=intervention_name)]

    if receiving_itn_broadcast_event:
        intervention_list.append(BroadcastEvent(camp=campaign, Event_Trigger=receiving_itn_broadcast_event))

    add_triggered_campaign_delay_event(campaign=campaign,
                                       start_day=start_day,
                                       demographic_coverage=demographic_coverage,
                                       trigger_condition_list=trigger_condition_list,
                                       listening_duration=listening_duration,
                                       delay_period_constant=delay_period_constant,
                                       node_ids=node_ids,
                                       repetitions=repetitions,
                                       timesteps_between_repetitions=timesteps_between_repetitions,
                                       node_property_restrictions=node_property_restrictions,
                                       ind_property_restrictions=ind_property_restrictions,
                                       individual_intervention=intervention_list)
