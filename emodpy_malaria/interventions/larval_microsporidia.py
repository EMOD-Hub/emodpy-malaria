from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emodpy_malaria.interventions.common import add_campaign_event


def _larval_microsporidia(
        campaign,
        strain_name: str,
        habitat_coverage: float = 1.0,
        habitat_target: str = "ALL_HABITATS",
        initial_infectivity: float = 1,
        box_duration: int = 100,
        decay_time_constant: float = 0.0,
        intervention_name: str = "LarvalMicrosporidiaIntervention",
        cost_to_consumer: float = 0):
    """
    Create a **LarvalMicrosporidiaIntervention** to be used in a campaign event.

    Args:
        campaign (emodpy.campaign.emod_campaign.EMODCampaign): The campaign object to which the intervention will be added. Provides the schema path.
        strain_name (str): The microsporidia strain with which to treat the habitat. This must be a known strain defined in
            the vector species parameters. This parameter is required to create the intervention, and there is no default value.
        habitat_coverage (float): Portion of habitat that is treated with the intervention. Values must be between 0 and 1. Default is 1.0.
        habitat_target (str): The type of habitat to target with the intervention. Default is "ALL_HABITATS".
            Habitat target is limited to habitats defined for the species that the microsporidia strain infects.
        initial_infectivity (float): The initial infectivity of the intervention, which defines the portion of larvae that
            are infected each day the intervention exists. Must be between 0 and 1. Default is 1.
        box_duration (int): The duration, in days, of the initial infectivity before it begins to wane.
            If box_duration = -1, the intervention will have a constant effect and decay_time_constant will be
            ignored. If box_duration = 0 and decay_time_constant > 0, the intervention will have an exponential
            decaying effect. If box_duration > 0 and decay_time_constant = 0, the intervention will have a
            box-shaped waning effect. If box_duration > 0 and decay_time_constant > 0, the intervention will
            have a box-shaped waning effect followed by an exponential decay. Default is 100.
        decay_time_constant (float): The time constant for the exponential decay of the intervention's effect, in days. Only
            relevant if box_duration = 0 or > 0 as described above in box_duration. Default is 0.0.
        intervention_name (str): The name of the intervention, for organizational purposes. Default
            is "LarvalMicrosporidiaIntervention".
        cost_to_consumer (float): The cost to consumer for each distribution of this intervention, if any. Default is 0.

    Returns:
        Configured **LarvalMicrosporidiaIntervention** object that can be added to a campaign event.
    """
    if not strain_name:
        raise ValueError("strain_name is required to create a LarvalMicrosporidiaIntervention. Please provide "
                         "a valid strain_name that is defined in the vector species parameters.")
    intervention = s2c.get_class_with_defaults("LarvalMicrosporidiaIntervention", campaign.schema_path)
    intervention.Intervention_Name = intervention_name
    intervention.Habitat_Coverage = habitat_coverage
    intervention.Habitat_Target = habitat_target
    intervention.Cost_To_Consumer = cost_to_consumer
    intervention.Strain_Name = strain_name
    intervention.Infectivity_Config = utils.get_waning_from_params(campaign.schema_path,
                                                                   initial=initial_infectivity,
                                                                   box_duration=box_duration,
                                                                   decay_time_constant=decay_time_constant)
    return intervention


def add_larval_microsporidia(
        campaign,
        strain_name: str,
        start_day: int = 1,
        num_repetitions: int = 1,
        timesteps_between_reps: int = 365,
        node_ids: list = None,
        node_property_restrictions: list[dict] = None,
        habitat_coverage: float = 1.0,
        habitat_target: str = "ALL_HABITATS",
        initial_infectivity: float = 1,
        box_duration: int = 100,
        decay_time_constant: float = 0.0,
        intervention_name: str = "LarvalMicrosporidiaIntervention",
        cost_to_consumer: float = 0
):
    """
    Create a new scheduled **LarvalMicrosporidia** intervention and add it to the campaign.
    This is a Node-level intervention that mimics seeding water bodies with microsporidia to infect mosquito
    larvae, reducing their ability to transmit malaria. The intervention can be configured with a habitat target
    (e.g., specific types of water bodies) and an initial infectivity which defines the portion of larvae that are
    infected each day the intervention exists. The effect of the intervention can wane over time, and the
    waning can be configured with a **box_duration** and **decay_time_constant** parameters.

    The intervention expires and is removed when infectivity reaches near-zero.

    Already existing **LarvalMicrosporidia** intervention(s) continue(s) to exist together with any new
    **LarvalMicrosporidia** interventions. Their effects, when affecting the same species in the same habitat,
    are resolved with the algorithm that can be found in
    the [LarvalMicrosporidiaIntervention Documentation](https://emod.idmod.org/emodpy-malaria/emod/parameter-campaign-node-larvalmicrosporidiaintervention/)


    Args:
        campaign (emodpy.campaign.emod_campaign.EMODCampaign): The campaign object to which the intervention will be added. Provides the schema path.
        strain_name (str): The microsporidia strain with which to treat the habitat. This must be a known strain defined in the vector species parameters.
        start_day (int): the day to distribute the **LarvalMicrosporidia** intervention for the first time. Default is 1.
        num_repetitions (int): Number of times to distribute the intervention.<br>
            If **num_repetitions** > 1, the intervention will be distributed every **timesteps_between_reps** days after the initial **start_day**.<br>
            If **num_repetitions** = 1, the intervention will be distributed once on **start_day**.<br>
            If **num_repetitions** = 2, the intervention will be distributed on **start_day** and (**start_day** + **timesteps_between_reps**), etc.<br>
            If **num_repetitions** = -1, the intervention will be distributed on **start_day** and every **timesteps_between_reps** indefinitely.<br>
        timesteps_between_reps (int): Number of days between repeated distributions of the intervention. Only relevant if **num_repetitions** > 1 or -1
            as described above in **num_repetitions**.
        node_ids (list): List of node IDs to which the intervention will be applied. If None, the intervention will be applied to all nodes.
        node_property_restrictions (list): A list of dictionaries of **NodeProperties** which the node must have to receive the intervention. If left at None,
            all nodes in **node_ids** receive the intervention.
        habitat_coverage (float): Portion of habitat that is treated with the intervention. Value must be between 0 and 1. Default is 1.0.
        habitat_target (str): The type of habitat to target with the intervention. Default is "ALL_HABITATS". Habitat target is limited to habitats defined for the species that the microsporidia strain infects.
        initial_infectivity (float): The initial infectivity of the intervention, which defines the portion of larvae that are infected each day the intervention exists.
            Must be between 0 and 1.
        box_duration (int): The duration, in days, of the initial infectivity before it begins to wane.<br>
            If **box_duration** = -1, the intervention will have a constant effect and **decay_time_constant** will be ignored.<br>
            If **box_duration** = 0 and **decay_time_constant** > 0, the intervention will have an exponential decaying effect.<br>
            If **box_duration** > 0 and **decay_time_constant** = 0, the intervention will have a box-shaped waning effect.<br>
            If **box_duration** > 0 and **decay_time_constant** > 0, the intervention will have a box-shaped waning effect followed by an exponential decay.<br>
        decay_time_constant (float): The time constant for the exponential decay of the intervention's effect, in days. Only relevant if **box_duration** = 0 or > 0
            as described above in **box_duration**.
        intervention_name (str): (Optional) The name of the intervention, for organizational purposes. Default is "LarvalMicrosporidiaIntervention".
        cost_to_consumer (float): The cost to consumer for each distribution of this intervention, if any. Default is 0.
    """
    node_intervention = _larval_microsporidia(campaign=campaign,
                                              habitat_coverage=habitat_coverage,
                                              habitat_target=habitat_target,
                                              initial_infectivity=initial_infectivity,
                                              box_duration=box_duration,
                                              decay_time_constant=decay_time_constant,
                                              strain_name=strain_name,
                                              intervention_name=intervention_name,
                                              cost_to_consumer=cost_to_consumer)
    add_campaign_event(campaign=campaign,
                       start_day=start_day,
                       node_ids=node_ids,
                       repetitions=num_repetitions,
                       timesteps_between_repetitions=timesteps_between_reps,
                       node_intervention=node_intervention,
                       node_property_restrictions=node_property_restrictions)
