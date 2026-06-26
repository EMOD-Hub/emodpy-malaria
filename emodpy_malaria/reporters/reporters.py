from emodpy.reporters.common import ReportNodeDemographics
from emodpy.reporters.common import ReportSimulationStats  # noqa: F401
from emodpy.reporters.common import ReportHumanMigrationTracking  # noqa: F401
from emodpy.reporters.common import ReportEventCounter  # noqa: F401
from emodpy.reporters.common import ReportPluginAgeAtInfection  # noqa: F401
from emodpy.reporters.common import ReportPluginAgeAtInfectionHistogram  # noqa: F401
from emodpy.reporters.common import ReportNodeEventRecorder  # noqa: F401
from emodpy.reporters.common import ReportCoordinatorEventRecorder  # noqa: F401
from emodpy.reporters.common import ReportSurveillanceEventRecorder  # noqa: F401
from emodpy.reporters.common import SpatialReport  # noqa: F401
from emodpy.reporters.common import InsetChart as _InsetChart
from emodpy.reporters.common import DemographicsReport  # noqa: F401
from emodpy.reporters.common import PropertyReport  # noqa: F401
from emodpy.reporters.common import ReportInfectionDuration  # noqa: F401
from emodpy.reporters.common import SpatialReportChannels  # noqa: F401
from emodpy.reporters.common import ReportDrugStatus  # noqa: F401
from emodpy.reporters.common import ReportEventRecorder # noqa: F401
from emodpy.reporters.base import ReportFilter
from emodpy.reporters.base import BuiltInReporter
from emodpy.reporters.base import Reporters
from typing import Union
from emodpy_malaria.utils import targeting_config
from emodpy_malaria.utils.emod_enum import SpatialOutputChannel, VectorGender, VectorGeneticsStratification, VectorStateEnum, DrugResistantStatisticType  # noqa: F401
from emodpy_malaria.utils.config_utils import validate_bins


class InsetChart(_InsetChart):
    """
    JSON report containing simulation-wide averages per time step across a wide range of malaria-specific
    data channels. Channels are fully determined by the simulation type and cannot be altered without
    modifying the EMOD source code.

    Output is written to ``InsetChart.json``. The report cannot be generated per-node; use
    ReportMalariaFiltered for node-level InsetChart-style output.

    Standard malaria channels:

    - **30-day Avg Infection Duration** — running average duration (days) of infections cleared in the
      last 30 days (naturally and via drugs). Controlled by **include_30day_avg_infection_duration**.
    - **Adult Vectors** — average number of adult vectors per node.
    - **Air Temperature** — average air temperature (Celsius) per node.
    - **Avg Num Infections** — average number of infections per infected person (may exceed 1).
    - **Avg Num Vector Infs** — average infections per infected/infectious vector. Only present with
      MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.
    - **Births** — cumulative live births.
    - **Blood Smear Gametocyte Prevalence** — fraction detectable by BLOOD_SMEAR_GAMETOCYTES diagnostic.
    - **Blood Smear Parasite Prevalence** — fraction detectable by BLOOD_SMEAR_PARASITES diagnostic.
    - **Campaign Cost** — cumulative campaign cost (USD) from Cost_To_Consumer.
    - **Daily Bites per Human** — average mosquito bites per person per day.
    - **Daily EIR** — entomological inoculation rate (infected bites/day/person).
    - **Disease Deaths** — cumulative malaria-attributed deaths.
    - **Fever Prevalence** — fraction with fever above Report_Detection_Threshold_Fever.
    - **Human Infectious Reservoir** — average infectiousness per individual to vectors.
    - **Infected** — fraction of population currently infected.
    - **Infected and Infectious Vectors** — fraction of adult female vectors with oocysts or sporozoites.
      Only present with MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.
    - **Infectious Vectors** — fraction of vectors currently infectious.
    - **Land Temperature** — average land temperature (Celsius) per node.
    - **Log Prevalence** — log10 of the Infected channel.
    - **Mean Parasitemia** — geometric mean parasites per microliter of blood.
    - **New Clinical Cases** — count of new clinical cases (controlled by Clinical_Fever_Threshold
      parameters).
    - **New Infections** — number of individuals newly infected (not total new infections).
    - **New Severe Cases** — new severe malaria cases based on anemia, parasite density, and fever
      probabilities.
    - **New Vector Infections** — vectors newly infected that day. Only present with
      MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.
    - **Newly Symptomatic** — 50% of new infections randomly selected as symptomatic.
    - **PCR Gametocyte Prevalence** — fraction detectable by PCR_GAMETOCYTES diagnostic.
    - **PCR Parasite Prevalence** — fraction detectable by PCR_PARASITES diagnostic.
    - **PfHRP2 Prevalence** — fraction detectable by PF_HRP2 diagnostic.
    - **Rainfall** — average rainfall (mm/day) per node.
    - **Relative Humidity** — average relative humidity per node.
    - **Statistical Population** — total individuals in the simulation.
    - **Symptomatic Population** — not connected in malaria simulations.
    - **True Prevalence** — fraction detectable by TRUE_PARASITE_DENSITY diagnostic.
    - **Variant Fraction-PfEMP1 Major** — average fraction of PfEMP1 antibody variants seen.

    Dynamic channels (added via configuration):

    - **Has_<InterventionName>** — one channel per entry in **has_interventions**. Fraction of population
      with that persistent intervention.
    - **HasIP_<Key>:<Value>** — one channel per value of each IP key in **has_ip**. Fraction of population
      with that IP value.
    - **Possible Mothers**, **New Pregnancies**, **Currently Pregnant** — added when
      **include_pregnancies** is True.

    See output details in [Inset Chart Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-inset-chart/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        has_ip (list[str], optional): A channel is added for each value of each IndividualProperty key
            provided. Channel name: ``HasIP_<Key>:<Value>``. Keys must be defined in demographics.

            Default: None

        has_interventions (list[str], optional): A channel is added for each intervention name provided.
            Channel name: ``Has_<InterventionName>``. Only pertains to persistent interventions.

            Default: None

        include_pregnancies (bool, optional): If True, adds pregnancy-related channels: Possible Mothers,
            New Pregnancies, Currently Pregnant.

            Default: False

        include_30day_avg_infection_duration (bool, optional): If True, includes the '30-day Avg Infection
            Duration' channel. If False, the channel is not in the report.

            Default: False

    """
    def __init__(self,
                 reporters_object: Reporters,
                 has_ip: list[str] = None,
                 has_interventions: list[str] = None,
                 include_pregnancies: bool = False,
                 include_30day_avg_infection_duration: bool = False):
        super().__init__(reporters_object=reporters_object,
                         has_ip=has_ip,
                         has_interventions=has_interventions,
                         include_pregnancies=include_pregnancies)
        self.parameters["Inset_Chart_Reporting_Include_30Day_Avg_Infection_Duration"] = 1 if include_30day_avg_infection_duration else 0

# ---------------------------------------------------------------------------
#  Standalone malaria BuiltInReporters
# ---------------------------------------------------------------------------


class MalariaSummaryReport(BuiltInReporter):
    """
    Provides a summary of malaria-related data stratified by age bins and parasitemia bins. Outputs prevalence, clinical
    incidence, severe disease, and parasite densities aggregated over configurable reporting intervals.

    See output details in [Malaria Summary Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-malaria-summary/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        reporting_interval (float): In days, Defines the cadence of the report by specifying how many time steps to
            collect data before writing the data to  the file. This will limit system memory usage and is advised when large output
            files are expected.

            Minimum value: 1
            Maximum value: 1000000

        age_bins (list[float], optional): The age bins (in years, in ascending order) to aggregate within and report. An
            empty array means the report will not stratify data by age.

            Minimum value: 0
            Maximum value: 125
            Default: []

        parasitemia_bins (list[float], optional): Parasitemia bins (in infected red blood cells per microliter of blood)
            to aggregate within and report. A value greater than or equal to zero in the first bin indicates that the
            uninfected people should be added to this bin. The values must be in ascending order.

            Minimum value: -3.40282e+38
            Maximum value: 3.40282e+38
            Default: []

        infectiousness_bins (list[float], optional): Infectiousness bins to aggregate within and report. The values must
            be in ascending order.

            Minimum value: 0
            Maximum value: 100
            Default: []

        max_number_reports (int, optional): The maximum number of report output files that will be produced for a given
            simulation.

            Minimum value: 0
            Maximum value: 1000000
            Default: 1

        pretty_format (bool, optional): When set to true (1), the JSON output will use pretty formatting. The default,
            false (0), saves space.

            Default: False

        add_prevalence_by_hrp2 (bool, optional): If true, the 'PfPR_2to10-HRP2' and the 'PfPR by Age Bin-HRP2'
            channels will be added. These channels use **detection_threshold_true_hrp2** to determine if a person's
            HRP2 level counts towards prevalence.

            Default: False

        add_true_density_vs_threshold (bool, optional): If set to true, four new channels will be added to the report
            that use true density instead of measured. These additional channels are: 'PfPR_2to10-True', 'PfPR by Age
            Bin-True', 'Pf Gametocyte Prevalence by Age Bin-True', and 'Mean Log Parasite Density by Age Bin-True'.
            The true densities will be compared to thresholds: **detection_threshold_true_parasite_density** and
            **detection_threshold_true_gametocyte_density**.

            Default: False

        detection_threshold_true_parasite_density (float, optional): Used when **add_true_density_vs_threshold** is true.
            The true parasite density is compared against this threshold. It impacts the 'PfPR_2to10-True', 'PfPR by
            Age Bin-True', and 'Mean Log Parasite Density by Age Bin-True' channels.

            Minimum value: 0
            Maximum value: 3.40282e+38
            Default: None

        detection_threshold_true_gametocyte_density (float, optional): Used when **add_true_density_vs_threshold** is true.
            The true gametocyte density is compared against this threshold. It impacts the 'Pf Gametocyte Prevalence by
            Age Bin-True' channel.

            Minimum value: 0
            Maximum value: 3.40282e+38
            Default: None

        detection_threshold_true_hrp2 (float, optional): Used when **add_prevalence_by_hrp2** is true. If the true HRP2
            value is greater than this threshold, the prevalence will be increased in the 'PfPR_2to10-HRP2' and the
            'PfPR by Age Bin-HRP2' channels.

            Minimum value: 0
            Maximum value: 3.40282e+38
            Default: None

        include_data_by_time_and_pfpr (bool, optional): When set to true, the 'DataByTimeAndPfPRBinsAndAgeBins' element
            is included in the report. You can save disk space by setting this to false.

            Default: True

        include_data_by_time_and_infectiousness (bool, optional): When set to true, the
            'DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins' element is included in the report. You can save disk
            space by setting this to false.

            Default: True

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 reporting_interval: float,
                 age_bins: list[float] = None,
                 parasitemia_bins: list[float] = None,
                 infectiousness_bins: list[float] = None,
                 max_number_reports: int = 1,
                 pretty_format: bool = False,
                 add_prevalence_by_hrp2: bool = False,
                 add_true_density_vs_threshold: bool = False,
                 detection_threshold_true_parasite_density: float = None,
                 detection_threshold_true_gametocyte_density: float = None,
                 detection_threshold_true_hrp2: float = None,
                 include_data_by_time_and_pfpr: bool = True,
                 include_data_by_time_and_infectiousness: bool = True,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='MalariaSummaryReport',
                         report_filter=report_filter)

        if add_prevalence_by_hrp2 and detection_threshold_true_hrp2 is None:
            raise ValueError("detection_threshold_true_hrp2 must be provided when add_prevalence_by_hrp2 is true.")
        if detection_threshold_true_hrp2 is not None and not add_prevalence_by_hrp2:
            raise UserWarning("detection_threshold_true_hrp2 is provided, but add_prevalence_by_hrp2 is false. "
                              "The provided detection_threshold_true_hrp2 will not be used.")
        if add_true_density_vs_threshold and (detection_threshold_true_parasite_density is None or detection_threshold_true_gametocyte_density is None):
            raise ValueError("Both detection_threshold_true_parasite_density and "
                             "detection_threshold_true_gametocyte_density must be provided when add_true_density_vs_threshold is true.")
        if (detection_threshold_true_parasite_density is not None or detection_threshold_true_gametocyte_density is not None) and not add_true_density_vs_threshold:
            raise UserWarning("At least one of detection_threshold_true_parasite_density or detection_threshold_true_gametocyte_density is provided, but add_true_density_vs_threshold is false. "
                              "The provided detection thresholds will not be used.")
        self.parameters.Reporting_Interval = reporting_interval
        self.parameters.Max_Number_Reports = max_number_reports
        if pretty_format:
            self.parameters.Pretty_Format = 1
        if add_prevalence_by_hrp2:
            self.parameters.Add_Prevalence_By_HRP2 = 1
            self.parameters.Detection_Threshold_True_HRP2 = detection_threshold_true_hrp2
        if add_true_density_vs_threshold:
            self.parameters.Add_True_Density_Vs_Threshold = 1
            self.parameters.Detection_Threshold_True_Parasite_Density = detection_threshold_true_parasite_density
            self.parameters.Detection_Threshold_True_Gametocyte_Density = detection_threshold_true_gametocyte_density

        self.parameters.Include_DataByTimeAndPfPRBinsAndAgeBins = 1 if include_data_by_time_and_pfpr else 0
        self.parameters.Include_DataByTimeAndInfectiousnessBinsAndPfPRBinsAndAgeBins = 1 if include_data_by_time_and_infectiousness else 0

        if age_bins is not None:
            self.parameters.Age_Bins = age_bins
        if parasitemia_bins is not None:
            self.parameters.Parasitemia_Bins = parasitemia_bins
        if infectiousness_bins is not None:
            self.parameters.Infectiousness_Bins = infectiousness_bins

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')

    def _set_min_age_years(self, min_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'min_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_max_age_years(self, max_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'max_age_years is not a valid parameter for {reporter_class_name}.')


class MalariaPatientJSONReport(BuiltInReporter):
    """
    The malaria patient data report (MalariaPatientJSONReport.json) is a JSON-formatted report that provides medical
    data for each individual on each day of the simulation. For a specified number of time steps, each "patient" will
    have information collected on the temperature of their fever, their parasite counts, treatments they received, and
    other relevant data.

    The output contains a ``patient_array`` where each patient has both constant fields (``id``, ``birthday``,
    ``initial_age``) and daily time-series arrays for: ``asexual_parasites`` (blood smear count),
    ``asexual_positive_fields``, ``gametocyte_positive_fields``, ``gametocytes`` (blood smear count), ``hemoglobin``,
    ``infected_mosquito_fraction``, ``temps`` (body temperature in Celsius, -1 if no fever), ``treatment`` (drug names
    separated by 'space+space'), ``true_asexual_parasites``, and ``true_gametocytes``.

    This reporter has no additional parameters beyond filtering.

    See output details in [Malaria Patient Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-malaria-patient/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='MalariaPatientJSONReport',
                         report_filter=report_filter)

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')


class ReportMalariaFiltered(BuiltInReporter):
    """
    The malaria filtered report (ReportMalariaFiltered.json) is the same as the default InsetChart report, but provides
    filtering options to select data by time, node, age, individual properties, and interventions. The output format and
    channels are identical to InsetChart.json.

    Standard malaria channels include: Adult Vectors, Air Temperature, Avg Num Infections, Births,
    Blood Smear Gametocyte Prevalence, Blood Smear Parasite Prevalence, Campaign Cost, Daily Bites per Human,
    Daily EIR, Disease Deaths, Fever Prevalence, Human Infectious Reservoir, Infected, Infectious Vectors,
    Land Temperature, Log Prevalence, Mean Parasitemia, New Clinical Cases, New Infections, New Severe Cases,
    Newly Symptomatic, PCR Gametocyte Prevalence, PCR Parasite Prevalence, PfHRP2 Prevalence, Rainfall,
    Relative Humidity, Statistical Population, True_Prevalence, and Variant Fraction-PfEMP1 Major. Additional
    dynamic channels (``Has_<Intervention>``, ``HasIP_<Key>:<Value>``) are added based on ``has_interventions``
    and ``has_ip``.

    See output details in [Filtered Malaria Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-filtered-malaria/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        has_ip (list[str], optional): A list of individual property Key:Value pairs. For each pair, a
            ``HasIP_<Key>:<Value>`` channel is added to the report showing the fraction of the filtered population
            with that property.

            Default: None

        has_interventions (list[str], optional): A list of intervention names (matching the ``Intervention_Name``
            parameter in the campaign). For each intervention, a ``Has_<InterventionName>`` channel is added showing the
            fraction of the filtered population that currently has that intervention.

            Default: None

        include_30day_avg_infection_duration (bool, optional): If true, the '30-Day Avg Infection Duration' channel is
            included. This is a running average of the duration of each infection that cleared in the last 30 days
            (both naturally and due to drugs).

            Default: True

        include_pregnancies (bool, optional): If true, three pregnancy-related channels are added to the report:
            'Possible Mothers', 'New Pregnancies', and 'Currently Pregnant'.

            Default: False

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 has_ip: list[str] = None,
                 has_interventions: list[str] = None,
                 include_30day_avg_infection_duration: bool = True,
                 include_pregnancies: bool = False,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportMalariaFiltered',
                         report_filter=report_filter)

        self.parameters.Include_30Day_Avg_Infection_Duration = 1 if include_30day_avg_infection_duration else 0
        self.parameters.Include_Pregnancies = 1 if include_pregnancies else 0
        if has_ip is not None:
            self.parameters.Has_IP = has_ip
        if has_interventions is not None:
            self.parameters.Has_Interventions = has_interventions

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')


class ReportMalariaFilteredIntraHost(BuiltInReporter):
    """
    Provides detailed intra-host malaria dynamics (parasite densities, immune responses) filtered by configurable
    criteria. Same parameters as ReportMalariaFiltered.

    See output details in [Filtered Malaria Intra-Host Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-malaria-filtered-intra-host/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        has_ip (list[str], optional): A list of individual property Key:Value pairs. For each pair, a set of channels
            will be added to the report for people with that property.

            Default: None

        has_interventions (list[str], optional): A list of intervention names. For each intervention, a set of channels
            will be added to the report for people who have that intervention.

            Default: None

        include_30day_avg_infection_duration (bool, optional): When true, the '30-Day Avg Infection Duration' channel
            will be included in the report.

            Default: True

        include_pregnancies (bool, optional): If true, three pregnancy-related channels are added to the report:
            'Possible Mothers', 'New Pregnancies', and 'Currently Pregnant'.

            Default: False

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 has_ip: list[str] = None,
                 has_interventions: list[str] = None,
                 include_30day_avg_infection_duration: bool = True,
                 include_pregnancies: bool = False,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportMalariaFilteredIntraHost',
                         report_filter=report_filter)

        self.parameters.Include_30Day_Avg_Infection_Duration = 1 if include_30day_avg_infection_duration else 0
        self.parameters.Include_Pregnancies = 1 if include_pregnancies else 0
        if has_ip is not None:
            self.parameters.Has_IP = has_ip
        if has_interventions is not None:
            self.parameters.Has_Interventions = has_interventions

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')


class MalariaImmunityReport(BuiltInReporter):
    """
    The malaria immunity report (MalariaImmunityReport.json) is a JSON-formatted report that provides statistics for
    several antibody types for specified age bins over a specified reporting duration. The report tracks the average and
    standard deviation in the fraction of observed antibodies for merozoite surface protein (MSP), Plasmodium falciparum
    erythrocyte membrane protein 1 (PfEMP1), and non-specific (less immunogenic) minor surface epitopes. The total
    amount possible is determined by the parameters ``Falciparum_MSP_Variants``, ``Falciparum_PfEMP1_Variants``, and
    ``Falciparum_Nonspecific_Types``. The greater the fraction, the more antibodies the individual has against possible
    new infections; the smaller the fraction, the more naive the individual's immune system is to malaria.

    Output channels (each stratified by age bin and reporting interval):

    - ``MSP Mean by Age Bin`` / ``MSP StdDev by Age Bin`` — average and standard deviation of the fraction of MSP
      antibodies over the total possible (``Falciparum_MSP_Variants``).
    - ``PfEMP1 Mean by Age Bin`` / ``PfEMP1 StdDev by Age Bin`` — average and standard deviation of the fraction of
      PfEMP1 antigens for which antibodies have developed over the total possible (``Falciparum_PfEMP1_Variants``).
    - ``Non-Specific Mean by Age Bin`` / ``Non-Specific StdDev by Age Bin`` — average and standard deviation of the
      fraction of non-specific minor epitope antibodies over the total possible (``Falciparum_Nonspecific_Types``).

    See output details in [Malaria Immunity Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-malaria-immunity/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        reporting_interval (float, optional): Defines the cadence of the report by specifying how many time steps to
            collect data before writing to the file. This will limit system memory usage and is advised when large output
            files are expected.

            Minimum value: 1
            Maximum value: 1000000
            Default: 1000000

        age_bins (list[float], optional): The age bins (in years, in ascending order) to aggregate within and report. An
            empty array does not stratify by age.

            Minimum value: 0
            Maximum value: 125
            Default: []

        max_number_reports (int, optional): The maximum number of report output files that will be produced for a given
            simulation.

            Minimum value: 0
            Maximum value: 1000000
            Default: 1000000

        pretty_format (bool, optional): When set to true, the JSON output will use pretty formatting. The default,
            false, saves space.

            Default: False

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 reporting_interval: float = 1000000,
                 age_bins: list[float] = None,
                 max_number_reports: int = 1000000,
                 pretty_format: bool = False,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='MalariaImmunityReport',
                         report_filter=report_filter)

        self.parameters.Reporting_Interval = reporting_interval
        self.parameters.Max_Number_Reports = max_number_reports
        self.parameters.Pretty_Format = 1 if pretty_format else 0
        if age_bins is not None:
            self.parameters.Age_Bins = age_bins

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')

    def _set_min_age_years(self, min_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'min_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_max_age_years(self, max_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'max_age_years is not a valid parameter for {reporter_class_name}.')


class ReportVectorGenetics(BuiltInReporter):
    """
    The vector genetics report is a CSV-formatted report that collects information on how many vectors of each
    genome/allele combination exist at each time, node, and vector state. Information can only be collected on one
    species per report; to track multiple species, configure multiple instances with different ``species`` values.

    When ``parasite_barcodes`` is provided, the report uses the ``ReportVectorGeneticsMalariaGenetics`` EMOD reporter
    class (for ``Malaria_Model`` = MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS), adding
    ``NumVectorsWithSporozoites_<barcode>`` columns. Otherwise it uses the standard ``ReportVectorGenetics`` class.

    Each row in the output represents one time step, node, and genome/allele combination. Stratification columns include
    ``Time``, ``NodeID``, and either ``Genome`` (when ``stratify_by`` is GENOME or SPECIFIC_GENOME) or ``Alleles``
    (when ``stratify_by`` is ALLELE or ALLELE_FREQ).

    Data columns include ``VectorPopulation`` (total female vectors in infectious, infected, or adult states) and,
    when ``include_vector_state_columns`` is true: ``STATE_INFECTIOUS``, ``STATE_INFECTED``, ``STATE_ADULT``,
    ``STATE_MALE``, ``STATE_IMMATURE``, ``STATE_LARVA``, and ``STATE_EGG``. When ``include_death_state_columns`` is
    true, additional columns are added for the number of vectors that died in each state (``VectorPopulationNumDied``,
    ``InfectiousNumDied``, ``InfectedNumDied``, ``AdultsNumDied``, ``MaleNumDied``) and average age at death
    (``VectorPopulationAvgAgeAtDeath``, ``InfectiousAvgAgeAtDeath``, ``InfectedAvgAgeAtDeath``,
    ``AdultsAvgAgeAtDeath``, ``MaleAvgAgeAtDeath``).

    See output details in [Vector Genetics Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-vector-genetics/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        species (str, optional): The vector species to report on; the name must match a species added via
            ``malaria_config.add_species()`` in the config builder. The name will be added to the report filename.
            If not specified, the first species found will be used.

            Default: None

        gender (Union[VectorGender, str], optional): The gender of the vectors to include in the report. This
            controls which state columns appear in the output. Use the ``VectorGender`` enum.

            Default: VectorGender.VECTOR_FEMALE

        include_vector_state_columns (bool, optional): If true, columns for each vector state (STATE_INFECTIOUS,
            STATE_INFECTED, STATE_ADULT, STATE_MALE, STATE_IMMATURE, STATE_LARVA, STATE_EGG) will be included.

            Default: True

        include_death_state_columns (bool, optional): If true, adds columns for the number of vectors that died in
            each state during the time step as well as the average age at death. It adds two columns (count and average
            age) for each of the following states: ADULT, INFECTED, INFECTIOUS, and MALE.

            Default: False

        combine_similar_genomes (bool, optional): If true, genomes are combined for each locus (ignoring **gender**) if
            the set of alleles of the two genomes are the same (e.g. '1-0' is considered the same as '0-1'). Only
            applies when ``stratify_by`` is GENOME or SPECIFIC_GENOME.

            Default: False

        stratify_by (Union[VectorGeneticsStratification, str], optional): Determines how the report will be
            stratified. Use the ``VectorGeneticsStratification`` enum. Possible values:

            - ``GENOME`` — one row per unique genome combination.
            - ``SPECIFIC_GENOME`` — only genomes matching ``specific_genome_combinations_for_stratification``
              (required).
            - ``ALLELE`` — stratify by allele combinations in ``allele_combinations_for_stratification`` (required).
            - ``ALLELE_FREQ`` — report frequency counts for alleles in ``alleles_for_stratification``.

            Default: VectorGeneticsStratification.GENOME

        specific_genome_combinations_for_stratification (list, optional): A list of genome combination objects. Required
            when ``stratify_by`` is SPECIFIC_GENOME. Each object has an ``Allele_Combination`` key containing a list of
            allele pairs. Use ``'*'`` to list all entries at a locus and ``'?'`` to combine all entries at a locus.

            Example::

                specific_genome_combinations_for_stratification=[
                    {"Allele_Combination": [["X", "X"], ["a0", "*"], ["b1", "b0"]]},
                    {"Allele_Combination": [["X", "X"], ["a1", "a0"], ["b0", "*"]]}
                ]

            Default: None

        allele_combinations_for_stratification (list, optional): A list of allele combination lists. Required when
            ``stratify_by`` is ALLELE. Each entry is a list of allele strings representing one combination to track.

            Example::

                allele_combinations_for_stratification=[["a0", "b0"], ["a1", "b1"]]

            Default: None

        alleles_for_stratification (list[str], optional): A list of allele strings for which to collect frequency
            counts. Used when ``stratify_by`` is ALLELE_FREQ. If empty, the report uses all possible alleles.

            Example::

                alleles_for_stratification=["a0", "a1", "b0", "b1"]

            Default: None

        parasite_barcodes (list[str], optional): A list of parasite barcode strings. When provided, the report switches
            to the ``ReportVectorGeneticsMalariaGenetics`` EMOD class, adding a
            ``NumVectorsWithSporozoites_<barcode>`` column for each barcode. Use ``'*'`` as a wild card.

            Example::

                parasite_barcodes=["AABBCCDD", "AABB****"]

            Default: None

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 species: str = None,
                 gender: Union[VectorGender, str] = VectorGender.VECTOR_FEMALE,
                 include_vector_state_columns: bool = True,
                 include_death_state_columns: bool = False,
                 combine_similar_genomes: bool = False,
                 stratify_by: Union[VectorGeneticsStratification, str] = VectorGeneticsStratification.GENOME,
                 specific_genome_combinations_for_stratification: list = None,
                 allele_combinations_for_stratification: list = None,
                 alleles_for_stratification: list[str] = None,
                 parasite_barcodes: list[str] = None,
                 report_filter: ReportFilter = None):
        if not isinstance(gender, VectorGender):
            try:
                gender = VectorGender(gender)
            except ValueError:
                raise ValueError(
                    f"gender must be a VectorGender enum value, got {gender!r}. "
                    f"Valid options: {list(VectorGender)}")
        if not isinstance(stratify_by, VectorGeneticsStratification):
            try:
                stratify_by = VectorGeneticsStratification(stratify_by)
            except ValueError:
                raise ValueError(
                    f"stratify_by must be a VectorGeneticsStratification enum value, got {stratify_by!r}. "
                    f"Valid options: {list(VectorGeneticsStratification)}")

        if stratify_by == VectorGeneticsStratification.SPECIFIC_GENOME and specific_genome_combinations_for_stratification is None:
            raise ValueError("specific_genome_combinations_for_stratification is required when stratify_by is SPECIFIC_GENOME.")
        if specific_genome_combinations_for_stratification is not None and stratify_by != VectorGeneticsStratification.SPECIFIC_GENOME:
            raise UserWarning("specific_genome_combinations_for_stratification is provided, but stratify_by is not SPECIFIC_GENOME. "
                              "The provided specific_genome_combinations_for_stratification will not be used.")
        if stratify_by == VectorGeneticsStratification.ALLELE and allele_combinations_for_stratification is None:
            raise ValueError("allele_combinations_for_stratification is required when stratify_by is ALLELE.")
        if allele_combinations_for_stratification is not None and stratify_by != VectorGeneticsStratification.ALLELE:
            raise UserWarning("allele_combinations_for_stratification is provided, but stratify_by is not ALLELE. "
                              "The provided allele_combinations_for_stratification will not be used.")
        if stratify_by == VectorGeneticsStratification.ALLELE_FREQ and alleles_for_stratification is None:
            raise ValueError("alleles_for_stratification is required when stratify_by is ALLELE_FREQ.")
        if alleles_for_stratification is not None and stratify_by != VectorGeneticsStratification.ALLELE_FREQ:
            raise UserWarning("alleles_for_stratification is provided, but stratify_by is not ALLELE_FREQ. "
                              "The provided alleles_for_stratification will not be used.")
        if combine_similar_genomes and stratify_by not in [VectorGeneticsStratification.GENOME, VectorGeneticsStratification.SPECIFIC_GENOME]:
            raise ValueError("combine_similar_genomes can only be true when stratify_by is GENOME or SPECIFIC_GENOME.")

        reporter_class_name = 'ReportVectorGeneticsMalariaGenetics' if parasite_barcodes is not None else 'ReportVectorGenetics'

        super().__init__(reporters_object=reporters_object,
                         reporter_class_name=reporter_class_name,
                         report_filter=report_filter)

        self.parameters.Gender = gender
        self.parameters.Include_Vector_State_Columns = 1 if include_vector_state_columns else 0
        self.parameters.Include_Death_By_State_Columns = 1 if include_death_state_columns else 0
        self.parameters.Combine_Similar_Genomes = 1 if combine_similar_genomes else 0
        self.parameters.Stratify_By = stratify_by

        if species is not None:
            self.parameters.Species = species
        if specific_genome_combinations_for_stratification is not None:
            self.parameters.Specific_Genome_Combinations_For_Stratification = specific_genome_combinations_for_stratification
        if allele_combinations_for_stratification is not None:
            self.parameters.Allele_Combinations_For_Stratification = allele_combinations_for_stratification
        if alleles_for_stratification is not None:
            self.parameters.Alleles_For_Stratification = alleles_for_stratification
        if parasite_barcodes is not None:
            self.parameters.Parasite_Barcodes = parasite_barcodes

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')

    def _set_min_age_years(self, min_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'min_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_max_age_years(self, max_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'max_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_ip_key_value(self, must_have_ip_key_value: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_ip_key_value is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_intervention(self, must_have_intervention: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_intervention is not a valid parameter for {reporter_class_name}.')


ReportVectorGeneticsMalariaGenetics = ReportVectorGenetics


class ReportVectorStats(BuiltInReporter):
    """
    The vector statistics report (ReportVectorStats.csv) is a CSV-formatted report that provides detailed life-cycle
    data on the vectors in the simulation. The report is stratified by time, node ID, and (optionally) species.

    ``ReportVectorStatsMalariaGenetics`` is an alias for this class — users only need ``ReportVectorStats`` and can
    pass the ``barcodes`` parameter to enable genetics output.

    When ``barcodes`` is provided, the report switches to the ``ReportVectorStatsMalariaGenetics`` EMOD reporter class
    (for ``Malaria_Model`` = MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS), adding genetics-specific columns for
    parasite status in the vector population. These additional columns include:

    - ``MigrationFromCountLocal`` / ``MigrationFromCountRegional`` — vector migration counts.
    - ``NumVectorsNone`` — uninfected vectors (no oocysts or sporozoites).
    - ``NumVectorsOnlyOocysts`` — infected but not yet infectious (oocysts only).
    - ``NumVectorsOnlySporozoites`` — infectious vectors (sporozoites only).
    - ``NumVectorsBothOocystsSporozoites`` — vectors with both oocysts and sporozoites.
    - ``NumBitesAdults`` / ``NumBitesInfected`` / ``NumBitesInfectious`` — bite counts by infection state.
    - ``NumDiedAdults`` / ``NumDiedInfected`` / ``NumDiedInfectious`` — death counts by infection state.
    - ``NumParasiteCohortsOocysts`` / ``NumParasiteCohortsSporozoites`` — parasite cohort counts.
    - ``NumOocysts`` / ``NumSporozoites`` — total parasite counts in the vector population.
    - ``NumInfectiousToAdult`` / ``NumInfectiousToInfected`` — state transition counts.
    - ``<Barcode>`` columns — one per entry in ``barcodes``, plus an ``OtherBarcodes`` column.

    Standard data columns always present include: ``Population``, ``VectorPopulation``, ``STATE_INFECTIOUS``,
    ``STATE_INFECTED``, ``STATE_ADULT``, ``STATE_MALE``, ``STATE_IMMATURE``, ``STATE_LARVA``, ``STATE_EGG``,
    ``NewEggsCount``, ``IndoorBitesCount``, ``IndoorBitesCountInfectious``, ``OutdoorBitesCount``,
    ``OutdoorBitesCountInfectious``, ``UnmatedAdults``, ``NewAdults``, ``DiedBeforeFeeding``,
    ``DiedDuringFeedingIndoor``, ``AvgDurationLarvaeToImmature``, and habitat columns
    (``AvailableHabitat``, ``EggCrowdingCorrection``).

    Optional column groups controlled by boolean parameters:

    - **Gestation** (``include_gestation_columns``): ``NumLookingToFeed``, ``NumFedCount``,
      ``NumGestatingBegin``/``End``, ``NumAttemptFeedIndoor``/``Outdoor``, ``NumAttemptButNotFeed``,
      ``NumGestatingOnDay_0`` through ``NumGestatingOnDay_7``.
    - **Death by state** (``include_death_state_columns``): ``NumDiedInfectious``, ``NumDiedInfected``,
      ``NumDiedAdults``, ``NumDiedMale``, ``AvgAgeAtDeathInfectious``, ``AvgAgeAtDeathInfected``,
      ``AvgAgeAtDeathAdults``, ``AvgAgeAtDeathMale``.
    - **Wolbachia** (``include_wolbachia_columns``): ``VECTOR_WOLBACHIA_FREE``, ``VECTOR_WOLBACHIA_A``,
      ``VECTOR_WOLBACHIA_B``, ``VECTOR_WOLBACHIA_AB``. Summation should equal ``VectorPopulation``.
    - **Microsporidia** (``include_microsporidia_columns``): ``HasMicrosporidia-STATE_XXX`` and
      ``NoMicrosporidia-STATE_XXX`` columns for each vector state.

    See output details in [Vector Statistics Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-vector-stats/) and
    [Vector Statistics Malaria Genetics Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-vector-stats-malaria-genetics/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        species_list (list[str], optional): The species for which to include information. If empty or absent, data for
            all species will be collected.

            Default: None

        include_wolbachia_columns (bool, optional): If true, columns will be added for each Wolbachia type
            (``VECTOR_WOLBACHIA_FREE``, ``VECTOR_WOLBACHIA_A``, ``VECTOR_WOLBACHIA_B``, ``VECTOR_WOLBACHIA_AB``).
            Their sum should equal ``VectorPopulation``.

            Default: False

        include_gestation_columns (bool, optional): If true, columns will be added for feeding and gestation data
            including ``NumLookingToFeed``, ``NumFedCount``, ``NumGestatingBegin``/``End``, indoor/outdoor attempt
            counts, and ``NumGestatingOnDay_0`` through ``NumGestatingOnDay_7``.

            Default: False

        include_microsporidia_columns (bool, optional): If true, columns will be added for each vector state showing
            the number of vectors with and without microsporidia (``HasMicrosporidia-STATE_XXX``,
            ``NoMicrosporidia-STATE_XXX``).

            Default: False

        include_death_state_columns (bool, optional): If true, adds columns for the number of vectors that died in
            each state during the time step (``NumDiedInfectious``, ``NumDiedInfected``, ``NumDiedAdults``,
            ``NumDiedMale``) and average age at death (``AvgAgeAtDeathInfectious``, ``AvgAgeAtDeathInfected``,
            ``AvgAgeAtDeathAdults``, ``AvgAgeAtDeathMale``).

            Default: False

        stratify_by_species (bool, optional): If true, data will be stratified by species for each node, adding a
            ``Species`` column. When false, species data is aggregated per node.

            Default: False

        barcodes (list[str], optional): A list of barcode strings. When provided, the report switches to the
            ``ReportVectorStatsMalariaGenetics`` EMOD class. For each barcode, a column is created showing the number
            of vectors with sporozoites matching that barcode. Use ``'*'`` as a wild card. An ``OtherBarcodes`` column
            is added for vectors with barcodes not in this list.

            Example::

                barcodes=["AAAAAA", "AAAATTA", "AA**AA"]

            Default: None

    """

    def __init__(self,
                 reporters_object: Reporters,
                 species_list: list[str] = None,
                 include_wolbachia_columns: bool = False,
                 include_gestation_columns: bool = False,
                 include_microsporidia_columns: bool = False,
                 include_death_state_columns: bool = False,
                 stratify_by_species: bool = False,
                 barcodes: list[str] = None):
        reporter_class_name = 'ReportVectorStatsMalariaGenetics' if barcodes is not None else 'ReportVectorStats'

        super().__init__(reporters_object=reporters_object,
                         reporter_class_name=reporter_class_name)

        self.parameters.Include_Wolbachia_Columns = 1 if include_wolbachia_columns else 0
        self.parameters.Include_Gestation_Columns = 1 if include_gestation_columns else 0
        self.parameters.Include_Microsporidia_Columns = 1 if include_microsporidia_columns else 0
        self.parameters.Include_Death_By_State_Columns = 1 if include_death_state_columns else 0
        self.parameters.Stratify_By_Species = 1 if stratify_by_species else 0

        if species_list is not None:
            self.parameters.Species_List = species_list
        if barcodes is not None:
            self.parameters.Barcodes = barcodes


ReportVectorStatsMalariaGenetics = ReportVectorStats


class ReportVectorMigration(BuiltInReporter):
    """
    Outputs data about vector migration between nodes.

    Note: this report can grow very large very quickly. Use the filtering parameters
    (``must_be_from_node``, ``must_be_to_node``, ``must_be_in_state``, ``species_list``,
    and ``report_filter`` start/end days) to limit output to only what you need.

    See output details in [Vector Migration Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-vector-migration/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        include_genome_data (bool, optional): When true, genome data will be included in the migration report.

            Default: False

        species_list (list[str], optional): A list of vector species to report on. An empty list or None means all species.

            Default: None

        must_be_from_node (list[int], optional): Only include vectors migrating from these node IDs.

            Default: None

        must_be_to_node (list[int], optional): Only include vectors migrating to these node IDs.

            Default: None

        must_be_in_state (list[Union[VectorStateEnum, str]], optional): Only include vectors in these states.
            Only STATE_MALE, STATE_ADULT, STATE_INFECTED, and STATE_INFECTIOUS actually migrate.
            Use the ``VectorStateEnum`` to list the states, None or empty list means all states.

            Default: None

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 include_genome_data: bool = False,
                 species_list: list[str] = None,
                 must_be_from_node: list[int] = None,
                 must_be_to_node: list[int] = None,
                 must_be_in_state: list[Union[VectorStateEnum, str]] = None,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportVectorMigration',
                         report_filter=report_filter)

        self.parameters.Include_Genome_Data = 1 if include_genome_data else 0
        if species_list is not None:
            self.parameters.Species_List = species_list
        if must_be_from_node is not None:
            self.parameters.Must_Be_From_Node = must_be_from_node
        if must_be_to_node is not None:
            self.parameters.Must_Be_To_Node = must_be_to_node
        if must_be_in_state is not None:
            validated_states = []
            for state in must_be_in_state:
                if not isinstance(state, VectorStateEnum):
                    try:
                        state = VectorStateEnum(state)
                    except ValueError:
                        raise ValueError(
                            f"must_be_in_state contains invalid value {state!r}. "
                            f"Valid options: {list(VectorStateEnum)}")
                validated_states.append(str(state))
            self.parameters.Must_Be_In_State = validated_states

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')

    def _set_node_ids(self, node_ids: list[int], reporter_class_name: str) -> None:
        raise ValueError(f'node_ids is not a valid parameter for {reporter_class_name}.')

    def _set_min_age_years(self, min_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'min_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_max_age_years(self, max_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'max_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_ip_key_value(self, must_have_ip_key_value: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_ip_key_value is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_intervention(self, must_have_intervention: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_intervention is not a valid parameter for {reporter_class_name}.')


class VectorHabitatReport(BuiltInReporter):
    """
    JSON report containing larval habitat data for each vector species in the simulation. Focuses on
    statistics relevant to mosquito developmental stages (eggs and larvae), such as egg capacity, larval
    crowding, and larval mortality.

    No configuration parameters are required. Output is written to ``VectorHabitatReport.json``.

    The report is organized as a binned JSON structure. The header contains ``Subchannel_Metadata`` that
    describes the Species:Habitat axis — one bin per habitat per species (e.g. "gambiae:TEMPORARY_RAINFALL",
    "funestus:WATER_VEGETATION"). Data arrays are two-dimensional: the outer dimension is species:habitat
    bins, the inner dimension is time steps.

    Output channels (7 total):

    - **Artificial Larval Mortality** — probability of larvae in the habitat being killed due to
      interventions (e.g. larvicides).
    - **Current Habitat Capacity** — number of larvae the habitat can currently hold.
    - **Egg Crowding Factor** — probability that eggs die due to overcrowding.
    - **Local Larval Growth Modifier** — local density-dependent hatching modifier that depends on
      larval crowding.
    - **Local Larval Mortality** — local larval mortality rate due to larval competition. Mortality is
      relative to a species baseline (1.0) and intermediate larval age (0.5).
    - **Rainfall Larval Mortality** — rate at which larvae are dying due to rainfall.
    - **Total Larva** — total number of larvae of that species in that habitat during that time step.

    See output details in [Vector Habitat Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-vector-habitat/).

    Args:
        reporters_object (Reporters): The reporters object.
    """

    def __init__(self, reporters_object: Reporters):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='VectorHabitatReport')


class ReportMicrosporidia(BuiltInReporter):
    """
    CSV report tracking vector population counts broken down by species and microsporidia strain at each
    time step. For every combination of species and strain — including a "NoMicrosporidia" row representing
    uninfected vectors — it reports the number of vectors in each life stage. Useful for monitoring how
    microsporidia spreads through vector populations over time.

    No configuration parameters are required. Output is written to ``ReportMicrosporidia.csv``. One row is
    written per time step, per node, per species, and per microsporidia strain.

    Output columns:

    - **Time** — simulation time in days when the data was collected.
    - **NodeID** — external ID of the node.
    - **Species** — name of the vector species.
    - **MicrosporidiaStrain** — name of the microsporidia strain. "NoMicrosporidia" indicates vectors
      not infected with any strain.
    - **VectorPopulation** — total number of adult female vectors in this species/strain group
      (STATE_INFECTIOUS + STATE_INFECTED + STATE_ADULT).
    - **STATE_INFECTIOUS** — number of adult female vectors that are infectious.
    - **STATE_INFECTED** — number of adult female vectors that are infected but not yet infectious.
    - **STATE_ADULT** — number of uninfected adult female vectors.
    - **STATE_MALE** — number of adult male vectors.
    - **STATE_IMMATURE** — number of immature vectors (male and female).
    - **STATE_LARVA** — number of larvae (male and female).
    - **STATE_EGG** — number of eggs (male and female).

    See output details in [Microsporidia Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-microsporidia/).

    Args:
        reporters_object (Reporters): The reporters object.
    """

    def __init__(self, reporters_object: Reporters):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportMicrosporidia')


class ReportInfectionStatsMalaria(BuiltInReporter):
    """
    Outputs per-infection statistics for malaria including parasite density, gametocyte counts, and immune responses.

    See output details in [Malaria Infection Statistics Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-infection-stats-malaria/).

    Please note, when "include_column" parameters are set to True, the infection will only be included in the report
    if it meets ALL the corresponding "include_data_threshold" parameters. For example, if include_column_gametocyte
    and include_column_irbc are both set to True, an infection will only be included if it meets the thresholds for both
    gametocytes and infected red blood cells. If an infection meets the threshold for one but not the other,
    it will be excluded from the report entirely.

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        reporting_interval (float, optional): Defines how often (in days) data is collected and written.

            Minimum value: 1
            Maximum value: 1000000
            Default: 1

        include_column_gametocyte (bool, optional): When true, the gametocyte count column will be included. You
            will also need to set **include_data_threshold_gametocytes** to specify the minimum gametocyte count
            for an infection to be included in the report. The infections that do not satisfy the gametocyte
            threshold will be excluded from the report entirely, even if they satisfy the thresholds for other columns.

            Default: False

        include_column_hepatocyte (bool, optional): When true, the hepatocyte count column will be included. You
            will also need to set **include_data_threshold_hepatocytes** to specify the minimum hepatocyte count for an
            infection to be included in the report. The infections that do not satisfy the hepatocyte threshold will be
            excluded from the report entirely, even if they satisfy the thresholds for other columns.

            Default: False

        include_column_irbc (bool, optional): When true, the infected red blood cell (IRBC) count column will be
            included. You will also need to set **include_data_threshold_irbc** to specify the minimum IRBC count
            for an infection to be included in the report. The infections that do not satisfy the IRBC threshold
            will be excluded from the report entirely, even if they satisfy the thresholds for other columns.

            Default: False

        include_data_threshold_gametocytes (float, optional): The minimum number of gametocytes required for a row to
            be included in the output. This threshold is only applied if **include_column_gametocyte** is set to true.

            Minimum value: 0
            Maximum value: 3.40282e+38
            Default: 0

        include_data_threshold_hepatocytes (float, optional): The minimum number of hepatocytes required for a row to
            be included in the output. This threshold is only applied if **include_column_hepatocyte** is set to true.

            Minimum value: 0
            Maximum value: 3.40282e+38
            Default: 0

        include_data_threshold_irbc (float, optional): The minimum number of infected red blood cells required for a
            row to be included in the output. This threshold is only applied if **include_column_irbc** is set to true.

            Minimum value: 0
            Maximum value: 3.40282e+38
            Default: 0

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day

    """

    def __init__(self,
                 reporters_object: Reporters,
                 reporting_interval: float = 1,
                 include_column_gametocyte: bool = False,
                 include_column_hepatocyte: bool = False,
                 include_column_irbc: bool = False,
                 include_data_threshold_gametocytes: float = None,
                 include_data_threshold_hepatocytes: float = None,
                 include_data_threshold_irbc: float = None,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportInfectionStatsMalaria',
                         report_filter=report_filter)

        if include_column_gametocyte and include_data_threshold_gametocytes is None:
            raise ValueError("include_data_threshold_gametocytes must be provided when include_column_gametocyte is true.")
        if include_column_hepatocyte and include_data_threshold_hepatocytes is None:
            raise ValueError("include_data_threshold_hepatocytes must be provided when include_column_hepatocyte is true.")
        if include_column_irbc and include_data_threshold_irbc is None:
            raise ValueError("include_data_threshold_irbc must be provided when include_column_irbc is true.")
        if include_data_threshold_gametocytes is not None and not include_column_gametocyte:
            raise UserWarning("include_data_threshold_gametocytes is provided, but include_column_gametocyte is false. "
                              "The provided include_data_threshold_gametocytes will not be used.")
        if include_data_threshold_hepatocytes is not None and not include_column_hepatocyte:
            raise UserWarning("include_data_threshold_hepatocytes is provided, but include_column_hepatocyte is false. "
                              "The provided include_data_threshold_hepatocytes will not be used.")
        if include_data_threshold_irbc is not None and not include_column_irbc:
            raise UserWarning("include_data_threshold_irbc is provided, but include_column_irbc is false. "
                              "The provided include_data_threshold_irbc will not be used.")

        self.parameters.Reporting_Interval = reporting_interval
        self.parameters.Include_Column_Gametocyte = 1 if include_column_gametocyte else 0
        self.parameters.Include_Column_Hepatocyte = 1 if include_column_hepatocyte else 0
        self.parameters.Include_Column_IRBC = 1 if include_column_irbc else 0
        if include_column_gametocyte:
            self.parameters.Include_Data_Threshold_Gametocytes = include_data_threshold_gametocytes
        if include_column_hepatocyte:
            self.parameters.Include_Data_Threshold_Hepatocytes = include_data_threshold_hepatocytes
        if include_column_irbc:
            self.parameters.Include_Data_Threshold_IRBC = include_data_threshold_irbc

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')

    def _set_node_ids(self, node_ids: list[int], reporter_class_name: str) -> None:
        raise ValueError(f'node_ids is not a valid parameter for {reporter_class_name}.')

    def _set_min_age_years(self, min_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'min_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_max_age_years(self, max_age_years: float, reporter_class_name: str) -> None:
        raise ValueError(f'max_age_years is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_ip_key_value(self, must_have_ip_key_value: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_ip_key_value is not a valid parameter for {reporter_class_name}.')

    def _set_must_have_intervention(self, must_have_intervention: str, reporter_class_name: str) -> None:
        raise ValueError(f'must_have_intervention is not a valid parameter for {reporter_class_name}.')

    def _set_filename_suffix(self, filename_suffix: str, reporter_class_name: str) -> None:
        raise ValueError(f'filename_suffix is not a valid parameter for {reporter_class_name}.')


class ReportAntibodies(BuiltInReporter):
    """
    The antibodies report (ReportAntibodiesCapacity.csv or ReportAntibodiesConcentration.csv) is a CSV-formatted report
    that provides antibody data for each qualifying individual on user-determined days of the simulation. The report
    contains one row per individual per reporting day, with each antibody variant represented as a separate column. The
    values can be either the concentration or capacity of each antibody, depending on the **contain_capacity_data**
    setting.

    Stratification columns include Time, NodeID, IndividualID, Gender, AgeYears, Infected, PyrogenicThreshold, and
    FeverKillingRate. Data columns include MSP variants (MSP_0 through MSP_n) and PfEMP1 variants (PfEMP1_0 through
    PfEMP1_m), where the number of variants is determined by the **Falciparum_MSP_Variants** and
    **Falciparum_PfEMP1_Variants** parameters set via ``malaria_config.set_team_defaults()``
    or ``malaria_config.set_parasite_genetics_params()``. For example, with the default
    ``Falciparum_PfEMP1_Variants`` of 1070, the report will contain over 1000 PfEMP1 columns alone, producing very
    wide CSV output. The report only records individuals who have been at least exposed to antigens; antibodies that
    have not been triggered appear as empty fields.

    Note: this report gets very large very quickly and adds processing time. It is advised to use the
    **reporting_interval** and other filtering options to limit the size of the report.

    See output details in [Antibodies Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-antibodies/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        reporting_interval (float, optional): Defines how many days will pass between each time the report collects
            data and writes to the file. Data will be recorded every reporting_interval days starting with the
            start_day. This will limit system memory usage and is advised when large output files are expected.

            Minimum value: 1
            Maximum value: 1000000
            Default: 1

        contain_capacity_data (bool, optional): When true, the data for each antibody is the capacity of the antibody;
            when false, the data is the concentration. The output filename reflects this setting:
            ReportAntibodiesCapacity.csv when true, ReportAntibodiesConcentration.csv when false.

            Default: False

        infected_only (bool, optional): When true, only individuals who are currently infected will be included in the
            report.

            Default: False

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 reporting_interval: float = 1,
                 contain_capacity_data: bool = False,
                 infected_only: bool = False,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportAntibodies',
                         report_filter=report_filter)

        self.parameters.Reporting_Interval = reporting_interval
        self.parameters.Contain_Capacity_Data = 1 if contain_capacity_data else 0
        self.parameters.Infected_Only = 1 if infected_only else 0

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')


class ReportFpgOutput(BuiltInReporter):
    """
    FPG simulations have complete knowledge of every parasite genome in the population, but real-world genomic
    surveillance collects data through specific sampling strategies that capture only a fraction of infections. This
    report bridges that gap by extracting the complete genetic data on all filtered infected individuals, allowing
    post-processing tools such as the FPGObservationalModel to apply realistic surveillance sampling strategies and
    study what genetic signals different approaches can detect.

    Unlike most EMOD reports which produce a single output file, this report produces a three-file ensemble:
    **infIndexRecursive-genomes-df.csv**, **variants.npy**, and **roots.npy**. This report is intended for simulations
    where **Malaria_Model** is set to ``MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS``.

    The CSV file contains one row per infected person per sampling time step. Stratification columns include population
    (node ID elsewhere), year, month, day, infIndex, age_day, fever_status, IndividualID, and recursive_count. Data columns
    include recursive_nid (genome indices into the .npy files), infection_ids, bite_ids, and optionally genome_ids.
    The **variants.npy** file contains nucleotide sequence data and **roots.npy** contains allele root data, both
    indexed by the recursive_nid values in the CSV.

    See output details in [FPG Observational Model Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-fpg-output-observational-model/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        sampling_period (float, optional): The number of days between sampling the population. Data is collected on
            days start_day, start_day + sampling_period, start_day + 2 * sampling_period, and so on. For approximate
            monthly sampling, use 30.4166667 (365/12).

            Minimum value: 1
            Maximum value: 3.40282e+38
            Default: 1

        minimum_parasite_density (float, optional): The minimum parasite density (asexual parasites per microliter of
            blood) that an infection must have to be included. A non-zero value filters out hepatocyte-stage infections
            and those with only gametocytes.

            Minimum value: 0
            Maximum value: 3.40282e+38
            Default: 1

        include_genome_ids (bool, optional): When true, an additional genome_ids column is appended to the CSV output
            containing EMOD's unique ID for the genome of each infection's parasite. This ID can be used to
            cross-reference genome data with other EMOD reports that include genome IDs.

            Default: False

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention

    """

    def __init__(self,
                 reporters_object: Reporters,
                 sampling_period: float = 1,
                 minimum_parasite_density: float = 1,
                 include_genome_ids: bool = False,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportFpgOutputForObservationalModel',
                         report_filter=report_filter)

        self.parameters.Sampling_Period = sampling_period
        self.parameters.Minimum_Parasite_Density = minimum_parasite_density
        self.parameters.Include_Genome_IDs = 1 if include_genome_ids else 0

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')

    def _set_filename_suffix(self, filename_suffix: str, reporter_class_name: str) -> None:
        raise ValueError(f'filename_suffix is not a valid parameter for {reporter_class_name}.')


class ReportFpgNewInfections(BuiltInReporter):
    """
    The full parasite genetics new infections report (ReportFpgNewInfections.csv) provides detailed information on
    new human infections for simulations where **Malaria_Model** is set to
    ``MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS``. Each row represents one new human infection.

    By default (report_crossover_data_instead = False), the report tracks the complete transmission chain for each new
    infection with columns including: SporozoiteToHuman_Time (day the infection happened), SporozoiteToHuman_NodeID,
    SporozoiteToHuman_VectorID, SporozoiteToHuman_BiteID, SporozoiteToHuman_HumanID, SporozoiteToHuman_NewInfectionID,
    SporozoiteToHuman_NewGenomeID, HomeNodeID (human's starting node), GametocyteToVector_Time (day the vector acquired
    gametocytes), GametocyteToVector_NodeID, GametocyteToVector_VectorID, GametocyteToVector_BiteID,
    GametocyteToVector_HumanID, FemaleGametocyteToVector_InfectionID, FemaleGametocyteToVector_GenomeID,
    MaleGametocyteToVector_InfectionID, and MaleGametocyteToVector_GenomeID.

    When report_crossover_data_instead is True, the report contains less detail on the transmission chain but adds
    a GenomeCrossoverLocations column listing the genome locations of crossovers that occurred during recombination to
    create this infection's genome. In this mode, columns include: SporozoiteToHuman_Time,
    SporozoiteToHuman_NewInfectionID, SporozoiteToHuman_NewGenomeID, FemaleGametocyteToVector_InfectionID,
    FemaleGametocyteToVector_GenomeID, MaleGametocyteToVector_InfectionID, MaleGametocyteToVector_GenomeID, and
    GenomeCrossoverLocations. This options allows for explicit tracking of crossover locations to validation purposes.

    See output details in [FPG New Infections Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-fpg-new-infections/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        report_crossover_data_instead (bool, optional): When true, instead of reporting new infections in full detail,
            the report will contain basic new infection information with the crossover locations that created each
            infection's genome. The output columns change accordingly (see class description above).

            Default: False

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 report_crossover_data_instead: bool = False,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportFpgNewInfections',
                         report_filter=report_filter)

        self.parameters.Report_Crossover_Data_Instead = 1 if report_crossover_data_instead else 0

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')


class SpatialReportMalariaFiltered(BuiltInReporter):
    """
    The filtered malaria spatial report (SpatialReportMalariaFiltered.bin) provides spatial information on malaria
    simulations, similar to the SpatialReport, but allows filtering the data by time, node ID, age, individual properties,
    and interventions, as well as collection over different intervals. Each selected channel is written to a separate
    binary file.

    Use emodpy_malaria.utils.emod_enum.SpatialOutputChannel to specify output channels for this report.

    See output details in [Spatial Malaria Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-malaria-spatial/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        spatial_output_channels (list[Union[SpatialOutputChannel, str]], optional): An array of channel names for
            spatial output by node and time step. The data from each channel will be written to a separate binary file.
            Use the ``SpatialOutputChannel`` enum to specify channels.

            Example::

                SpatialReportMalariaFiltered(reporters,
                    spatial_output_channels=[SpatialOutputChannel.PREVALENCE,
                                            SpatialOutputChannel.NEW_INFECTIONS])

            Default: None

        reporting_interval (float, optional): The number of days to collect data before normalizing it by
            the reporting_interval to produce a per-day average.

            Minimum value: 0
            Maximum value: 3.40282e+38
            Default: 1

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 spatial_output_channels: list[Union[SpatialOutputChannel, str]] = None,
                 reporting_interval: float = 1,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='SpatialReportMalariaFiltered',
                         report_filter=report_filter)

        self.parameters.Reporting_Interval = reporting_interval
        if spatial_output_channels is not None:
            validated_channels = []
            for channel in spatial_output_channels:
                if not isinstance(channel, SpatialOutputChannel):
                    try:
                        channel = SpatialOutputChannel(channel)
                    except ValueError:
                        raise ValueError(
                            f"Invalid spatial output channel {channel!r}. "
                            f"Valid options: {list(SpatialOutputChannel)}")
                validated_channels.append(channel)
            self.parameters.Spatial_Output_Channels = validated_channels

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')


class ReportInterventionPopAvg(BuiltInReporter):
    """
    CSV report providing population-average data on the usage and efficacy of persistent interventions.
    For each persistent intervention distributed to a node or person, the report provides one row per
    node per time step with the fraction of people (or nodes) that have the intervention and the average
    efficacy across multiple effect categories.

    Only persistent interventions — those that exist between time steps (e.g. SimpleBednet,
    UsageDependentBednet, Ivermectin, Larvicides) — are tracked. Transient interventions like diagnostics,
    which execute and disappear within a single time step, are not included.

    For individual-level interventions, efficacy values are averaged over the people in the node who have
    the intervention. For node-level interventions (typically vector control), there is usually one instance
    per node, so the values represent that single intervention's efficacy.

    Not all interventions provide data for this report. If an intervention does not provide support,
    a warning is issued in standard output.

    Output is written to ``ReportInterventionPopAvg.csv``.

    Stratification columns:

    - **Time** — simulation day when the data was collected.
    - **NodeID** — external ID of the node.

    Data columns:

    - **NodePopulation** — population of the node that has the indicated intervention.
    - **InterventionName** — name of the intervention (custom via Intervention_Name parameter, or
      the class name by default).
    - **FractionHas** — fraction of people in the node with at least one instance of the intervention.
      For node-level interventions, this is almost always 1.0.
    - **AvgNumberOfInterventions** — for individuals, the average number of instances per person who
      has the intervention. For nodes, the count of instances in the node.
    - **AvgEfficacy-Attracting** — average attracting efficacy (e.g. HumanHostSeekingTrap).
    - **AvgEfficacy-Repelling** — average repelling efficacy (e.g. IRSHousingModification,
      SpatialRepellentHousingModification).
    - **AvgEfficacy-Blocking** — average blocking efficacy (e.g. SimpleBednet).
    - **AvgEfficacy-Killing** — average killing efficacy (e.g. SimpleBednet, Ivermectin, Larvicides,
      SpaceSpraying).
    - **AvgEfficacy-Usage** — average usage efficacy (e.g. UsageDependentBednet).
    - **AvgEfficacy-AcquisitionBlocking** — average acquisition blocking efficacy (e.g. SimpleVaccine).
    - **AvgEfficacy-TransmissionBlocking** — average transmission blocking efficacy (e.g. SimpleVaccine).
    - **AvgEfficacy-MortalityBlocking** — average mortality blocking efficacy (e.g. SimpleVaccine).
    - **DrugConcentration** — for drug interventions, the average drug concentration across people in
      the node with the drug during this time step. For MultiPackComboDrug, each person contributes the
      sum of concentrations of drugs taken from the pack.

    See output details in [Intervention Population Average Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-intervention-population-average/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportInterventionPopAvg',
                         report_filter=report_filter)

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')


class MalariaSurveyAnalyzer(BuiltInReporter):
    """
    JSON report providing detailed individual-level malaria data for each event that occurs during the
    reporting interval. Each individual who experiences a specified event is captured as an entry in a
    ``patient_array``, with per-event snapshots of parasite densities, gametocyte counts, infectiousness,
    and diagnostic measurements. Multiple output files can be produced — one per reporting interval.

    Output is written to ``MalariaSurveyJSONAnalyzer.json``. Each file contains:

    - **ntsteps** — number of days of the simulation for which data was collected. Equals the reporting
      interval unless the simulation ended before the interval completed.
    - **patient_array** — array with one entry per individual who experienced the specified event(s).

    Per-patient metadata:

    - **id** — individual ID.
    - **node_id** — external ID of the node the person is in at the time of the first event.
    - **initial_age** — age in days when the report started tracking the individual.
    - **local_birthday** — day the individual was born/created, relative to the start of the report.

    Per-event data arrays (each entry corresponds to one event occurrence):

    - **strain_ids** — antigen/clade ID and genome ID of the individual's current infection(s).
    - **ip_data** — individual property value(s) based on **ip_key_to_collect** (all IPs if not specified).
    - **true_asexual_parasites** — actual (true) parasite density.
    - **true_gametocytes** — actual (true) gametocyte density.
    - **smeared_true_asexual_parasites** — true parasite density smeared using NASBADensityWithUncertainty.
    - **smeared_true_gametocytes** — true gametocyte density smeared using NASBADensityWithUncertainty.
    - **asexual_parasites** — parasite density measured via BLOOD_SMEAR_PARASITES diagnostic.
    - **gametocytes** — gametocyte density measured via BLOOD_SMEAR_GAMETOCYTES diagnostic.
    - **pcr_parasites** — parasite density measured via PCR_PARASITES diagnostic.
    - **pcr_gametocytes** — gametocyte density measured via PCR_GAMETOCYTES diagnostic.
    - **pfhrp2** — HRP2 level measured via PF_HRP2 diagnostic.
    - **smeared_asexual_parasites** — positive fields of view (pos_asexual_fields) with parasite density.
    - **smeared_gametocytes** — positive fields of view (pos_gametocyte_fields) with gametocyte density.
    - **infectiousness** — infectiousness of the individual at the time of the event.
    - **infectiousness_smeared** — binomial infectiousness smearing.
    - **infectiousness_age_scaled** — infectiousness adjusted for age-dependent surface area biting.
    - **pos_asexual_fields** — number of positive fields of view for parasite smears.
    - **pos_gametocyte_fields** — number of positive fields of view for gametocyte smears.
    - **temps** — body temperature in Celsius if the individual has a fever, otherwise -1.

    See output details in [Malaria Survey Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-malaria-survey/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        event_trigger_list (list[str], optional): A list of individual-level events that trigger a survey snapshot.
            If no events are listed, an exception is thrown.

            Default: None

        reporting_interval (float, optional): Defines the cadence of the report by specifying how many time steps to
            collect data before writing to the file. This limits system memory usage and is advised when large output
            files are expected.

            Minimum value: 1
            Maximum value: 1000000
            Default: 365

        max_number_reports (int, optional): The maximum number of report output files that will be produced for a given
            simulation.

            Minimum value: 0
            Maximum value: 1000000
            Default: 1000000

        pretty_format (bool, optional): When set to true (1), the JSON output will use pretty formatting. The default,
            false (0), saves space.

            Default: False

        ip_key_to_collect (str, optional): The name of an IndividualProperty key whose value to collect. An empty
            string or None means collect values for all IPs.

            Default: None

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 event_trigger_list: list[str] = None,
                 reporting_interval: float = 365,
                 max_number_reports: int = 1000000,
                 pretty_format: bool = False,
                 ip_key_to_collect: str = None,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='MalariaSurveyJSONAnalyzer',
                         report_filter=report_filter)

        self.parameters.Reporting_Interval = reporting_interval
        self.parameters.Max_Number_Reports = max_number_reports
        self.parameters.Pretty_Format = 1 if pretty_format else 0
        if event_trigger_list is not None:
            self.parameters.Event_Trigger_List = event_trigger_list
        if ip_key_to_collect is not None:
            self.parameters.IP_Key_To_Collect = ip_key_to_collect

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')


class ReportSimpleMalariaTransmission(BuiltInReporter):
    """
    JSON report tracking malaria transmission events — who transmitted malaria to whom, via which
    vector, and with what parasite strains. Each entry in the output represents a new infection and
    records the full transmission chain: the transmitting individual, the vector, and the acquiring
    individual. This report requires **Malaria_Model** to be set to
    MALARIA_MECHANISTIC_MODEL_WITH_CO_TRANSMISSION. Typically used as input to the GenEpi model.

    Output is written to ``ReportSimpleMalariaTransmission.csv``. The file contains a ``transmissions``
    array of CoTransmission objects with the following fields:

    - **node_id** — ID of the node where the infection occurred.
    - **transmitTime** — day when the vector was infected. 0 if the infection was due to
      OutbreakIndividual.
    - **transmitIndividualId** — ID of the individual that infected the vector. 0 if due to
      OutbreakIndividual.
    - **transmitInfectionIds** — list of infection IDs of the individual who infected the vector.
      Empty if due to OutbreakIndividual.
    - **transmitGametocyteDensities** — parallel list to transmitInfectionIds where each value is
      the gametocyte density for the corresponding infection. Empty if due to OutbreakIndividual.
    - **vectorId** — ID of the vector that carried the infection from the transmitting individual
      to the acquiring individual. 0 if due to OutbreakIndividual.
    - **acquireTime** — day the vector infected the acquiring individual.
    - **acquireIndividualId** — ID of the individual who received the infection. 0 for
      human-to-vector transmission events.
    - **acquireInfectionIds** — list of infections created due to the bite. Currently contains
      one entry.
    - **concurrentInfectionIds** — IDs of other infections the acquiring individual already had
      when they received this new infection.

    When **include_human_to_vector_transmission** is true, human-to-vector events are also recorded.
    These can be identified by ``acquireIndividualId`` = 0 and ``transmitTime`` = ``acquireTime``.
    This can make the file size quite large.

    See output details in [Simple Malaria Transmission Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-simple-malaria-transmission/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        include_human_to_vector_transmission (bool, optional): When true, human-to-vector transmission events will be
            included in the report. These events have acquireIndividualId=0 and transmitTime=acquireTime.

            .. warning:: Enabling this can make the output file size very large.

            Default: False

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day
                - node_ids
                - min_age_years
                - max_age_years
                - must_have_ip_key_value
                - must_have_intervention
                - filename_suffix

    """

    def __init__(self,
                 reporters_object: Reporters,
                 include_human_to_vector_transmission: bool = False,
                 report_filter: ReportFilter = None):
        super().__init__(reporters_object=reporters_object,
                         reporter_class_name='ReportSimpleMalariaTransmission',
                         report_filter=report_filter)

        self.parameters.Include_Human_To_Vector_Transmission = 1 if include_human_to_vector_transmission else 0

    def _set_start_year(self, start_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'start_year is not a valid parameter for {reporter_class_name}.')

    def _set_end_year(self, end_year: float, reporter_class_name: str) -> None:
        raise ValueError(f'end_year is not a valid parameter for {reporter_class_name}.')


# ---------------------------------------------------------------------------
#  Inheritance chain reporters — extend emodpy base reporters
# ---------------------------------------------------------------------------


class SqlReportMalaria(BuiltInReporter):
    """
    SQLite report providing epidemiological and transmission data. Extends the base SqlReport with
    malaria-specific tables and optionally genetics data (barcode, drug resistance, HRP) per infection.

    Three EMOD reporter classes are selected based on the **include_malaria** and
    **include_malaria_genetics** flags:

    - ``include_malaria=False, include_malaria_genetics=False`` — uses **SqlReport** (generic,
      no malaria-specific tables).
    - ``include_malaria=True`` — uses **SqlReportMalaria**, adding malaria-specific health and
      infection data plus an optional drug status table.
    - ``include_malaria_genetics=True`` — uses **SqlReportMalariaGenetics**, which additionally
      includes genetics data (barcode, drug resistance, HRP) in the infection data table.

    The **include_drug_status_table** parameter is only valid when **include_malaria** or
    **include_malaria_genetics** is True.

    See output details in [SQL Malaria Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-sql-malaria/) and
    [SQL Malaria Genetics Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-sql-malaria-genetics/) and [SQL Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-sql/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        include_malaria (bool, optional): When True, uses the SqlReportMalaria EMOD reporter class which adds
            malaria-specific health and infection data tables.

            Default: True

        include_malaria_genetics (bool, optional): When True, uses the SqlReportMalariaGenetics EMOD reporter
            class which additionally includes genetics data (barcode, drug resistance, HRP) per infection.
            Takes precedence over **include_malaria**.

            Default: False

        include_health_table (bool, optional): If True, include the Health table which has data for each time
            step for the health of an individual.

            Default: True

        include_individual_properties (bool, optional): If True, include a table with all possible individual
            properties and include IP data for each person in the Health table.

            Default: False

        include_infection_data_table (bool, optional): If True, include the InfectionData table which has data
            for each time step for each active infection.

            Default: True

        include_drug_status_table (bool, optional): If True, include the table that provides data at each time
            step for each drug the person has. Only valid when **include_malaria** or **include_malaria_genetics**
            is True.

            Default: False

        report_filter (ReportFilter, optional): Common report filtering parameters. Valid filtering parameters for this
            report are:

                - start_day
                - end_day

    """

    def __init__(self,
                 reporters_object: Reporters,
                 include_malaria: bool = True,
                 include_malaria_genetics: bool = False,
                 include_health_table: bool = True,
                 include_individual_properties: bool = False,
                 include_infection_data_table: bool = True,
                 include_drug_status_table: bool = False,
                 report_filter: ReportFilter = None):
        if include_drug_status_table and not include_malaria and not include_malaria_genetics:
            raise ValueError(
                "include_drug_status_table requires include_malaria=True or "
                "include_malaria_genetics=True. The base SqlReport does not support drug status tracking.")

        if include_malaria_genetics:
            reporter_class_name = 'SqlReportMalariaGenetics'
        elif include_malaria:
            reporter_class_name = 'SqlReportMalaria'
        else:
            reporter_class_name = 'SqlReport'

        BuiltInReporter.__init__(self, reporters_object=reporters_object,
                                 reporter_class_name=reporter_class_name,
                                 report_filter=report_filter)
        self.parameters.Include_Health_Table = 1 if include_health_table else 0
        self.parameters.Include_Individual_Properties = 1 if include_individual_properties else 0
        self.parameters.Include_Infection_Data_Table = 1 if include_infection_data_table else 0
        if include_malaria or include_malaria_genetics:
            self.parameters.Include_Drug_Status_Table = 1 if include_drug_status_table else 0


SqlReportMalariaGenetics = SqlReportMalaria


class ReportNodeDemographicsMalaria(ReportNodeDemographics):
    """
    CSV report extending ReportNodeDemographics with malaria-specific statistics. Provides population
    data stratified by node, with additional columns for malaria parasite counts, infectiousness,
    gametocyte density, and clinical symptom status.

    Output is written to ``ReportNodeDemographicsMalaria.csv``.

    Stratification columns:

    - **Time** — simulation day when the data was collected.
    - **NodeID** — external ID of the node.
    - **Gender** — M or F. Only present if **stratify_by_gender** is True.
    - **AgeYears** — max age in years of the bin. Only present if **age_bins** is non-empty.
    - **IndividualProp** — IP value for the row. Only present if **ip_key_to_collect** is set.
    - **HasClinicalSymptoms** — T or F. Only present if **stratify_by_has_clinical_symptoms** is True.

    Data columns:

    - **NumIndividuals** — number of individuals that meet the stratification criteria.
    - **NumInfected** — number of infected individuals that meet the stratification criteria.
    - **NodeProp = <keys>** — one column per node property with its value. Absent if no NodeProperties.
    - **AvgInfectiousness** — average infectiousness to mosquitoes, based on mature gametocyte count.
    - **AvgParasiteDensity** — average true parasite density.
    - **AvgGametocyteDensity** — average true gametocyte density.
    - **AvgVariantFractionPfEMP1Major** — average fraction of PfEMP1 Major antibody variants the
      individual has relative to Falciparum_PfEMP1_Variants.
    - **AvgNumInfections** — average number of infections.
    - **AvgInfectionClearedDuration** — average duration to clear infections.
    - **NumInfectionsCleared** — number of cleared infections.
    - **NumHasFever** — number of people with fever per the Report_Detection_Threshold_Fever parameter.
    - **NumHasClinicalSymptoms** — number of people with clinical symptoms. Only present if
      **stratify_by_has_clinical_symptoms** is False (otherwise the stratification separates them).

    See output details in [Malaria Node Demographics Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-malaria-node-demographics/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        age_bins (list[float], optional): The age bins (in years, in strictly ascending order) to aggregate
            within and report. An empty list or None means the report will not stratify by age.

            Default: None

        ip_key_to_collect (str, optional): The name of the IndividualProperties key by which to stratify
            the report. An empty string or None means the report is not stratified by IP.

            Default: None

        stratify_by_gender (bool, optional): When True, stratify the report by gender (M/F columns).

            Default: True

        stratify_by_has_clinical_symptoms (bool, optional): When True, add an extra stratification for
            people who have clinical symptoms vs. those who do not.

            Default: False

    """

    def __init__(self,
                 reporters_object: Reporters,
                 age_bins: list[float] = None,
                 ip_key_to_collect: str = None,
                 stratify_by_gender: bool = True,
                 stratify_by_has_clinical_symptoms: bool = False):
        BuiltInReporter.__init__(self, reporters_object=reporters_object,
                                 reporter_class_name='ReportNodeDemographicsMalaria')
        if ip_key_to_collect:
            self.parameters.IP_Key_To_Collect = ip_key_to_collect
        if age_bins:
            validate_bins(age_bins, 'age_bins')
        self.parameters.Age_Bins = age_bins if age_bins else []
        self.parameters.Stratify_By_Gender = 1 if stratify_by_gender else 0
        self.parameters.Stratify_By_Has_Clinical_Symptoms = 1 if stratify_by_has_clinical_symptoms else 0


class ReportNodeDemographicsMalariaGenetics(ReportNodeDemographics):
    """
    CSV report extending ReportNodeDemographicsMalaria with parasite genetics data — barcode counts,
    drug resistance markers, and HRP markers per node. Requires **Malaria_Model** to be set to
    MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

    Output is written to ``ReportNodeDemographicsMalariaGenetics.csv``.

    Stratification columns (same as ReportNodeDemographicsMalaria):

    - **Time** — simulation day when the data was collected.
    - **NodeID** — external ID of the node.
    - **Gender** — M or F. Only present if **stratify_by_gender** is True.
    - **AgeYears** — max age in years of the bin. Only present if **age_bins** is non-empty.
    - **IndividualProp** — IP value for the row. Only present if **ip_key_to_collect** is set.
    - **HasClinicalSymptoms** — T or F. Only present if **stratify_by_has_clinical_symptoms** is True.

    Data columns (inherited from ReportNodeDemographicsMalaria):

    - **NumIndividuals** — number of individuals that meet the stratification criteria.
    - **NumInfected** — number of infected individuals that meet the stratification criteria.
    - **NodeProp = <keys>** — one column per node property with its value.
    - **AvgInfectiousness** — average infectiousness to mosquitoes, based on mature gametocyte count.
    - **AvgParasiteDensity** — average true parasite density.
    - **AvgGametocyteDensity** — average true gametocyte density.
    - **AvgVariantFractionPfEMP1Major** — average fraction of PfEMP1 Major antibody variants.
    - **AvgNumInfections** — average number of infections.
    - **AvgInfectionClearedDuration** — average duration to clear infections.
    - **NumInfectionsCleared** — number of cleared infections.
    - **NumHasFever** — number of people with fever.
    - **NumHasClinicalSymptoms** — number with clinical symptoms (only if stratification is off).

    Genetics-specific data columns:

    - **[barcode]** — one column per barcode string in **barcodes**. Contains the number of human
      infections matching that barcode. Wildcards ('*') at a locus include all values at that locus
      (e.g. 'A*T' includes AAT, ACT, AGT, ATT).
    - **OtherBarcodes** — number of infections whose barcode is not counted by any defined barcode column.
    - **[drug_resistant_string]** — one column per entry in **drug_resistant_strings**. The value depends
      on **drug_resistant_and_hrp_statistic_type**: either a person count or an infection count.
    - **NoDrugResistance** — infections/people with drug resistant strings not matching any defined column.
    - **[hrp_string]** — one column per entry in **hrp_strings**.
    - **OtherHRP** — infections with HRP strings not matching any defined column.

    See output details in [Malaria Node Demographics Genetics Report](https://emod.idmod.org/emodpy-malaria/emod/software-report-malaria-node-demographics-genetics/).

    Args:
        reporters_object (Reporters): The reporters object given by emodpy.

        age_bins (list[float], optional): The age bins (in years, in strictly ascending order) to aggregate
            within and report. An empty list or None means the report will not stratify by age.

            Default: []

        ip_key_to_collect (str, optional): The name of the IndividualProperties key by which to stratify
            the report. An empty string or None means the report is not stratified by IP.

            Default: None

        stratify_by_gender (bool, optional): When True, stratify the report by gender (M/F columns).

            Default: True

        barcodes (list[str], optional): A list of barcode strings. The report contains the number of human
            infections with each barcode. Use '*' as a wildcard at a locus to include all values at that
            locus. For example, 'A*T' includes AAT, ACT, AGT, and ATT. An OtherBarcodes column is added
            for barcodes not matching any defined string.

            Default: None

        drug_resistant_and_hrp_statistic_type (Union[DrugResistantStatisticType, str], optional): Controls
            what statistic is reported in the drug resistant and HRP columns.

            - ``NUM_PEOPLE_WITH_RESISTANT_INFECTION`` — a person is counted if they have at least one
              infection with that drug resistant marker.
            - ``NUM_INFECTIONS`` — the total number of infections with that marker.

            Default: NUM_PEOPLE_WITH_RESISTANT_INFECTION

        drug_resistant_strings (list[str], optional): A list of strings representing drug resistant markers.
            A column is created for each with the count of infections/people matching that marker. Use '*'
            as a wildcard at a locus. A NoDrugResistance column is added for unmatched markers.

            Default: None

        hrp_strings (list[str], optional): A list of strings representing HRP markers. A column is created
            for each with the count of infections matching that marker. Use '*' as a wildcard at a locus.
            An OtherHRP column is added for unmatched markers.

            Default: None

        include_identity_by_xxx (bool, optional): When True, include columns for average Identity By State
            (IBS) and Identity By Descent (IBD) for all new infections with unique **barcodes** in the last year.

            Default: False

    """

    def __init__(self,
                 reporters_object: Reporters,
                 age_bins: list[float] = None,
                 ip_key_to_collect: str = None,
                 stratify_by_gender: bool = True,
                 barcodes: list[str] = None,
                 drug_resistant_and_hrp_statistic_type: Union[DrugResistantStatisticType, str] = DrugResistantStatisticType.NUM_PEOPLE_WITH_RESISTANT_INFECTION,
                 drug_resistant_strings: list[str] = None,
                 hrp_strings: list[str] = None,
                 include_identity_by_xxx: bool = False):
        if not isinstance(drug_resistant_and_hrp_statistic_type, DrugResistantStatisticType):
            try:
                drug_resistant_and_hrp_statistic_type = DrugResistantStatisticType(drug_resistant_and_hrp_statistic_type)
            except ValueError:
                raise ValueError(
                    f"drug_resistant_and_hrp_statistic_type must be a DrugResistantStatisticType enum value, "
                    f"got {drug_resistant_and_hrp_statistic_type!r}. "
                    f"Valid options: {list(DrugResistantStatisticType)}")

        BuiltInReporter.__init__(self, reporters_object=reporters_object,
                                 reporter_class_name='ReportNodeDemographicsMalariaGenetics')
        if ip_key_to_collect:
            self.parameters.IP_Key_To_Collect = ip_key_to_collect
        if age_bins:
            validate_bins(age_bins, 'age_bins')
        self.parameters.Age_Bins = age_bins if age_bins else []
        self.parameters.Stratify_By_Gender = 1 if stratify_by_gender else 0
        self.parameters.Drug_Resistant_And_HRP_Statistic_Type = str(drug_resistant_and_hrp_statistic_type)
        self.parameters.Include_Identity_By_XXX = 1 if include_identity_by_xxx else 0
        if barcodes is not None:
            self.parameters.Barcodes = barcodes
        if drug_resistant_strings is not None:
            self.parameters.Drug_Resistant_Strings = drug_resistant_strings
        if hrp_strings is not None:
            self.parameters.HRP_Strings = hrp_strings


# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [ReportNodeDemographics,
                 ReportSimulationStats,
                 ReportHumanMigrationTracking,
                 ReportEventCounter,
                 ReportEventRecorder,
                 ReportPluginAgeAtInfection,
                 ReportPluginAgeAtInfectionHistogram,
                 ReportNodeEventRecorder,
                 ReportCoordinatorEventRecorder,
                 ReportSurveillanceEventRecorder,
                 InsetChart,
                 SpatialReport,
                 ReportFilter,
                 DemographicsReport,
                 PropertyReport,
                 ReportInfectionDuration,
                 ReportDrugStatus,
                 SpatialReportChannels,
                 MalariaSummaryReport,
                 MalariaPatientJSONReport,
                 ReportMalariaFiltered,
                 ReportMalariaFilteredIntraHost,
                 MalariaImmunityReport,
                 ReportVectorGenetics,
                 ReportVectorGeneticsMalariaGenetics,
                 ReportVectorStats,
                 ReportVectorStatsMalariaGenetics,
                 ReportVectorMigration,
                 VectorHabitatReport,
                 ReportMicrosporidia,
                 ReportInfectionStatsMalaria,
                 ReportAntibodies,
                 ReportFpgOutput,
                 ReportFpgNewInfections,
                 SpatialReportMalariaFiltered,
                 ReportInterventionPopAvg,
                 MalariaSurveyAnalyzer,
                 ReportSimpleMalariaTransmission,
                 SqlReportMalaria,
                 SqlReportMalariaGenetics,
                 ReportNodeDemographicsMalaria,
                 ReportNodeDemographicsMalariaGenetics]

for _ in __all_exports:
    _.__module__ = __name__

__all__ = [_.__name__ for _ in __all_exports] + ['targeting_config']
