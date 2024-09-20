"""
This module contains functionality for vaccine distribution.
"""

from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emod_api.interventions import common
from emodpy_malaria.interventions.outbreak import add_campaign_event


def _intervention(campaign,
                  vaccine_type: str = "AcquisitionBlocking",
                  vaccine_take: float = 1,
                  vaccine_initial_effect: float = 1,
                  vaccine_box_duration: int = 365,
                  vaccine_exponential_decay_rate: float = 1.0,
                  efficacy_is_multiplicative: bool = True):
    """
        Configures a SimpleVaccine intervention.

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        vaccine_type: The type of vaccine to distribute in a vaccine intervention. Options are: "Generic",
            "TransmissionBlocking", "AcquisitionBlocking", "MortalityBlocking"
        vaccine_take: The rate at which delivered vaccines will successfully stimulate an immune response and achieve
            the desired efficacy.
        vaccine_initial_effect: Initial efficacy of the vaccine, before decay.
        vaccine_box_duration: Duration in days of initial efficacy of vaccine before it starts to decay.
        vaccine_exponential_decay_rate: The exponential rate of vaccine efficacy after the box duration.
        efficacy_is_multiplicative: The overall vaccine efficacy when individuals receive more than one vaccine.
            When set to true (1), the vaccine efficacies are multiplied together; when set to false (0), the
            efficacies are additive.

    Returns:
        Configured SimpleVaccine intervention
    """
    vaccine_types = ["Generic", "TransmissionBlocking", "AcquisitionBlocking", "MortalityBlocking"]
    if vaccine_type not in vaccine_types:
        ValueError(f"Please specify a valid vaccine_type, vaccine_types are {vaccine_types}.")

    schema_path = campaign.schema_path
    intervention = s2c.get_class_with_defaults("SimpleVaccine", schema_path)
    intervention.Vaccine_Type = vaccine_type
    intervention.Vaccine_Take = vaccine_take
    intervention.Efficacy_Is_Multiplicative = 1 if efficacy_is_multiplicative else 0
    intervention.Waning_Config = utils.get_waning_from_params(schema_path,
                                                              vaccine_initial_effect,
                                                              vaccine_box_duration,
                                                              vaccine_exponential_decay_rate)

    return intervention


def add_scheduled_vaccine(campaign,
                          start_day: int = 1,
                          demographic_coverage: float = 1.0,
                          target_num_individuals: int = None,
                          node_ids: list = None,
                          repetitions: int = 1,
                          timesteps_between_repetitions: int = 365,
                          ind_property_restrictions: list = None,
                          node_property_restrictions: list = None,
                          target_age_min: int = 0,
                          target_age_max: int = 125,
                          target_gender: str = "All",
                          broadcast_event: str = None,
                          vaccine_type: str = "AcquisitionBlocking",
                          vaccine_take: float = 1,
                          vaccine_initial_effect: float = 1,
                          vaccine_box_duration: int = 365,
                          vaccine_exponential_decay_rate: float = 1.0,
                          efficacy_is_multiplicative: bool = True):
    """
        Adds a scheduled SimpleVaccine event, with an optional BroadcastEvent, broadcast when vaccine is received.

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
        node_property_restrictions: A list of the NodeProperty key:value pairs, as defined in the demographics file,
            that nodes must have to receive the intervention. Sets **Node_Property_Restrictions**
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        broadcast_event: "The name of the event to be broadcast. This event must be set in the
            **Custom_Coordinator_Events** configuration parameter. When None or Empty, nothing is broadcast.
        vaccine_type: The type of vaccine to distribute in a vaccine intervention. Options are: "Generic",
            "TransmissionBlocking", "AcquisitionBlocking", "MortalityBlocking"
        vaccine_take: The rate at which delivered vaccines will successfully stimulate an immune response and achieve
            the desired efficacy.
        vaccine_initial_effect: Initial efficacy of the vaccine, before decay.
        vaccine_box_duration: Duration in days of initial efficacy of vaccine before it starts to decay.
        vaccine_exponential_decay_rate: The exponential rate of vaccine efficacy after the box duration.
        efficacy_is_multiplicative: The overall vaccine efficacy when individuals receive more than one vaccine.
            When set to true (1), the vaccine efficacies are multiplied together; when set to false (0), the
            efficacies are additive.

    Returns:
        Nothing
    """

    intervention_list = [_intervention(campaign, vaccine_type=vaccine_type,
                                       vaccine_take=vaccine_take,
                                       vaccine_initial_effect=vaccine_initial_effect,
                                       vaccine_box_duration=vaccine_box_duration,
                                       vaccine_exponential_decay_rate=vaccine_exponential_decay_rate,
                                       efficacy_is_multiplicative=efficacy_is_multiplicative)]
    if broadcast_event:
        intervention_list.append(common.BroadcastEvent(campaign, Event_Trigger=broadcast_event))

    add_campaign_event(campaign=campaign,
                       start_day=start_day,
                       demographic_coverage=demographic_coverage,
                       target_num_individuals=target_num_individuals,
                       node_ids=node_ids,
                       repetitions=repetitions,
                       timesteps_between_repetitions=timesteps_between_repetitions,
                       ind_property_restrictions=ind_property_restrictions,
                       node_property_restrictions=node_property_restrictions,
                       target_age_min=target_age_min,
                       target_age_max=target_age_max,
                       target_gender=target_gender,
                       intervention=intervention_list)


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
    add_scheduled_vaccine(campaign, start_day)
    if filename is None:
        filename = "SimpleVaccine.json"
    campaign.save(filename)
    return filename
