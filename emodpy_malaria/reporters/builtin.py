from dataclasses import dataclass

from emodpy.reporters.base import BuiltInReporter
from emod_api import schema_to_class as s2c
from idmtools.assets import Asset
import json
import urllib.request
from enum import Enum
from emodpy_malaria.utils import MAX_AGE_YEARS

vis_url = "https://bryanressler-idmod.github.io/vis.json"


class VectorState(Enum):
    STATE_INFECTIOUS = "STATE_INFECTIOUS"
    STATE_INFECTED = "STATE_INFECTED"
    STATE_ADULT = "STATE_ADULT"
    STATE_MALE = "STATE_MALE"
    STATE_IMMATURE = "STATE_IMMATURE"
    STATE_LARVA = "STATE_LARVA"
    STATE_EGG = "STATE_EGG"


class DrugResistantAndHRPStatisticType(Enum):
    NUM_PEOPLE_WITH_RESISTANT_INFECTION = "NUM_PEOPLE_WITH_RESISTANT_INFECTION"
    NUM_INFECTIONS = "NUM_INFECTIONS"


def check_vectors(task):
    """
        Checks that there are species defined for the simulation

    Args:
        task: task to which to add the reporter, which also contains the config file

    Returns:
        Nothing

    Raises:
        ValueError: No Vector_Species_Params defined. You need to define at least one to use ReportVectorGenetics.
    """
    if task and not task.config.parameters.Vector_Species_Params:  # else assume we're in unittest
        raise ValueError(f"No Vector_Species_Params defined. You need to define at least one to "
                         f"use ReportVectorGenetics.\n")


def all_vectors_if_none(task):
    """
        Creates a list of all species names available in the tasks's config and returns
        a list of all species defined for the simulation

    Args:
        task: task to which to add the reporter, which also contains the config file

    Returns:
        A list of all species' names defined in the config
    """
    species_list = []
    for species_params in task.config.parameters.Vector_Species_Params:
        species_list.append(species_params["Name"])
    return species_list


def add_visualizations(task):
    """
        Adds pointer files that create visualization for reports relevant to malaria.
        Currently, "AllInsets", "BinnedReport", "MalariaInterventions", "MalariaSummaryReport"
        
    Args:
        task:  task to which to add the pointer files as assets

    Returns:
        Nothing
    """
    relevant_diseases = ["generic", "malaria"]
    sites = []
    with urllib.request.urlopen(vis_url) as vis_file:
        vis = json.load(vis_file)
    for disease in relevant_diseases:
        sites.extend(vis["diseases"][disease])
    for site in sites:
        pointer = vis["sites"][site]["url"]
        pointer_file_name = f"{site}.html"
        task.common_assets.add_asset(Asset(filename=pointer_file_name, content=pointer), fail_on_duplicate=False)


def add_report_vector_genetics(task, manifest,
                               start_day: int = 0,
                               end_day: int = 365000,
                               node_ids: list = None,
                               species: str = None,
                               gender: str = "VECTOR_FEMALE",
                               include_vector_state: bool = True,
                               include_death_state: bool = False,
                               stratify_by: str = "GENOME",
                               combine_similar_genomes: bool = False,
                               specific_genome_combinations_for_stratification: list = None,
                               allele_combinations_for_stratification: list = None,
                               alleles_for_stratification: list = None,
                               filename_suffix: str = ""):
    """
    Adds ReportVectorGenetics to the simulation. See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start reporting data
        end_day: the day of the simulation to stop reporting data
        node_ids: the list of nodes in which to collect data, empty or None means all nodes
        species: the species to include information on
        gender: gender of species to include information on. Default: "VECTOR_FEMALE",
            other options: "VECTOR_MALE", "VECTOR_BOTH_GENDERS"
        include_vector_state: if True(1), adds the columns for vectors in the different states (i.e Eggs, Larva, etc)
        include_death_state: if True(1), adds columns for the number of vectors that died in this state during this
            time step as well as the average age.  It adds two columns for each of the following states: ADULT,
            INFECTED, INFECTIOUS, and MALE
        stratify_by: the way to stratify data. Default: "GENOME",
            other options: "SPECIFIC_GENOME", "ALLELE", "ALLELE_FREQ"
        combine_similar_genomes: if True(1), genomes are combined if for each locus (ignoring gender) the set of allele
            of the two genomes are the same (i.e. 1-0 is similar to 0-1). Depends on: "GENOME", "SPECIFIC_GENOME"
            specific_genome_combinations_for_stratification: if stratifying by "SPECIFIC_GENOME", then use these genomes
            to stratify by. Example::

                [{"Allele_Combination": [[ "a0",  "*" ], [ "b1", "b0" ]]},
                {"Allele_Combination": [[ "a1", "a0" ], [ "b0",  "*" ]]}]
        specific_genome_combinations_for_stratification: ff stratifying by "SPECIFIC_GENOME", then use these genomes
            to stratify by. '*' = list all entries at that location, '?' = combine all entries at that location
        allele_combinations_for_stratification: if stratifying by "ALLELE", then also add these allele name
            combos to the stratification, Example::

                [[ "a0", "b0" ], [ "a1", "b1" ]]

        alleles_for_stratification: For example::

            [ "a0", "a1", "b0", "b1" ]

        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    # verifying that there are alleles to report on
    if task:
        check_vectors(task)
        if not species:
            raise ValueError(f"Please define species for which to collect information, available species are "
                             f"{all_vectors_if_none(task)}.\n")

    reporter = ReportVectorGenetics()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Species = species
        params.Gender = gender
        params.Include_Vector_State_Columns = 1 if include_vector_state else 0
        params.Include_Death_By_State_Columns = 1 if include_death_state else 0
        params.Stratify_By = stratify_by
        if stratify_by == "GENOME" or stratify_by == "SPECIFIC_GENOME":
            params.Combine_Similar_Genomes = 1 if combine_similar_genomes else 0
        if stratify_by == "SPECIFIC_GENOME":
            params.Specific_Genome_Combinations_For_Stratification = specific_genome_combinations_for_stratification if specific_genome_combinations_for_stratification else []
        elif stratify_by == "ALLELE":
            params.Allele_Combinations_For_Stratification = allele_combinations_for_stratification if allele_combinations_for_stratification else []
        elif stratify_by == "ALLELE_FREQ":
            params.Alleles_For_Stratification = alleles_for_stratification if alleles_for_stratification else []
        params.Filename_Suffix = filename_suffix
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_vector_stats(task, manifest,
                            species_list: list = None,
                            stratify_by_species: bool = False,
                            include_death_state: bool = False,
                            include_wolbachia: bool = False,
                            include_gestation: bool = False,
                            include_microsporidia: bool = False):
    """
    Adds ReportVectorStats report to the simulation. See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        species_list: a list of species to include information on, default of None or [] means "all species"
        stratify_by_species: if True(1), data will break out each the species for each node
        include_death_state: if True(1), adds columns for the number of vectors that died in this state during this
            time step as well as the average age.  It adds two columns for each of the following states: ADULT,
            INFECTED, INFECTIOUS, and MALE
        include_wolbachia: if True(1), add a column for each type of Wolbachia
        include_gestation: if True(1), adds columns for feeding and gestation
        include_microsporidia: if True(1), adds columns for the number of vectors that have microsporidia in
            each state during this time step
    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    if task:
        check_vectors(task)
        if not species_list:
            species_list = all_vectors_if_none(task)

    reporter = ReportVectorStats()  # Create the reporter

    def rec_config_builder(params):
        params.Species_List = species_list
        params.Stratify_By_Species = 1 if stratify_by_species else 0
        params.Include_Death_By_State_Columns = 1 if include_death_state else 0
        params.Include_Wolbachia_Columns = 1 if include_wolbachia else 0
        params.Include_Gestation_Columns = 1 if include_gestation else 0
        params.Include_Microsporidia_Columns = 1 if include_microsporidia else 0
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_summary_report(task, manifest,
                               start_day: int = 0,
                               end_day: int = 365000,
                               node_ids: list = None,
                               reporting_interval: float = 365,
                               must_have_ip_key_value: str = "",
                               must_have_intervention: str = "",
                               include_time_age_pfpr_bins: bool = True,
                               include_time_age_pfpr_infectious_bins: bool = True,
                               add_true_density: bool = False,
                               parasite_detection_threshold: float = 0.0,
                               gametocyte_detection_threshold: float = 0.0,
                               add_hrp2_prevalence: bool = False,
                               hrp2_detection_threshold: float = 0.0,
                               age_bins: list = None,
                               infectiousness_bins: list = None,
                               max_number_reports: int = 100,
                               parasitemia_bins: list = None,
                               pretty_format: bool = False,
                               filename_suffix: str = ""):
    """
    Adds MalariaSummaryReport to the simulation. See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to starts collecting data for the report
        end_day: the day of the simulation to stop reporting data
        node_ids: a list of nodes from which to collect data for the report
        reporting_interval: Defines the cadence of the report by specifying how many time steps to collect data
            before writing to the file
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the an intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        include_time_age_pfpr_bins: When set to true, the 'DataByTimeAndPfPRBinsAndAgeBins' element is included 
            in the report.  Default is true.  You can save disk space by setting this to false.
        include_time_age_pfpr_infectious_bins: When set to true, the 'DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins'
            element is included in the report.  Default is true.  You can save disk space by setting this to false.
        add_true_density: If set to true, four new channels will be added to the report that use true density instead 
            of measured.  These additional channels are:
            * 'PfPR_2to10-True', 
            * 'PfPR by Age Bin-True', 
            * 'Pf Gametocyte Prevalence by Age Bin-True', and 
            * 'Mean Log Parasite Density by Age Bin-True'.
            The true densities will be compared to thresholds 'parasite_detection_threshold' and
            'gametocyte_detection_threshold'. The Default is False.
        parasite_detection_threshold: Used when 'add_true_density' is true.  The true parasite density
            is compared against this threshold.  It impacts the:
            * 'PfPR_2to10-True', 
            * 'PfPR by Age Bin-True', and 
            * 'Mean Log Parasite Density by Age Bin-True'
            channels.  Default is zero.
        gametocyte_detection_threshold: Used when 'add_true_density' is true.  The true gametocyte 
            density is compared against this threshold.  It impacts the 'Pf Gametocyte Prevalence by Age Bin-True' channel.
            Default is zero.
        add_hrp2_prevalence: If true, the 'PfPR_2to10-HRP2' and the 'PfPR by Age Bin-HRP2' channels will be added.
            These channels will use 'Detection_Threshold_True_HRP2' to determine if person's HRP2 level counts towards prevalence.
        hrp2_detection_threshold: Used when 'add_hrp2_prevalence' is true.  If the true HRP2 value is greater than this threshold,
            the prevalence will be increased in the 'PfPR_2to10-HRP2' and the 'PfPR by Age Bin-HRP2' channels.
        age_bins: The max age in years per bin, listed in ascending order. Use a large value for the last bin,
            to collect all remaining individuals
        infectiousness_bins: infectiousness Bins to aggregate within for the report
        max_number_reports: the maximum number of report output files that will be produced for a given simulation
        parasitemia_bins: Parasitemia bins on which to aggregate. A value <= 0 in the first bin indicates that
            uninfected individuals are added to this bin. You must sort your input data from low to high.
        pretty_format: if True(1) sets pretty JSON formatting, which includes carriage returns, line feeds, and spaces
            for easier readability. The default, 0 (false), saves space where everything is on one line.
        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = MalariaSummaryReport()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Node_IDs_Of_Interest = node_ids if node_ids else []

        params.Include_DataByTimeAndPfPRBinsAndAgeBins = 1 if include_time_age_pfpr_bins else 0
        params.Include_DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins = 1 if include_time_age_pfpr_infectious_bins else 0

        params.Add_True_Density_Vs_Threshold = 1 if add_true_density else 0
        if add_true_density:
            params.Detection_Threshold_True_Parasite_Density = parasite_detection_threshold
            params.Detection_Threshold_True_Gametocyte_Density = gametocyte_detection_threshold

        params.Add_Prevalence_By_HRP2 = 1 if add_hrp2_prevalence else 0
        if add_hrp2_prevalence:
            params.Detection_Threshold_True_HRP2 = hrp2_detection_threshold

        params.Age_Bins = age_bins if age_bins else []
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Infectiousness_Bins = infectiousness_bins if infectiousness_bins else []
        params.Max_Number_Reports = max_number_reports
        params.Parasitemia_Bins = parasitemia_bins if parasitemia_bins else []
        params.Pretty_Format = 1 if pretty_format else 0
        params.Reporting_Interval = reporting_interval
        params.Filename_Suffix = filename_suffix
        return params

    reporter.config(rec_config_builder, manifest)

    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_patient_json_report(task, manifest,
                                    start_day: int = 0,
                                    end_day: int = 365000,
                                    node_ids: list = None,
                                    min_age_years: float = 0,
                                    max_age_years: float = MAX_AGE_YEARS,
                                    must_have_ip_key_value: str = "",
                                    must_have_intervention: str = "",
                                    filename_suffix: str = ""):
    """
    Adds MalariaPatientJSONReport report to the simulation. See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to starts collecting data for the report
        end_day: the day of the simulation to stop reporting data
        node_ids: a list of nodes from which to collect data for the report
        min_age_years: minimum age in years of people to collect data on
        max_age_years: maximum age in years of people to collect data on
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = MalariaPatientJSONReport()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Max_Age_Years = max_age_years
        params.Min_Age_Years = min_age_years
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Filename_Suffix = filename_suffix
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_cotransmission_report(task, manifest,
                                      start_day: int = 0,
                                      end_day: int = 365000,
                                      node_ids: list = None,
                                      min_age_years: float = 0,
                                      max_age_years: float = MAX_AGE_YEARS,
                                      must_have_ip_key_value: str = "",
                                      must_have_intervention: str = "",
                                      include_human_to_vector: int = 0,
                                      filename_suffix: str = ""):
    """
    Adds ReportSimpleMalariaTransmission report to the simulation.
    See class definition for description of the report.
    This is the report used to track malaria CoTransmission (co_transmission)
    
    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day to start collecting data for the report.
        end_day: the day of the simulation to stop reporting data
        node_ids: list of nodes for which to collect data for the report
        min_age_years: minimum age in years of people to collect data on
        max_age_years: maximum age in years of people to collect data on
        include_human_to_vector: ff set to 1, Human-to-Vector transmission events will be included.  One can identify
            these events because the 'acquireIndividualId'=0 and transmitTime=acquireTime.
            WARNING:  This can make the file size quite large
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    if task and task.config.parameters.Malaria_Model != "MALARIA_MECHANISTIC_MODEL_WITH_CO_TRANSMISSION":
        raise ValueError(f"The cotransmission report (ReportSimpleMalariaTransmission) requires Malaria_Model"
                         f" to be set to 'MALARIA_MECHANISTIC_MODEL_WITH_CO_TRANSMISSION', however, "
                         f"{task.config.parameters.Malaria_Model} is being used.\n ")

    reporter = ReportSimpleMalariaTransmission()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Max_Age_Years = max_age_years
        params.Min_Age_Years = min_age_years
        params.Include_Human_To_Vector_Transmission = include_human_to_vector
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Filename_Suffix = filename_suffix
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_malaria_filtered(task, manifest,
                                start_day: int = 0,
                                end_day: int = 365000,
                                node_ids: list = None,
                                min_age_years: float = 0,
                                max_age_years: float = MAX_AGE_YEARS,
                                must_have_ip_key_value: str = "",
                                must_have_intervention: str = "",
                                has_interventions: list = None,
                                include_30day_avg_infection_duration: bool = True,
                                filename_suffix: str = ""):
    """
    Adds ReportMalariaFiltered report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day:  the day of the simulation to start collecting data
        end_day: the day of simulation to stop collecting data
        node_ids: list of nodes for which to collect the data, None or [] collects all the nodes
        min_age_years: Minimum age in years of people to collect data on
        max_age_years: Maximum age in years of people to collect data on
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the an intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        has_interventions: a list of intervention names, a channel is added to the report for each InterventionName
            provided.  The channel name will be Has_<InterventionName> and will be the fraction of the population
            that has that intervention. The **Intervention_Name** in the campaign should be the values in this parameter
        include_30day_avg_infection_duration: if True(1) the '30-Day Avg Infection Duration' channel is included
            in the report
        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = ReportMalariaFiltered()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Filename_Suffix = filename_suffix
        params.Has_Interventions = has_interventions if has_interventions else []
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Include_30Day_Avg_Infection_Duration = 1 if include_30day_avg_infection_duration else 0
        params.Max_Age_Years = max_age_years
        params.Min_Age_Years = min_age_years
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_malaria_filtered_intrahost(task, manifest,
                                          start_day: int = 0,
                                          end_day: int = 365000,
                                          node_ids: list = None,
                                          min_age_years: float = 0,
                                          max_age_years: float = MAX_AGE_YEARS,
                                          must_have_ip_key_value: str = "",
                                          must_have_intervention: str = "",
                                          has_interventions: list = None,
                                          include_30day_avg_infection_duration: bool = True,
                                          filename_suffix: str = ""):
    """
    Adds ReportMalariaFilteredIntraHost report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day:  the day of the simulation to start collecting data
        end_day: the day of simulation to stop collecting data
        node_ids: list of nodes for which to collect the data, None or [] collects all the nodes
        min_age_years: Minimum age in years of people to collect data on
        max_age_years: Maximum age in years of people to collect data on
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the an intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        has_interventions: a list of intervention names, a channel is added to the report for each InterventionName
            provided.  The channel name will be Has_<InterventionName> and will be the fraction of the population
            that has that intervention. The **Intervention_Name** in the campaign should be the values in this parameter
        include_30day_avg_infection_duration: if True(1) the '30-Day Avg Infection Duration' channel is included
            in the report
        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = ReportMalariaFilteredIntraHost()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Filename_Suffix = filename_suffix
        params.Has_Interventions = has_interventions if has_interventions else []
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Include_30Day_Avg_Infection_Duration = 1 if include_30day_avg_infection_duration else 0
        params.Max_Age_Years = max_age_years
        params.Min_Age_Years = min_age_years
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_spatial_report_malaria_filtered(task, manifest,
                                        start_day: int = 0,
                                        end_day: int = 365000,
                                        reporting_interval: int = 1,
                                        node_ids: list = None,
                                        min_age_years: float = 0,
                                        max_age_years: float = MAX_AGE_YEARS,
                                        must_have_ip_key_value: str = "",
                                        must_have_intervention: str = "",
                                        spatial_output_channels: list = None,
                                        filename_suffix: str = ""):
    """
    Adds SpatialReportMalariaFiltered report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day:  the day of the simulation to start collecting data
        end_day: the day of simulation to stop collecting data
        reporting_interval: defines the cadence of the report by specifying how many time steps to collect data before
            writing to the file.
        node_ids: list of nodes for which to collect the data, None or [] collects all the nodes
        min_age_years: Minimum age in years of people to collect data on
        max_age_years: Maximum age in years of people to collect data on
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the an intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        spatial_output_channels: list of names of channels you want to have output for. Available channels are:
            "Adult_Vectors", "Air_Temperature", "Births", "Blood_Smear_Gametocyte_Prevalence",
            "Blood_Smear_Parasite_Prevalence", "Campaign_Cost", "Daily_Bites_Per_Human", "Daily_EIR", "Disease_Deaths",
            "Fever_Prevalence", "Human_Infectious_Reservoir", "Infected", "Infectious_Vectors", "Land_Temperature",
            "Mean_Parasitemia", "New_Clinical_Cases", "New_Infections", "New_Reported_Infections", "New_Severe_Cases",
            "PCR_Gametocyte_Prevalence", "PCR_Parasite_Prevalence", "PfHRP2_Prevalence", "Population", "Prevalence",
            "Rainfall", "Relative_Humidity", "True_Prevalence"
            Defaults: ["Blood_Smear_Parasite_Prevalence", "New_Clinical_Cases", "Population"]
        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = SpatialReportMalariaFiltered()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Reporting_Interval = reporting_interval
        params.Max_Age_Years = max_age_years
        params.Min_Age_Years = min_age_years
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Spatial_Output_Channels = spatial_output_channels if spatial_output_channels else [
            "Blood_Smear_Parasite_Prevalence",
            "New_Clinical_Cases",
            "Population"]
        params.Filename_Suffix = filename_suffix
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_event_counter(task, manifest,
                             start_day: int = 0,
                             end_day: int = 365000,
                             node_ids: list = None,
                             event_trigger_list: list = None,
                             min_age_years: float = 0,
                             max_age_years: float = MAX_AGE_YEARS,
                             must_have_ip_key_value: str = "",
                             must_have_intervention: str = "",
                             filename_suffix: str = ""):
    """
    Adds ReportEventCounter report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start counting events
        end_day: the day of simulation to stop collecting data
        node_ids: list of nodes in which to count the events
        event_trigger_list: list of events which to count
        min_age_years: Minimum age in years of people to collect data on
        max_age_years: Maximum age in years of people to collect data on
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the an intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = ReportEventCounter()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Event_Trigger_List = event_trigger_list if event_trigger_list else []
        params.Max_Age_Years = max_age_years
        params.Min_Age_Years = min_age_years
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Filename_Suffix = filename_suffix
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_sql_report_malaria(task, manifest,
                           start_day: int = 0,
                           end_day: int = 365000,
                           include_infection_table: bool = True,
                           include_health_table: bool = True,
                           include_drug_table: bool = False,
                           include_individual_properties: bool = False):
    """
    Adds SqlReportMalaria report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data
        include_infection_table: if True(1), include the table that provides data at each time step for each active
            infection
        include_health_table: if True(1), include the table that provides data at each time step for a person's health
        include_drug_table: if True(1), include the table that provides data at each time step for each drug used
        include_individual_properties: if True(1), add columns to the Health table for each Property(key).
            The values in the columns are integers that are the primary key in a new IndividualProperties
            table that contains the strings.

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = SqlReportMalaria()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Include_Infection_Data_Table = 1 if include_infection_table else 0
        params.Include_Health_Table = 1 if include_health_table else 0
        params.Include_Drug_Status_Table = 1 if include_drug_table else 0
        params.Include_Individual_Properties = 1 if include_individual_properties else 0
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_sql_report_malaria_genetics(task, manifest,
                                    start_day: int = 0,
                                    end_day: int = 365000,
                                    include_infection_table: bool = True,
                                    include_health_table: bool = True,
                                    include_drug_table: bool = False,
                                    include_individual_properties: bool = False):
    """
    Adds SqlReportMalariaGenetics report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data
        include_infection_table: if True(1), include the table that provides data at each time step for each active
            infection
        include_health_table: if True(1), include the table that provides data at each time step for a person's health
        include_drug_table: if True(1), include the table that provides data at each time step for each drug used
        include_individual_properties: if True(1), add columns to the Health table for each Property(key).
            The values in the columns are integers that are the primary key in a new IndividualProperties
            table that contains the strings.

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    if task and task.config.parameters.Malaria_Model != "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS":
        raise ValueError(f"The cotransmission report (ReportSimpleMalariaTransmission) requires Malaria_Model"
                         f" to be set to 'MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS', however, "
                         f"{task.config.parameters.Malaria_Model} is being used.\n ")

    reporter = SqlReportMalariaGenetics()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Include_Infection_Data_Table = 1 if include_infection_table else 0
        params.Include_Health_Table = 1 if include_health_table else 0
        params.Include_Drug_Status_Table = 1 if include_drug_table else 0
        params.Include_Individual_Properties = 1 if include_individual_properties else 0
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_vector_habitat_report(task, manifest):
    """
    Adds VectorHabitatReport report to the simulation. See class definition for description of the report.
    You do not need to configure any data parameters to generate this report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    if task and not task.config.parameters.Vector_Species_Params:  # else assume we're in unittest
        raise ValueError(f"No Vector_Species_Params defined. You need to define at least one to "
                         f"use VectorHabitatReport.\n")

    reporter = VectorHabitatReport()  # Create the reporter

    def rec_config_builder(params):
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_immunity_report(task, manifest,
                                start_day: int = 0,
                                end_day: int = 365000,
                                node_ids: list = None,
                                reporting_interval: int = 1,
                                max_number_reports: int = 365000,
                                age_bins: list = None,
                                must_have_ip_key_value: str = "",
                                must_have_intervention: str = "",
                                pretty_format: bool = False,
                                filename_suffix: str = ""):
    """
    Adds MalariaImmunityReport report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of simulation to stop collecting data
        node_ids: list of nodes for which to collect data
        reporting_interval: defines the cadence of the report by specifying how many time steps to collect data before
            writing to the file.
        max_number_reports: the maximum number of report output files that will be produced for a given simulation
        age_bins: The max age in years per bin, listed in ascending order. Use a large value for the last bin,
            to collect all remaining individuals
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the an intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        pretty_format: if True(1), sets pretty JSON formatting, which includes carriage returns, line feeds, and spaces
            for easier readability. The default, 0 (false), saves space where everything is on one line.
        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = MalariaImmunityReport()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Reporting_Interval = reporting_interval
        params.Max_Number_Reports = max_number_reports
        params.Age_Bins = age_bins if age_bins else []
        params.Pretty_Format = 1 if pretty_format else 0
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Filename_Suffix = filename_suffix

        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_survey_analyzer(task, manifest,
                                start_day: int = 0,
                                end_day: int = 365000,
                                node_ids: list = None,
                                event_trigger_list: list = None,
                                reporting_interval: float = 1,
                                max_number_reports: int = 365000,
                                ip_key_to_collect: str = "",
                                must_have_ip_key_value: str = "",
                                must_have_intervention: str = "",
                                pretty_format: int = 0,
                                filename_suffix: str = ""):
    """
    Adds MalariaSurveyJSONAnalyzer report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of simulation to stop collecting data
        reporting_interval: defines the cadence of the report by specifying how many time steps to collect data
            before writing to the file
        event_trigger_list: list of individual events to include into the report
        max_number_reports: the maximum number of report output files that will be produced for a given simulation
        node_ids: list of nodes for which to collect data
        ip_key_to_collect: name of the Individual Property Key whose value to collect.  Empty string means
            collect values for all Individual Properties
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the an intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        pretty_format: if True(1), sets pretty JSON formatting, which includes carriage returns, line feeds, and spaces
            for easier readability. The default, 0 (false), saves space where everything is on one line.
        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    if not event_trigger_list:
        raise ValueError("event_trigger_list cannot be empty, please define individual"
                         " events to include into the report.\n")

    reporter = MalariaSurveyJSONAnalyzer()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Max_Number_Reports = max_number_reports
        params.Event_Trigger_List = event_trigger_list if event_trigger_list else []
        params.IP_Key_To_Collect = ip_key_to_collect
        params.Pretty_Format = 1 if pretty_format else 0
        params.Reporting_Interval = reporting_interval
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Filename_Suffix = filename_suffix

        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_drug_status_report(task, manifest,
                           start_day: int = 0,
                           end_day: int = 365000):
    """
    Adds ReportDrugStatus report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = ReportDrugStatus()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day

        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_infection_stats_malaria(task, manifest,
                                       start_day: int = 0,
                                       end_day: int = 365000,
                                       reporting_interval: int = 30,
                                       include_hepatocyte: bool = True,
                                       hepatocyte_threshold: int = 0,
                                       include_irbc: bool = True,
                                       irbc_threshold: int = 0,
                                       include_gametocyte: bool = True,
                                       gametocyte_threshold: int = 0):
    """
    Adds ReportInfectionStatsMalaria report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data
        reporting_interval: defines the cadence of the report by specifying how many time steps to collect data
            before writing to the file
        include_hepatocyte: If set to True, then a column will be added to the report providing the count of the
            infected hepatocytes. Default is True.
        hepatocyte_threshold: If the column is included and the number of hepatocytes related to this
            infection are greater than or equal to this value, then the row of data will be included. Default is 0,
            so any/all counts of hepatocytes will be included.
        include_irbc: If set to True, then a column will be added to the report with the number of Infected Red
            Blood Cells from this infection. Default is True.
        irbc_threshold: If the column is included and the number of IRBCs related to this infection are greater
            than or equal to this value, then the row of data will be included. Default is 0,
            so any/all counts of IRBCs will be included.
        include_gametocyte: If set to True, then a column will be added to the report that contains the number
            of gametocytes (male & female) from this infection. Default is True.
        gametocyte_threshold: "If the column is included and the number of gametocytes related to this infection
            are greater than or equal to this value, then the row of data will be included. Default is 0,
            so any/all counts of gametocytes will be included.

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = ReportInfectionStatsMalaria()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Reporting_Interval = reporting_interval
        params.Include_Column_Hepatocyte = include_hepatocyte
        params.Include_Column_IRBC = include_irbc
        params.Include_Column_Gametocyte = include_gametocyte
        params.Include_Data_Threshold_Hepatocytes = hepatocyte_threshold
        params.Include_Data_Threshold_IRBC = irbc_threshold
        params.Include_Data_Threshold_Gametocytes = gametocyte_threshold
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_human_migration_tracking(task, manifest):
    """
    Adds ReportHumanMigrationTracking report to the simulation.
    There are no special parameter that need to be configured to generate the report. However, the simulation
    must have migration enabled.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = ReportHumanMigrationTracking()  # Create the reporter

    def rec_config_builder(params):
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_node_demographics(task, manifest,
                                 age_bins: list = None,
                                 ip_key_to_collect: str = "",
                                 stratify_by_gender: bool = True):
    """
    Adds ReportNodeDemographics report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        age_bins: the age bins (in years) to aggregate within and report. An empty array does not stratify by age. You
            must sort your input data from low to high.
        ip_key_to_collect: The name of the Individual Properties Key by which to stratify the report.
            An empty string does not stratify by Individual Properties
        stratify_by_gender: if True(1), to stratify by gender. Set to False (0) to not stratify by gender.

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = ReportNodeDemographics()  # Create the reporter

    def rec_config_builder(params):
        params.IP_Key_To_Collect = ip_key_to_collect
        params.Age_Bins = age_bins if age_bins else []
        params.Stratify_By_Gender = 1 if stratify_by_gender else 0
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_node_demographics_malaria(task, manifest,
                                         age_bins: list = None,
                                         ip_key_to_collect: str = "",
                                         stratify_by_gender: bool = True,
                                         stratify_by_clinical_symptoms: bool = False):
    """
    Adds ReportNodeDemographicsMalaria report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        age_bins: the age bins (in years) to aggregate within and report. An empty array does not stratify by age. You
            must sort your input data from low to high.
        ip_key_to_collect: The name of theIndividualProperties key by which to stratify the report.
            An empty string does not stratify by Individual Properties
        stratify_by_gender: if True(1), to stratify by gender. Set to False (0) to not stratify by gender.
        stratify_by_clinical_symptoms: if set to True(1), the data will have an extra stratification for people who have
            clinical symptoms and those that do not.  Default is 0 or no extra stratification
    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = ReportNodeDemographicsMalaria()  # Create the reporter

    def rec_config_builder(params):
        params.IP_Key_To_Collect = ip_key_to_collect
        params.Age_Bins = age_bins if age_bins else []
        params.Stratify_By_Gender = stratify_by_gender
        params.Stratify_By_Has_Clinical_Symptoms = stratify_by_clinical_symptoms
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_node_demographics_malaria_genetics(task, manifest,
                                                  barcodes: list = None,
                                                  drug_resistant_strings: list = None,
                                                  drug_resistant_and_hrp_statistic_type: DrugResistantAndHRPStatisticType = DrugResistantAndHRPStatisticType.NUM_PEOPLE_WITH_RESISTANT_INFECTION,
                                                  hrp_strings: list = None,
                                                  age_bins: list = None,
                                                  ip_key_to_collect: str = "",
                                                  stratify_by_gender: bool = True,
                                                  include_identity_by_xxx: bool = False):
    """
    Adds ReportNodeDemographicsMalariaGenetics report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        barcodes: a list of barcode strings. The report contains the number of human infections with each barcode.
            Use '*' for a wild card at a loci to include all values at that loci.  For example, “A*T” includes AAT,
            ACT, AGT, and ATT. The report contains a BarcodeOther column for barcodes that are not defined.
            Note: There is no validation that the barcode strings are valid barcodes for the scenario.
        drug_resistant_strings: a list of strings representing the set of drug resistant markers.  A column will be
            created with the number of humans infections with that barcode.  One can use '*' for a wild card.
            A 'BarcodeOther' column will be created for barcodes not define
        hrp_strings: A list of strings representing the set of HRP markers.  A column will be created with the
            number of humans infections with that HRP string.  One can use '*' for a wild card.
            A 'OtherHRP' column will be created for HRP strings not defined.
        drug_resistant_and_hrp_statistic_type: indicates the statistic in the Drug Resistant & HRP columns:
            NUM_PEOPLE_WITH_RESISTANT_INFECTION = A person is counted if they have one infection with that drug
            resistant marker;  NUM_INFECTIONS = The total number of infections with that marker.
        age_bins: the age bins (in years) to aggregate within and report. An empty array does not stratify by age. You
            must sort your input data from low to high.
        ip_key_to_collect: The name of theIndividualProperties key by which to stratify the report.
            An empty string does not stratify by Individual Properties
        stratify_by_gender: if True(1), to stratify by gender. Set to False(0) to not stratify by gender.
        include_identity_by_xxx: if True(1), include columns about the average Identity By State (IBS) and
            Identity By Descent (IBD) for all new infections with unique barcodes in the last year.

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = ReportNodeDemographicsMalariaGenetics()  # Create the reporter

    def rec_config_builder(params):
        params.IP_Key_To_Collect = ip_key_to_collect
        params.Age_Bins = age_bins if age_bins else []
        params.Stratify_By_Gender = 1 if stratify_by_gender else 0
        params.Barcodes = barcodes if barcodes else []
        params.Drug_Resistant_Strings = drug_resistant_strings if drug_resistant_strings else []
        params.HRP_Strings = hrp_strings if hrp_strings else []
        if type(drug_resistant_and_hrp_statistic_type) is DrugResistantAndHRPStatisticType:
            params.Drug_Resistant_And_HRP_Statistic_Type = drug_resistant_and_hrp_statistic_type.value
        else:  # assume they passed in a string directly
            params.Drug_Resistant_And_HRP_Statistic_Type = drug_resistant_and_hrp_statistic_type
        params.Include_Identity_By_XXX = 1 if include_identity_by_xxx else 0
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_vector_migration(task, manifest,
                                start_day: int = 0,
                                end_day: int = None,
                                species_list: list[str] = None,
                                must_be_in_state: list[VectorState] = None,
                                must_be_from_node: list[int] = None,
                                must_be_to_node: list[int] = None,
                                include_genome_data: bool = False,
                                filename_suffix: str = ""):
    """
    Adds ReportVectorMigration report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data
        species_list: a list of species to include information on, default of None or [] means "all species".
        must_be_in_state: A list of vector states for which you want to record the migration. Only STATE_MALE,
            STATE_ADULT, STATE_INFECTED, STATE_INFECTIOUS migrate.
        must_be_from_node: A list of node IDs. A vector must be travelling FROM one of these nodes to be recorded into
            the report. Empty list means vectors traveling from any/all nodes will be recorded.
        must_be_to_node: A list of node IDs. A vector must be travelling TO one of these nodes to be recorded into the
            report. Empty list means vectors traveling to any/all nodes will be recorded.
        include_genome_data: If set to True, adds a Genome column for migrating vectors. Vectors with no
            custom alleles will still have their sex alleles listed.
        filename_suffix: Augments the filename of the report. If multiple reports are being generated, this allows you
            to distinguish among the multiple reports.

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    check_vectors(task)

    reporter = ReportVectorMigration()  # Create the reporter

    def rec_config_builder(params):
        if start_day:
            params.Start_Day = start_day
        if end_day:
            params.End_Day = end_day
        if species_list:
            params.Species_List = species_list
        if must_be_in_state:
            must_be_in_state_strings = []
            for state in must_be_in_state:
                if type(state) is VectorState:
                    must_be_in_state_strings.append(state.value)
                else:
                    must_be_in_state_strings.append(state)
            params.Must_Be_In_State = must_be_in_state_strings
        if must_be_from_node:
            params.Must_Be_From_Node = must_be_from_node
        if must_be_to_node:
            params.Must_Be_To_Node = must_be_to_node
        params.Include_Genome_Data = 1 if include_genome_data else 0
        if filename_suffix:
            params.Filename_Suffix = filename_suffix
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_vector_stats_malaria_genetics(task, manifest,
                                             species_list: list = None,
                                             stratify_by_species: bool = False,
                                             include_death_state: bool = False,
                                             include_wolbachia: bool = False,
                                             include_gestation: bool = False,
                                             include_microsporidia: bool = False,
                                             barcodes: list = None):
    """
    Adds ReportVectorStatsMalariaGenetics report to the simulation. See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        species_list: a list of species to include information on, default of None or [] means "all species"
        stratify_by_species: if True(1), data will break out each the species for each node
        include_death_state: if True(1), adds columns for the number of vectors that died in this state during this
            time step as well as the average age.  It adds two columns for each of the following states: ADULT,
            INFECTED, INFECTIOUS, and MALE
        include_wolbachia: if True(1), add a column for each type of Wolbachia
        include_gestation: if True(1), adds columns for feeding and gestation
        include_microsporidia: if True(1), adds columns for the number of vectors that have microsporidia in
            each state during this time step
        barcodes: a list of barcode strings. The report contains the number of human infections with each barcode.
            Use '*' for a wild card at a loci to include all values at that loci.  For example, “A*T” includes AAT,
            ACT, AGT, and ATT. The report contains a BarcodeOther column for barcodes that are not defined.
            Note: There is no validation that the barcode strings are valid barcodes for the scenario.
    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    if task:
        check_vectors(task)
        if not species_list:
            species_list = all_vectors_if_none(task)

    reporter = ReportVectorStatsMalariaGenetics()  # Create the reporter

    def rec_config_builder(params):
        params.Species_List = species_list
        params.Stratify_By_Species = 1 if stratify_by_species else 0
        params.Include_Death_By_State_Columns = 1 if include_death_state else 0
        params.Include_Wolbachia_Columns = 1 if include_wolbachia else 0
        params.Include_Gestation_Columns = 1 if include_gestation else 0
        params.Include_Microsporidia_Columns = 1 if include_microsporidia else 0
        params.Barcodes = barcodes if barcodes else []
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_event_recorder(task, event_list: list = None,
                       only_include_events_in_list: bool = True,
                       ips_to_record: list = None,
                       start_day: int = 0,
                       end_day: int = 365000,
                       node_ids: list = None,
                       min_age_years: float = 0,
                       max_age_years: float = 365000,
                       must_have_ip_key_value: str = "",
                       must_have_intervention: str = "",
                       property_change_ip_to_record: str = ""):
    """
    Adds ReportEventRecorder report to the simulation.
    The health events and interventions report (ReportEventRecorder.csv) provides information on each individual’s
    demographics and health status at the time of an event. Additionally, it is possible to see the value of specific
    IndividualProperties, as assigned in the demographics file (see NodeProperties and IndividualProperties for more
    information).

    Args:
        task: task to which to add the reporter
        event_list: a list of events to record or exclude, depending on value of only_include_events_in_list
        only_include_events_in_list: if True, only record events listed.  if False, record ALL events EXCEPT for the
            ones listed
        ips_to_record: list of individual properties to include in report
        start_day: The day of the simulation to start collecting data
        end_day: The day of the simulation to stop collecting data.
        node_ids: Data will be collected for the nodes in this list, if None - all nodes have data collected.
        min_age_years: Minimum age in years of people to collect data on
        max_age_years: Maximum age in years of people to collect data on
        must_have_ip_key_value: A Key:Value pair that the individual must have in order to be included. Empty string
            means don't look at IndividualProperties
        must_have_intervention: The name of the intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        property_change_ip_to_record:If the string is not empty, then the recorder will add the PropertyChange event to
            the list of events that the report is listening to. However, it will only record the events where the
            property changed the value of the given key

    Returns:
        Nothing
    """
    # Documentation: https://docs.idmod.org/projects/emod-malaria/en/latest/software-report-event-recorder.html
    if not event_list:
        if only_include_events_in_list:
            raise ValueError("Please define event_list parameter when setting only_include_events_in_list to True.\n")
        else:
            event_list = []

    task.config.parameters.Report_Event_Recorder = 1
    task.config.parameters.Report_Event_Recorder_Events = event_list
    task.config.parameters.Report_Event_Recorder_Individual_Properties = ips_to_record if ips_to_record else []
    task.config.parameters.Report_Event_Recorder_Start_Day = start_day
    task.config.parameters.Report_Event_Recorder_End_Day = end_day
    task.config.parameters.Report_Event_Recorder_Node_IDs_Of_Interest = node_ids if node_ids else []
    task.config.parameters.Report_Event_Recorder_Min_Age_Years = min_age_years
    task.config.parameters.Report_Event_Recorder_Max_Age_Years = max_age_years
    task.config.parameters.Report_Event_Recorder_Must_Have_IP_Key_Value = must_have_ip_key_value
    task.config.parameters.Report_Event_Recorder_Must_Have_Intervention = must_have_intervention
    task.config.parameters.Report_Event_Recorder_PropertyChange_IP_Key_Of_Interest = property_change_ip_to_record
    task.config.parameters.Report_Event_Recorder_Ignore_Events_In_List = 0 if only_include_events_in_list else 1


def add_node_event_recorder(task, event_list: list = None,
                            only_include_events_in_list: bool = True,
                            stats_by_node_properties: list = None,
                            stats_by_individual_properties: str = ""):
    """
    Adds ReportEventRecorderNode report to the simulation.

    Args:
        task: task to which to add the reporter
        event_list: A list of node-level events to record or exclude, depending on value of
            only_include_node_events_in_list
        only_include_events_in_list: If True, only record node-level events listed.  if False, record ALL
            node-level events EXCEPT for the ones listed
        stats_by_node_properties: Specifies an array of (optional) node property keys, as defined in
            NodeProperties in the demographics file, to be added as additional columns to the
            ReportNodeEventRecorder.csv output report.  An empty array equals no additional columns added.
        stats_by_individual_properties: Specifies an array of (optional) individual property keys, as defined in
            IndividualProperties in the demographics file, to be added to the ReportNodeEventRecorder.csv output
            report. An empty array equals no additional columns added

    Returns:
        Nothing
    """

    if not event_list:
        if only_include_events_in_list:
            raise ValueError("Please define event_list parameter when setting only_include_events_in_list to True.\n")
        else:
            event_list = []

    task.config.parameters.Report_Node_Event_Recorder = 1
    task.config.parameters.Report_Node_Event_Recorder_Events = event_list
    task.config.parameters.Report_Node_Event_Recorder_Ignore_Events_In_List = 0 if only_include_events_in_list else 1
    task.config.parameters.Report_Node_Event_Recorder_Node_Properties = stats_by_node_properties if stats_by_node_properties else []
    task.config.parameters.Report_Node_Event_Recorder_Stats_By_IPs = stats_by_individual_properties if stats_by_individual_properties else []


def add_coordinator_event_recorder(task, event_list: list = None,
                                   only_include_events_in_list: bool = True):
    """
    Adds ReportEventRecorderCoordinator report to the simulation.

    Args:
        task: task to which to add the reporter
        event_list: A list of coordinator-level events to record or exclude, depending on value of
            only_include_coordinator_events_in_list
        only_include_events_in_list: If True, only record node-level events listed.  if False, record ALL
            node-level events EXCEPT for the ones listed

    Returns:
        Nothing
    """

    if not event_list:
        if only_include_events_in_list:
            raise ValueError("Please define event_list parameter.\n")
        else:
            event_list = []

    task.config.parameters.Report_Coordinator_Event_Recorder = 1
    task.config.parameters.Report_Coordinator_Event_Recorder_Events = event_list
    task.config.parameters.Report_Coordinator_Event_Recorder_Ignore_Events_In_List = 0 if only_include_events_in_list else 1


def add_report_intervention_pop_avg(task, manifest,
                                    start_day: int = 0,
                                    end_day: int = 365000,
                                    node_ids: list = None,
                                    min_age_years: float = 0,
                                    max_age_years: float = MAX_AGE_YEARS,
                                    must_have_ip_key_value: str = "",
                                    must_have_intervention: str = "",
                                    filename_suffix: str = ""):
    """
    Adds ReportInterventionPopAvg reporter. See class definition for description of the report.

    Args:
        task: Task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: Schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data
        node_ids: List of nodes for which to collect data
        min_age_years: Minimum age in years of people to collect data on
        max_age_years: Maximum age in years of people to collect data on
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the an intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        filename_suffix: augments the filename of the report. If multiple reports are being generated,
            this allows you to distinguish among the multiple reports

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    reporter = ReportInterventionPopAvg()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Max_Age_Years = max_age_years
        params.Min_Age_Years = min_age_years
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Filename_Suffix = filename_suffix
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_microsporidia(task, manifest):
    """
    Adds ReportMicrosporidia reporter. See class definition for description of the report.
    There are no special parameter that need to be configured to generate the report.

    Args:
        task: Task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: Schema path file

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    reporter = ReportMicrosporidia()  # Create the reporter

    def rec_config_builder(params):
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_fpg_output(task, manifest,
                          start_day: int = 0,
                          end_day: int = 365000,
                          node_ids: list = None,
                          min_age_years: float = 0,
                          max_age_years: float = MAX_AGE_YEARS,
                          must_have_ip_key_value: str = "",
                          must_have_intervention: str = "",
                          include_genome_ids: bool = False,
                          minimum_parasite_density: float = 1,
                          sampling_period: float = 1):
    """
    Adds ReportFpgOutputForObservationalModel reporter. See class definition for description of the report.

    Args:
        task: Task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: Schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data
        node_ids: List of nodes for which to collect data
        min_age_years: Minimum age in years of people to collect data on
        max_age_years: Maximum age in years of people to collect data on
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the an intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        include_genome_ids: Add a column that has a list of Genome IDs (hashcode) for the person.
        minimum_parasite_density: The minimum density that the infection must have to be included in the list
            of infections. A value of zero implies include all infections. Number of asexual parasites
            per micro liter of blood.
        sampling_period: The number of days between sampling the population. This implies one should get data
            on days Start_Day, Start_Day+Sampling_Period, Start_Day+2*Sampling_Period, and so on.

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    if task:
        if task.config.parameters.Malaria_Model != "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS":
            raise ValueError(f"ERROR: This report only works with 'Malaria_Model' = "
                             f"'MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS', but you have "
                             f"'Malaria_Model' = '{task.config.parameters.Malaria_Model}' .\n")

    reporter = ReportFpgOutputForObservationalModel()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Max_Age_Years = max_age_years
        params.Min_Age_Years = min_age_years
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Include_Genome_IDs = 1 if include_genome_ids else 0
        params.Minimum_Parasite_Density = minimum_parasite_density
        params.Sampling_Period = sampling_period

        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_fpg_new_infections(task, manifest,
                                  start_day: int = 0,
                                  end_day: int = 365000,
                                  node_ids: list = None,
                                  min_age_years: float = 0,
                                  max_age_years: float = MAX_AGE_YEARS,
                                  must_have_ip_key_value: str = "",
                                  must_have_intervention: str = "",
                                  filename_suffix: str = ""):
    """
    Adds ReportFpgNewInfections reporter.

    The report will give one line for each new infection object that gets created. That line will provide
    information about the where the gametocytes came from to create the sporozoites that created the new
    infection. This can allow the user to track where infections come from. This includes the idea of
    parasites coming from other locations - i.e. importation.

    This can only be used with the FPG model.

    Args:
        task: Task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: Schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data
        node_ids: List of nodes for which to collect data
        min_age_years: Minimum age in years of people to collect data on
        max_age_years: Maximum age in years of people to collect data on
        must_have_ip_key_value: a "Key:Value" pair that the individual must have in order to be included. Empty string
            means don't look at IPs (individual properties)
        must_have_intervention: the name of the intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        filename_suffix: Augments the filename of the report. If multiple reports of this class are being generated,
            this allows you to distinguish among them.

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    if task:
        if task.config.parameters.Malaria_Model != "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS":
            raise ValueError(f"ERROR: This report only works with 'Malaria_Model' = "
                             f"'MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS', but you have "
                             f"'Malaria_Model' = '{task.config.parameters.Malaria_Model}' .\n")

    reporter = ReportFpgNewInfections()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Node_IDs_Of_Interest = node_ids if node_ids else []
        params.Max_Age_Years = max_age_years
        params.Min_Age_Years = min_age_years
        params.Must_Have_IP_Key_Value = must_have_ip_key_value
        params.Must_Have_Intervention = must_have_intervention
        params.Filename_Suffix = filename_suffix
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_antibodies(task, manifest,
                          start_day: int = 0,
                          end_day: int = 365000,
                          reporting_interval: int = 30,
                          contain_capacity_data: bool = False):
    """
    Adds ReportAntibodies reporter.

    Args:
        task: Task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: Schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data
        reporting_interval: interval (in days) at which to report antibody data
        contain_capacity_data: If true, the data for each antibody is the capacity of the antibody,
            otherwise it's the current concentration.

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """
    reporter = ReportAntibodies()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Reporting_Interval = reporting_interval
        params.Contain_Capacity_Data = 1 if contain_capacity_data else 0

        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_simulation_stats(task, manifest):
    """
    Adds ReportSimulationStats to collect data on the computational performance of the model
    (duration, memory, number of persisted interventions, etc).

    There are no special parameter that need to be configured to generate the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file

    Returns:
        if task is not set, returns the configured reporter, otherwise returns nothing
    """

    reporter = ReportSimulationStats()  # Create the reporter

    def rec_config_builder(params):
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


@dataclass
class ReportVectorGenetics(BuiltInReporter):
    """
        The vector genetics report is a CSV-formatted report (ReportVectorGenetics.csv) that collects
        information on how many vectors of each genome/allele combination exist at each time, node,
        and vector state. Information can only be collected on one species per report.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportVectorGenetics"  # OK to hardcode? config["class"]
        rvg_params = s2c.get_class_with_defaults("ReportVectorGenetics", manifest.schema_file)
        rvg_params = config_builder(rvg_params)
        rvg_params.finalize()
        rvg_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(rvg_params))


@dataclass
class ReportInfectionStatsMalaria(BuiltInReporter):
    """
        ReportInfectionStatsMalaria
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportInfectionStatsMalaria"  # OK to hardcode? config["class"]
        rvg_params = s2c.get_class_with_defaults("ReportInfectionStatsMalaria", manifest.schema_file)
        rvg_params = config_builder(rvg_params)
        rvg_params.finalize()
        rvg_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(rvg_params))


@dataclass
class ReportVectorStats(BuiltInReporter):
    """
        The vector statistics report is a CSV-formatted report (ReportVectorStats.csv) that provides detailed
        life-cycle data on the vectors in the simulation. The report is stratified by time, node ID,
        and (optionally) species.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportVectorStats"  # OK to hardcode? config["class"]
        rvg_params = s2c.get_class_with_defaults("ReportVectorStats", manifest.schema_file)
        rvg_params = config_builder(rvg_params)
        rvg_params.finalize()
        rvg_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(rvg_params))


@dataclass
class MalariaSummaryReport(BuiltInReporter):
    """
        The population-level malaria summary report is a JSON-formatted report (MalariaSummaryReport.json) that provides
        a summary of malaria data across the population. The data are grouped into different bins such as age,
        parasitemia, and infectiousness.
    """

    def config(self, config_builder, manifest):
        self.class_name = "MalariaSummaryReport"
        report_params = s2c.get_class_with_defaults("MalariaSummaryReport", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class MalariaPatientJSONReport(BuiltInReporter):
    """
        The malaria patient data report is a JSON-formatted report (MalariaPatientReport.json) that provides medical
        data for each individual on each day of the simulation. For example, for a specified number of time steps,
        each “patient” has information collected on the temperature of their fever, their parasite counts, treatments
        they received, and other relevant data.
    """

    def config(self, config_builder, manifest):
        self.class_name = "MalariaPatientJSONReport"
        report_params = s2c.get_class_with_defaults("MalariaPatientJSONReport", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class ReportSimpleMalariaTransmission(BuiltInReporter):
    """
        The simple malaria transmission report (ReportSimpleMalariaTransmission.csv) is a csv report that
        provides data on malaria transmission, by tracking who transmitted malaria to whom.  The report can only be used
        when the simulation setup parameter **Malaria_Model** is set to MALARIA_MECHANISTIC_MODEL_WITH_CO_TRANSMISSION.
        This report is typically used as input to the GenEpi model.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportSimpleMalariaTransmission"
        report_params = s2c.get_class_with_defaults("ReportSimpleMalariaTransmission", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class ReportMalariaFiltered(BuiltInReporter):
    """
        The malaria filtered report (ReportMalariaFiltered.json) is the same as the default InsetChart report, but
        provides filtering options to enable the user to select the data to be displayed for each time step or for
        each node. See InsetChart for more information about InsetChart.json.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportMalariaFiltered"
        report_params = s2c.get_class_with_defaults("ReportMalariaFiltered", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class SpatialReportMalariaFiltered(BuiltInReporter):
    """
        The filtered malaria spatial report (SpatialReportMalariaFiltered.bin) provides spatial information on malaria
        simulations and allows for filtering the data and collection over different intervals. This report is similar to
        the Spatial output report but allows for data collection and filtering over different intervals using the
        Start_Day and a Reporting_Interval parameters
    """

    def config(self, config_builder, manifest):
        self.class_name = "SpatialReportMalariaFiltered"
        report_params = s2c.get_class_with_defaults("SpatialReportMalariaFiltered", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class ReportMalariaFilteredIntraHost(BuiltInReporter):
    """
        The filtered malaria spatial report (ReportMalariaFilteredIntraHost.bin) provides TBD
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportMalariaFilteredIntraHost"
        report_params = s2c.get_class_with_defaults("ReportMalariaFilteredIntraHost", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class ReportEventCounter(BuiltInReporter):
    """
        The event counter report is a JSON-formatted file (ReportEventCounter.json) that keeps track of how many of
        each event types occurs during a time step. The report produced is similar to the InsetChart.json channel
        report, where there is one channel for each event defined in the configuration file (config.json).
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportEventCounter"
        report_params = s2c.get_class_with_defaults("ReportEventCounter", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class SqlReportMalariaGenetics(BuiltInReporter):
    """
        The SqlReportMalariaGenetics outputs epidemiological and transmission data. Because of the quantity and complexity of
        the data, the report output is a multi-table SQLite relational database (see https://sqlitebrowser.org/).
        Use the configuration parameters to manage the size of the database.
    """

    def config(self, config_builder, manifest):
        self.class_name = "SqlReportMalariaGenetics"
        report_params = s2c.get_class_with_defaults("SqlReportMalariaGenetics", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class SqlReportMalaria(BuiltInReporter):
    """
        The SqlReportMalaria outputs epidemiological and transmission data. This report does not contain any genomics
        data. Because of the quantity and complexity of the data, the report output is a multi-table SQLite relational
        database (see https://sqlitebrowser.org/). Use the configuration parameters to manage the size of the database.
    """

    def config(self, config_builder, manifest):
        self.class_name = "SqlReportMalaria"
        report_params = s2c.get_class_with_defaults("SqlReportMalaria", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class VectorHabitatReport(BuiltInReporter):
    """
        The vector habitat report is a JSON-formatted file (VectorHabitatReport.json) containing habitat data for each
        vector species included in the simulation. It focuses on statistics relevant to mosquito developmental stages
        (e.g. eggs and larvae), such as egg capacity and larval crowding.
    """

    def config(self, config_builder, manifest):
        self.class_name = "VectorHabitatReport"
        report_params = s2c.get_class_with_defaults("VectorHabitatReport", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class MalariaImmunityReport(BuiltInReporter):
    """
        The malaria immunity report is a JSON-formatted file (MalariaImmunityReport.json) that provides statistics for
        several antibody types for specified age bins over a specified reporting duration. Specifically, the report
        tracks the average and standard deviation in the fraction of observed antibodies for merozoite surface protein (
        MSP), Plasmodium falciparum erythrocyte membrane protein 1 (PfEMP1), and non-specific (and less immunogenic)
        minor surface epitopes.  The total possible is determined by parameters Falciparum_MSP_Variants,
        Falciparum_PfEMP1_Variants, and Falciparum_Nonspecific_Types.  The greater the fraction, the more antibodies the
        individual has against possible new infections.  The smaller the fraction, the more naïve the individual’s
        immune system is to malaria.
    """

    def config(self, config_builder, manifest):
        self.class_name = "MalariaImmunityReport"
        report_params = s2c.get_class_with_defaults("MalariaImmunityReport", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class MalariaSurveyJSONAnalyzer(BuiltInReporter):
    def config(self, config_builder, manifest):
        self.class_name = "MalariaSurveyJSONAnalyzer"
        report_params = s2c.get_class_with_defaults("MalariaSurveyJSONAnalyzer", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportDrugStatus(BuiltInReporter):
    """
        The drug status report provides status information on the drugs that an individual has taken or is waiting to
        take. Because the report provides information for each drug, for each individual, and for each time step, you
        may want to use the Start_Day and End_Day parameters to limit the size the output file.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportDrugStatus"
        report_params = s2c.get_class_with_defaults("ReportDrugStatus", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportHumanMigrationTracking(BuiltInReporter):
    """
        The human migration tracking report is a CSV-formatted report (ReportHumanMigrationTracking.csv) that provides
        details about human travel during simulations. The report provides one line for each surviving individual who
        migrates during the simulation.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportHumanMigrationTracking"
        report_params = s2c.get_class_with_defaults("ReportHumanMigrationTracking", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportNodeDemographics(BuiltInReporter):
    """
        The node demographics report is a CSV-formatted report (ReportNodeDemographics.csv) that provides population
        information stratified by node. For each time step, the report collects data on each node and age bin.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportNodeDemographics"
        report_params = s2c.get_class_with_defaults("ReportNodeDemographics", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportNodeDemographicsMalaria(BuiltInReporter):
    """
    This report extends the data collected in the ReportNodeDemographics by adding data about the number of
    infections with specific barcodes. The malaria node demographics genetics report does not include columns for
    Genome_Markers because this report assumes that the simulation setup parameter Malaria_Model is set to
    MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

    Note: If you need detailed data on the infections with different barcodes, use the SqlReportMalaria. That report
    contains data on all barcodes, without specifying what they are.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportNodeDemographicsMalaria"
        report_params = s2c.get_class_with_defaults("ReportNodeDemographicsMalaria", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportNodeDemographicsMalariaGenetics(BuiltInReporter):
    """
    This report extends the data collected in the ReportNodeDemographics by adding data about the number of
    infections with specific barcodes. The malaria node demographics genetics report does not include columns for
    Genome_Markers because this report assumes that the simulation setup parameter Malaria_Model is set to
    MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

    Note: If you need detailed data on the infections with different barcodes, use the SqlReportMalaria. That report
    contains data on all barcodes, without specifying what they are.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportNodeDemographicsMalariaGenetics"
        report_params = s2c.get_class_with_defaults("ReportNodeDemographicsMalariaGenetics", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportVectorMigration(BuiltInReporter):
    """
        This report provides detailed information on where and when vectors are migrating.  Because there can be one
        line for each migrating vector, you may want to use the Start_Day and End_Day parameters to limit the
        size the output file.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportVectorMigration"
        report_params = s2c.get_class_with_defaults("ReportVectorMigration", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportVectorStatsMalariaGenetics(BuiltInReporter):
    """
    This report extends the data collected in the ReportVectorStats by adding data about the number of
    infections with specific barcodes. The malaria node demographics genetics report does not include columns for
    Genome_Markers because this report assumes that the simulation setup parameter Malaria_Model is set to
    MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportVectorStatsMalariaGenetics"
        report_params = s2c.get_class_with_defaults("ReportVectorStatsMalariaGenetics", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportInterventionPopAvg(BuiltInReporter):
    """
    ReportInterventionPopAvg is a CSV-formatted report that gives population average
    data on the usage of interventions.  It provides data on the fraction of people
    or nodes that have an intervention as well as averages on the intervention's efficacy.
    For each persistent intervention that has been distributed to a node or person,
    the report provides one line in the CSV for each intervention used in that node.
    Since node-level intervention (usually vector control) can only have one per node,
    the data will be for that one intervention.  The individual-level interventions
    will have data for the people in that node.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportInterventionPopAvg"
        report_params = s2c.get_class_with_defaults("ReportInterventionPopAvg", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportFpgOutputForObservationalModel(BuiltInReporter):
    """
    ReportFpgOutputForObservationalModel generates two files:
    infIndexRecursive-genomes-df.csv - This file will be the list of infected people in each node
    at each time step where each row represents one person.
    variantsXXX_afFPG.npy - This file is a two dimensional numpy array. It is an array of genomes
    where each row is an genome and each column is a 0 or 1. The 'XXX' will indicate the number
    of genome locations found in a single genome (i.e. 24, 100, etc.).
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportFpgOutputForObservationalModel"
        report_params = s2c.get_class_with_defaults("ReportFpgOutputForObservationalModel", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportSimulationStats(BuiltInReporter):
    """
    Adds ReportSimulationStats to collect data on the computational performance of the model
    (duration, memory, number of persisted interventions, etc).
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportSimulationStats"
        report_params = s2c.get_class_with_defaults("ReportSimulationStats", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportMicrosporidia(BuiltInReporter):
    """
    ReportMicrosporidia generates a ReportMicrosporidia.csv. It is a stratified report where the data is stratified
    by time, node, species and microsporidia strain; with columns of counts of vectors in each state for that
    stratification.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportMicrosporidia"
        report_params = s2c.get_class_with_defaults("ReportMicrosporidia", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportFpgNewInfections(BuiltInReporter):
    """
    ReportFpgNewInfections generates a ReportFpgNewInfections.csv
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportFpgNewInfections"
        report_params = s2c.get_class_with_defaults("ReportFpgNewInfections", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportAntibodies(BuiltInReporter):
    """
    ReportAntibodies generates a ReportAntibodies.csv
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportAntibodies"
        report_params = s2c.get_class_with_defaults("ReportAntibodies", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))
