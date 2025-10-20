from emod_api import schema_to_class as s2c
from emod_api.interventions import utils, common

iv_name = "Larvicides"

# TBD: since this is a private function it probably doesn't need defaults or even hints.
def _create_intervention(
        campaign,
        spray_coverage: float = 1.0,
        killing_effect: float = 1,
        habitat_target: str = None,
        insecticide: str = None,
        box_duration: int = 100,
        decay_time_constant: float = 0.0
    ):
    intervention = s2c.get_class_with_defaults("Larvicides", campaign.schema_path)
    intervention.Intervention_Name = iv_name
    intervention.Spray_Coverage = spray_coverage
    intervention.Habitat_Target = habitat_target
    if insecticide:
        intervention.Insecticide_Name = insecticide
    else:
        intervention.pop( "Insecticide_Name" )

    # Users prefer time contant. g_w_f_p currently takes rate, but about to be changed. 
    rate = 1.0/decay_time_constant if decay_time_constant>0 else 0
    killing = utils.get_waning_from_params(campaign.schema_path, killing_effect, box_duration, rate)
    intervention.Larval_Killing_Config = killing
    return intervention

def _create_event(
        campaign,
        start_day: int = 1,
        num_repetitions: int = -1,
        timesteps_between_reps: int = 365,
        spray_coverage: float = 1.0,
        killing_effect: float = 1,
        habitat_target: str = "ALL_HABITATS",
        insecticide: str = None,
        box_duration: int = 100,
        decay_time_constant: float = 0.0,
        node_ids: list = None
):
    """
        Create a new Larvicides scheduled campaign intervention.
        box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
        box_duration > 0 + decay_time_constant = 0 => WaningEffectBox/Constant (depending on duration)
        box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential

        Args:
            campaign:
            start_day: the day to distribute the Larvicides intervention
            num_repetitions: Optional number of repetitions.
            timesteps_between_reps: Gap between repetitions, if num_reptitions specified.
            spray_coverage: how much of each node to cover (total portion killed = killing effect * coverage)
            killing_effect: portion of vectors killed by the intervention (Initial_Effect in WaningEffect)
            habitat_target: E.g., (TBD)
            box_duration: Box_Duration of the WaningEffect
            decay_time_constant: decay_time_constant of the WaningEffect
            node_ids: list of node ids to which distribute the intervention

        Returns:
            The formatted intervention ready to be added to the campaign.

    """
    intervention = _create_intervention( campaign, spray_coverage=spray_coverage, killing_effect=killing_effect, habitat_target=habitat_target, box_duration=box_duration, decay_time_constant=decay_time_constant, insecticide=insecticide ) 
    sce = common.ScheduledCampaignEvent( campaign, Start_Day=start_day, Number_Repetitions=num_repetitions, Timesteps_Between_Repetitions=timesteps_between_reps, Intervention_List=[intervention], Node_Ids=node_ids )
    return sce

def add_larvicide(
        campaign,
        start_day: int = 1,
        num_repetitions: int = -1,
        timesteps_between_reps: int = 365,
        spray_coverage: float = 1.0,
        killing_effect: float = 1,
        habitat_target: str = "ALL_HABITATS",
        insecticide: str = None,
        box_duration: int = 100,
        decay_time_constant: float = 0.0,
        node_ids: list = None
    ):
    """
        Create a new Larvicides scheduled campaign intervention & add to campaign.
        box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
        box_duration > 0 + decay_time_constant = 0 => WaningEffectBox/Constant (depending on duration)
        box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential

        Inspired by: https://github.com/InstituteforDiseaseModeling/dtk-tools/blob/master/dtk/interventions/novel_vector_control.py#L279.

        Args:
            campaign:
            start_day: the day to distribute the Larvicides intervention.
            num_repetitions: Optional number of repetitions.
            timesteps_between_reps: Gap between repetitions, if num_reptitions specified.
            spray_coverage: how much of each node to cover (total portion killed = killing effect * coverage).
            killing_effect: portion of vectors killed by the intervention (Initial_Effect in WaningEffect).
            habitat_target: Possible values are: "TEMPORARY_RAINFALL", "WATER_VEGETATION", "HUMAN_POPULATION",
                "CONSTANT", "BRACKISH_SWAMP", "LINEAR_SPLINE", "ALL_HABITATS". The latter is the default.
            insecticide: insecticide name. Must be a value in the config but consistency is not checked at this time.
            box_duration: Box_Duration of the WaningEffect.
            decay_time_constant: decay_time_constant of the WaningEffect.
            node_ids: list of node ids to which distribute the intervention.

        Returns:
            N/A.
    """

    campaign.add(_create_event(campaign, start_day=start_day, spray_coverage=spray_coverage,
                               killing_effect=killing_effect, habitat_target=habitat_target,
                               insecticide=insecticide, box_duration=box_duration,
                               decay_time_constant=decay_time_constant, node_ids=node_ids ) )


def new_intervention_as_file(campaign, start_day: int = 1, filename: str = None):
    """
    Creates a file with Larvicides intervention
    Args:
        campaign:
        start_day: the day to distribute the Larvicides intervention
        filename: name of the filename created

    Returns:
    filename of the file created
    """

    campaign.reset()
    add_larvicide( campaign, start_day=start_day )
    if filename is None:
        filename = "Larvicides.json"
    campaign.save(filename)
    return filename
