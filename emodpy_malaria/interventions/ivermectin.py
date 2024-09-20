from emod_api import schema_to_class as s2c
from emod_api.interventions.common import utils
from emodpy_malaria.interventions.common import add_campaign_event, add_triggered_campaign_delay_event


def add_scheduled_ivermectin(campaign,
                             start_day: int = 1,
                             demographic_coverage: float = 1.0,
                             target_num_individuals: int = None,
                             node_ids: list = None,
                             repetitions: int = 1,
                             timesteps_between_repetitions: int = 365,
                             ind_property_restrictions: list = None,
                             node_property_restrictions: list = None,
                             killing_initial_effect: float = 1,
                             killing_box_duration: float = 0,
                             killing_decay_time_constant: float = 0,
                             insecticide: str = "",
                             cost: float = 1,
                             intervention_name: str = "Ivermectin"
                             ):
    """
        Adds a scheduled Ivermectin CampaignEvent to the campaign, which can be repeated any number of times.
        It’s possible to have multiple Ivermectin interventions attached to a person if they have
        different Intervention_Name values.

        Note: for WaningEffect,
        box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
        box_duration > 0 + decay_time_constant = 0 => WaningEffectBox/Constant (depending on duration)
        box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential

    Args:
        campaign: A campaign builder that also contains schema_path parameters
        start_day: The day on which the intervention is distributed
        demographic_coverage: probability of choosing an individual, is ignored if "target_num_individuals" is set
        target_num_individuals: number of individuals to receive ivermectin, demographic_coverage will be ignored
            if this is set
        node_ids: The list of nodes to apply this intervention to (**Node_List** parameter). If not provided,
            intervention is distributed to all nodes.
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        node_property_restrictions: A list of the NodeProperty key:value pairs, as defined in the demographics file,
            that nodes must have to receive the intervention. Sets **Node_Property_Restrictions**
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        insecticide:The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        cost: Unit cost per Ivermectin dosing (unamortized)
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple Ivermectin interventions
            attached to a person if they have different Intervention_Name values.
    Returns:
        Nothing

    """

    intervention = _ivermectin(campaign=campaign,
                               killing_initial_effect=killing_initial_effect,
                               killing_box_duration=killing_box_duration,
                               killing_decay_time_constant=killing_decay_time_constant,
                               insecticide=insecticide,
                               cost=cost,
                               intervention_name=intervention_name)

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


def add_triggered_ivermectin(campaign,
                             start_day: int = 1,
                             trigger_condition_list: list = None,
                             listening_duration: int = -1,
                             delay_period_constant: float = 0,
                             demographic_coverage: float = 1.0,
                             node_ids: list = None,
                             ind_property_restrictions: list = None,
                             node_property_restrictions: list = None,
                             killing_initial_effect: float = 1,
                             killing_box_duration: float = 0,
                             killing_decay_time_constant: float = 0,
                             insecticide: str = "",
                             cost: float = 1,
                             intervention_name: str = "Ivermectin"):
    """
        Adds a triggered Ivermectin CampaignEvent to the campaign, that responds to a trigger after an optional
        delay. The intervention is distributed on start_day and responds to triggers for a listening_duration of days.

        It’s possible to have multiple Ivermectin interventions attached to a person if they have
        different Intervention_Name values.

        Note: for WaningEffect,
        box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
        box_duration > 0 + decay_time_constant = 0 => WaningEffectBox/Constant (depending on duration)
        box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential


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
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        node_property_restrictions: A list of the NodeProperty key:value pairs, as defined in the demographics file,
            that nodes must have to receive the intervention. Sets **Node_Property_Restrictions**
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        insecticide:The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        cost: Unit cost per Ivermectin dosing (unamortized)
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple Ivermectin interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        Nothing
    """

    intervention = _ivermectin(campaign=campaign,
                               killing_initial_effect=killing_initial_effect,
                               killing_box_duration=killing_box_duration,
                               killing_decay_time_constant=killing_decay_time_constant,
                               insecticide=insecticide,
                               cost=cost,
                               intervention_name=intervention_name)

    add_triggered_campaign_delay_event(campaign=campaign,
                                       start_day=start_day,
                                       trigger_condition_list=trigger_condition_list,
                                       listening_duration=listening_duration,
                                       delay_period_constant=delay_period_constant,
                                       demographic_coverage=demographic_coverage,
                                       node_ids=node_ids,
                                       ind_property_restrictions=ind_property_restrictions,
                                       node_property_restrictions=node_property_restrictions,
                                       individual_intervention=intervention)


def _ivermectin(campaign,
                killing_initial_effect: float = 1,
                killing_box_duration: float = 0,
                killing_decay_time_constant: float = 90,
                insecticide: str = "",
                cost: float = 1,
                intervention_name: str = "Ivermectin"):
    """
        Configures Ivermectin intervention.
        Note: for WaningEffect,
        box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
        box_duration > 0 + decay_time_constant = 0 => WaningEffectBox/Constant (depending on duration)
        box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential

    Args:
        campaign: A campaign builder that also contains schema_path parameters
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        insecticide:The name of the insecticide defined in config.Insecticides for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if config.Insecticides does not define anything.
        cost: Unit cost per Ivermectin dosing (unamortized)
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple Ivermectin interventions
            attached to a person if they have different Intervention_Name values.

    Returns:
        configured Ivermectin intervention

    """
    schema_path = campaign.schema_path

    intervention = s2c.get_class_with_defaults("Ivermectin", schema_path)
    intervention.Killing_Config = utils.get_waning_from_params(schema_path,
                                                               initial=killing_initial_effect,
                                                               box_duration=killing_box_duration,
                                                               decay_rate=1. / killing_decay_time_constant if
                                                               killing_decay_time_constant else 0)
    intervention.Insecticide_Name = insecticide
    intervention.Cost_To_Consumer = cost
    intervention.Intervention_Name = intervention_name

    return intervention
