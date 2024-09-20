from emod_api import schema_to_class as s2c
from emodpy_malaria.interventions.common import add_campaign_event


def add_challenge_trial(campaign, start_day: int = 0, node_ids: list = None, demographic_coverage: float = 1,
                        infectious_bites: int = 5, sporozoites: int = 0, intervention_name: str = "MalariaChallenge"):
    """
        Add an intervention to distribute an infectious challenge mosquito bites or sporozoites to individuals
        to the campaign using the **MalariaChallenge** class, a node-level intervention.

    Args:
        campaign: A campaign builder that also contains schema_path parameters
        start_day: The day to distribute the intervention; default = 0.
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        demographic_coverage: The fraction of individuals receiving the challenge
        infectious_bites: The number of infectious bites a person is challenged with, Default: 5
            sprorozoites needs to be set to 0
        sporozoites: The number of sporozoites a person is challenged with. Default: 0. To use "sporozoites", set
            infectious_bites to 0.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class.

    Returns:
        Nothing

    """
    if sporozoites and infectious_bites:
        raise ValueError(f"Please enter a positive value for either 'infectious_bites' or 'sporozoites', "
                         f"but not both.\n")

    intervention = _malaria_challenge(campaign, demographic_coverage=demographic_coverage,
                                      infectious_bites=infectious_bites, sporozoites=sporozoites,
                                      intervention_name=intervention_name)

    add_campaign_event(campaign, start_day=start_day, node_ids=node_ids, node_intervention=intervention)


def _malaria_challenge(campaign, demographic_coverage: float = 1, infectious_bites: int = 5, sporozoites: int = 0,
                       intervention_name: str = "MalariaChallenge"):
    """
        Configures a MalariaChallenge node-level intervention

    Args:
        campaign: A campaign builder that also contains schema_path parameters
        demographic_coverage: The fraction of individuals receiving the challenge
        infectious_bites: The number of infectious bites a person is challenged with, Default: 5
            sprorozoites needs to be set to 0
        sporozoites: The number of sporozoites a person is challenged with. Default: 0. To use "sporozoites", set
            infectious_bites to 0.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class.

    Returns:
        Configured MalariaChallenge intervention object
    """
    schema_path = campaign.schema_path
    intervention = s2c.get_class_with_defaults("MalariaChallenge", schema_path)
    intervention.Intervention_Name = intervention_name
    intervention.Coverage = demographic_coverage
    if sporozoites:
        intervention.Sporozoite_Count = sporozoites
    elif infectious_bites:
        intervention.Infectious_Bite_Count = infectious_bites
    else:
        raise ValueError(f"Please enter a positive value for either 'infectious_bites' or 'sporozoites', "
                         f"but not both.\n")

    return intervention
