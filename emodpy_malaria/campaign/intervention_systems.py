import random
from typing import List, Optional, Union

from emod_api import campaign as api_campaign

from emodpy_malaria.campaign.individual_intervention import AdherentDrug  # noqa: F401
from emodpy_malaria.campaign.individual_intervention import (
    AntimalarialDrug,
    BroadcastEvent,
    BroadcastEventToOtherNodes,
    DelayedIntervention,
    MalariaDiagnostic,
    MultiInterventionDistributor,
    PropertyValueChanger,
)
from emodpy_malaria.campaign.distributor import (
    add_intervention_scheduled,
    add_intervention_triggered,
)
from emodpy_malaria.campaign.common import (
    CommonInterventionParameters,
    MAX_AGE_YEARS,
    PropertyRestrictions,
    RepetitionConfig,
    TargetDemographicsConfig,
)
from emodpy_malaria.utils.distributions import (
    BaseDistribution,
    ConstantDistribution,
    ExponentialDistribution,
)
from emodpy_malaria.utils.emod_enum import DiagnosticType, NodeSelectionType, StrEnum

from emodpy.campaign.node_intervention import _NodeLevelHealthTriggeredIV
from emodpy.campaign.event_coordinator import StandardEventCoordinator
from emodpy.campaign.event import create_campaign_event


class CampaignType(StrEnum):
    MDA = "MDA"
    SMC = "SMC"
    MSAT = "MSAT"
    MTAT = "MTAT"
    fMDA = "fMDA"
    rfMSAT = "rfMSAT"
    rfMDA = "rfMDA"
    PMC = "PMC"


# ──────────────────────────────────────────────────────────────────────
# Drug code lookup
# ──────────────────────────────────────────────────────────────────────

DRUG_CODES = {
    "ALP": ["Artemether", "Lumefantrine", "Primaquine"],
    "AL": ["Artemether", "Lumefantrine"],
    "ASA": ["Artesunate", "Amodiaquine"],
    "DP": ["DHA", "Piperaquine"],
    "DPP": ["DHA", "Piperaquine", "Primaquine"],
    "PPQ": ["Piperaquine"],
    "DHA_PQ": ["DHA", "Primaquine"],
    "DHA": ["DHA"],
    "PMQ": ["Primaquine"],
    "DA": ["DHA", "Abstract"],
    "CQ": ["Chloroquine"],
    "SP": ["Sulfadoxine", "Pyrimethamine"],
    "SPP": ["Sulfadoxine", "Pyrimethamine", "Primaquine"],
    "SPA": ["Sulfadoxine", "Pyrimethamine", "Amodiaquine"],
    "Vehicle": ["Vehicle"],
}


# ──────────────────────────────────────────────────────────────────────
# Public helpers
# ──────────────────────────────────────────────────────────────────────

def drug_configs_from_code(campaign: api_campaign, drug_code: str) -> list[AntimalarialDrug]:
    """
    Build a list of :class:`~emodpy_malaria.campaign.individual_intervention.AntimalarialDrug`
    interventions from a shorthand drug code.

    Args:
        campaign (api_campaign, required):
            The campaign object.
        drug_code (str, required):
            A key from :data:`DRUG_CODES` (e.g. ``"AL"``, ``"DP"``, ``"SP"``).

    Returns:
        list[AntimalarialDrug]: One intervention per drug in the regimen.

    Raises:
        ValueError: If *drug_code* is not in :data:`DRUG_CODES`.
    """
    if not drug_code or drug_code not in DRUG_CODES:
        valid = ", ".join(DRUG_CODES.keys())
        raise ValueError(f"Invalid drug_code {drug_code!r}. Valid codes: {valid}")
    return [
        AntimalarialDrug(campaign, drug_type=d, common_intervention_parameters=CommonInterventionParameters(cost=1))
        for d in DRUG_CODES[drug_code]
    ]


# ──────────────────────────────────────────────────────────────────────
# Private helpers
# ──────────────────────────────────────────────────────────────────────

def _build_interventions(drug_configs, receiving_drugs_event, expire_recent_drugs):
    interventions = list(drug_configs)
    if receiving_drugs_event:
        interventions.append(receiving_drugs_event)
    if expire_recent_drugs:
        interventions.append(expire_recent_drugs)
    return interventions


def _wrap_with_disqualifying(campaign, interventions, disqualifying_properties):
    if disqualifying_properties:
        return [MultiInterventionDistributor(
            campaign, intervention_list=interventions,
            common_intervention_parameters=CommonInterventionParameters(
                disqualifying_properties=disqualifying_properties))]
    return interventions


def _make_diagnostic(campaign, diagnostic_type: Union[DiagnosticType, str],
                     detection_threshold, measurement_sensitivity,
                     positive_diagnosis, negative_diagnosis=None, days_to_diagnosis=0):
    if not isinstance(diagnostic_type, DiagnosticType):
        diagnostic_type = DiagnosticType(diagnostic_type)
    return MalariaDiagnostic(
        campaign,
        diagnostic_type=diagnostic_type,
        detection_threshold=detection_threshold,
        measurement_sensitivity=measurement_sensitivity,
        positive_diagnosis=positive_diagnosis,
        negative_diagnosis=negative_diagnosis,
        days_to_diagnosis=days_to_diagnosis)


def _fmda_broadcast(campaign, fmda_radius, node_selection_type: Union[NodeSelectionType, str],
                    event_trigger="Give_Drugs"):
    if not isinstance(node_selection_type, NodeSelectionType):
        node_selection_type = NodeSelectionType(node_selection_type)
    return BroadcastEventToOtherNodes(
        campaign,
        broadcast_event=event_trigger,
        include_my_node=True,
        node_selection_type=node_selection_type,
        max_distance_to_other_nodes_km=float(fmda_radius) if isinstance(fmda_radius, (int, float)) and fmda_radius > 0 else 0)


def _add_triggered_event_with_blackout(campaign, intervention_list, triggers_list, start_day,
                                       node_ids, duration, target_config,
                                       prop_restrictions, disqualifying_properties,
                                       event_name, blackout_period=0,
                                       blackout_on_first_occurrence=False,
                                       blackout_event_trigger=None):
    interventions = _wrap_with_disqualifying(campaign, intervention_list, disqualifying_properties)
    nlhti = _NodeLevelHealthTriggeredIV(
        campaign,
        intervention_list=interventions,
        trigger_condition_list=triggers_list,
        target_demographics_config=target_config,
        property_restrictions=prop_restrictions,
        duration=duration,
        blackout_period=blackout_period,
        blackout_on_first_occurrence=blackout_on_first_occurrence,
        blackout_event_trigger=blackout_event_trigger)
    coordinator = StandardEventCoordinator(campaign, intervention_list=[nlhti])
    event = create_campaign_event(campaign, coordinator=coordinator, event_name=event_name,
                                  node_ids=node_ids, start_day=start_day)
    campaign.add(event.to_schema_dict(campaign))


# ──────────────────────────────────────────────────────────────────────
# add_treatment_seeking
# ──────────────────────────────────────────────────────────────────────

def add_treatment_seeking(campaign: api_campaign,
                          targets: list[dict],
                          drug: list[str] = None,
                          start_day: float = 1,
                          node_ids: Optional[List[int]] = None,
                          property_restrictions: PropertyRestrictions = None,
                          drug_ineligibility_duration: float = 0,
                          duration: float = -1,
                          broadcast_event_name: str = "Received_Treatment") -> None:
    """
    Add event-triggered treatment-seeking behavior to the campaign. When an individual
    broadcasts one of the trigger events (e.g. ``NewClinicalCase``), they receive a
    drug regimen and a broadcast event indicating treatment was received.

    Each entry in **targets** produces a separate triggered campaign event, allowing
    different trigger/coverage/age/delay combinations in the same call.

    Args:
        campaign (api_campaign, required):
            The campaign object to which events will be added.

        targets (list[dict], required):
            A list of dictionaries, each defining one trigger-and-target combination.
            Each dictionary supports the following keys:

            * ``trigger`` (str, **required**) -- The individual event that triggers
              drug distribution (e.g. ``"NewClinicalCase"``, ``"NewSevereCase"``).
            * ``coverage`` (float, optional) -- Fraction of qualifying individuals
              who receive treatment. Default: 1.0.
            * ``agemin`` (float, optional) -- Minimum age in years. Default: 0.
            * ``agemax`` (float, optional) -- Maximum age in years.
              Default: :data:`~emodpy_malaria.campaign.common.MAX_AGE_YEARS`.
            * ``rate`` (float, optional) -- Rate parameter for an exponential delay
              (1 / mean delay in days) between trigger and treatment. A value of 0
              means treatment is immediate. Default: 0.

            Example::

                targets = [
                    {"trigger": "NewClinicalCase", "coverage": 0.8,
                     "agemin": 15, "agemax": 70, "rate": 0.3},
                    {"trigger": "NewSevereCase", "coverage": 0.9}
                ]

        drug (list[str], optional):
            Names of antimalarial drugs to distribute. Each name must match a drug
            configured in the simulation's **Malaria_Drug_Params**.
            Default: ``["Artemether", "Lumefantrine"]``.

        start_day (float, optional):
            The simulation day on which the triggered event begins listening.
            Default: 1.

        node_ids (Optional[List[int]], optional):
            Node IDs where the event applies. If ``None``, applies to all nodes.
            Default: None.

        property_restrictions (PropertyRestrictions, optional):
            A :class:`~emodpy_malaria.campaign.common.PropertyRestrictions` object
            specifying individual property restrictions for receiving treatment.
            Default: None.

        drug_ineligibility_duration (float, optional):
            Number of days an individual is ineligible for additional drugs after
            receiving treatment. Implemented by setting the individual property
            ``DrugStatus`` to ``RecentDrug`` for this duration. Set to 0 to disable.
            Default: 0.

        duration (float, optional):
            Number of days the triggered event listens for triggers. A value of -1
            means it listens indefinitely.
            Default: -1.

        broadcast_event_name (str, optional):
            Event broadcast when an individual receives treatment.
            Default: ``"Received_Treatment"``.

    Returns:
        None, adds events to the campaign.

    Example:
        >>> from emodpy_malaria.campaign.intervention_systems import add_treatment_seeking
        >>> from emod_api import campaign as api_campaign
        >>> my_campaign = api_campaign
        >>> my_campaign.set_schema("path_to_schema.json")
        >>> from emodpy_malaria.campaign.common import PropertyRestrictions
        >>> add_treatment_seeking(
        ...     campaign=my_campaign,
        ...     targets=[
        ...         {"trigger": "NewClinicalCase", "coverage": 0.8, "rate": 0.3},
        ...         {"trigger": "NewSevereCase", "coverage": 0.9}
        ...     ],
        ...     drug=["Artemether", "Lumefantrine"],
        ...     start_day=1,
        ...     property_restrictions=PropertyRestrictions(
        ...         individual_property_restrictions=[["Risk:High"]]),
        ...     drug_ineligibility_duration=14
        ... )
    """
    if drug is None:
        drug = ["Artemether", "Lumefantrine"]

    if not targets:
        raise ValueError(
            "Please define targets for treatment seeking. It is a list of dictionaries:\n"
            'ex: [{"trigger": "NewClinicalCase", "coverage": 0.8, "agemin": 15, '
            '"agemax": 70, "rate": 0.3}]')

    for target in targets:
        if "trigger" not in target:
            raise ValueError(
                "Please define trigger for each target dictionary.\n"
                'ex: [{"trigger": "NewClinicalCase", "coverage": 0.7, "agemax": 3}]')
        if "seek" in target:
            raise ValueError(
                "The 'seek' parameter has been removed. Please remove it from your "
                "targets dictionary and modify the coverage parameter directly.")

    interventions = [AntimalarialDrug(campaign, drug_type=d) for d in drug]
    interventions.append(BroadcastEvent(campaign, broadcast_event=broadcast_event_name))

    if drug_ineligibility_duration > 0:
        interventions.append(PropertyValueChanger(
            campaign,
            target_property_key="DrugStatus",
            target_property_value="RecentDrug",
            revert=drug_ineligibility_duration))

    for target in targets:
        coverage = target.get("coverage", 1.0)
        age_min = target.get("agemin", 0)
        age_max = target.get("agemax", MAX_AGE_YEARS)
        rate = target.get("rate", 0)

        target_demographics_config = TargetDemographicsConfig(
            demographic_coverage=coverage,
            target_age_min=age_min,
            target_age_max=age_max)

        delay_distribution = None
        if rate > 0:
            delay_distribution = ExponentialDistribution(1.0 / rate)

        add_intervention_triggered(
            campaign=campaign,
            intervention_list=interventions,
            triggers_list=[target["trigger"]],
            start_day=start_day,
            duration=duration,
            event_name="Treatment_Seeking_Behavior",
            node_ids=node_ids,
            delay_distribution=delay_distribution,
            target_demographics_config=target_demographics_config,
            property_restrictions=property_restrictions)


# ──────────────────────────────────────────────────────────────────────
# add_diagnostic_survey
# ──────────────────────────────────────────────────────────────────────

def add_diagnostic_survey(
        campaign: api_campaign,
        drug: Union[str, list] = None,
        diagnostic_type: Union[DiagnosticType, str] = DiagnosticType.BLOOD_SMEAR_PARASITES,
        detection_threshold: float = 40,
        measurement_sensitivity: float = 0.1,
        treatment_delay: BaseDistribution = None,
        start_day: float = 1,
        node_ids: Optional[List[int]] = None,
        event_name: str = "Diagnostic Survey",
        positive_diagnosis_configs: list = None,
        negative_diagnosis_configs: list = None,
        received_test_event: str = "Received_Test",
        target_demographics_config: TargetDemographicsConfig = None,
        property_restrictions: PropertyRestrictions = None,
        disqualifying_properties: list = None,
        repetition_config: RepetitionConfig = None,
        trigger_condition_list: list = None,
        duration: float = -1,
        triggered_campaign_delay: BaseDistribution = None,
        check_eligibility_at_trigger: bool = False,
        expire_recent_drugs: bool = False) -> None:
    """
    Add a scheduled or triggered diagnostic survey to the campaign using a
    :class:`~emodpy_malaria.campaign.individual_intervention.MalariaDiagnostic`.
    Upon positive or negative diagnosis, the interventions in
    **positive_diagnosis_configs** or **negative_diagnosis_configs** are distributed
    to the individual.

    The **drug** parameter provides a convenient shorthand: when set, it builds drug
    intervention configs and appends them to **positive_diagnosis_configs**
    automatically. If **treatment_delay** is also set, the drugs are wrapped in a
    :class:`~emodpy_malaria.campaign.individual_intervention.DelayedIntervention`.

    The diagnostic broadcasts ``"TestedPositive"`` and ``"TestedNegative"`` events.
    If **positive_diagnosis_configs** or **negative_diagnosis_configs** are provided,
    separate triggered events listen for internal tether broadcasts and distribute the
    configured interventions.

    Args:
        campaign (api_campaign, required):
            The campaign object to which events will be added.

        drug (Union[str, list], optional):
            Drug regimen to distribute on positive diagnosis. Either a drug code
            string from :data:`DRUG_CODES` (e.g. ``"AL"``, ``"DP"``) or a list
            of drug intervention objects (e.g.
            :class:`~emodpy_malaria.campaign.individual_intervention.AdherentDrug`
            instances). When provided, the resolved drug interventions are added
            to **positive_diagnosis_configs**. Default: None.

        diagnostic_type (Union[DiagnosticType, str], optional):
            Type of malaria diagnostic. See
            :class:`~emodpy_malaria.utils.emod_enum.DiagnosticType` for valid values.
            Default: ``DiagnosticType.BLOOD_SMEAR_PARASITES``.

        detection_threshold (float, optional):
            Detection threshold whose units depend on **diagnostic_type**.
            Default: 40.

        measurement_sensitivity (float, optional):
            Volume of blood tested in microliters (blood-smear diagnostics).
            Default: 0.1.

        treatment_delay (BaseDistribution, optional):
            Delay distribution between positive diagnosis and drug distribution.
            Only used when **drug** is provided. For example,
            ``ConstantDistribution(3)`` for a fixed 3-day delay.
            Default: None (no delay).

        start_day (float, optional):
            Simulation day the survey is created. If triggered, runs on trigger.
            Default: 1.

        node_ids (Optional[List[int]], optional):
            Node IDs where the survey applies. ``None`` applies to all nodes.

        event_name (str, optional):
            Descriptive name for the campaign event. Default: ``"Diagnostic Survey"``.

        positive_diagnosis_configs (list, optional):
            Intervention objects distributed to individuals who test positive.
            If **drug** is also provided, the drug interventions are appended
            to this list.

        negative_diagnosis_configs (list, optional):
            Intervention objects distributed to individuals who test negative.

        received_test_event (str, optional):
            Event broadcast when an individual receives the test.
            Default: ``"Received_Test"``.

        target_demographics_config (TargetDemographicsConfig, optional):
            Targeting configuration (coverage, age range, gender).

        property_restrictions (PropertyRestrictions, optional):
            Individual/node property restrictions for receiving the diagnostic.

        disqualifying_properties (list, optional):
            Property key:value pairs that prevent an individual from receiving
            the diagnostic.

        repetition_config (RepetitionConfig, optional):
            Repetition configuration. For scheduled surveys, passed directly to
            ``add_intervention_scheduled``. For triggered surveys with repetitions,
            implemented via delayed relay broadcasts.

        trigger_condition_list (list, optional):
            Events that trigger the survey. If ``None``, the survey is scheduled.

        duration (float, optional):
            Days to listen for trigger events. ``-1`` means indefinite.
            Default: -1.

        triggered_campaign_delay (BaseDistribution, optional):
            Delay distribution between trigger and survey distribution.

        check_eligibility_at_trigger (bool, optional):
            If ``True`` and the triggered survey is delayed, property restrictions
            are checked at the initial trigger rather than at distribution time.
            Default: False.

        expire_recent_drugs (bool, optional):
            If ``True``, adds ``"DrugStatus:None"`` to property restrictions for
            the positive result action so only individuals without recent drugs
            receive positive-diagnosis interventions. Default: False.

    Returns:
        None, adds events to the campaign.
    """
    if not isinstance(diagnostic_type, DiagnosticType):
        try:
            diagnostic_type = DiagnosticType(diagnostic_type)
        except ValueError:
            raise ValueError(
                f"Invalid diagnostic_type {diagnostic_type!r}. "
                f"Valid options: {list(DiagnosticType)}.")

    if drug is not None:
        if isinstance(drug, str):
            drug_configs = drug_configs_from_code(campaign, drug)
        elif isinstance(drug, list):
            for i, item in enumerate(drug):
                if not isinstance(item, AdherentDrug):
                    raise TypeError(
                        f"drug[{i}] must be an AdherentDrug instance, "
                        f"got {type(item).__name__}.")
            drug_configs = drug
        else:
            raise TypeError(
                f"drug must be a string (drug code) or a list of AdherentDrug instances, "
                f"got {type(drug).__name__}.")
        if treatment_delay is not None:
            if len(drug_configs) > 1:
                drug_mid = MultiInterventionDistributor(
                    campaign, intervention_list=drug_configs)
            else:
                drug_mid = drug_configs[0]
            drug_configs = [DelayedIntervention(
                campaign,
                delay_period_distribution=treatment_delay,
                intervention_to_distribute_at_delay_completion=drug_mid)]
        if positive_diagnosis_configs is None:
            positive_diagnosis_configs = drug_configs
        else:
            positive_diagnosis_configs = list(positive_diagnosis_configs) + drug_configs

    received_test = BroadcastEvent(campaign, broadcast_event=received_test_event)

    tested_positive_tether = f"TestedPositive_{random.randint(1, 100000)}"
    tested_negative_tether = f"TestedNegative_{random.randint(1, 100000)}"

    positive_action = MultiInterventionDistributor(
        campaign, intervention_list=[
            BroadcastEvent(campaign, broadcast_event="TestedPositive"),
            BroadcastEvent(campaign, broadcast_event=tested_positive_tether)])

    negative_action = MultiInterventionDistributor(
        campaign, intervention_list=[
            BroadcastEvent(campaign, broadcast_event="TestedNegative"),
            BroadcastEvent(campaign, broadcast_event=tested_negative_tether)])

    diagnostic = _make_diagnostic(
        campaign, diagnostic_type, detection_threshold, measurement_sensitivity,
        positive_diagnosis=positive_action,
        negative_diagnosis=negative_action)

    interventions = [diagnostic, received_test]
    if disqualifying_properties:
        interventions = [MultiInterventionDistributor(
            campaign, intervention_list=interventions,
            common_intervention_parameters=CommonInterventionParameters(
                disqualifying_properties=disqualifying_properties))]

    repetitions = repetition_config.number_repetitions if repetition_config else 1
    tsteps_btwn = repetition_config.timesteps_between_repetitions if repetition_config else 0

    if trigger_condition_list:
        if duration == -1:
            diagnosis_config_listening_duration = -1
        else:
            diagnosis_config_listening_duration = duration + 1

        actual_trigger = list(trigger_condition_list)
        actual_prop_restrictions = property_restrictions

        if repetitions > 1 or triggered_campaign_delay is not None:
            trigger_prop_restrictions = None
            if check_eligibility_at_trigger:
                trigger_prop_restrictions = property_restrictions
                actual_prop_restrictions = None

            broadcast_event_name = f"Diagnostic_Survey_Now_{random.randint(1, 100000)}"
            for x in range(repetitions):
                rep_offset = x * tsteps_btwn
                if triggered_campaign_delay is not None and rep_offset <= 0:
                    delay_dist = triggered_campaign_delay
                elif rep_offset > 0:
                    delay_dist = ConstantDistribution(rep_offset)
                else:
                    delay_dist = None
                add_intervention_triggered(
                    campaign,
                    intervention_list=[BroadcastEvent(campaign, broadcast_event=broadcast_event_name)],
                    triggers_list=trigger_condition_list,
                    start_day=start_day + 1,
                    duration=duration,
                    event_name="Diag_Survey_Now",
                    node_ids=node_ids,
                    delay_distribution=delay_dist,
                    property_restrictions=trigger_prop_restrictions)
            actual_trigger = [broadcast_event_name]

        add_intervention_triggered(
            campaign,
            intervention_list=interventions,
            triggers_list=actual_trigger,
            start_day=start_day + 1,
            duration=duration,
            event_name=event_name,
            node_ids=node_ids,
            target_demographics_config=target_demographics_config,
            property_restrictions=actual_prop_restrictions)
    else:
        diagnosis_config_listening_duration = duration
        add_intervention_scheduled(
            campaign,
            intervention_list=interventions,
            start_day=start_day + 1,
            node_ids=node_ids,
            target_demographics_config=target_demographics_config,
            property_restrictions=property_restrictions,
            repetition_config=repetition_config)

    positive_prop_restrictions = property_restrictions
    if expire_recent_drugs:
        if property_restrictions and property_restrictions.individual_property_restrictions:
            augmented = [group + ["DrugStatus:None"]
                         for group in property_restrictions.individual_property_restrictions]
            positive_prop_restrictions = PropertyRestrictions(
                individual_property_restrictions=augmented,
                node_property_restrictions=property_restrictions.node_property_restrictions)
        else:
            positive_prop_restrictions = PropertyRestrictions(
                individual_property_restrictions=[["DrugStatus:None"]])

    if positive_diagnosis_configs:
        add_intervention_triggered(
            campaign,
            intervention_list=positive_diagnosis_configs,
            triggers_list=[tested_positive_tether],
            start_day=start_day,
            duration=diagnosis_config_listening_duration,
            event_name=f"{event_name} Positive Result Action",
            node_ids=node_ids,
            property_restrictions=positive_prop_restrictions)

    if negative_diagnosis_configs:
        add_intervention_triggered(
            campaign,
            intervention_list=negative_diagnosis_configs,
            triggers_list=[tested_negative_tether],
            start_day=start_day,
            duration=diagnosis_config_listening_duration,
            event_name=f"{event_name} Negative Result Action",
            node_ids=node_ids)


# ──────────────────────────────────────────────────────────────────────
# add_drug_campaign
# ──────────────────────────────────────────────────────────────────────

def add_drug_campaign(campaign: api_campaign,
                      campaign_type: Union[CampaignType, str] = CampaignType.MDA,
                      drug: Union[str, list[AdherentDrug]] = None,
                      start_days: list = None,
                      target_demographics_config: TargetDemographicsConfig = None,
                      repetition_config: RepetitionConfig = None,
                      property_restrictions: PropertyRestrictions = None,
                      node_ids: Optional[List[int]] = None,
                      drug_ineligibility_duration: float = 0,
                      receiving_drugs_event_name: str = "Received_Campaign_Drugs",
                      disqualifying_properties: list = None,
                      diagnostic_type: Union[DiagnosticType, str] = DiagnosticType.BLOOD_SMEAR_PARASITES,
                      diagnostic_threshold: float = 40,
                      measurement_sensitivity: float = 0.1,
                      treatment_delay: BaseDistribution = None,
                      fmda_radius: float = 0,
                      node_selection_type: Union[NodeSelectionType, str] = NodeSelectionType.DISTANCE_ONLY,
                      trigger_coverage: float = 1.0,
                      snowballs: int = 0,
                      trigger_condition_list: list = None,
                      duration: float = -1,
                      triggered_campaign_delay: BaseDistribution = None,
                      check_eligibility_at_trigger: bool = False,
                      trigger_name: str = None,
                      birth_property_restrictions: PropertyRestrictions = None) -> dict:
    """
    Add a drug intervention campaign from a list of malaria campaign types.

    Campaign types:

    * **MDA** / **SMC** -- Mass drug administration. Distributes drugs directly.
    * **MSAT** / **MTAT** -- Mass screening and treatment. Runs a diagnostic survey
      and distributes drugs on positive result.
    * **fMDA** -- Focal mass drug administration. Diagnostic survey triggers drug
      distribution to the individual's node and neighboring nodes.
    * **rfMSAT** -- Reactive focal mass screening and treatment. Treatment of an
      index case triggers diagnostic surveys on neighboring nodes, cascading via
      **snowballs**.
    * **rfMDA** -- Reactive focal mass drug administration. Treatment of an index
      case triggers drug distribution to neighboring nodes.
    * **PMC** -- Preventive malaria chemoprevention (birth-triggered). Distributes
      drugs to newborns after a configurable delay.

    Args:
        campaign (api_campaign, required):
            The campaign object.
        campaign_type (Union[CampaignType, str], optional):
            The type of drug campaign:

            * ``MDA`` -- Mass drug administration; distributes drugs to everyone.
            * ``SMC`` -- Seasonal malaria chemoprevention; same as MDA.
            * ``MSAT`` -- Mass screening and treatment; diagnose then treat positives.
            * ``MTAT`` -- Mass testing and treatment; same as MSAT.
            * ``fMDA`` -- Focal MDA; diagnostic triggers drugs to nearby nodes.
            * ``rfMSAT`` -- Reactive focal MSAT; index-case treatment triggers
              diagnostic surveys on neighboring nodes, cascading via snowballs.
            * ``rfMDA`` -- Reactive focal MDA; index-case treatment triggers drug
              distribution to neighboring nodes.
            * ``PMC`` -- Preventive malaria chemoprevention; birth-triggered drug
              distribution to newborns.

            Default: ``CampaignType.MDA``.
        drug (Union[str, list[AdherentDrug]], required):
            The drug regimen to distribute. Either a drug code string from
            :data:`DRUG_CODES` (e.g. ``"AL"``, ``"DP"``, ``"SP"``) or a list of
            drug intervention objects (e.g.
            :class:`~emodpy_malaria.campaign.individual_intervention.AdherentDrug`
            instances).
        start_days (list, optional):
            Simulation days for drug distribution. Default: ``[1]``.
        target_demographics_config (TargetDemographicsConfig, optional):
            Targeting configuration (coverage, age, gender, residents_only).
        repetition_config (RepetitionConfig, optional):
            Repetition and interval configuration.
        property_restrictions (PropertyRestrictions, optional):
            Individual/node property restrictions.
        node_ids (Optional[List[int]], optional):
            Node IDs. ``None`` applies to all nodes.
        drug_ineligibility_duration (float, optional):
            Days to set ``DrugStatus:RecentDrug`` after receiving drugs.
            Default: 0.
        receiving_drugs_event_name (str, optional):
            Event broadcast on drug receipt. Default: ``"Received_Campaign_Drugs"``.
        disqualifying_properties (list, optional):
            Properties that prevent drug receipt.
        diagnostic_type (Union[DiagnosticType, str], optional):
            Diagnostic type for screening campaigns.
            Default: ``DiagnosticType.BLOOD_SMEAR_PARASITES``.
        diagnostic_threshold (float, optional):
            Detection threshold. Default: 40.
        measurement_sensitivity (float, optional):
            Measurement sensitivity. Default: 0.1.
        treatment_delay (BaseDistribution, optional):
            Delay distribution between diagnosis and drug distribution (MSAT, fMDA)
            or between index case treatment and RCD response (rfMSAT, rfMDA).
            For example, ``ConstantDistribution(3)`` for a fixed 3-day delay.
            Default: None (no delay).
        fmda_radius (float, optional):
            Radius in km for focal response. Default: 0.
        node_selection_type (Union[NodeSelectionType, str], optional):
            Node selection for focal broadcasts.
            Default: ``NodeSelectionType.DISTANCE_ONLY``.
        trigger_coverage (float, optional):
            Fraction of trigger events initiating RCD (rfMSAT, rfMDA) or fraction
            receiving diagnostic in fMDA. Default: 1.0.
        snowballs (int, optional):
            Number of cascading snowball rounds for rfMSAT. Default: 0.
        trigger_condition_list (list, optional):
            Events that trigger the campaign. ``None`` means scheduled.
        duration (float, optional):
            Days to listen for triggers. ``-1`` means indefinite. Default: -1.
        triggered_campaign_delay (BaseDistribution, optional):
            Delay distribution after trigger before campaign runs.
        check_eligibility_at_trigger (bool, optional):
            Check property restrictions at trigger time vs distribution time.
            Default: False.
        trigger_name (str, optional):
            PMC trigger name (e.g. ``"IPTi_1"``). Required for PMC campaigns.
        birth_property_restrictions (PropertyRestrictions, optional):
            Property restrictions for the PMC birth trigger event.

    Returns:
        dict: Metadata with campaign type, drug code, and coverage info.
    """
    if not isinstance(campaign_type, CampaignType):
        try:
            campaign_type = CampaignType(campaign_type)
        except ValueError:
            raise ValueError(
                f"Invalid campaign_type {campaign_type!r}. "
                f"Valid options: {list(CampaignType)}.")

    if drug is None:
        raise ValueError(
            "drug is required: provide a drug code string (e.g. 'AL', 'DP') "
            "or a list of drug intervention objects.")
    if isinstance(drug, str):
        drug_code = drug
        drug_configs = drug_configs_from_code(campaign, drug_code)
    elif isinstance(drug, list):
        for i, item in enumerate(drug):
            if not isinstance(item, AdherentDrug):
                raise TypeError(
                    f"drug[{i}] must be an AdherentDrug instance, "
                    f"got {type(item).__name__}.")
        drug_code = None
        drug_configs = drug
    else:
        raise TypeError(
            f"drug must be a string (drug code) or a list of AdherentDrug instances, "
            f"got {type(drug).__name__}.")

    receiving_drugs_event = BroadcastEvent(
        campaign, broadcast_event=receiving_drugs_event_name)
    if campaign_type in (CampaignType.rfMSAT, CampaignType.rfMDA):
        receiving_drugs_event = BroadcastEvent(
            campaign, broadcast_event="Received_RCD_Drugs")
    if drug_code and "Vehicle" in drug_code:
        receiving_drugs_event = BroadcastEvent(
            campaign, broadcast_event="Received_Vehicle")

    expire_recent_drugs = None
    if drug_ineligibility_duration > 0:
        expire_recent_drugs = PropertyValueChanger(
            campaign,
            target_property_key="DrugStatus",
            target_property_value="RecentDrug",
            revert=drug_ineligibility_duration)

    if start_days is None:
        start_days = [1]
    if disqualifying_properties is None:
        disqualifying_properties = []

    if campaign_type in (CampaignType.MDA, CampaignType.SMC):
        if treatment_delay is not None:
            raise ValueError("treatment_delay is not used in MDA or SMC campaigns.")
        _add_mda(campaign, start_days=start_days, drug_configs=drug_configs,
                 receiving_drugs_event=receiving_drugs_event,
                 expire_recent_drugs=expire_recent_drugs,
                 target_demographics_config=target_demographics_config,
                 repetition_config=repetition_config,
                 property_restrictions=property_restrictions,
                 disqualifying_properties=disqualifying_properties,
                 node_ids=node_ids,
                 trigger_condition_list=trigger_condition_list,
                 duration=duration,
                 triggered_campaign_delay=triggered_campaign_delay,
                 check_eligibility_at_trigger=check_eligibility_at_trigger)

    elif campaign_type in (CampaignType.MSAT, CampaignType.MTAT):
        _add_msat(campaign, start_days=start_days, drug_configs=drug_configs,
                  receiving_drugs_event=receiving_drugs_event,
                  expire_recent_drugs=expire_recent_drugs,
                  target_demographics_config=target_demographics_config,
                  repetition_config=repetition_config,
                  property_restrictions=property_restrictions,
                  disqualifying_properties=disqualifying_properties,
                  node_ids=node_ids,
                  diagnostic_type=diagnostic_type,
                  diagnostic_threshold=diagnostic_threshold,
                  measurement_sensitivity=measurement_sensitivity,
                  treatment_delay=treatment_delay,
                  trigger_condition_list=trigger_condition_list,
                  duration=duration,
                  triggered_campaign_delay=triggered_campaign_delay,
                  check_eligibility_at_trigger=check_eligibility_at_trigger)

    elif campaign_type == CampaignType.fMDA:
        _add_fmda(campaign, start_days=start_days, drug_configs=drug_configs,
                  receiving_drugs_event=receiving_drugs_event,
                  expire_recent_drugs=expire_recent_drugs,
                  target_demographics_config=target_demographics_config,
                  repetition_config=repetition_config,
                  property_restrictions=property_restrictions,
                  disqualifying_properties=disqualifying_properties,
                  node_ids=node_ids,
                  diagnostic_type=diagnostic_type,
                  diagnostic_threshold=diagnostic_threshold,
                  measurement_sensitivity=measurement_sensitivity,
                  treatment_delay=treatment_delay,
                  trigger_coverage=trigger_coverage,
                  fmda_radius=fmda_radius,
                  node_selection_type=node_selection_type,
                  trigger_condition_list=trigger_condition_list,
                  duration=duration,
                  triggered_campaign_delay=triggered_campaign_delay,
                  check_eligibility_at_trigger=check_eligibility_at_trigger)

    elif campaign_type == CampaignType.rfMSAT:
        _add_rfmsat(campaign, start_day=start_days[0], drug_configs=drug_configs,
                    receiving_drugs_event=receiving_drugs_event,
                    expire_recent_drugs=expire_recent_drugs,
                    target_demographics_config=target_demographics_config,
                    property_restrictions=property_restrictions,
                    disqualifying_properties=disqualifying_properties,
                    node_ids=node_ids,
                    diagnostic_type=diagnostic_type,
                    diagnostic_threshold=diagnostic_threshold,
                    measurement_sensitivity=measurement_sensitivity,
                    treatment_delay=treatment_delay,
                    trigger_coverage=trigger_coverage,
                    fmda_radius=fmda_radius,
                    node_selection_type=node_selection_type,
                    snowballs=snowballs,
                    duration=duration)

    elif campaign_type == CampaignType.rfMDA:
        _add_rfmda(campaign, start_day=start_days[0], drug_configs=drug_configs,
                   receiving_drugs_event=receiving_drugs_event,
                   expire_recent_drugs=expire_recent_drugs,
                   target_demographics_config=target_demographics_config,
                   property_restrictions=property_restrictions,
                   disqualifying_properties=disqualifying_properties,
                   node_ids=node_ids,
                   treatment_delay=treatment_delay,
                   trigger_coverage=trigger_coverage,
                   fmda_radius=fmda_radius,
                   node_selection_type=node_selection_type,
                   duration=duration)

    elif campaign_type == CampaignType.PMC:
        if treatment_delay is not None:
            raise ValueError("treatment_delay is not used in PMC campaigns.")
        _add_pmc(campaign, start_day=start_days[0], drug_configs=drug_configs,
                 trigger_name=trigger_name,
                 target_demographics_config=target_demographics_config,
                 node_ids=node_ids,
                 duration=duration,
                 triggered_campaign_delay=triggered_campaign_delay,
                 property_restrictions=property_restrictions,
                 birth_property_restrictions=birth_property_restrictions)

    return {
        "drug_campaign.type": campaign_type,
        "drug_campaign.drug": drug_code or drug,
        "drug_campaign.trigger_coverage": trigger_coverage,
        "drug_campaign.coverage": (
            target_demographics_config.demographic_coverage
            if target_demographics_config else 1.0),
    }


# ──────────────────────────────────────────────────────────────────────
# MDA / SMC
# ──────────────────────────────────────────────────────────────────────

def _add_mda(campaign, start_days, drug_configs, receiving_drugs_event,
             expire_recent_drugs, target_demographics_config, repetition_config,
             property_restrictions, disqualifying_properties, node_ids,
             trigger_condition_list, duration, triggered_campaign_delay,
             check_eligibility_at_trigger):

    interventions = _build_interventions(drug_configs, receiving_drugs_event, expire_recent_drugs)
    wrapped = _wrap_with_disqualifying(campaign, interventions, disqualifying_properties)

    repetitions = repetition_config.number_repetitions if repetition_config else 1
    tsteps_btwn = repetition_config.timesteps_between_repetitions if repetition_config else 0

    if trigger_condition_list:
        actual_trigger = list(trigger_condition_list)
        actual_prop_restrictions = property_restrictions

        if repetitions > 1 or triggered_campaign_delay is not None:
            broadcast_event_name = f"MDA_Now_{random.randint(1, 10000)}"
            trigger_prop_restrictions = None
            if check_eligibility_at_trigger:
                trigger_prop_restrictions = property_restrictions
                actual_prop_restrictions = None

            for x in range(repetitions):
                rep_offset = x * tsteps_btwn
                if triggered_campaign_delay is not None and rep_offset <= 0:
                    delay_dist = triggered_campaign_delay
                elif rep_offset > 0:
                    delay_dist = ConstantDistribution(rep_offset)
                else:
                    delay_dist = None
                add_intervention_triggered(
                    campaign,
                    intervention_list=[BroadcastEvent(campaign, broadcast_event=broadcast_event_name)],
                    triggers_list=trigger_condition_list,
                    start_day=start_days[0] + 1,
                    duration=duration,
                    event_name="MDA_Delayed",
                    node_ids=node_ids,
                    delay_distribution=delay_dist,
                    property_restrictions=trigger_prop_restrictions)
            actual_trigger = [broadcast_event_name]

        add_intervention_triggered(
            campaign,
            intervention_list=wrapped,
            triggers_list=actual_trigger,
            start_day=start_days[0],
            duration=duration,
            event_name="MDA_Now",
            node_ids=node_ids,
            target_demographics_config=target_demographics_config,
            property_restrictions=actual_prop_restrictions)
    else:
        for start_day in start_days:
            add_intervention_scheduled(
                campaign,
                intervention_list=wrapped,
                start_day=start_day,
                node_ids=node_ids,
                target_demographics_config=target_demographics_config,
                property_restrictions=property_restrictions,
                repetition_config=repetition_config)


# ──────────────────────────────────────────────────────────────────────
# MSAT / MTAT
# ──────────────────────────────────────────────────────────────────────

def _add_msat(campaign, start_days, drug_configs, receiving_drugs_event,
              expire_recent_drugs, target_demographics_config, repetition_config,
              property_restrictions, disqualifying_properties, node_ids,
              diagnostic_type, diagnostic_threshold, measurement_sensitivity,
              treatment_delay, trigger_condition_list, duration,
              triggered_campaign_delay, check_eligibility_at_trigger):

    event_config = _build_interventions(drug_configs, receiving_drugs_event, expire_recent_drugs)

    if treatment_delay is not None:
        if len(event_config) > 1:
            drug_mid = MultiInterventionDistributor(
                campaign, intervention_list=event_config)
        else:
            drug_mid = event_config[0]
        msat_cfg = [DelayedIntervention(
            campaign,
            delay_period_distribution=treatment_delay,
            intervention_to_distribute_at_delay_completion=drug_mid)]
    else:
        msat_cfg = event_config

    if trigger_condition_list:
        add_diagnostic_survey(
            campaign,
            diagnostic_type=diagnostic_type,
            detection_threshold=diagnostic_threshold,
            measurement_sensitivity=measurement_sensitivity,
            start_day=start_days[0],
            node_ids=node_ids,
            positive_diagnosis_configs=msat_cfg,
            target_demographics_config=target_demographics_config,
            property_restrictions=property_restrictions,
            disqualifying_properties=disqualifying_properties,
            repetition_config=repetition_config,
            trigger_condition_list=trigger_condition_list,
            duration=duration,
            triggered_campaign_delay=triggered_campaign_delay,
            check_eligibility_at_trigger=check_eligibility_at_trigger,
            expire_recent_drugs=expire_recent_drugs is not None)
    else:
        for start_day in start_days:
            add_diagnostic_survey(
                campaign,
                diagnostic_type=diagnostic_type,
                detection_threshold=diagnostic_threshold,
                measurement_sensitivity=measurement_sensitivity,
                start_day=start_day,
                node_ids=node_ids,
                positive_diagnosis_configs=msat_cfg,
                target_demographics_config=target_demographics_config,
                property_restrictions=property_restrictions,
                disqualifying_properties=disqualifying_properties,
                repetition_config=repetition_config,
                duration=duration,
                expire_recent_drugs=expire_recent_drugs is not None)


# ──────────────────────────────────────────────────────────────────────
# fMDA
# ──────────────────────────────────────────────────────────────────────

def _add_fmda(campaign, start_days, drug_configs, receiving_drugs_event,
              expire_recent_drugs, target_demographics_config, repetition_config,
              property_restrictions, disqualifying_properties, node_ids,
              diagnostic_type, diagnostic_threshold, measurement_sensitivity,
              treatment_delay, trigger_coverage, fmda_radius, node_selection_type,
              trigger_condition_list, duration, triggered_campaign_delay,
              check_eligibility_at_trigger):

    fmda_trigger_tether = f"Give_Drugs_fMDA_{random.randint(1, 10000)}"

    fmda_broadcast_to_neighbors = _fmda_broadcast(
        campaign, fmda_radius, node_selection_type, event_trigger=fmda_trigger_tether)
    fmda_trigger_event = BroadcastEvent(campaign, broadcast_event="Give_Drugs_fMDA")
    fmda_setup = [fmda_broadcast_to_neighbors, fmda_trigger_event]

    if treatment_delay is not None:
        fmda_mid = MultiInterventionDistributor(campaign, intervention_list=fmda_setup)
        fmda_setup = [DelayedIntervention(
            campaign,
            delay_period_distribution=treatment_delay,
            intervention_to_distribute_at_delay_completion=fmda_mid)]

    interventions = _build_interventions(drug_configs, receiving_drugs_event, expire_recent_drugs)

    trigger_target = None
    if trigger_coverage != 1.0:
        trigger_target = TargetDemographicsConfig(demographic_coverage=trigger_coverage)

    repetitions = repetition_config.number_repetitions if repetition_config else 1
    tsteps_btwn = repetition_config.timesteps_between_repetitions if repetition_config else 0

    if trigger_condition_list:
        add_diagnostic_survey(
            campaign,
            diagnostic_type=diagnostic_type,
            detection_threshold=diagnostic_threshold,
            measurement_sensitivity=measurement_sensitivity,
            start_day=start_days[0] + 1,
            node_ids=node_ids,
            positive_diagnosis_configs=fmda_setup,
            target_demographics_config=trigger_target,
            property_restrictions=property_restrictions,
            repetition_config=repetition_config,
            trigger_condition_list=trigger_condition_list,
            duration=duration,
            triggered_campaign_delay=triggered_campaign_delay,
            check_eligibility_at_trigger=check_eligibility_at_trigger,
            expire_recent_drugs=expire_recent_drugs is not None)
    else:
        for start_day in start_days:
            for rep in range(repetitions):
                add_diagnostic_survey(
                    campaign,
                    diagnostic_type=diagnostic_type,
                    detection_threshold=diagnostic_threshold,
                    measurement_sensitivity=measurement_sensitivity,
                    start_day=start_day + 1 + tsteps_btwn * rep,
                    node_ids=node_ids,
                    positive_diagnosis_configs=fmda_setup,
                    target_demographics_config=trigger_target,
                    property_restrictions=property_restrictions,
                    disqualifying_properties=disqualifying_properties,
                    expire_recent_drugs=expire_recent_drugs is not None)

    _add_triggered_event_with_blackout(
        campaign,
        intervention_list=interventions,
        triggers_list=[fmda_trigger_tether],
        start_day=start_days[0],
        node_ids=node_ids,
        duration=duration,
        target_config=target_demographics_config,
        prop_restrictions=property_restrictions,
        disqualifying_properties=disqualifying_properties,
        event_name="Distribute fMDA",
        blackout_period=1,
        blackout_on_first_occurrence=True,
        blackout_event_trigger="fMDA_Blackout_Event_Trigger")


# ──────────────────────────────────────────────────────────────────────
# rfMSAT
# ──────────────────────────────────────────────────────────────────────

def _add_rfmsat(campaign, start_day, drug_configs, receiving_drugs_event,
                expire_recent_drugs, target_demographics_config,
                property_restrictions, disqualifying_properties, node_ids,
                diagnostic_type, diagnostic_threshold, measurement_sensitivity,
                treatment_delay, trigger_coverage, fmda_radius, node_selection_type,
                snowballs, duration):

    snowball_triggers = [f"Diagnostic_Survey_{i}" for i in range(snowballs + 1)]

    initial_broadcast = _fmda_broadcast(
        campaign, fmda_radius, node_selection_type,
        event_trigger=snowball_triggers[0])

    trigger_target = None
    if trigger_coverage != 1.0:
        trigger_target = TargetDemographicsConfig(demographic_coverage=trigger_coverage)

    if treatment_delay is not None:
        rcd_intervention = DelayedIntervention(
            campaign,
            delay_period_distribution=treatment_delay,
            intervention_to_distribute_at_delay_completion=initial_broadcast)
    else:
        rcd_intervention = initial_broadcast

    add_intervention_triggered(
        campaign,
        intervention_list=[rcd_intervention],
        triggers_list=["Received_Treatment"],
        start_day=start_day,
        duration=duration,
        event_name="Trigger RCD MSAT",
        node_ids=node_ids,
        target_demographics_config=trigger_target)

    event_config = _build_interventions(drug_configs, receiving_drugs_event, expire_recent_drugs)

    add_diagnostic_survey(
        campaign,
        diagnostic_type=diagnostic_type,
        detection_threshold=diagnostic_threshold,
        measurement_sensitivity=measurement_sensitivity,
        start_day=start_day,
        node_ids=node_ids,
        trigger_condition_list=[snowball_triggers[0]],
        event_name="Reactive MSAT level 0",
        positive_diagnosis_configs=event_config,
        target_demographics_config=target_demographics_config,
        property_restrictions=property_restrictions,
        disqualifying_properties=disqualifying_properties,
        duration=duration,
        expire_recent_drugs=expire_recent_drugs is not None)

    for snowball in range(snowballs):
        next_broadcast = _fmda_broadcast(
            campaign, fmda_radius, node_selection_type,
            event_trigger=snowball_triggers[snowball + 1])
        snowball_configs = [next_broadcast, receiving_drugs_event] + list(drug_configs)

        add_diagnostic_survey(
            campaign,
            diagnostic_type=diagnostic_type,
            detection_threshold=diagnostic_threshold,
            measurement_sensitivity=measurement_sensitivity,
            start_day=start_day,
            node_ids=node_ids,
            trigger_condition_list=[snowball_triggers[snowball]],
            event_name=f"Snowball level {snowball}",
            positive_diagnosis_configs=snowball_configs,
            target_demographics_config=target_demographics_config,
            property_restrictions=property_restrictions,
            disqualifying_properties=disqualifying_properties,
            duration=duration,
            expire_recent_drugs=expire_recent_drugs is not None)


# ──────────────────────────────────────────────────────────────────────
# rfMDA
# ──────────────────────────────────────────────────────────────────────

def _add_rfmda(campaign, start_day, drug_configs, receiving_drugs_event,
               expire_recent_drugs, target_demographics_config,
               property_restrictions, disqualifying_properties, node_ids,
               treatment_delay, trigger_coverage, fmda_radius, node_selection_type,
               duration):

    rfmda_trigger = "Give_Drugs_rfMDA"
    fmda_broadcast = _fmda_broadcast(
        campaign, fmda_radius, node_selection_type, event_trigger=rfmda_trigger)

    trigger_target = None
    if trigger_coverage != 1.0:
        trigger_target = TargetDemographicsConfig(demographic_coverage=trigger_coverage)

    if treatment_delay is not None:
        rcd_intervention = DelayedIntervention(
            campaign,
            delay_period_distribution=treatment_delay,
            intervention_to_distribute_at_delay_completion=fmda_broadcast)
    else:
        rcd_intervention = fmda_broadcast

    add_intervention_triggered(
        campaign,
        intervention_list=[rcd_intervention],
        triggers_list=["Received_Treatment"],
        start_day=start_day,
        duration=duration,
        event_name="Trigger RCD MDA",
        node_ids=node_ids,
        target_demographics_config=trigger_target,
        property_restrictions=property_restrictions)

    interventions = _build_interventions(drug_configs, receiving_drugs_event, expire_recent_drugs)

    _add_triggered_event_with_blackout(
        campaign,
        intervention_list=interventions,
        triggers_list=[rfmda_trigger],
        start_day=start_day,
        node_ids=node_ids,
        duration=duration,
        target_config=target_demographics_config,
        prop_restrictions=property_restrictions,
        disqualifying_properties=disqualifying_properties,
        event_name="Distribute rfMDA")


# ──────────────────────────────────────────────────────────────────────
# PMC (formerly IPTi)
# ──────────────────────────────────────────────────────────────────────

def _add_pmc(campaign, start_day, drug_configs, trigger_name,
             target_demographics_config, node_ids, duration,
             triggered_campaign_delay, property_restrictions,
             birth_property_restrictions):

    if not trigger_name:
        raise ValueError("trigger_name is required for PMC campaigns.")

    trigger_coverage = 1.0
    drug_coverage = 1.0
    if target_demographics_config:
        trigger_coverage = target_demographics_config.demographic_coverage
        drug_coverage = target_demographics_config.demographic_coverage

    trigger_target = TargetDemographicsConfig(demographic_coverage=trigger_coverage)
    drug_target = TargetDemographicsConfig(demographic_coverage=drug_coverage)

    broadcast = BroadcastEvent(campaign, broadcast_event=trigger_name)
    if triggered_campaign_delay is not None:
        birth_intervention = DelayedIntervention(
            campaign,
            delay_period_distribution=triggered_campaign_delay,
            intervention_to_distribute_at_delay_completion=broadcast)
    else:
        birth_intervention = broadcast

    add_intervention_triggered(
        campaign,
        intervention_list=[birth_intervention],
        triggers_list=["Births"],
        start_day=start_day,
        duration=duration,
        event_name="PMC_Birth_Trigger",
        node_ids=node_ids,
        target_demographics_config=trigger_target,
        property_restrictions=birth_property_restrictions)

    received_event_name = f"Received_{trigger_name}"
    drug_interventions = list(drug_configs) + [
        BroadcastEvent(campaign, broadcast_event=received_event_name)]

    add_intervention_triggered(
        campaign,
        intervention_list=drug_interventions,
        triggers_list=[trigger_name],
        start_day=start_day,
        duration=duration,
        event_name="PMC_Drug_Distribution",
        node_ids=node_ids,
        target_demographics_config=drug_target,
        property_restrictions=property_restrictions)
