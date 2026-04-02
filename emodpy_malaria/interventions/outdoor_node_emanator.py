from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emodpy_malaria.interventions.common import add_campaign_event


def _outdoor_node_emanator(campaign,
                           killing_initial_effect: float,
                           killing_box_duration: float,
                           killing_decay_time_constant: float,
                           repelling_initial_effect: float,
                           repelling_box_duration: float,
                           repelling_decay_time_constant: float,
                           spray_coverage: float = 1.0,
                           insecticide: str = "",
                           cost: float = 0,
                           new_property_value: str = "",
                           intervention_name: str = "OutdoorNodeEmanator"):
    """
        Configures OutdoorNodeEmanator intervention.

        Note: for killing and repelling effects - depending on the parameters you set,
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
        spray_coverage: The proportion of the node affected. This value is multiplied by the current efficacy of the
            waning effects.
        insecticide: The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        cost: Unit cost per OutdoorNodeEmanator
        new_property_value: New NodeProperty value to assign to individuals receiving this intervention. Must be
            in format of "PropertyName:Value", e.g. "EmanatorNode:Yes".
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class.

    Returns:
        Configured OutdoorNodeEmanator intervention
    """
    schema_path = campaign.schema_path
    intervention = s2c.get_class_with_defaults("OutdoorNodeEmanator", schema_path)
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
    intervention.Spray_Coverage = spray_coverage
    intervention.New_Property_Value = new_property_value
    intervention.Insecticide_Name = insecticide

    return intervention


def add_outdoor_node_emanator_scheduled(campaign,
                                        killing_initial_effect: float,
                                        killing_box_duration: float,
                                        killing_decay_time_constant: float,
                                        repelling_initial_effect: float,
                                        repelling_box_duration: float,
                                        repelling_decay_time_constant: float,
                                        start_day: int,
                                        spray_coverage: float = 1.0,
                                        node_ids: list = None,
                                        repetitions: int = 1,
                                        timesteps_between_repetitions: int = 365,
                                        node_property_restrictions: list = None,
                                        receiving_broadcast_event: str = None,
                                        insecticide: str = "",
                                        cost: float = 0,
                                        new_property_value: str = "",
                                        intervention_name: str = "OutdoorNodeEmanator"
                                        ):
    """
        Add a scheduled OutdoorNodeEmanator intervention.

    Args:
        campaign: object for building, modifying, and writing campaign configuration files.
        start_day: The day the intervention is given out.
        node_ids: List of node ids representing nodes to target with the intervention. [] or None indicates all
            nodes will be targeted.
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**.
        node_property_restrictions: A list of dictionaries of NodeProperties, which are needed for the node
            to receive the intervention. Sets the **Node_Property_Restrictions**.
        receiving_broadcast_event: Optional. BroadcastNodeEvent that's sent out when OutdoorNodeEmanator is
            received.
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
        cost: Unit cost per OutdoorNodeEmanator
        new_property_value: New NodeProperty value to assign to nodes receiving this intervention. Must be
            in format of "PropertyName:Value", e.g. "EmanatorNode:Yes".
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class.

    Returns:
        Nothing

    """
    intervention = _outdoor_node_emanator(campaign,
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
        broadcast_node_event = s2c.get_class_with_defaults("BroadcastNodeEvent", campaign.schema_path)
        broadcast_node_event.Broadcast_Event = receiving_broadcast_event
        intervention = [intervention, broadcast_node_event]

    add_campaign_event(campaign,
                       start_day=start_day,
                       node_ids=node_ids,
                       repetitions=repetitions,
                       timesteps_between_repetitions=timesteps_between_repetitions,
                       node_property_restrictions=node_property_restrictions,
                       node_intervention=intervention)
