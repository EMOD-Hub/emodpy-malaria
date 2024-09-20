from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json

schema_path = None
iv_name = "MosquitoRelease"


def MosquitoRelease(
        campaign,
        start_day: int = 0,
        released_number: int = None,
        released_fraction: float = None,
        released_infectious: float = 0,
        released_species: str = "arabiensis",
        released_genome: list = None,
        node_ids: list = None
):
    """
    Release mosquitoes of a given species and genome into each node.

    Args:
        campaign:
        start_day: The day to release the vectors.
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
        node_ids: The list of node IDs to receive a release of vectors.  The same 
            number of vectors will be released to each node.

    Returns:
    Formatted intervention
    """
    schema_path = campaign.schema_path
    if not released_genome:
        released_genome = [["X", "X"]]
    if (released_number and released_fraction) or (not released_number and not released_fraction):
        raise ValueError("Please define either released_number or released_fraction to determine how to release "
                         "mosquitoes, \n not both.\n")

    # First, get the objects
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)

    coordinator.Node_Property_Restrictions = []
    coordinator.Property_Restrictions_Within_Node = []
    coordinator.Property_Restrictions = []

    intervention = s2c.get_class_with_defaults("MosquitoRelease", schema_path)

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    event.Start_Day = start_day

    # Third, do the actual settings
    intervention.Intervention_Name = iv_name

    if released_number:
        intervention.Released_Type = "FIXED_NUMBER"
        intervention.Released_Number = released_number
    else:
        intervention.Released_Type = "FRACTION"
        intervention.Released_Fraction = released_fraction

    intervention.Released_Infectious = released_infectious
    intervention.Released_Species = released_species
    intervention.Released_Genome = released_genome
    intervention.Released_Wolbachia = "VECTOR_WOLBACHIA_FREE"

    event.Nodeset_Config = utils.do_nodes(schema_path, node_ids)

    return event


def new_intervention_as_file(camp, start_day: int = 1, filename: str = None):
    """

    Args:
        camp:
        start_day: The day to release the vectors.
        filename: name of campaign filename to be created

    Returns:
        returns filename
    """
    camp.add(MosquitoRelease(camp, start_day), first=True)
    if not filename:
        filename = "MosquitoRelease.json"
    camp.save(filename)
    return filename
