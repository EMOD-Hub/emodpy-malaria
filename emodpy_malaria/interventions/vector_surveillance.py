import emod_api.config.default_from_schema_no_validation as dfs
from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from enum import Enum
from emod_api.utils import Distributions


class CountType(Enum):
    ALLELE_FREQ = "ALLELE_FREQ"
    GENOME_FRACTION = "GENOME_FRACTION"


class VectorGender(Enum):
    VECTOR_FEMALE = "VECTOR_FEMALE"
    VECTOR_MALE = "VECTOR_MALE"
    VECTOR_BOTH_GENDERS = "VECTOR_BOTH_GENDERS"


def add_vector_surveillance_event_coordinator(
        campaign,
        start_trigger_condition_list: list,
        update_period: float,
        sample_size: dict,
        species: str,
        gender: VectorGender,
        count_type: CountType,
        coordinator_name: str = None,
        node_ids: list = None,
        start_day: int = 0,
        duration: int = None,
        stop_trigger_condition_list: list = None,
        survey_completed_event: str = None
):
    """
    This function adds a VectorSurveillanceEventCoordinator to the campaign.

    VectorSurveillanceEventCoordinator is a coordinator that samples the vector population at a given interval.
    The vector population sampled is determined by the species and gender parameters. The number of vectors sampled
    is determined by the sample_size parameter, which defines a distribution from which the sample size is drawn at each
    sampling event.

    The results of the surveillance are passed to the respond() function in dtk_vector_surveillance.py.
    Surveillance results are two lists: list_data_names and list_data_values. The list_data_names list contains the
    names of all the alleles present (when CountType.ALLELE_FREQ) or genomes possible (when CountType.GENOME_FRACTION)
    in the vector population. The list_data_values list contains either the fraction of each of the alleles at its
    locus of the vectors sampled (when CountType.ALLELE_FREQ) or the fraction of each of the genomes in the vectors
    sampled (when CountType.GENOME_FRACTION).

    The respond() function in dtk_vector_surveillance.py is called each time any VectorSurveillanceEventCoordinator
    samples the vectors. The respond() function receives the following info from the VectorSurveillanceEventCoordinator:
    time, responder_id, coordinator_name, num_vectors_sampled, list_data_names, list_data_values
    You can write any code you want in the respond() function to process the data, using coordinator_name to
    differentiate between different VectorSurveillanceEventCoordinators if needed. The respond() function returns a list
    of event names to be broadcast as coordinator-level events at completion of the survey. The events are added by you
    based on your processing of the sampled vectors. These events are used to trigger interventions in the campaign that
    will run the next day. The events in the list should correspond to the events used in the campaign or be manually 
    added to the config.parameters.Custom_Coordinator_Events parameter list.

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_trigger_condition_list: List of coordinator-level events. Any of the events in the list will activate
            the run of vector surveillance intervention. The list cannot be empty. emod_api.interventions.common.py
            has a function add_broadcast_coordinator_event that sends out coordinator-level events to act as triggers.
        update_period: The number of days between the sampling of the mosquito population. If the mosquitoes are
            sampled on day 1 and the period is 30, then the next sample will be taken on day 31
        sample_size: Distribution that will be used to pick the sample size of the surveillance.
            Please use emod_api.utils.Distributions to generate the distribution dictionary to pass in.
            The distribution and values to use for determining the sample size we take of the
            vector population. If the population is less than this number, then the entire population will
            be selected.
        species: The name of the species to sample the mosquitoes from. This string must be defined by the Name
            parameter in the config.Vector_Species_Param parameters.
        gender: The sex of the vectors we are sampling.  Options are: VectorGender.VECTOR_FEMALE,
            VectorGender.VECTOR_MALE, VectorGender.VECTOR_BOTH_GENDERS
        count_type: The type of count to use for the vector counter. Options are: CountType.ALLELE_FREQ,
            CountType.GENOME_FRACTION.
        coordinator_name: The name of the coordinator - this name can be used in the embedded python code to help
            differentiate between coordinators. It is recommended that this name be unique, but not enforced.
        node_ids: The list of nodes whose mosquitoes will be surveyed. The mosquitoes from these nodes will be
            considered to be one group when sampled. None or [] means sample from all nodes. Default: None
        start_day: the day the surveillance coordinator is distributed, it needs to be triggered to run
        duration: The time period (in days) that the event coordinator exists after it is distributed at start_time
            before it expires and is removed from the simulation. On (start_day + duration) day of the simulation,
            the coordinator will stop running if it's been triggered and will be removed from the simulation. It cannot
            be activated again.
            Default: None, meaning the coordinator never expires.
        stop_trigger_condition_list: Optional list of coordinator-level events. Any of the events in the list will stop
            the running of vector surveillance intervention. emod_api.interventions.common.py has a function
            add_broadcast_coordinator_event that sends out coordinator-level events to act as triggers.
        survey_completed_event: String representing coordinator-level event that will be sent out after every time a
            vector survey runs the respond() function and its resulting events (if any) are sent out.

    Returns:
        configured VectorSurveillanceEventCoordinator intervention
    """
    schema_path = campaign.schema_path
    vector_counter = dfs.schema_to_config_subnode(schema_path, ["idmTypes", "idmType:VectorCounter"]).parameters
    vector_counter.Count_Type = count_type.name
    vector_counter.Gender = gender.name
    vector_counter.Species = species
    vector_counter.Update_Period = update_period
    prefix = "Sample_Size_"
    Distributions.set_distribution_parameters(vector_counter, sample_size, prefix)

    v_s_e_c = s2c.get_class_with_defaults("VectorSurveillanceEventCoordinator", schema_path)
    v_s_e_c.Start_Trigger_Condition_List = start_trigger_condition_list
    campaign.custom_coordinator_events.extend(start_trigger_condition_list)
    if coordinator_name:
        v_s_e_c.Coordinator_Name = coordinator_name
    v_s_e_c.Counter = vector_counter
    if stop_trigger_condition_list:
        v_s_e_c.Stop_Trigger_Condition_List = stop_trigger_condition_list
        campaign.custom_coordinator_events.extend(stop_trigger_condition_list)
    if duration:
        v_s_e_c.Duration = duration
    if survey_completed_event:
        responder = dfs.schema_to_config_subnode(schema_path, ["idmTypes", "idmType:VectorResponder"]).parameters
        responder.Survey_Completed_Event = survey_completed_event
        campaign.custom_coordinator_events.append(survey_completed_event)
        v_s_e_c.Responder = responder

    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    event.Event_Coordinator_Config = v_s_e_c
    event.Start_Day = start_day
    event.Nodeset_Config = utils.do_nodes(schema_path, node_ids)

    campaign.add(event)
