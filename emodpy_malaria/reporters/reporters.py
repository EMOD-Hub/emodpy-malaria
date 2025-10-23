from emodpy.reporters.common import ReportNodeDemographics
from emodpy.reporters.common import ReportSimulationStats
from emodpy.reporters.common import ReportHumanMigrationTracking
from emodpy.reporters.common import ReportEventCounter
from emodpy.reporters.common import ReportPluginAgeAtInfection
from emodpy.reporters.common import ReportPluginAgeAtInfectionHistogram
from emodpy.reporters.common import SqlReport
from emodpy.reporters.common import ReportNodeEventRecorder
from emodpy.reporters.common import ReportCoordinatorEventRecorder
from emodpy.reporters.common import ReportSurveillanceEventRecorder
from emodpy.reporters.common import SpatialReport
from emodpy.reporters.common import InsetChart as _InsetChart
from emodpy.reporters.common import DemographicsReport
from emodpy.reporters.common import PropertyReport
from emodpy.reporters.common import ReportInfectionDuration
from emodpy.reporters.common import SpatialReportChannels
from emodpy.reporters.base import ReportFilter
from emodpy.reporters.base import BuiltInReporter
from emodpy.reporters.base import ConfigReporter
from emodpy.reporters.base import Reporters
from emodpy.utils import (validate_key_value_pair, validate_value_range, validate_bins,
                          validate_intervention_name, validate_individual_property, validate_list_of_strings,
                          validate_individual_event)
from emodpy_malaria.utils.targeting_config import AbstractTargetingConfig
from emodpy_malaria.utils import targeting_config
from emodpy_malaria.utils.emod_enum import RelationshipType


class ReportVectorStats(BuiltInReporter):
    """
    The vector statistics report (ReportVectorStats.csv) provides a summary of vector-related statistics over the
    reporting period, including counts of vectors in various states and metrics related to vector behavior and
    interactions with humans.

    For more information, see :doc:`emod-hiv:emod/software-report-vector-stats`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy.

        species_list (list, optional): A list of vector species names to include in the report. If empty, all species
            will be included.

            Default: None

        stratify_by_species (bool, optional): When True, the report will be stratified by vector species.

            Default: False

        include_death_state (bool, optional): When True, the report will include counts of vectors in different death
            states.

            Default: False

        include_wolbachia (bool, optional): When True, the report will include counts of vectors infected with
            Wolbachia.

            Default: False

        include_gestation (bool, optional): When True, the report will include counts of vectors in different
            gestation states.

            Default: False

        include_microsporidia (bool, optional): When True, the report will include counts of vectors infected with
            microsporidia.

            Default: False

    """
    def __init__(self,
                 reporters_object: Reporters,
                 species_list: list = None,
                 stratify_by_species: bool = False,
                 include_death_state: bool = False,
                 include_wolbachia: bool = False,
                 include_gestation: bool = False,
                 include_microsporidia: bool = False):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportVectorStats')
        if species_list is None:
            species_list = []
        self.parameters.Species_List = species_list
        self.parameters.Stratify_By_Species = 1 if stratify_by_species else 0
        self.parameters.Include_Death_By_State_Columns = 1 if include_death_state else 0
        self.parameters.Include_Wolbachia_Columns = 1 if include_wolbachia else 0
        self.parameters.Include_Gestation_Columns = 1 if include_gestation else 0
        self.parameters.Include_Microsporidia_Columns = 1 if include_microsporidia else 0

class ReportHIVByAgeAndGender(ConfigReporter):
    """
    The age- and gender-stratified HIV report (ReportHIVByAgeAndGender.csv) provides a detailed set of HIV-related
    statistics, with numerous ways to customize and stratify the output. The report format facilitates further analysis
    using a pivot table.

    Some results, such as population size or number infected, are reported as single 'snapshots' at the end of the
    reporting period. Other values, such as deaths or new infections, are aggregated for the entire reporting period.

    For more information, see :doc:`emod-hiv:emod/software-report-age-gender`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy.

        collect_gender_data (bool, optional): When True, the 'Gender' column will be added where 0 is for males and 1
            for females.

            Default: False

        collect_age_bins_data (list[float], optional): A list of age bins (values in years) used to stratify the report
            by age. When this parameter is used, the 'Age' column will be added and the reports and will have a row for
            each bin value. The row will include all individuals whose age is between the value in the bin (inclusive)
            and the next bin's value (exclusive). The values between the bins cannot be equal and must be listed in
            ascending order. Leave the array empty to not stratify the report by age. The maximum number of age bins is
            100. Note: setting this will multiply the number of rows in the output report by the number of bins.

        collect_circumcision_data (bool, optional): When True, the 'IsCircumcised' column is included in the output
            report. The report data will be stratified by those who have the MaleCircumcision intervention (1) and
            those who do not (0). Note: setting this to True will double the number of rows for males in the output
            report.

            Default: False

        collect_hiv_data (bool, optional): When True, the 'HasHIV' column is included in the output report. The report
            data will be stratified by those individuals who have HIV (1) and those who do not (0). Cannot be used
            with Report_HIV_ByAgeAndGender_Collect_HIV_Stage_Data. Note: setting this to True doubles the number
            of rows in the output report.

            Default: False

        collect_hiv_stage_data (bool, optional): When True, the 'HIV_Stage' column is included in the output report.
            The report data will be stratified by HIV Infection Stage (NOT_INFECTED, ACUTE, LATENT, AIDS, ON_ART).
            Cannot be used with collect_hiv_data or collect_on_art_data.
            Note: setting this to True multiplies the number of rows in the output report by five.

            Default: False

        collect_on_art_data (bool, optional): When set to True, the 'On_ART' column is included in the output report.
            The report data will be stratified by those individuals who are on ART (1) and those who are not (0).
            Cannot be used with collect_hiv_stage_data. Note: setting this to True doubles the number of rows in the
            output report.

            Default: False

        collect_ip_data (list[str], optional): A list of individual property (IP) keys used to stratify the report.
            A column 'IP_Key:X' will be added to the report for each IP listed, and a row for each possible
            IP Key:Value pair. For more information, see :doc:`emod-hiv:emod/model-properties`.

            Default: None

        collect_intervention_data (list[str], optional): A list of interventions used to stratify the report. This
            allows for reporting on a subset (or all) of the interventions that an individual has been on, of those
            listed in the intervention_name campaign parameter. Those with the intervention will have a 1 in the
            column and those without will have 0. Note: this can only be used with interventions that
            remain with an individual for a period of time, such as VMMC, vaccine/PrEP, or those with a delay state
            in the cascade of care.

            Default: None

        collect_targeting_config_data (list[AbstractTargetingConfig], optional): Creates a 'MeetsTargetingConfig_X'
            column for each targeting config defined in the list where X is the position of the targeting config in the
            list. In cell, value 1 indicates that the individuals match the targeting config and 0 indicating that they
            do not.

            Default: None

        add_transmitters (bool, optional): When True, the 'Transmitters' column will be added to the report. It
            indicates the total number of the individuals in that row who transmitted HIV during this reporting period.
            This may not add up to the number of new infections in the reporting period if any of the new infections
            were due to the OutbreakIndividual intervention or maternal transmission.

            Default: False

        stratify_infected_by_cd4 (bool, optional): When True, the number of infected individuals will be segregated
            into four columns based on CD4 count ('Infected CD4 Under 200 (Not On ART)',
            'Infected CD4 200 to 349 (Not On ART)', 'Infected CD4 350 to 499 (Not On ART)',
            'Infected CD4 500 Plus (Not On ART)')
            Note: this creates additional polling columns, but not more stratification rows.

            Default: False

        event_counter_list (list[str], optional): A list of individual-level events. A column will be added to the
            report for each event listed, showing the number of times the event occurred during the reporting for the
            people in the row. To be counted, the individual must qualify for that row at the time the event occurred,
            not necessarily at the end of the reporting period (the individual themselves might end up being counted
            in a different row). See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used by EMOD,
            or add custom events you're using in campaigns.
            parameter in config.

            Default: None

        add_relationships (bool, optional): When True, the report will contain data on the population currently in a
            relationship and ever in a relationship for each relationship type (TRANSITORY, INFORMAL, MARITAL, and
            COMMERCIAL), eight columns total. Additionally, columns containing a sum of individuals in two or more
            partnerships (Has Concurrent Partners) and a sum of the lifetime number of relationships (Lifetime Partners)
            will be included.

            Default: False

        add_concordant_relationships (bool, optional): When True, a Concordant column for each relationship type
            (TRANSITORY, INFORMAL, MARITAL, and COMMERCIAL) is included in the output report. These contain totals for
            each relationship of each type where both partners have the same HIV status.

            Default: False

        reporting_period (float, optional): The number of days between records in output report.
            Note: Due to an old design choice, the reporting_period for his report is halved within EMOD’s code.
            To keep it consistent with other reporters that use reporting periods, emodpy will automatically multiply
            this value by 2 before passing it to EMOD. This means the reporting_period you enter here will correctly
            represent the actual time between report entries, rather than being halved.

            Minimum value: 15
            Maximum value: 182,500
            Default value: 182.5 (every 6 months)

        use_old_format (bool, optional): When True, data collection is offset by one time step: the first entry includes
            an extra time step, and subsequent entries occur at reporting_period but remain offset. This is a
            superseded functionality. When set to False, data is collected as expected - data is collected for and reported
            every reporting_period.

            Default: False

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_year
                - end_year

    """
    def __init__(self,
                 reporters_object: Reporters,
                 collect_gender_data: bool = False,
                 collect_age_bins_data: list[float] = None,
                 collect_circumcision_data: bool = False,
                 collect_hiv_data: bool = False,
                 collect_hiv_stage_data: bool = False,
                 collect_on_art_data: bool = False,
                 collect_ip_data: list[str] = None,
                 collect_intervention_data: list[str] = None,
                 collect_targeting_config_data: list[AbstractTargetingConfig] = None,
                 add_transmitters: bool = False,
                 stratify_infected_by_cd4: bool = False,
                 event_counter_list: list[str] = None,
                 add_relationships: bool = False,
                 add_concordant_relationships: bool = False,
                 reporting_period: float = 182.5,
                 use_old_format: bool = False,
                 report_filter: ReportFilter = None):
        reporter_parameter_prefix = "Report_HIV_ByAgeAndGender"
        super().__init__(reporter_parameter_prefix=reporter_parameter_prefix, report_filter=report_filter)
        if collect_hiv_stage_data and (collect_on_art_data or collect_hiv_data):
            raise ValueError("collect_hiv_stage_data cannot be used with collect_on_art_data or collect_hiv_data.")

        self.parameters[
            f"{reporter_parameter_prefix}_Add_Concordant_Relationships"] = 1 if add_concordant_relationships else 0
        self.parameters[f"{reporter_parameter_prefix}_Add_Relationships"] = 1 if add_relationships else 0
        self.parameters[f"{reporter_parameter_prefix}_Add_Transmitters"] = 1 if add_transmitters else 0
        self.parameters[f"{reporter_parameter_prefix}_Collect_On_Art_Data"] = 1 if collect_on_art_data else 0
        self.parameters[
            f"{reporter_parameter_prefix}_Collect_Circumcision_Data"] = 1 if collect_circumcision_data else 0
        self.parameters[f"{reporter_parameter_prefix}_Collect_Gender_Data"] = 1 if collect_gender_data else 0
        self.parameters[f"{reporter_parameter_prefix}_Collect_HIV_Data"] = 1 if collect_hiv_data else 0
        self.parameters[f"{reporter_parameter_prefix}_Collect_HIV_Stage_Data"] = 1 if collect_hiv_stage_data else 0
        self.parameters[f"{reporter_parameter_prefix}_Stratify_Infected_By_CD4"] = 1 if stratify_infected_by_cd4 else 0
        self.parameters[f"{reporter_parameter_prefix}_Collect_Age_Bins_Data"] = (
            validate_bins(bins=collect_age_bins_data,
                          param_name="collect_age_bins_data",
                          min_value=0,
                          max_value=9.3228e+35) if collect_age_bins_data else [])
        self.parameters[f"{reporter_parameter_prefix}_Collect_IP_Data"] = (
            validate_list_of_strings(strings=collect_ip_data,
                                     param_name="collect_ip_data",
                                     empty_list_ok=True,
                                     process_string_callback=validate_individual_property))
        self.parameters[f"{reporter_parameter_prefix}_Collect_Intervention_Data"] = (
            validate_list_of_strings(strings=collect_intervention_data,
                                     param_name="collect_intervention_data",
                                     empty_list_ok=True,
                                     process_string_callback=validate_intervention_name))
        self.parameters[f"{reporter_parameter_prefix}_Event_Counter_List"] = (
            validate_list_of_strings(strings=event_counter_list,
                                     param_name="event_counter_list",
                                     empty_list_ok=True,
                                     process_string_callback=validate_individual_event))
        if collect_targeting_config_data:
            targeting_config_data_schema_dict = []
            for targeting_config in collect_targeting_config_data:
                if not isinstance(targeting_config, AbstractTargetingConfig):
                    raise ValueError(f"collect_targeting_config_data must be a list of AbstractTargetingConfig objects, "
                                     f"but we found a type {type(targeting_config).__name__}.")
                else:
                    targeting_config_data_schema_dict.append(targeting_config.to_schema_dict(reporters_object))

            self.parameters[
                f"{reporter_parameter_prefix}_Collect_Targeting_Config_Data"] = targeting_config_data_schema_dict
        else:
            self.parameters[f"{reporter_parameter_prefix}_Collect_Targeting_Config_Data"] = []

        # see note in parameter description about doubling the reporting period
        self.parameters["Report_HIV_Period"] = 2 * validate_value_range(reporting_period,
                                                                        param_name="reporting_period",
                                                                        min_value=15,
                                                                        max_value=182500,
                                                                        param_type=float)
        if use_old_format:
            self.parameters[f"{reporter_parameter_prefix}_Use_Old_Format"] = 1

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        self.parameters[f"{reporter_class_name}_Stop_Year"] = end_year

    def _set_start_day(self, start_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_day is not a valid parameter for {reporter_class_name}.')

    def _set_end_day(self, end_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_day is not a valid parameter for {reporter_class_name}.')

    def _set_node_ids(self, node_ids: list[int], reporter_class_name: str) -> None:
        raise ValueError(f'node_ids is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_ip_key_value(self, must_have_ip_key_value: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_ip_key_value is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_intervention(self, must_have_intervention: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_intervention is not a valid parameter for {reporter_class_name}.')

    def _set_filename_suffix(self, filename_suffix: str, reporter_class_name: str) -> None:
        raise ValueError(f'filename_suffix is not a valid parameter for {reporter_class_name}.')

    def _set_min_age_years(self, min_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'min_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_max_age_years(self, max_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'max_age_years is not a valid parameter for {reporter_class_name}.')


class ReportRelationshipStart(ConfigReporter):
    """
    The relationship formation report (RelationshipStart.csv) provides information about each relationship and its
    members, evaluated at the time of relationship formation. The report includes the relationship type, start time,
    scheduled end time, and detailed information about each participant: ID, gender, age, infection status,
    circumcision status for males, co-infections, number of relationships (active, recent, lifetime), and individual
    properties. The male in the relationship is indicated on the report as participant 'A', and the female as
    participant 'B'.

    For more information, see :doc:`emod-hiv:emod/software-report-relationship-start`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy.

        include_hiv_disease_statistics (bool, optional): When True, the report will include information on CD4 count,
            viral load, disease stage, HIV positivity, and HIV testing results for each partner at the start of the
            relationship.

            Default: False

        include_other_relationship_statistics (bool, optional): When True, the report will include information on the
            number of active and lifetime relationships of each type (TRANSITORY, INFORMAL, MARITAL, and COMMERCIAL)
            for each partner in the relationship, as well as total relationships in the past six month and total
            lifetime relationships. Additionally, a bitmask column will indicate which types of concurrent relationships
            are allowed; these are configured using the Concurrency_Configuration parameter in the demographics, see
            :doc:`emod-hiv:emod/parameter-demographics`.

            Default: False

        individual_properties (list[str], optional): A list of strings individual property (IP) keys that will be
            included in the report as applicable to each partner at the start of the relationship. One column will be
            added to the report for each partner, for each key in the list. For more information, see
            :doc:`emod-hiv:emod/model-properties`.

        report_filter (ReportFilter, optional): Common report filtering parameters. To be included into the report, only
            one of the partners needs to satisfy the field. Valid filtering parameters for this report are:

                - start_year
                - end_year
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention

    """

    def __init__(self,
                 reporters_object: Reporters,
                 include_hiv_disease_statistics: bool = True,
                 include_other_relationship_statistics: bool = True,
                 individual_properties: list[str] = None,
                 report_filter: ReportFilter = None):
        reporter_parameter_prefix = "Report_Relationship_Start"
        super().__init__(reporter_parameter_prefix=reporter_parameter_prefix, report_filter=report_filter)
        self.parameters[f"{reporter_parameter_prefix}"] = 1
        self.parameters[
            f"{reporter_parameter_prefix}_Include_HIV_Disease_Statistics"] = 1 if include_hiv_disease_statistics else 0
        self.parameters[f"{reporter_parameter_prefix}_Include_Other_Relationship_Statistics"] = (
            1 if include_other_relationship_statistics else 0)
        self.parameters[f"{reporter_parameter_prefix}_Individual_Properties"] = (
            validate_list_of_strings(strings=individual_properties,
                                     param_name="individual_properties",
                                     empty_list_ok=True,
                                     process_string_callback=validate_individual_property))

    def _set_start_day(self, start_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_day is not a valid parameter for {reporter_class_name}.')

    def _set_end_day(self, end_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_day is not a valid parameter for {reporter_class_name}.')

    def _set_filename_suffix(self, filename_suffix: str, reporter_class_name: str) -> None:
        raise ValueError(f'filename_suffix is not a valid parameter for {reporter_class_name}.')


class ReportCoitalActs(ConfigReporter):
    """
    The coital act report (RelationshipConsummated.csv) provides detailed information about each coital act that occurs
    during the simulation. The report includes unique identifiers for each coital act and relationship; the relationship
    type, number of acts, whether a condom was used, and whether transmission occurred; and detailed information about
    each participant, including age, gender, infection status, circumcision status, co-infection status, and treatment
    status. Each participant in a relationship is referred to as either participant “A” or participant “B”.

    One row of data is returned per coital act, and results are ordered on a per-relationship basis. Note: if a person
    is engaged in coital acts in multiple relationships during a time step, the order of those acts is unknown, only
    in which relationship they occurred. Additionally, if a person gets infected during a time step, they cannot
    re-transmit that infection during the same time step. The report does record during which coital act transmission
    occurred.

    If an uninfected person has coital acts with multiple infected partners during the same time step, all acts with the
    possibility of transmission are randomly ordered, so that the person has an equal chance of getting infected from
    any one of their partners. The probability of transmission from any one of these coital acts is still determined by
    the simulation parameters (number of acts, acquisition multipliers, etc.)

    For more information, please see :doc:`emod-hiv:emod/software-report-relationship-consummated`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy.

        relationship_type (RelationshipType, optional): A RelationshipType enum indicating the type of relationship
            the coital act has to occur in to be reported. Options are TRANSITORY, INFORMAL, MARITAL, and COMMERCIAL.
            Leave empty or None to include all relationship types. Default: None
            Note: RelationshipType.COUNT is not a valid parameter for this report.

        has_intervention_with_name (list[str], optional) : An list of intervention names where a column is added for
            each name. The column will have a value of 1 if the person has the intervention and 0 if they do not.
            The intervention_name parameter in the campaigns are the available values for this parameter.

            Default: None

        individual_properties (list[str], optional): A list of strings individual property (IP) keys that will be
            included in the report as columns. Each person will have the value of that key in their row. For more
            information, see :doc:`emod-hiv:emod/model-properties`.
            Default: None

        partners_with_ip_key_value (list[str], optional): A list of strings in format of "Key:Value", denoting specific
            IndividualProperty key:value pair. For each IP Key:Value string in the list, two columns will be added -
            one for each partner indicating the number of their partners for whom that IP Key:Value applies. For more
            information, see :doc:`emod-hiv:emod/model-properties`.

            Default: None

        report_filter (ReportFilter, optional): Common report filtering parameters. To be included into the report, only
            one of the partners needs to satisfy the field. Valid filtering parameters for this
            report are:

                - start_year
                - end_year
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention

    """

    def __init__(self,
                 reporters_object: Reporters,
                 relationship_type: RelationshipType = None,
                 has_intervention_with_name: list[str] = None,
                 individual_properties: list[str] = None,
                 partners_with_ip_key_value: list[str] = None,
                 report_filter: ReportFilter = None):
        reporter_parameter_prefix = "Report_Coital_Acts"
        super().__init__(reporter_parameter_prefix=reporter_parameter_prefix, report_filter=report_filter)
        if relationship_type is not None:
            if isinstance(relationship_type, RelationshipType):
                if relationship_type == RelationshipType.COUNT:
                    raise ValueError("relationship_type RelationshipType.COUNT is not a valid parameter for"
                                     " ReportCoitalActs.")
                self.parameters[f"{reporter_parameter_prefix}_Relationship_Type"] = relationship_type.value
            else:
                raise ValueError(f"relationship_type {relationship_type} is not an instance of RelationshipType enum.")
        if partners_with_ip_key_value:
            validated_ip_key_values = []
            for ip_key_value in partners_with_ip_key_value:
                if (ip_key_value == "") or (ip_key_value is None):
                    raise ValueError("The 'key:value' entries of argument 'partners_with_ip_key_value' cannot be empty string or None.")
                validated_ip_key_values.append(validate_key_value_pair(s=ip_key_value))
            self.parameters[f"{reporter_parameter_prefix}_Partners_With_IP_Key_Value"] = validated_ip_key_values
        self.parameters[f"{reporter_parameter_prefix}_Individual_Properties"] = (
            validate_list_of_strings(strings=individual_properties,
                                     param_name="individual_properties",
                                     empty_list_ok=True,
                                     process_string_callback=validate_individual_property))
        self.parameters[f"{reporter_parameter_prefix}_Has_Intervention_With_Name"] = (
            validate_list_of_strings(strings=has_intervention_with_name,
                                     param_name="has_intervention_with_name",
                                     empty_list_ok=True,
                                     process_string_callback=validate_intervention_name))

    def _set_start_day(self, start_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_day is not a valid parameter for {reporter_class_name}.')

    def _set_end_day(self, end_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_day is not a valid parameter for {reporter_class_name}.')

    def _set_filename_suffix(self, filename_suffix: str, reporter_class_name: str) -> None:
        raise ValueError(f'filename_suffix is not a valid parameter for {reporter_class_name}.')


class ReportRelationshipEnd(ConfigReporter):
    """
    The relationship dissolution report (RelationshipEnd.csv) provides detailed information about each relationship and
    its members, evaluated at the time of relationship dissolution. The report includes the relationship id,
    relationship type, start time, scheduled end time, actual end time (which may differ from the scheduled end time,
    for instance, due to the death of a partner), and information about each participant. The relationship id is unique
    to each relationship and is the same across all reports that reference relationships: ReportRelationshipStart,
    ReportTransmission, and the ReportCoitalActs.

    For more information, please see :doc:`emod-hiv:emod/software-report-relationship-end`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy
    """

    def __init__(self,
                 reporters_object: Reporters):
        reporter_parameter_prefix = "Report_Relationship_End"
        super().__init__(reporter_parameter_prefix=reporter_parameter_prefix)


class ReportTransmission(ConfigReporter):
    """
    The HIV relationship transmission report (TransmissionReport.csv) provides detailed information about each
    transmission event and relationship members, evaluated at the time of disease transmission within the relationship.
    It includes the time/date of transmission and information about the transmitter and recipient, including: age,
    gender, current and lifetime number of relationships, infection stage, circumcision status for males, co-infections,
    and disease-specific biomarkers, if applicable.

    For more information, see :doc:`emod-hiv:emod/software-report-transmission`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy

    """

    def __init__(self,
                 reporters_object: Reporters):
        reporter_parameter_prefix = "Report_Transmission"
        super().__init__(reporter_parameter_prefix=reporter_parameter_prefix)


class ReportHIVART(ConfigReporter):
    """
    The ART initiation and discontinuation report (ReportHIVART.csv) provides information on individuals at time of
    ART initiation and discontinuation, including ID, age, gender, and CD4 count at ART initiation.

    For more information, see :doc:`emod-hiv:emod/software-report-hivart`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy

    """

    def __init__(self,
                 reporters_object: Reporters):
        reporter_parameter_prefix = "Report_HIV_ART"
        super().__init__(reporter_parameter_prefix=reporter_parameter_prefix)


class ReportHIVInfection(ConfigReporter):
    """
    The HIV disease progression report (ReportHIVInfection.csv) provides information on each individual’s disease state
    at each time step, including age, gender, CD4 count, survival prognosis, ART status, and factors impacting
    transmission and acquisition.

    For more information, see :doc:`emod-hiv:emod/software-report-hivinfection`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy
        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_year
                - end_year
    """

    def __init__(self,
                 reporters_object: Reporters,
                 report_filter: ReportFilter = None):
        reporter_parameter_prefix = "Report_HIV_Infection"
        super().__init__(reporter_parameter_prefix=reporter_parameter_prefix,
                         report_filter=report_filter)

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        self.parameters[f"{reporter_class_name}_Stop_Year"] = end_year

    def _set_start_day(self, start_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_day is not a valid parameter for {reporter_class_name}.')

    def _set_end_day(self, end_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_day is not a valid parameter for {reporter_class_name}.')

    def _set_node_ids(self, node_ids: list[int], reporter_class_name: str) -> None:
        raise ValueError(f'node_ids is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_ip_key_value(self, must_have_ip_key_value: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_ip_key_value is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_intervention(self, must_have_intervention: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_intervention is not a valid parameter for {reporter_class_name}.')

    def _set_filename_suffix(self, filename_suffix: str, reporter_class_name: str) -> None:
        raise ValueError(f'filename_suffix is not a valid parameter for {reporter_class_name}.')

    def _set_min_age_years(self, min_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'min_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_max_age_years(self, max_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'max_age_years is not a valid parameter for {reporter_class_name}.')


class ReportHIVMortality(ConfigReporter):
    """
    The HIV mortality report (HIVMortality.csv) provides information about individuals at the time of their death,
    including disease status, CD4 count, medical history, and relationship history.

    For more information, see :doc:`emod-hiv:emod/software-report-hivmort`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy

    """

    def __init__(self,
                 reporters_object: Reporters):
        reporter_parameter_prefix = "Report_HIV_Mortality"
        super().__init__(reporter_parameter_prefix=reporter_parameter_prefix)


class ReportRelationshipMigrationTracking(BuiltInReporter):
    """
    The relationship migration tracking report (ReportRelationshipMigrationTracking.csv) provides information about
    the relationships a person has when they are migrating. It will give information when they are leaving and entering
    a node. When leaving a node, the information will be about the status of the relationships just before they leave.
    When entering the new node, the information will be about the relationships that have been updated. For example,
    a person could leave with a relationship paused, find their partner in the new node, and get their relationship
    back to normal. This helps to know about how the status of the relationships have changed—migrated, paused, or
    terminated.

    The person initiating a migration event will first have their relationships listed in the state before migrating
    starts. If a partner is asked to migrate with them, then that partner’s relationships will also be listed. When the
    people are immigrating into the new node, the list of relationships that are continuing in the new node will be
    listed. Any migrated partner should only have the relationship with the partner initiating migration. Their other
    relationships will have been terminated.

    For more information, see :doc:`emod-hiv:emod/software-report-relationship-migration-tracking`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy.
        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_year
                - end_year
                - filename_suffix
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention


    """

    def __init__(self,
                 reporters_object: Reporters,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportRelationshipMigrationTracking',
                         report_filter=report_filter)

    def _set_start_day(self, start_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_day is not a valid parameter for {reporter_class_name}.')

    def _set_end_day(self, end_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_day is not a valid parameter for {reporter_class_name}.')


class ReportPfaQueues(BuiltInReporter):
    """
    The pair forming algorithm (PFA) queues report (ReportPfaQueues.csv) provides data to analyze the relationship
    formation process and evaluate who is left unpaired at each stage.

    The report includes several key columns: Time, which represents the simulation day when the data is recorded, and
    NodeID, which specifies the external ID of the simulation node. Additionally, the columns labeled <Before/After>
    (e.g., TRANSITORY_M_Before_20) indicate the count of individuals in specific bins at different stages of the
    process. The "Before" stage represents the moment just before individuals are paired, capturing those who have
    entered the PFA and are eligible for relationship formation based on the formation rate. The "After" stage reflects
    the individuals remaining in the PFA after pairing, who will wait until the next time step to enter a relationship
    of the specified type.

    For more information:
    `ReportPfaQueues <https://github.com/EMOD-Hub/emodpy-hiv/issues/14>`_

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy.

    """

    def __init__(self,
                 reporters_object: Reporters):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportPfaQueues')


class ReportRelationshipCensus(BuiltInReporter):
    """
    The relationship census report (ReportRelationshipCensus.csv) is a CSV-formatted report that extracts relationship
    numbers for each person during each taking of the census. The census is a one-day event collecting data for that
    person as of that day.

    For more information, see :doc:`emod-hiv:emod/software-report-relationship-census`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy.
        report_filename: The name for the file of the generated report including file extension
        reporting_interval_years: Number of years between census-taking.
        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_year
                - end_year

    """

    def __init__(self,
                 reporters_object: Reporters,
                 report_filename: str = "ReportRelationshipCensus.csv",
                 reporting_interval_years: float = 1,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportRelationshipCensus',
                         report_filter=report_filter)
        self.parameters.Report_File_Name = report_filename
        self.parameters.Reporting_Interval_Years = validate_value_range(param=reporting_interval_years,
                                                                        param_name="reporting_interval_years",
                                                                        min_value=0,
                                                                        max_value=100,
                                                                        param_type=float)

    def _set_end_day(self, end_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_day is not a valid parameter for {reporter_class_name}.')

    def _set_start_day(self, start_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_day is not a valid parameter for {reporter_class_name}.')

    def _set_node_ids(self, node_ids: list[int], reporter_class_name: str) -> None:
        raise ValueError(f'node_ids is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_ip_key_value(self, must_have_ip_key_value: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_ip_key_value is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_intervention(self, must_have_intervention: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_intervention is not a valid parameter for {reporter_class_name}.')

    def _set_filename_suffix(self, filename_suffix: str, reporter_class_name: str) -> None:
        raise ValueError(f'filename_suffix is not a valid parameter for {reporter_class_name}.')

    def _set_min_age_years(self, min_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'min_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_max_age_years(self, max_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'max_age_years is not a valid parameter for {reporter_class_name}.')


class ReportEventRecorder(ConfigReporter):
    """
    The health events and interventions report (ReportEventRecorder.csv) provides information on each individual’s
    demographics and health status at the time of an event. Additionally, it is possible to see the value of specific
    IndividualProperties, as assigned in the demographics file.

    For more information, see :doc:`emod-hiv:emod/software-report-event-recorder`.

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy.

        event_list (list[str]): The list of individual-level events to include in the output report. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used by EMOD,
            or add custom events you're using in campaigns.

        individual_properties (list[str], optional): A list of strings individual property (IP) keys that will be
            included in the report as applicable to each partner at the start of the relationship. One column will be
            added to the report for each partner, for each key in the list. For more information, see
            :doc:`emod-hiv:emod/model-properties`.

            Default: None

        property_change_ip_to_record (str, optional): IndividualProperty key string for which recorder will add the
            PropertyChange event to the list of events that the report is listening to. However, it will only record
            the events where the property changed the value of this given key. For more information,
            see :doc:`emod-hiv:emod/model-properties`.

            Default: None

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_year
                - end_year
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention

    """

    def __init__(self,
                 reporters_object: Reporters,
                 event_list: list[str],
                 individual_properties: list[str] = None,
                 property_change_ip_to_record: str = None,
                 report_filter: ReportFilter = None):
        reporter_parameter_prefix = "Report_Event_Recorder"
        super().__init__(reporter_parameter_prefix=reporter_parameter_prefix, report_filter=report_filter)
        # always use the event list as the list of events to record
        self.parameters[f"{reporter_parameter_prefix}_Ignore_Events_In_List"] = 0
        self.parameters[f"{reporter_parameter_prefix}_Events"] = (
            validate_list_of_strings(strings=event_list,
                                     param_name="event_list",
                                     empty_list_ok=False,
                                     process_string_callback=validate_individual_event))
        self.parameters[f"{reporter_parameter_prefix}_Individual_Properties"] = (
            validate_list_of_strings(strings=individual_properties,
                                     param_name="individual_properties",
                                     empty_list_ok=True,
                                     process_string_callback=validate_individual_property))
        if property_change_ip_to_record:
            self.parameters[f"{reporter_parameter_prefix}_PropertyChange_IP_Key_Of_Interest"] = (
                validate_individual_property(individual_property=property_change_ip_to_record))

    def _set_start_day(self, start_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_day is not a valid parameter for {reporter_class_name}.')

    def _set_end_day(self, end_day: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_day is not a valid parameter for {reporter_class_name}.')

    def _set_filename_suffix(self, filename_suffix: str, reporter_class_name: str) -> None:
        raise ValueError(f'filename_suffix is not a valid parameter for {reporter_class_name}.')


class InsetChart(_InsetChart):
    """
    The inset chart (InsetChart.json) is an output report that is automatically generated with every simulation. It
    contains simulation-wide averages, one per time step, for a wide number of data channels. The channels are fully
    specified by the simulation type and cannot be altered without making changes to the EMOD source code. Python or
    other tools can be used to create charts out of the information contained in the file.

    For more information, see :doc:`emod-hiv:emod/software-report-inset-chart`

    Args:
        reporters_object (Reporters): The reporters object given by the emodpy
        has_ip (list[str], optional): A channel is added to InsetChart for each value of each
            IndividualProperty key provided.  The channel name will be HasIP_<Key:Value> and will be the fraction
            of the population that has that value for that Individual Property Key. For more information,
            see :doc:`emod-hiv:emod/model-properties`.
            Default: None
        has_interventions (list[str], optional): A channel is added to InsetChart for each intervention name provided.
            The channel name will be Has_<InterventionName> and will be the fraction of the population that has that
            intervention. The intervention_name parameter in the campaigns are the available values for this
            parameter.
            Default: None
        include_pregnancies (bool, optional): If True, channels are added about pregnancies and possible mothers.
            Default: False
        include_coital_acts (bool, optional): If True, include channels about the number of coital acts per relationship
            type per timestep and those using condoms.
            Default: True
        event_channels_list (list[str], optional): This is the list of events included in the InsetChart report. If
            events are specified with this parameter, the InsetChart will include a channel for each event listed.
            If no events are listed, a 'Number of Events' channel will display the total number of all events that
            occurred during the simulation. See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already
            used by EMOD or add custom events you're using in campaigns.
            Default: None
    """

    def __init__(self,
                 reporters_object: Reporters,
                 has_ip: list[str] = None,
                 has_interventions: list[str] = None,
                 include_pregnancies: bool = False,
                 include_coital_acts: bool = True,
                 event_channels_list: list[str] = None):
        super().__init__(reporters_object=reporters_object,
                         has_ip=has_ip,
                         has_interventions=has_interventions,
                         include_pregnancies=include_pregnancies)
        self.parameters["Inset_Chart_Include_Coital_Acts"] = 1 if include_coital_acts else 0
        self.parameters["Report_HIV_Event_Channels_List"] = (
            validate_list_of_strings(strings=event_channels_list,
                                     param_name="event_channels_list",
                                     empty_list_ok=True,
                                     process_string_callback=validate_individual_event))


# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [ReportVectorStats,
                 ReportNodeDemographics,
                 ReportSimulationStats,
                 ReportHumanMigrationTracking,
                 ReportEventCounter,
                 ReportEventRecorder,
                 ReportPluginAgeAtInfection,
                 ReportPluginAgeAtInfectionHistogram,
                 SqlReport,
                 ReportNodeEventRecorder,
                 ReportCoordinatorEventRecorder,
                 ReportSurveillanceEventRecorder,
                 InsetChart,
                 SpatialReport,
                 ReportHIVByAgeAndGender,
                 ReportRelationshipStart,
                 ReportCoitalActs,
                 ReportRelationshipEnd,
                 ReportTransmission,
                 ReportHIVART,
                 ReportHIVInfection,
                 ReportHIVMortality,
                 ReportRelationshipMigrationTracking,
                 ReportPfaQueues,
                 ReportRelationshipCensus,
                 ReportFilter,
                 DemographicsReport,
                 PropertyReport,
                 ReportInfectionDuration,
                 SpatialReportChannels,
                 RelationshipType,
                 targeting_config]

# The following loop sets the __module__ attribute of each class in __all_exports to the name of the current module.
# This is done to ensure that when these classes are imported from this module, their __module__ attribute correctly
# reflects their source module.

for _ in __all_exports:
    _.__module__ = __name__

# __all__: A list that defines the public interface of this module.
# This is essential to ensure that Sphinx builds documentation for these classes, including those that are imported
# from emodpy.
# It contains the names of all the classes that should be accessible when this module is imported using the syntax
# 'from module import *'.
# Here, it is set to the names of all classes in __all_exports.

__all__ = [_.__name__ for _ in __all_exports]
