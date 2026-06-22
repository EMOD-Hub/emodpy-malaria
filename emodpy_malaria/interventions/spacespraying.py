from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emodpy_malaria.interventions.common import add_campaign_event

iv_name = "SpaceSpraying"


def add_scheduled_space_spraying(
        campaign,
        start_day: int = 1,
        node_ids: list = None,
        repetitions: int = 1,
        timesteps_between_repetitions: int = 365,
        spray_coverage: float = 1.0,
        insecticide: str = "",
        killing_initial_effect: float = 1,
        killing_box_duration: float = -1,
        killing_decay_time_constant: float = 0,
        intervention_name: str = iv_name,
        cost_to_consumer: float = 0
):
    """
    Configures and adds a node-targeted **SpaceSpraying** intervention to the campaign.

    For killing effects - depending on the parameters you set,
    different **WaningEffect** classes will be used:<br>
        • box_duration = -1 => WaningEffectConstant, decay_time_constant is ignored<br>
        • box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential<br>
        • box_duration > 0 + decay_time_constant = 0 => WaningEffectBox<br>
        • box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential<br>

    Args:
        campaign (emodpy.campaign.emod_campaign.EMODCampaign): campaign object to which the intervention will be added, and schema_path container
        start_day (int): The day the intervention is given out.
        node_ids (list): List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention.
        repetitions (int): The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**.
        timesteps_between_repetitions (int): The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**.
        spray_coverage (float): The portion of the node that has been sprayed. This value is multiplied by the current
            efficacy of the **WaningEffect**.
        insecticide (str): The name of the insecticide defined in <config.Insecticides> for this intervention.
            If insecticides are being used, then this must be defined as one of those values. If they are not
            being used, then this does not needed to be specified or can be empty string. It cannot have a
            value if <config.Insecticides> does not define anything.
        intervention_name (str): The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It is possible to have multiple **SpaceSpraying** interventions
            if they have different **Intervention_Name** values.
        killing_initial_effect (float): Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration (float): Box duration of effect in days before the decay of **killing_initial_effect**.
            -1 indicates effect is indefinite (WaningEffectConstant).
        killing_decay_time_constant (float): The exponential decay length, in days of the **killing_initial_effect**.
        cost_to_consumer (float): Per unit cost when distributed.

    """
    node_intervention = _space_spraying(campaign=campaign,
                                        spray_coverage=spray_coverage,
                                        insecticide=insecticide,
                                        intervention_name=intervention_name,
                                        killing_initial_effect=killing_initial_effect,
                                        killing_box_duration=killing_box_duration,
                                        killing_decay_time_constant=killing_decay_time_constant,
                                        cost_to_consumer=cost_to_consumer)
    add_campaign_event(campaign=campaign,
                       start_day=start_day,
                       node_ids=node_ids,
                       repetitions=repetitions,
                       timesteps_between_repetitions=timesteps_between_repetitions,
                       node_intervention=node_intervention)


def _space_spraying(campaign,
                    spray_coverage: float = 1.0,
                    insecticide: str = "",
                    killing_initial_effect: float = 1,
                    killing_box_duration: float = -1,
                    killing_decay_time_constant: float = 0,
                    intervention_name: str = iv_name,
                    cost_to_consumer: float = 0):
    """
    Configures the node-targeted **SpaceSpraying** intervention.

    Args:
        campaign (emodpy.campaign.emod_campaign.EMODCampaign): campaign object to which the intervention will be added, and schema_path container
        spray_coverage (float): The portion of the node that has been sprayed.  This value is multiplied by the current
            efficacy of the WaningEffect
        insecticide (str): The name of the insecticide defined in <config.Insecticides> for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if <config.Insecticides> does not define anything.
        intervention_name (str): The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It is possible to have multiple **SpaceSpraying** interventions
            if they have different **Intervention_Name** values.
        killing_initial_effect (float): Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration (float): Box duration of effect in days before the decay of **killing_initial_effect**.
            -1 indicates effect is indefinite (WaningEffectConstant)
        killing_decay_time_constant (float): The exponential decay length, in days of the **killing_initial_effect**.
        cost_to_consumer (float): Per unit cost when distributed.

    Returns:
        Configured **SpaceSpraying** intervention.
    """
    schema_path = campaign.schema_path

    intervention = s2c.get_class_with_defaults("SpaceSpraying", campaign.schema_path)
    intervention.Intervention_Name = intervention_name
    intervention.Insecticide_Name = insecticide
    intervention.Spray_Coverage = spray_coverage
    intervention.Cost_To_Consumer = cost_to_consumer
    intervention.Killing_Config = utils.get_waning_from_params(schema_path=schema_path,
                                                               initial=killing_initial_effect,
                                                               box_duration=killing_box_duration,
                                                               decay_time_constant=killing_decay_time_constant)

    return intervention


def new_intervention_as_file(campaign, start_day: int = 0, filename: str = "SpaceSpraying.json"):
    """
    Creates a file with **SpaceSpraying** intervention.

    Args:
        campaign (emodpy.campaign.emod_campaign.EMODCampaign): campaign object to which the intervention will be added, and schema_path container
        start_day (int): the day to distribute the **SpaceSpraying** intervention
        filename (str): name of the filename created.

    Returns:
        (str): filename of the file created.
    """
    add_scheduled_space_spraying(campaign=campaign, start_day=start_day)
    campaign.save(filename)
    return filename
