from emod_api import schema_to_class as s2c
from emodpy_malaria.interventions.common import add_campaign_event

iv_name = "MosquitoRelease"


def _mosquito_release(campaign,
                      intervention_name: str = iv_name,
                      released_number: int = None,
                      released_fraction: float = None,
                      released_infectious: bool = False,
                      released_species: str = "arabiensis",
                      released_genome: list = None,
                      released_microsopridia: bool = False
                      ):
    """
        Configures node-targeted MosquitoRelease intervention
    Args:
        campaign: A campaign builder that also contains schema_path parameters
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple MosquitoRelease interventions
            if they have different Intervention_Name values.
        released_number: The number of vectors to release, sets Released_Type = "FIXED_NUMBER"
        released_fraction: The fraction of the current population of mosquitoes to release.
            The 'population' will depend on the gender of the mosquitoes being
            released and it will be the population from the previous time step.
            Sets Released_Type = "FRACTION"
        released_infectious: The fraction of vectors released that are to be infectious.
            One can only use this feature when 'Malaria_Model'!='MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS'
        released_species: The case sensitive name of the species of vectors to be released.
        released_genome: This defines the alleles of the genome of the vectors to be released.
            It must define all of the alleles including the gender 'gene'.  '*' is not allowed.
        released_microsopridia: A boolean indicating if the released vectors are infected with microsporidia or not.

    Returns:
        Configured MosquitoRelease intervention
    """
    if not released_genome:
        released_genome = [["X", "X"]]
    if (released_number and released_fraction) or (not released_number and not released_fraction):
        raise ValueError("Please define either released_number or released_fraction to determine how to release "
                         "mosquitoes, \n not both.\n")

    intervention = s2c.get_class_with_defaults("MosquitoRelease", campaign.schema_path)
    intervention.Intervention_Name = intervention_name

    if released_number:
        intervention.Released_Number = released_number
    else:
        intervention.Released_Fraction = released_fraction

    intervention.Released_Infectious = 1 if released_infectious else 0
    intervention.Released_Species = released_species
    intervention.Released_Genome = released_genome
    intervention.Released_Wolbachia = "VECTOR_WOLBACHIA_FREE"
    intervention.Released_Microsporidia = 1 if released_microsopridia else 0
    return intervention


def add_scheduled_mosquito_release(
        campaign,
        start_day: int = 0,
        node_ids: list = None,
        repetitions: int = 1,
        timesteps_between_repetitions: int = 365,
        intervention_name: str = iv_name,
        released_number: int = None,
        released_fraction: float = None,
        released_infectious: bool = False,
        released_species: str = "arabiensis",
        released_genome: list = None,
        released_microsopridia: bool = False):
    """
        Adds to the campaign a node-level MosquitoRelease intervention

    Args:
        campaign: A campaign builder that also contains schema_path parameters
        start_day: The day to release the vectors.
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple MosquitoRelease interventions
            if they have different Intervention_Name values.
        released_number: The number of vectors to release, sets Released_Type = "FIXED_NUMBER"
        released_fraction: The fraction of the current population of mosquitoes to release.
            The 'population' will depend on the gender of the mosquitoes being
            released and it will be the population from the previous time step.
            Sets Released_Type = "FRACTION"
        released_infectious: The fraction of vectors released that are to be infectious.
            One can only use this feature when 'Malaria_Model'!='MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS'
        released_species: The case sensitive name of the species of vectors to be released.
        released_genome: This defines the alleles of the genome of the vectors to be released.
            It must define all of the alleles including the gender 'gene'.  '*' is not allowed.
        released_microsopridia: A boolean indicating if the released vectors are infected with microsporidia or not.

    Returns:
        Formatted intervention
    """

    if not released_genome:
        released_genome = [["X", "X"]]
    if (released_number and released_fraction) or (not released_number and not released_fraction):
        raise ValueError("Please define either released_number or released_fraction to determine how to release "
                         "mosquitoes, \n not both.\n")

    node_intervention = _mosquito_release(campaign=campaign,
                                          intervention_name=intervention_name,
                                          released_number=released_number,
                                          released_fraction=released_fraction,
                                          released_infectious=released_infectious,
                                          released_species=released_species,
                                          released_genome=released_genome,
                                          released_microsopridia=released_microsopridia)
    add_campaign_event(campaign=campaign,
                       start_day=start_day,
                       node_ids=node_ids,
                       repetitions=repetitions,
                       timesteps_between_repetitions=timesteps_between_repetitions,
                       node_intervention=node_intervention)


def new_intervention_as_file(campaign, start_day: int = 1, filename: str = "MosquitoRelease.json"):
    """
        Creates a campaign file with a MosquitoRelease intervention
        
    Args:
        campaign: A campaign builder that also contains schema_path parameters
        start_day: The day to release the vectors.
        filename: name of campaign filename to be created

    Returns:
        returns filename
    """
    add_scheduled_mosquito_release(campaign=campaign, start_day=start_day, released_number=1)
    campaign.save(filename)
    return filename
