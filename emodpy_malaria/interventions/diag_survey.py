import random
from emod_api.interventions.common import BroadcastEvent
from emod_api.interventions.common import MultiInterventionDistributor
from emod_api.interventions.common import TriggeredCampaignEvent
from emodpy_malaria.interventions.common import _malaria_diagnostic, add_campaign_event


def add_diagnostic_survey(
        campaign,
        coverage: float = 1,
        repetitions: int = 1,
        tsteps_btwn_repetitions: int = 365,
        target: object = 'Everyone',
        start_day: int = 1,
        diagnostic_type: str = 'BLOOD_SMEAR_PARASITES',
        diagnostic_threshold: float = 40,
        measurement_sensitivity: float = 0.1,
        event_name: str = "Diagnostic Survey",
        node_ids: list = None,
        positive_diagnosis_configs: list = None,
        negative_diagnosis_configs: list = None,
        received_test_event: str = 'Received_Test',
        ind_property_restrictions: list = None,
        disqualifying_properties: list = None,
        trigger_condition_list: list = None,
        listening_duration: int = -1,
        triggered_campaign_delay: int = 0,
        check_eligibility_at_trigger: bool = False,
        expire_recent_drugs: any = None):
    """
        Add an intervention to create either a scheduled or a triggered event to the
        campaign using the
        :py:class:`~emodpy_malaria.interventions.common.MalariaDiagnostic` class, an
        individual-level class, to test individuals. Upon positive or negative
        diagnosis, the list of events to occur (as defined in
        **positive_diagnosis_configs** or **negative_diagnosis_configs**) is then executed.
        These events can trigger other listening interventions.

        Args:
            camp: The :py:obj:`emod_api:emod_api.campaign` object for building,
                modifying, and writing campaign configuration files.

            coverage: The probability an individual receives the diagnostic.

            repetitions: Number of repetitions of the survey intervention.

            tsteps_btwn_repetitions: Timesteps between repetitions.

            target: A dictionary targeting an age range and gender of
                individuals for treatment. In the format
                ``{"agemin": x, "agemax": y, "gender": z}``. Default is Everyone.

            start_day: The day of the simulation on which the intervention is created.
                If triggered, runs on trigger, not on **start_day**.

            diagnostic_type: Type of malaria diagnostic used. Default is
                **BLOOD_SMEAR_PARASITES**. Available options are:

                * BLOOD_SMEAR_PARASITES
                * BLOOD_SMEAR_GAMETOCYTES
                * PCR_PARASITES
                * PCR_GAMETOCYTES
                * PF_HRP2
                * TRUE_INFECTION_STATUS
                * TRUE_PARASITE_DENSITY
                * FEVER

            diagnostic_threshold: The diagnostic detection threshold based on
                **diagnostic_type**:

                TRUE_INFECTION_STATUS

                BLOOD_SMEAR_PARASITES
                    In parasites/microliter, use measurement = float( 1.0 / measurementSensitivity *
                    Poisson(measurementSensitivity * true_parasite_density)).
                BLOOD_SMEAR_GAMETOCYTES
                    In gametocytes/microliter, use measurement = float( 1.0 / measurementSensitivity *
                    Poisson(measurementSensitivity * true_gametocyte_density)).
                PCR_PARASITES and PCR_GAMETOCYTES
                    Use the true values and an algorithm based on the paper
                    `Improving statistical inference on pathogen densities estimated by
                    quantitative molecular methods : malaria gametocytaemia as a case study
                    <https://doi.org/10.1186/s12859-014-0402-2>`_.
                PF_HRP2
                    Add a new method to get the PfHRP2 value and check against
                    the threshold.
                TRUE_PARASITE_DENSITY
                    Check the true parasite density against the threshold.
                FEVER
                    Check the person's fever against the threshold.

            measurement_sensitivity: Setting for **Measurement_Sensitivity** in
                :py:class:`~emodpy_malaria.interventions.common.MalariaDiagnostic`.

            event_name: Description of the event.

            node_ids: The list of nodes to apply this intervention to (**Node_List**
                parameter). If not provided, set value of NodeSetAll.

            positive_diagnosis_configs: List of events to happen to an individual
                who receives a positive result from test.

            negative_diagnosis_configs: List of events to happen to individual who
                receives a negative result from test.

            received_test_event: String for individuals to broadcast upon receiving
                diagnostic.

            ind_property_restrictions: List of IndividualProperty key:value pairs that
                individuals must have to receive the diagnostic intervention.
                For example, ``[{"IndividualProperty1":"PropertyValue1"},
                {"IndividualProperty2":"PropertyValue2"}]``. Default is no
                restrictions.

            disqualifying_properties: List of IndividualProperty key:value pairs that
                cause an intervention to be aborted. For example,
                ``[{"IndividualProperty1":"PropertyValue1"},
                {"IndividualProperty2":"PropertyValue2"}]``.

            trigger_condition_list: List of events that will trigger a diagnostic survey.

            listening_duration: Duration after start day to stop listening for events, as
                specified in **trigger_condition_list**. Default is -1, non-stop
                listening.

            triggered_campaign_delay: Delay of running the intervention after receiving
                a trigger from the **trigger_condition_list**.

            check_eligibility_at_trigger: If triggered event is delayed, you have an
                option to check individual/node's eligibility at the initial trigger
                or when the event is actually distributed after delay.

            expire_recent_drugs: Adds ``[{"DrugStatus:None"}]`` to
                **Property_Restrictions_Within_Node** for positive test config, so
                only those with that property receive drugs.

        Returns:
           None
    """

    if ind_property_restrictions is None:
        ind_property_restrictions = []
    if disqualifying_properties is None:
        disqualifying_properties = []

    received_test_event = BroadcastEvent(campaign, Event_Trigger=received_test_event)

    tested_positive = BroadcastEvent(campaign, Event_Trigger="TestedPositive")
    tested_negative = BroadcastEvent(campaign, Event_Trigger="TestedNegative")
    tested_positive_tether = "TestedPositive_{}".format(random.randint(1, 100000))
    tested_negative_tether = "TestedNegative_{}".format(random.randint(1, 100000))

    intervention_cfg = _malaria_diagnostic(
        campaign,
        measurement_sensitivity=measurement_sensitivity,
        detection_threshold=diagnostic_threshold,
        diagnostic_type=diagnostic_type)

    bcast = BroadcastEvent(campaign, Event_Trigger=tested_positive_tether)
    mid = MultiInterventionDistributor(campaign, Intervention_List=[tested_positive, bcast])

    intervention_cfg.Positive_Diagnosis_Config = mid

    intervention_cfg.Negative_Diagnosis_Config = MultiInterventionDistributor(
        campaign, Intervention_List=[tested_negative, BroadcastEvent(campaign, Event_Trigger=tested_negative_tether)])

    interventions = [intervention_cfg, received_test_event]

    gender = "All"
    age_min = 0
    age_max = 9.3228e+35
    if target != "Everyone" and isinstance(target, dict):
        try:
            age_min = target["agemin"]
            age_max = target["agemax"]
            if 'gender' in target:
                gender = target["gender"]
                target = "ExplicitAgeRangesAndGender"
            else:
                target = "ExplicitAgeRanges"
        except KeyError:
            raise KeyError("Unknown target_group parameter. Please pass in 'Everyone' or a dictionary of "
                           "{'agemin' : x, 'agemax' : y, 'gender': 'Female'} to target  to individuals between x and "
                           "y years of age, and (optional) gender.\n")

    if trigger_condition_list:
        if listening_duration == -1:
            diagnosis_config_listening_duration = -1
        else:
            diagnosis_config_listening_duration = listening_duration + 1
        # if once triggered, you want the diagnostic survey to repeat or if there is a delay (or both)
        # this creates a series of broadcast events that once triggered send out "Diagnostic_Survey_Now"
        # at pre-determined intervals
        if repetitions > 1 or triggered_campaign_delay > 0:
            # create a trigger for each of the delays.
            trigger_ind_property_restrictions = []
            if check_eligibility_at_trigger:
                trigger_ind_property_restrictions = ind_property_restrictions
                ind_property_restrictions = []
            broadcast_event = "Diagnostic_Survey_Now_{}".format(random.randint(1, 100000))
            for x in range(repetitions):
                tcde = TriggeredCampaignEvent(
                    campaign,
                    Start_Day=start_day + 1,
                    Event_Name="Diag_Survey_Now",
                    Node_Ids=node_ids,
                    Triggers=trigger_condition_list,
                    Duration=listening_duration,
                    Intervention_List=[BroadcastEvent(campaign, broadcast_event)],
                    Property_Restrictions=trigger_ind_property_restrictions,
                    Delay=triggered_campaign_delay + (x * tsteps_btwn_repetitions))
                campaign.add(tcde)
                trigger_condition_list = [broadcast_event]

        survey_event = TriggeredCampaignEvent(
            campaign,
            Start_Day=start_day + 1,
            Event_Name=event_name,
            Node_Ids=node_ids,
            Triggers=trigger_condition_list,
            Target_Residents_Only=1,
            Duration=listening_duration,
            Demographic_Coverage=coverage,
            Target_Age_Min=age_min,
            Target_Age_Max=age_max,
            Target_Gender=gender,
            Property_Restrictions=ind_property_restrictions,
            Disqualifying_Properties=disqualifying_properties,
            Intervention_List=interventions)

        campaign.add(survey_event)

    else:
        diagnosis_config_listening_duration = listening_duration
        add_campaign_event(
            campaign,
            start_day=start_day + 1,
            node_ids=node_ids,
            ind_property_restrictions=ind_property_restrictions,
            repetitions=repetitions,
            timesteps_between_repetitions=tsteps_btwn_repetitions,
            demographic_coverage=coverage,
            target_age_min=age_min,
            target_age_max=age_max,
            target_gender=gender,
            individual_intervention=interventions)

    if expire_recent_drugs:
        if ind_property_restrictions:
            for property_restriction in ind_property_restrictions:
                property_restriction["DrugStatus"] = "None"
        else:
            ind_property_restrictions = [{"DrugStatus": "None"}]

    if positive_diagnosis_configs:
        tested_positive_event = TriggeredCampaignEvent(
            campaign,
            Start_Day=start_day,
            Event_Name=event_name + "Positive Result Action",
            Node_Ids=node_ids,
            Duration=diagnosis_config_listening_duration,
            Property_Restrictions=ind_property_restrictions,
            Triggers=[tested_positive_tether],
            Intervention_List=positive_diagnosis_configs
        )
        campaign.add(tested_positive_event)

    if negative_diagnosis_configs:
        tested_negative_event = TriggeredCampaignEvent(
            campaign,
            Start_Day=start_day,
            Event_Name=event_name + "Negative Result Action",
            Node_Ids=node_ids,
            Duration=diagnosis_config_listening_duration,
            Triggers=[tested_negative_tether],
            Intervention_List=negative_diagnosis_configs
        )
        campaign.add(tested_negative_event)

    return
