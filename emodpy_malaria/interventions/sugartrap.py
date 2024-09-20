from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emodpy_malaria.interventions.common import add_campaign_event, add_triggered_campaign_delay_event
import json

sugar_trap = "SugarTrap"


def _sugar_trap(campaign,
                cost_to_consumer: float = 0,
                expiration_config: dict = None,
                expiration_constant: float = 30,
                insecticide: str = "",
                intervention_name: str = sugar_trap,
                killing_initial_effect: float = 1,
                killing_box_duration: float = -1,
                killing_decay_time_constant: float = 0):
    """
        Configures SugarTrap intervention

        Note: for WaningEffect,
        box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
        box_duration > 0 + decay_time_constant = 0 => WaningEffectBox or Constant if box_duration is -1
        box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        cost_to_consumer: Per unit cost when distributed
        expiration_config: (Optional) A dictionary of parameters that define a distribution from which a duration will be
            selected for when the trap expires. If the trap is distributed on day 1 and has a duration of 10,
            it will expire on day 10 - 10 days of  efficacy including the day of distribution. If the duration is zero,
            the trap is still distributed but is not applied and expires that day.
            If this is not defined, 'expiration_constant' parameter is used, a CONSTANT_DISTRIBUTION.

            Examples::

                        Please note this is not "Expiration_Period_*", but just "Expiration_*"
                        for Gaussian: {"Expiration_Distribution": "GAUSSIAN_DISTRIBUTION",
                            "Expiration_Gaussian_Mean": 20, "Expiration_Gaussian_Std_Dev":10}
                        for Exponential {"Expiration_Distribution": "EXPONENTIAL_DISTRIBUTION",
                            "Expiration_Exponential":150}

        expiration_constant: Each SugarTrap intervention will expire after this exact time. This is overwritten
            by whatever distribution is defined in 'expiration_config' parameter, if defined. Default is
            SugarTrap will expire after 30 days.
        insecticide: The name of the insecticide defined in <config.Insecticides> for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if <config.Insecticides> does not define anything.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple UsageDependentBednets interventions
            attached to a person if they have different Intervention_Name values.
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
            -1 indicates effect is indefinite (WaningEffectConstant)
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.

    Returns:
        Configured SugarTrap intervention
    """
    schema_path = campaign.schema_path
    intervention = s2c.get_class_with_defaults("SugarTrap", schema_path)
    if not expiration_config:
        intervention.Expiration_Constant = expiration_constant
    else:
        for param in expiration_config:
            setattr(intervention, param, expiration_config[param])

    intervention.Intervention_Name = intervention_name
    intervention.Insecticide_Name = insecticide
    intervention.Killing_Config = utils.get_waning_from_params(schema_path=schema_path, initial=killing_initial_effect,
                                                               box_duration=killing_box_duration,
                                                               decay_time_constant=killing_decay_time_constant)
    intervention.Cost_To_Consumer = cost_to_consumer

    return intervention


def add_scheduled_sugar_trap(
        campaign,
        start_day: int = 0,
        node_ids: list = None,
        repetitions: int = 1,
        timesteps_between_repetitions: int = 365,
        cost_to_consumer: float = 0,
        expiration_config: dict = None,
        expiration_constant: float = 30,
        insecticide: str = "",
        intervention_name: str = sugar_trap,
        killing_initial_effect: float = 1,
        killing_box_duration: float = -1,
        killing_decay_time_constant: float = 0):
    """
        Creates and adds a scheduled intervention that distributes a SugarTrap (ATSB) to the campaign.

        Note: for WaningEffect,
        box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
        box_duration > 0 or -1 + decay_time_constant = 0 => WaningEffectBox or Constant if box_duration is -1
        box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day the intervention is given out.
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        cost_to_consumer: Per unit cost when distributed
        expiration_config: (Optional) A dictionary of parameters that define a distribution from which a duration will be
            selected for when the trap expires. If the trap is distributed on day 1 and has a duration of 10,
            it will expire on day 10 - 10 days of  efficacy including the day of distribution. If the duration is zero,
            the trap is still distributed but is not applied and expires that day.
            If this is not defined, 'expiration_constant' parameter is used, a CONSTANT_DISTRIBUTION.

            Examples::

                        Please note this is not "Expiration_Period_*", but just "Expiration_*"
                        for Gaussian: {"Expiration_Distribution": "GAUSSIAN_DISTRIBUTION",
                            "Expiration_Gaussian_Mean": 20, "Expiration_Gaussian_Std_Dev":10}
                        for Exponential {"Expiration_Distribution": "EXPONENTIAL_DISTRIBUTION",
                            "Expiration_Exponential":150}

        expiration_constant: Each SugarTrap intervention will expire after this exact time. This is overwritten
            by whatever distribution is defined in 'expiration_config' parameter, if defined. Default is
            SugarTrap will expire after 30 days.
        insecticide: The name of the insecticide defined in <config.Insecticides> for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if <config.Insecticides> does not define anything.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple UsageDependentBednets interventions
            attached to a person if they have different Intervention_Name values.
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
            -1 indicates effect is indefinite (WaningEffectConstant)
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.

    Returns:
        Nothing
    """
    node_intervention = _sugar_trap(campaign=campaign,
                                    cost_to_consumer=cost_to_consumer,
                                    expiration_config=expiration_config,
                                    expiration_constant=expiration_constant,
                                    insecticide=insecticide,
                                    intervention_name=intervention_name,
                                    killing_initial_effect=killing_initial_effect,
                                    killing_box_duration=killing_box_duration,
                                    killing_decay_time_constant=killing_decay_time_constant)
    add_campaign_event(campaign=campaign,
                       start_day=start_day,
                       node_ids=node_ids,
                       repetitions=repetitions,
                       timesteps_between_repetitions=timesteps_between_repetitions,
                       node_intervention=node_intervention)


def new_intervention_as_file(campaign, start_day: int = 0, filename: str = "SugarTrap.json"):
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

    add_scheduled_sugar_trap(campaign=campaign, start_day=start_day)
    campaign.save(filename)
    return filename
