from emod_api import schema_to_class as s2c
from emodpy_malaria.interventions.common import add_campaign_event


def add_scheduled_antimalarial_drug(
        campaign,
        start_day: int = 1,
        demographic_coverage: float = 1.0,
        target_num_individuals: int = None,
        node_ids: list = None,
        repetitions: int = 1,
        timesteps_between_repetitions: int = 365,
        ind_property_restrictions: list = None,
        target_age_min: int = 0,
        target_age_max: int = 125,
        target_gender: str = "All",
        drug_type: str = None,
        cost_to_consumer: float = 0,
        intervention_name: str = None
):
    """
    Add an antimalarial drug intervention to your campaign. This is equivalent to 
    :doc:`emod-malaria:parameter-campaign-individual-antimalarialdrug`.

    Args:
        campaign: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will be added.
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
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        drug_type: The name of the drug to distribute in a drug intervention. Possible values are
            contained in **Malaria_Drug_Params** in :doc:`emod-malaria:parameter-configuration-drugs`.
            Use :py:meth:`~emodpy_malaria.config.set_team_drug_params` to set those values
        cost_to_consumer: Per-unit cost when drug is distributed
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class.  Default is AntimalarialDrug_<drug_type>.

    Returns:
        The intervention event.
    """
    antimalarial_drug = _antimalarial_drug(campaign=campaign,
                                           drug_type=drug_type,
                                           cost_to_consumer=cost_to_consumer,
                                           intervention_name=intervention_name)
    add_campaign_event(campaign=campaign,
                       start_day=start_day, demographic_coverage=demographic_coverage,
                       target_num_individuals=target_num_individuals, node_ids=node_ids,
                       repetitions=repetitions, timesteps_between_repetitions=timesteps_between_repetitions,
                       ind_property_restrictions=ind_property_restrictions,
                       target_age_max=target_age_max, target_age_min=target_age_min,
                       target_gender=target_gender, individual_intervention=antimalarial_drug)


def _antimalarial_drug(campaign,
                       drug_type: str = None,
                       cost_to_consumer: float = 0,
                       intervention_name: str = None):
    """
        Configures individual-targeted AntimalarialDrug intervention
    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        drug_type: The name of the drug to distribute in a drug intervention. Possible values are
            contained in **Malaria_Drug_Params** in :doc:`emod-malaria:parameter-configuration-drugs`.
            Use :py:meth:`~emodpy_malaria.config.set_team_drug_params` to set those values
        cost_to_consumer: Per-unit cost when drug is distributed
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. Default is AntimalarialDrug_<drug_type>.

    Returns:
        Configured individual-targeted AntimalarialDrug intervention
    """
    if not drug_type:
        raise ValueError("Please pass in 'drug_type', as defined in Malaria_Drug_Params.Name.\n")
    intervention = s2c.get_class_with_defaults("AntimalarialDrug", campaign.schema_path)
    intervention.Drug_Type = drug_type
    intervention.Cost_To_Consumer = cost_to_consumer
    intervention.Intervention_Name = intervention_name if intervention_name else "AntimalarialDrug_" + drug_type
    return intervention


def new_intervention_as_file(campaign, start_day, drug_type="Chloroquine", filename="AntimalarialDrug.json"):
    """
    Take an :doc:`emod-malaria:parameter-campaign-individual-antimalarialdrug`
    intervention from a JSON file and add it to your campaign.

    Args:
        campaign: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will be added.
        start_day: The day of the simulation on which the drug is distributed. We recommend 
            aligning this with the start of the simulation.
        drug_type: The name of the drug to distribute in a drug intervention. Possible values are
            contained in **Malaria_Drug_Params** in :doc:`emod-malaria:parameter-configuration-drugs`.
            Use :py:meth:`~emodpy_malaria.config.set_team_drug_params` to set those values
        filename: The JSON file that contains the intervention.

    Returns:
        The filename.
    """
    add_scheduled_antimalarial_drug(campaign=campaign, start_day=start_day, drug_type=drug_type)
    campaign.save(filename)
    return filename
