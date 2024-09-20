# Just bringing over API and preproc of 
# https://github.com/InstituteforDiseaseModeling/dtk-tools/blob/master/dtk/interventions/itn_age_season.py 
# wholesale for now. Maybe use most of this API with the schema-backed emod_api mechanism.
from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
import json
import numpy as np
import sys

def _get_seasonal_times_and_values(schema_path, seasonal_dependence):    
    #Assign seasonal net usage 
    #Times are days of the year
    #Input can be provided either as (times, values) for linear spline or (min coverage, day of maximum coverage)
    #under the assumption of sinusoidal dynamics. In the first case, the same value should be provided
    #for both 0 and 365; times > 365 will be ignored.
    seasonal_times = None
    seasonal_values = None
    if not seasonal_dependence:        
        # Option 1: Nothing specified, our default, uniform. But why not just not have a seasonal multiplier?
        seasonal_times = [*range(0,361,30),365]
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
    waning = s2c.get_class_with_defaults( "WaningEffectMapLinearSeasonal", schema_path )
    waning.Initial_Effect = 1.0
    waning.Durability_Map.Times = [float(x) for x in seasonal_times]
    waning.Durability_Map.Values = [float(x) for x in seasonal_values]

    return waning
    

def _get_age_times_and_values(schema_path, age_dependence):    
    # Assign age-dependent net usage #
    # Times are ages in years (note difference from seasonal dependence)
    age_times = [0, 125] # Dan B has hard-coded an upper limit of 125, will return error for larger values
    age_values = [1, 1]
    if not age_dependence:
        pass
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

    waning = s2c.get_class_with_defaults( "WaningEffectMapLinearAge", schema_path )
    waning.Initial_Effect = 1.0
    waning.Durability_Map.Times = age_times
    waning.Durability_Map.Values = age_values

    return waning


# UDBednet is short for Usage Dependent Bednet
def UDBednet(
    camp,
    start_day: int = 1,
    discard_config: dict = None,

    coverage: float = 1,
    ind_property_restrictions: list = None,

    blocking_eff: float = 0.9,
    blocking_constant_duration: int = 0,
    blocking_decay_rate: float = 1/730.,
    killing_eff: float = 0.6,
    killing_constant_duration: int = 0,
    killing_decay_rate: float = 1/1460.,
    repelling_eff: float = 0,
    repelling_constant_duration: int = 0,
    repelling_decay_rate: float = 1/1460.,
    iv_name: str = "UsageDependentBednet",

    age_dependence: dict = None,
    seasonal_dependence: dict = None,

    insecticide: str = None,

    node_ids: list = None,
    # birth_triggered: bool = False, # add Birth to tcl
    triggered_campaign_delay: dict = None,
    triggers: list = None,
    duration: int = -1,
    check_eligibility_at_trigger: bool = False):

    """
    Add an insecticide-treated net (ITN) intervention with a seasonal usage
    pattern to the campaign using the **UsageDependentBednet** class. The
    arguments **birth_triggered** and **triggered_condition_list** are mutually
    exclusive. If both are provided, **triggered_condition_list** is ignored.
    You must add the following custom events to your config.json:
        
        * Bednet_Discarded
        * Bednet_Got_New_One
        * Bednet_Using

    Args:
        start: The day on which to start distributing the bednets
            (**Start_Day** parameter).
        coverage: Fraction of the population receiving bed nets in a given distribution event
        blocking_config: The value passed gets directly assigned to the Blocking_Config parameter.
            Durations are in days.
            Default is blocking_config= WaningEffectExponential(Decay_Time_Constant=730, Initial_Effect=0.9)
            
            This could be dictionary such as::

                {
                    "Box_Duration": 3650,
                    "Initial_Effect": 0,
                    "class": "WaningEffectBox"
                }

        killing_config: The value passed gets directly assigned to the Killing_Config parameter.
            Durations are in days.
            Default is killing_config = WaningEffectExponential(Decay_Time_Constant=1460, Initial_Effect=0.6)
            
            This could be dictionary such as::

                {
                    "Box_Duration": 3650,
                    "Initial_Effect": 0,
                    "Decay_Time_Constant": 150,
                    "class": "WaningEffectBoxExponential"
                }

        repelling_config: The value passed gets directly assigned to the Repelling_Config parameter.
            Durations are in days.
            Default is repelling_config = WaningEffectExponential(Decay_Time_Constant=1460, Initial_Effect=0.0)
            
            This could be dictionary such as::

                {
                    "Box_Duration": 3650,
                    "Initial_Effect": 0,
                    "Decay_Time_Constant": 150,
                    "class": "WaningEffectBoxExponential"
                }

        discard_config: A dictionary of parameters needed to define expiration distribution.
            No need to definite the distribution with all its parameters
            Default is bednet being discarded with EXPONENTIAL_DISTRIBUTION with Expiration_Period_Exponential of 10 years
            
            Examples::

                        for Gaussian: {"Expiration_Period_Distribution": "GAUSSIAN_DISTRIBUTION",
                            "Expiration_Period_Gaussian_Mean": 20, "Expiration_Period_Gaussian_Std_Dev":10}
                        for Exponential {"Expiration_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
                            "Expiration_Period_Exponential":150}

        age_dependence: A dictionary defining the age dependence of net use.
            Must contain a list of ages in years and list of usage rate. Default
            is uniform across all ages.
            Times are in years of age
            Examples::

                {"Times":[], "Values":[]} or {"youth_cov":0.7, "youth_min_age":3, "youth_max_age":13}

        seasonal_dependence: A dictionary defining the seasonal dependence of net use.
            Default is constant use during the year. Times are given in days
            of the year; values greater than 365 are ignored. Dictionaries
            can be (times, values) for linear spline or (minimum coverage,
            day of maximum coverage) for sinusoidal dynamics.
            Times are days of the year
            Examples::

                {"Times":[], "Values":[]} or {"min_cov":0.45, "max_day":300}

        node_ids: The list of nodes to apply this intervention to (**Node_List**
            parameter). If not provided, set value of NodeSetAll.

        birth_triggered: If true, event is specified as a birth-triggered intervention.
        duration: If run as a birth-triggered event or a trigger_condition_list,
            specifies the duration for the distribution to continue. Default
            is to continue until the end of the simulation.
        triggered_campaign_delay: (Optional) After the trigger is received,
            the number of time steps until the campaign starts. Eligibility
            of people or nodes for the campaign is evaluated on the start
            day, not the triggered day. triggered_campaign_delay is a dict. 
            Specify the actual delay distribution params, not the distribution type.
            E.g., { "Delay_Distribution_Constant": 14" }
            Delay is in days
        trigger_condition_list: (Optional) A list of the events that will
            trigger the ITN intervention. If included, **start** is the day
            when monitoring for triggers begins. This argument cannot
            configure birth-triggered ITN (use **birth_triggered** instead).
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention (
            **Property_Restrictions_Within_Node** parameter). In the format ``[{
            "BitingRisk":"High"}, {"IsCool":"Yes}]``.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention (**Node_Property_Restrictions**
            parameter). In the format ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``
        check_eligibility_at_trigger: if triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay.
    Returns:
        None

    NOTE:
    Previous was of setting discard config is no longer available, you can translate it to the current way by:
    discard_config the old way {'halflife1': 260, 'halflife2': 2106, 'fraction1': float(table_dict['fast_fraction'])
    discard_config translated = {"Expiration_Period_Distribution": "DUAL_EXPONENTIAL_DISTRIBUTION",
    "Expiration_Period_Mean_1": discard_halflife, or halflife1
    "Expiration_Period_Mean_2": 365 * 40, or halflife2
    "Expiration_Period_Proportion_1": 1 or 'fraction1'}

    #fixme This is dtk-tools commenting, needs an update for emodpy
    Example::

            discard_config = {"Expiration_Period_Exponential": 10 * 365}
            age_dependence = {"Times": [0, 4, 10, 60],
                       "Values": [1, 0.9, 0.8, 0.5]}
            add_ITN_age_season(config_builder, start=1, coverage=1, killing_config=killing_config,
                        blocking_config=blocking_config, discard_config = discard_config
                        age_dependence=age_dependence, cost=5, birht_triggered=True, duration=-1,
                        node_property_restrictions=[{"Place": "Rural"]):

    """

    if not discard_config:
        discard_config = { "Expiration_Period_Exponential": 10 * 365 }

    # PRE-PROCESSING DONE
    schema_path = camp.schema_path
    blocking = utils.get_waning_from_params( schema_path, blocking_eff, blocking_constant_duration, blocking_decay_rate ) 
    killing = utils.get_waning_from_params( schema_path, killing_eff, killing_constant_duration, killing_decay_rate ) 
    repelling = utils.get_waning_from_params( schema_path, repelling_eff, repelling_constant_duration, repelling_decay_rate )

    event = s2c.get_class_with_defaults( "CampaignEvent", schema_path )
    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", schema_path )
    intervention = s2c.get_class_with_defaults( "UsageDependentBednet", schema_path )
    seasonal_waning = _get_seasonal_times_and_values( schema_path, seasonal_dependence )
    age_waning = _get_age_times_and_values( schema_path, age_dependence )
    intervention.Usage_Config_List = list()
    intervention.Usage_Config_List.append( seasonal_waning )
    intervention.Usage_Config_List.append( age_waning )

    # These should be built-in events at this point
    intervention.Received_Event = camp.get_send_trigger("Bednet_Got_New_One", old=True)
    intervention.Using_Event = camp.get_send_trigger("Bednet_Using", old=True)
    intervention.Discard_Event = camp.get_send_trigger("Bednet_Discarded", old=True)

    # I kind of hate this but let's try it for now
    for param in discard_config:
        setattr(intervention, param, discard_config[param])

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    Intervention_Config = intervention
    intervention.Killing_Config = killing 
    intervention.Blocking_Config = blocking 
    intervention.Repelling_Config = repelling 
    event.Start_Day = float(start_day)

    # Third, do the actual settings
    #intervention.Vaccine_Type = "AcquisitionBlocking"
    intervention.Intervention_Name = iv_name 
    if insecticide is None:
        intervention.pop( "Insecticide_Name" ) # this is not permanent
    else:
        intervention.Insecticide_Name = insecticide
    #intervention.Duplicate_Policy = dupe_policy

    event.Nodeset_Config = utils.do_nodes( schema_path, node_ids )

    if triggers is not None:
        meta_intervention = s2c.get_class_with_defaults( "NodeLevelHealthTriggeredIV", schema_path )
        meta_intervention.pop( "Actual_NodeIntervention_Config" )
        delay_intervention = s2c.get_class_with_defaults( "DelayedIntervention", schema_path )
        meta_intervention.Actual_IndividualIntervention_Config = delay_intervention
        delay_intervention.Actual_IndividualIntervention_Configs = [ intervention ]
        meta_intervention.Trigger_Condition_List.extend( triggers )
        if triggered_campaign_delay is None:
            triggered_campaign_delay = dict()
            triggered_campaign_delay[ "Delay_Period_Constant" ] = 7 
        for param in triggered_campaign_delay: # better be literally usable Delayed Config settings, yuck
            setattr(delay_intervention, param, triggered_campaign_delay[param])
        if check_eligibility_at_trigger and ind_property_restrictions:
            meta_intervention.Property_Restrictions = ind_property_restrictions # using this raw!?
        meta_intervention.Duration = duration 

        coordinator.Intervention_Config = meta_intervention
        coordinator.pop( "Target_Gender" )
    else:
        #coordinator.Property_Restrictions_Within_Node = ind_property_restrictions
        coordinator.Demographic_Coverage = coverage
        if ind_property_restrictions:
            coordinator.Property_Restrictions = ind_property_restrictions # using this raw!?

    return event


def new_intervention_as_file(camp, start_day, filename=None):
    camp.add(UDBednet(camp, start_day), first=True)
    if filename is None:
        filename = "UsageDependentBednet.json"
    camp.save( filename )
    return filename
