from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emodpy_malaria.interventions.common import add_campaign_event


def _larvicides(
        campaign,
        spray_coverage: float = 1.0,
        killing_effect: float = 1,
        habitat_target: str = None,
        insecticide: str = None,
        box_duration: int = 100,
        decay_time_constant: float = 0.0,
        intervention_name: str = "Larvicides",
        cost_to_consumer: float = 0
):
    intervention = s2c.get_class_with_defaults("Larvicides", campaign.schema_path)
    intervention.Intervention_Name = intervention_name
    intervention.Spray_Coverage = spray_coverage
    intervention.Habitat_Target = habitat_target
    intervention.Cost_To_Consumer = cost_to_consumer
    if insecticide:
        intervention.Insecticide_Name = insecticide
    else:
        intervention.pop("Insecticide_Name")

    intervention.Larval_Killing_Config = utils.get_waning_from_params(campaign.schema_path,
                                                                      initial=killing_effect,
                                                                      box_duration=box_duration,
                                                                      decay_time_constant=decay_time_constant)
    return intervention


def add_larvicide(
        campaign,
        start_day: int = 1,
        num_repetitions: int = 0,
        timesteps_between_reps: int = 365,
        spray_coverage: float = 1.0,
        killing_effect: float = 1,
        habitat_target: str = "ALL_HABITATS",
        insecticide: str = None,
        box_duration: int = 100,
        decay_time_constant: float = 0.0,
        node_ids: list = None,
        intervention_name: str = "Larvicides",
        cost_to_consumer: float = 0,
        node_property_restrictions: dict = None
):
    """
    Create a new **Larvicides** scheduled campaign intervention.

    For killing effects - depending on the parameters you set, different **WaningEffect** classes will be used:<br>
        • box_duration = -1 => WaningEffectConstant, decay_time_constant is ignored<br>
        • box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential<br>
        • box_duration > 0 + decay_time_constant = 0 => WaningEffectBox<br>
        • box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential<br>

    Args:
        campaign (emodpy.campaign.emod_campaign.EMODCampaign):
        start_day (int): the day to distribute the **Larvicides** intervention.
        num_repetitions (int): Optional number of repetitions.
        timesteps_between_reps (int): Gap between repetitions, if **num_repetitions** is specified.
        spray_coverage (float): How much of each node to cover (total portion killed = killing effect * coverage).
        killing_effect (float): Portion of vectors killed by the intervention (Initial_Effect in WaningEffect).
        habitat_target (str): The type of habitat to target with the intervention. Default is "ALL_HABITATS".
        box_duration (int): Box_Duration of the WaningEffect
        decay_time_constant (float): decay_time_constant of the WaningEffect
        node_ids (list): list of node ids to which distribute the intervention
        insecticide (str): name of the insecticide defined in <config.Insecticides> for this intervention
        intervention_name (str): name of the intervention
        cost_to_consumer (float): Per unit cost when distributed
        node_property_restrictions (dict): dict of node property restrictions
    """
    node_intervention = _larvicides(campaign=campaign,
                                    spray_coverage=spray_coverage,
                                    insecticide=insecticide,
                                    habitat_target=habitat_target,
                                    intervention_name=intervention_name,
                                    killing_effect=killing_effect,
                                    box_duration=box_duration,
                                    decay_time_constant=decay_time_constant,
                                    cost_to_consumer=cost_to_consumer)
    add_campaign_event(campaign=campaign,
                       start_day=start_day,
                       node_ids=node_ids,
                       repetitions=num_repetitions,
                       timesteps_between_repetitions=timesteps_between_reps,
                       node_intervention=node_intervention,
                       node_property_restrictions=node_property_restrictions
                       )


def new_intervention_as_file(campaign, start_day: int = 1, filename: str = None):
    """
    Creates a file with **Larvicides** intervention.

    Args:
        campaign (emodpy.campaign.emod_campaign.EMODCampaign): campaign object to which the intervention will be added.
        start_day (int): the day to distribute the **Larvicides** intervention.
        filename (str): name of the filename created.

    Returns:
        (str): filename of the file created
    """

    campaign.reset()
    add_larvicide(campaign, start_day=start_day)
    if filename is None:
        filename = "Larvicides.json"
    campaign.save(filename)
    return filename
