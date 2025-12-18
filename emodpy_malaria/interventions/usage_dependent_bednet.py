# Just bringing over API and preproc of 
# https://github.com/InstituteforDiseaseModeling/dtk-tools/blob/master/dtk/interventions/itn_age_season.py 
# wholesale for now. Maybe use most of this API with the schema-backed emod_api mechanism.
from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emodpy_malaria.interventions import common as malaria_common
import numpy as np
import sys


def _get_seasonal_times_and_values(campaign, seasonal_dependence):
    # Assign seasonal net usage
    # Times are days of the year
    # Input can be provided either as (times, values) for linear spline or (min coverage, day of maximum coverage)
    # under the assumption of sinusoidal dynamics. In the first case, the same value should be provided
    # for both 0 and 365; times > 365 will be ignored.
    if not seasonal_dependence:
        # Option 1: Nothing specified, our default, uniform. But why not just not have a seasonal multiplier?
        seasonal_times = [*range(0, 361, 30), 365]
        seasonal_values = len(seasonal_times) * [1]
    elif all([k in seasonal_dependence.keys() for k in ['Times', 'Values']]):
        # Option 2: Take raw values from user
        seasonal_times = seasonal_dependence['Times']
        seasonal_values = seasonal_dependence['Values']
    elif all([k in seasonal_dependence.keys() for k in ['min_cov', 'max_day']]):
        # Option 3: Create values from parameters
        seasonal_times = np.append(np.arange(0, 361, 30), 365)
        if seasonal_dependence['min_cov'] == 0:
            seasonal_dependence['min_cov'] = seasonal_dependence['min_cov'] + sys.float_info.epsilon
        seasonal_values = (1 - seasonal_dependence['min_cov']) / 2 * np.cos(
            2 * np.pi / 365 * (seasonal_times - seasonal_dependence['max_day'])) + \
                          (1 + seasonal_dependence['min_cov']) / 2
    else:
        raise ValueError('Did not find all the keys were were looking for. Possible dictionaries can be:\n'
                         '{"Times":[], "Values":[]} or {"min_cov":0.45, "max_day":300}\n')
    waning = s2c.get_class_with_defaults("WaningEffectMapLinearSeasonal", campaign.schema_path)
    waning.Initial_Effect = 1.0
    waning.Durability_Map.Times = [float(x) for x in seasonal_times]
    waning.Durability_Map.Values = [float(x) for x in seasonal_values]

    return waning


def _get_age_times_and_values(campaign, age_dependence):
    # Assign age-dependent net usage #
    # Times are ages in years (note difference from seasonal dependence)
    if not age_dependence:
        age_times = [0, 125]
        age_values = [1, 1]
    elif all([k in age_dependence.keys() for k in ['Times', 'Values']]):
        age_times = age_dependence['Times']
        age_values = age_dependence['Values']
    elif all([k in age_dependence.keys() for k in ['youth_cov', 'youth_min_age', 'youth_max_age']]):
        age_times = [0, age_dependence['youth_min_age'] - 0.1, age_dependence['youth_min_age'],
                     age_dependence['youth_max_age'] - 0.1, age_dependence['youth_max_age']]
        age_values = [1, 1, age_dependence['youth_cov'], age_dependence['youth_cov'], 1]
    else:
        raise ValueError('Did not find all the keys were were looking for. Possible dictionaries can be:\n'
                         '{"Times":[], "Values":[]} or {"youth_cov":0.7, "youth_min_age":3, "youth_max_age":13}\n')

    waning = s2c.get_class_with_defaults("WaningEffectMapLinearAge", campaign.schema_path)
    waning.Initial_Effect = 1.0
    waning.Durability_Map.Times = age_times
    waning.Durability_Map.Values = age_values

    return waning


def add_scheduled_usage_dependent_bednet(
        campaign,
        start_day: int = 1,
        demographic_coverage: float = 1,
        target_num_individuals: int = None,
        node_ids: list = None,
        ind_property_restrictions: list = None,
        target_age_min: float = 0,
        target_age_max: float = malaria_common.MAX_AGE_YEARS,
        target_gender: str = "All",
        intervention_name: str = "UsageDependentBednet",
        discard_config: dict = None,
        insecticide: str = "",
        repelling_initial_effect: float = 0,
        repelling_box_duration: int = 0,
        repelling_decay_time_constant: float = 1460,
        blocking_initial_effect: float = 0.9,
        blocking_box_duration: int = 0,
        blocking_decay_time_constant: float = 730,
        blocking_linear_times: list = None,
        blocking_linear_values: list = None,
        blocking_expire_at_end: int = 0,
        killing_initial_effect: float = 0,
        killing_box_duration: int = 0,
        killing_decay_time_constant: float = 1460,
        age_dependence: dict = None,
        seasonal_dependence: dict = None,
        dont_allow_duplicates: bool = False):
    """
    Add an insecticide-treated net (ITN) intervention with a seasonal usage
    pattern to the campaign using the **UsageDependentBednet** class.

    Note: for killing, blocking, repelling effects - depending on the parameters you set,
    different WaningEffect classes will be used:
    box_duration = -1 => WaningEffectConstant, decay_time_constant is ignored
    box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
    box_duration > 0 + decay_time_constant = 0 => WaningEffectBox
    box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day on which to start distributing the bednets
            (**Start_Day** parameter).
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        target_num_individuals: The exact number of people to select out of the targeted group. If this value is set,
            demographic_coverage parameter is ignored
        node_ids: The list of nodes to apply this intervention to (**Node_List** parameter). If not provided,
            intervention is distributed to all nodes.
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention (
            **Property_Restrictions_Within_Node** parameter). In the format ``[{
            "BitingRisk":"High"}, {"IsCool":"Yes}]``.
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple UsageDependentBednets interventions
            attached to a person if they have different Intervention_Name values.
        discard_config: A dictionary of parameters needed to define expiration distribution.
            No need to definite the distribution with all its parameters
            Default is bednet being discarded with EXPONENTIAL_DISTRIBUTION with Expiration_Period_Exponential of 10 years

            Examples::

                    for Gaussian: {"Expiration_Period_Distribution": "GAUSSIAN_DISTRIBUTION",
                                   "Expiration_Period_Gaussian_Mean": 20,
                                   "Expiration_Period_Gaussian_Std_Dev":10}
                    for Exponential: {"Expiration_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
                                     "Expiration_Period_Exponential":150}

        insecticide: The name of the insecticide defined in <config.Insecticides> for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if <config.Insecticides> does not define anything.
        repelling_initial_effect: Initial strength of the Repelling effect. The effect may decay over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial_Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial_Effect.
        blocking_initial_effect: Initial strength of the Blocking effect. The effect may decay over time.
        blocking_box_duration: Box duration of effect in days before the decay of Blocking Initial_Effect.
        blocking_decay_time_constant: The exponential decay length, in days of the Blocking Initial_Effect.
        blocking_linear_times: An array of days that matches the defined linear values for Blocking Initial_Effect
        blocking_linear_values: An array of multiplier values that matches the defined linear days for
            Blocking Initial_Effect.
        blocking_expire_at_end: Set to 1 to have efficacy go to zero and let the intervention expire when the end of
            the map is reached.  Only vaccines and bednet usage currently support this expiration feature.
            defaults to 0.
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        age_dependence: A dictionary defining the age dependence of net use.
            Must contain a list of ages in years and list of usage rate. Default
            is uniform across all ages.
            Times are in years of age
            Examples::

                {"Times":[], "Values":[]} or {"youth_cov":0.7, "youth_min_age":3, "youth_max_age":13}

        seasonal_dependence: A dictionary defining the seasonal dependence of net use. Time since start will
            reset to zero once it reaches 365. This allows you to simulate seasonal effects. Times are given in days
            of the year; values greater than 365 are ignored. Dictionaries can be (times, values) for linear spline
            or (minimum coverage, day of maximum coverage) for sinusoidal dynamics.
            Default is constant use during the year.
            Examples::

                {"Times":[], "Values":[]} or {"min_cov":0.45, "max_day":300}
        dont_allow_duplicates: Set to True to prevent individual from receiving another copy of the intervention.
            Default is False.

    Returns:
        None
        NOTE:
            Previous way of setting discard config is no longer available, you can translate it to the current way by:
            discard_config the old way {'halflife1': 260, 'halflife2': 2106, 'fraction1': float(table_dict['fast_fraction'])
            discard_config translated = {"Expiration_Period_Distribution": "DUAL_EXPONENTIAL_DISTRIBUTION",
                                        "Expiration_Period_Mean_1": discard_halflife, or halflife1
                                        "Expiration_Period_Mean_2": 365 * 40, or halflife2
                                        "Expiration_Period_Proportion_1": 1 or 'fraction1'}

        Example::

                discard_config = {"Expiration_Period_Exponential": 10 * 365}
                age_dependence = {"Times": [0, 4, 10, 60],
                           "Values": [1, 0.9, 0.8, 0.5]}
                add_usage_dependent_bednet(campaign, start_day=12, demographic_coverage=0.25,
                            age_dependence=age_dependence):

    """

    intervention = _usage_dependent_bednet(campaign=campaign,
                                           intervention_name=intervention_name,
                                           discard_config=discard_config,
                                           insecticide=insecticide,
                                           repelling_initial_effect=repelling_initial_effect,
                                           repelling_box_duration=repelling_box_duration,
                                           repelling_decay_time_constant=repelling_decay_time_constant,
                                           blocking_initial_effect=blocking_initial_effect,
                                           blocking_box_duration=blocking_box_duration,
                                           blocking_decay_time_constant=blocking_decay_time_constant,
                                           blocking_linear_times=blocking_linear_times,
                                           blocking_linear_values=blocking_linear_values,
                                           blocking_expire_at_end=blocking_expire_at_end,
                                           killing_initial_effect=killing_initial_effect,
                                           killing_box_duration=killing_box_duration,
                                           killing_decay_time_constant=killing_decay_time_constant,
                                           age_dependence=age_dependence,
                                           seasonal_dependence=seasonal_dependence,
                                           dont_allow_duplicates=dont_allow_duplicates)

    malaria_common.add_campaign_event(campaign=campaign,
                                      start_day=start_day,
                                      demographic_coverage=demographic_coverage,
                                      target_num_individuals=target_num_individuals,
                                      node_ids=node_ids,
                                      target_age_min=target_age_min,
                                      target_age_max=target_age_max,
                                      target_gender=target_gender,
                                      ind_property_restrictions=ind_property_restrictions,
                                      individual_intervention=intervention)


def add_triggered_usage_dependent_bednet(campaign,
                                         start_day: int = 1,
                                         demographic_coverage: float = 1,
                                         node_ids: list = None,
                                         ind_property_restrictions: list = None,
                                         trigger_condition_list: list = None,
                                         triggered_campaign_delay: float = None,
                                         listening_duration: int = -1,
                                         target_age_min: float = 0,
                                         target_age_max: float = malaria_common.MAX_AGE_YEARS,
                                         target_gender: str = "All",
                                         intervention_name: str = "UsageDependentBednet",
                                         discard_config: dict = None,
                                         insecticide: str = "",
                                         repelling_initial_effect: float = 0,
                                         repelling_box_duration: int = 0,
                                         repelling_decay_time_constant: float = 1460,
                                         blocking_initial_effect: float = 0.9,
                                         blocking_box_duration: int = 0,
                                         blocking_decay_time_constant: float = 730,
                                         blocking_linear_times: list = None,
                                         blocking_linear_values: list = None,
                                         blocking_expire_at_end: int = 0,
                                         killing_initial_effect: float = 0,
                                         killing_box_duration: int = 0,
                                         killing_decay_time_constant: float = 1460,
                                         age_dependence: dict = None,
                                         seasonal_dependence: dict = None,
                                         dont_allow_duplicates: bool = False):
    """
    Add an insecticide-treated net (ITN) intervention with a seasonal usage
    pattern to the campaign using the **UsageDependentBednet** class.

    Note: for killing, blocking, repelling effects - depending on the parameters you set,
    different WaningEffect classes will be used:
    box_duration = -1 => WaningEffectConstant, decay_time_constant is ignored
    box_duration = 0 + decay_time_constant > 0 => WaningEffectExponential
    box_duration > 0 + decay_time_constant = 0 => WaningEffectBox
    box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential


    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day on which to start distributing the bednets
            (**Start_Day** parameter).
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        node_ids: The list of nodes to apply this intervention to (**Node_List** parameter). If not provided,
            intervention is distributed to all nodes.
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        trigger_condition_list: (Optional) A list of the events that will
            trigger the ITN intervention. If included, **start** is the day
            when monitoring for triggers begins.
        triggered_campaign_delay: (Optional) Delay in days before the intervention is
            given out after being triggered.
        listening_duration: If run as a birth-triggered event or a trigger_condition_list,
            specifies the duration for the distribution to continue. Default
            is to continue until the end of the simulation.
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention (
            **Property_Restrictions_Within_Node** parameter). In the format ``[{
            "BitingRisk":"High"}, {"IsCool":"Yes}]``.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple UsageDependentBednets interventions
            attached to a person if they have different Intervention_Name values.
        discard_config: A dictionary of parameters needed to define expiration distribution.
            No need to definite the distribution with all its parameters
            Default is bednet being discarded with EXPONENTIAL_DISTRIBUTION with Expiration_Period_Exponential of 10 years

            Examples::

                        for Gaussian: {"Expiration_Period_Distribution": "GAUSSIAN_DISTRIBUTION",
                                       "Expiration_Period_Gaussian_Mean": 20,
                                       "Expiration_Period_Gaussian_Std_Dev":10}
                        for Exponential: {"Expiration_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
                                         "Expiration_Period_Exponential":150}
        insecticide: The name of the insecticide defined in <config.Insecticides> for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if <config.Insecticides> does not define anything.

        repelling_initial_effect: Initial strength of the Repelling effect. The effect may decay over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial_Effect.
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial_Effect.
        blocking_initial_effect: Initial strength of the Blocking effect. The effect may decay over time.
        blocking_box_duration: Box duration of effect in days before the decay of Blocking Initial_Effect.
        blocking_decay_time_constant: The exponential decay length, in days of the Blocking Initial_Effect.
        blocking_linear_times: An array of days that matches the defined linear values for Blocking Initial_Effect.
        blocking_linear_values: An array of multiplier values that matches the defined linear days for
            Blocking Initial_Effect.
        blocking_expire_at_end: Set to 1 to have efficacy go to zero and let the intervention expire when the end of
            the map is reached.  Only vaccines and bednet usage currently support this expiration feature.
            defaults to 0.
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        age_dependence: A dictionary defining the age dependence of net use.
            Must contain a list of ages in years and list of usage rate. Default
            is uniform across all ages.
            Times are in years of age
            Examples::

                {"Times":[], "Values":[]} or {"youth_cov":0.7, "youth_min_age":3, "youth_max_age":13}

        seasonal_dependence: A dictionary defining the seasonal dependence of net use. Time since start will
            reset to zero once it reaches 365. This allows you to simulate seasonal effects. Times are given in days
            of the year; values greater than 365 are ignored. Dictionaries can be (times, values) for linear spline
            or (minimum coverage, day of maximum coverage) for sinusoidal dynamics.
            Default is constant use during the year.
            Examples::

                {"Times":[], "Values":[]} or {"min_cov":0.45, "max_day":300}
        dont_allow_duplicates: Set to True to prevent individual from receiving another copy of the intervention.
            Default is False.


    Returns:
        None

    NOTE:
        Previous way of setting discard config is no longer available, you can translate it to the current way by:
        discard_config the old way {'halflife1': 260, 'halflife2': 2106, 'fraction1': float(table_dict['fast_fraction'])
        discard_config translated = {"Expiration_Period_Distribution": "DUAL_EXPONENTIAL_DISTRIBUTION",
        "Expiration_Period_Mean_1": discard_halflife, or halflife1
        "Expiration_Period_Mean_2": 365 * 40, or halflife2
        "Expiration_Period_Proportion_1": 1 or 'fraction1'}


    Example::

            discard_config = {"Expiration_Period_Exponential": 10 * 365}
            age_dependence = {"Times": [0, 4, 10, 60],
                       "Values": [1, 0.9, 0.8, 0.5]}
            add_usage_dependent_bednet(campaign, start=12, coverage=0.25,
                        age_dependence=age_dependence):

    """

    intervention = _usage_dependent_bednet(campaign=campaign,
                                           intervention_name=intervention_name,
                                           discard_config=discard_config,
                                           insecticide=insecticide,
                                           repelling_initial_effect=repelling_initial_effect,
                                           repelling_box_duration=repelling_box_duration,
                                           repelling_decay_time_constant=repelling_decay_time_constant,
                                           blocking_initial_effect=blocking_initial_effect,
                                           blocking_box_duration=blocking_box_duration,
                                           blocking_decay_time_constant=blocking_decay_time_constant,
                                           blocking_linear_times=blocking_linear_times,
                                           blocking_linear_values=blocking_linear_values,
                                           blocking_expire_at_end=blocking_expire_at_end,
                                           killing_initial_effect=killing_initial_effect,
                                           killing_box_duration=killing_box_duration,
                                           killing_decay_time_constant=killing_decay_time_constant,
                                           age_dependence=age_dependence,
                                           seasonal_dependence=seasonal_dependence,
                                           dont_allow_duplicates=dont_allow_duplicates)
    malaria_common.add_triggered_campaign_delay_event(campaign=campaign,
                                                      start_day=start_day,
                                                      demographic_coverage=demographic_coverage,
                                                      trigger_condition_list=trigger_condition_list,
                                                      listening_duration=listening_duration,
                                                      delay_period_constant=triggered_campaign_delay,
                                                      ind_property_restrictions=ind_property_restrictions,
                                                      node_ids=node_ids,
                                                      target_age_min=target_age_min,
                                                      target_age_max=target_age_max,
                                                      target_gender=target_gender,
                                                      individual_intervention=intervention)


def _usage_dependent_bednet(campaign,
                            intervention_name: str = "UsageDependentBednet",
                            discard_config: dict = None,
                            insecticide: str = "",
                            repelling_initial_effect: float = 0,
                            repelling_box_duration: int = 0,
                            repelling_decay_time_constant: float = 1460,
                            blocking_initial_effect: float = 0.9,
                            blocking_box_duration: int = 0,
                            blocking_decay_time_constant: float = 730,
                            blocking_linear_times: list = None,
                            blocking_linear_values: list = None,
                            blocking_expire_at_end: int = 0,
                            killing_initial_effect: float = 0,
                            killing_box_duration: int = 0,
                            killing_decay_time_constant: float = 1460,
                            age_dependence: dict = None,
                            seasonal_dependence: dict = None,
                            dont_allow_duplicates: bool = False):
    """
        Configures UsageDependentBednet intervention

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. It’s possible to have multiple UsageDependentBednets interventions
            attached to a person if they have different Intervention_Name values.
        discard_config: A dictionary of parameters needed to define expiration distribution.
            No need to definite the distribution with all its parameters
            Default is bednet being discarded with EXPONENTIAL_DISTRIBUTION with Expiration_Period_Exponential of 10 years

            Examples::

                        for Gaussian: {"Expiration_Period_Distribution": "GAUSSIAN_DISTRIBUTION",
                                       "Expiration_Period_Gaussian_Mean": 20,
                                       "Expiration_Period_Gaussian_Std_Dev":10}
                        for Exponential: {"Expiration_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
                                         "Expiration_Period_Exponential":150}
        insecticide: The name of the insecticide defined in <config.Insecticides> for this intervention.
            If insecticides are being used, then this must be defined as one of those values.  If they are not
            being used, then this does not needed to be specified or can be empty string.  It cannot have a
            value if <config.Insecticides> does not define anything.

        repelling_initial_effect: Initial strength of the Repelling effect. The effect may decay over time.
        repelling_box_duration: Box duration of effect in days before the decay of Repelling Initial_Effect.
            -1 indicates effect is indefinite (WaningEffectConstant)
        repelling_decay_time_constant: The exponential decay length, in days of the Repelling Initial_Effect.
        blocking_initial_effect: Initial strength of the Blocking effect. The effect may decay over time.
        blocking_box_duration: Box duration of effect in days before the decay of Blocking Initial_Effect.
            -1 indicates effect is indefinite (WaningEffectConstant)
        blocking_decay_time_constant: The exponential decay length, in days of the Blocking Initial_Effect.
        blocking_linear_times: An array of days that matches the defined linear values for Blocking Initial_Effect
            if this is set, WaningEffectMapLinear is used, box_duration and decay_time_constant is ignored for blocking
        blocking_linear_values: An array of multiplier values that matches the defined linear days for
            Blocking Initial_Effect. if this is set, WaningEffectMapLinear is used, box_duration and
            decay_time_constant is ignored for blocking
        blocking_expire_at_end: Set to 1 to have efficacy go to zero and let the intervention expire when the end of
            the map is reached.  Only vaccines and bednet usage currently support this expiration feature.
            defaults to 0.
        killing_initial_effect: Initial strength of the Killing effect. The effect may decay over time.
        killing_box_duration: Box duration of effect in days before the decay of Killing Initial_Effect.
            -1 indicates effect is indefinite (WaningEffectConstant)
        killing_decay_time_constant: The exponential decay length, in days of the Killing Initial_Effect.
        age_dependence: A dictionary defining the age dependence of net use.
            Must contain a list of ages in years and list of usage rate. Default
            is uniform across all ages.
            Times are in years of age
            Examples::

                {"Times":[], "Values":[]} or {"youth_cov":0.7, "youth_min_age":3, "youth_max_age":13}

        seasonal_dependence: A dictionary defining the seasonal dependence of net use. Time since start will
            reset to zero once it reaches 365. This allows you to simulate seasonal effects. Times are given in days
            of the year; values greater than 365 are ignored. Dictionaries can be (times, values) for linear spline
            or (minimum coverage, day of maximum coverage) for sinusoidal dynamics.
            Default is constant use during the year.
            Examples::

                {"Times":[], "Values":[]} or {"min_cov":0.45, "max_day":300}
        dont_allow_duplicates: Set to True to prevent individual from receiving another copy of the intervention.
            Default is False.

    Returns:
       A configured UsageDependentBednet intervention.
    """
    if not discard_config:
        discard_config = {"Expiration_Period_Exponential": 10 * 365}

    schema_path = campaign.schema_path

    if blocking_linear_values or blocking_linear_values:
        if len(blocking_linear_times) != len(blocking_linear_values):
            raise ValueError("'blocking_linear_times' and 'blocking_linear_values' lists must be the same length.\n")
        times_values = list(zip(blocking_linear_times, blocking_linear_values))
        blocking = utils.get_waning_from_points(schema_path=schema_path, initial=blocking_initial_effect,
                                                times_values=times_values,
                                                expire_at_end=blocking_expire_at_end)
    else:
        blocking = utils.get_waning_from_parameters(schema_path=schema_path, initial=blocking_initial_effect,
                                                    box_duration=blocking_box_duration,
                                                    decay_time_constant=blocking_decay_time_constant)
    killing = utils.get_waning_from_parameters(schema_path=schema_path, initial=killing_initial_effect,
                                               box_duration=killing_box_duration,
                                               decay_time_constant=killing_decay_time_constant)
    repelling = utils.get_waning_from_parameters(schema_path=schema_path, initial=repelling_initial_effect,
                                                 box_duration=repelling_box_duration,
                                                 decay_time_constant=repelling_decay_time_constant)

    intervention = s2c.get_class_with_defaults("UsageDependentBednet", schema_path)

    seasonal_waning = _get_seasonal_times_and_values(campaign, seasonal_dependence)
    age_waning = _get_age_times_and_values(campaign, age_dependence)
    intervention.Usage_Config_List = list()
    intervention.Usage_Config_List.append(seasonal_waning)
    intervention.Usage_Config_List.append(age_waning)

    intervention.Received_Event = campaign.get_send_trigger("Bednet_Got_New_One", old=True)
    intervention.Using_Event = campaign.get_send_trigger("Bednet_Using", old=True)
    intervention.Discard_Event = campaign.get_send_trigger("Bednet_Discarded", old=True)
    intervention.Killing_Config = killing
    intervention.Blocking_Config = blocking
    intervention.Repelling_Config = repelling
    intervention.Intervention_Name = intervention_name
    intervention.Insecticide_Name = insecticide
    intervention.Dont_Allow_Duplicates = 1 if dont_allow_duplicates else 0

    # I kind of hate this but let's try it for now
    for param in discard_config:
        setattr(intervention, param, discard_config[param])

    return intervention


def new_intervention_as_file(camp, start_day, filename="UsageDependentBednet.json"):
    add_scheduled_usage_dependent_bednet(camp, start_day)
    camp.save(filename)
    return filename
