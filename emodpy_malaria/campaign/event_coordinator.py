from typing import Union
from functools import partial

from emod_api import campaign as api_campaign, schema_to_class as s2c

from emodpy.campaign.event_coordinator import BaseEventCoordinator
from emodpy.campaign.event_coordinator import StandardEventCoordinator  # noqa: F401
from emodpy.campaign.event_coordinator import (  # noqa: F401
    NodeIdAndCoverage as NodeIdAndCoverage,
    BroadcastCoordinatorEvent as BroadcastCoordinatorEvent,
    CommunityHealthWorkerEventCoordinator as CommunityHealthWorkerEventCoordinator,
    Action as Action,
    Responder as Responder,
    IncidenceCounter as IncidenceCounter,
    IncidenceEventCoordinator as IncidenceEventCoordinator,
    IncidenceCounterSurveillance as IncidenceCounterSurveillance,
    ResponderSurveillance as ResponderSurveillance,
    SurveillanceEventCoordinator as SurveillanceEventCoordinator,
    CoverageByNodeEventCoordinator as CoverageByNodeEventCoordinator,
)
from emodpy.utils.distributions import BaseDistribution
from emodpy_malaria.campaign.common import TargetDemographicsConfig, PropertyRestrictions  # noqa: F401
from emodpy_malaria.campaign.node_intervention import _validate_vector_sampling_type
from emodpy_malaria.utils.emod_enum import VectorCountType, VectorGender


class VectorCounter:
    """
    Defines the sampling parameters for a :class:`VectorSurveillanceEventCoordinator`.
    Specifies which vector species and gender to sample, how many to sample, how often,
    and what statistic to compute from the sample.

    Args:
        species (str, required):
            The name of the vector species to sample. Must match a species name defined
            in the **Vector_Species_Params** configuration parameter.

        sample_size_distribution (BaseDistribution, required):
            The distribution used to determine the number of vectors in the sample for
            each sampling event. If the population is smaller than the drawn sample size,
            the entire population is selected.
             Use the distribution classes
            from :mod:`emodpy_malaria.utils.distributions`:

            * :class:`~emodpy_malaria.utils.distributions.ConstantDistribution`
            * :class:`~emodpy_malaria.utils.distributions.UniformDistribution`
            * :class:`~emodpy_malaria.utils.distributions.GaussianDistribution`
            * :class:`~emodpy_malaria.utils.distributions.ExponentialDistribution`
            * :class:`~emodpy_malaria.utils.distributions.PoissonDistribution`
            * :class:`~emodpy_malaria.utils.distributions.LogNormalDistribution`
            * :class:`~emodpy_malaria.utils.distributions.WeibullDistribution`
            * :class:`~emodpy_malaria.utils.distributions.DualConstantDistribution`
            * :class:`~emodpy_malaria.utils.distributions.DualExponentialDistribution`

        count_type (Union[VectorCountType, str], required):
            The attribute to count in the sampled mosquitoes. Use the
            :class:`~emodpy_malaria.utils.emod_enum.VectorCountType` enum values:

            * ``VectorCountType.ALLELE_FREQ`` -- Calculates the frequency of every allele
              in the sampled population. Each vector contributes 0, 1, or 2 occurrences
              of each allele.
            * ``VectorCountType.GENOME_FRACTION`` -- Calculates the fraction of each
              genome (grouped by similarity) in the sampled population.

        gender (Union[VectorGender, str], required):
            The sex of the vectors to sample. Use the
            :class:`~emodpy_malaria.utils.emod_enum.VectorGender` enum values:

            * ``VectorGender.VECTOR_FEMALE``
            * ``VectorGender.VECTOR_MALE``
            * ``VectorGender.VECTOR_BOTH_GENDERS``

        update_period (float, required):
            The number of days between sampling events. If sampled on day 1 with a period
            of 30, the next sample is taken on day 31.
            Minimum value: 0
            Maximum value: 999999.
    """

    def __init__(self,
                 species: str,
                 sample_size_distribution: BaseDistribution,
                 count_type: Union[VectorCountType, str],
                 gender: Union[VectorGender, str],
                 update_period: float):
        if not species or not isinstance(species, str):
            raise ValueError("species must be a non-empty string.")
        if not isinstance(sample_size_distribution, BaseDistribution):
            raise ValueError(
                f"sample_size_distribution must be a BaseDistribution instance, "
                f"got {type(sample_size_distribution).__name__}.")
        if not isinstance(count_type, VectorCountType):
            try:
                count_type = VectorCountType(count_type)
            except ValueError:
                raise ValueError(
                    f"count_type must be a VectorCountType enum value, got {count_type!r}. "
                    f"Valid options: {list(VectorCountType)}")
        if not isinstance(gender, VectorGender):
            try:
                gender = VectorGender(gender)
            except ValueError:
                raise ValueError(
                    f"gender must be a VectorGender enum value, got {gender!r}. "
                    f"Valid options: {list(VectorGender)}")
        if not 0 <= update_period <= 999999:
            raise ValueError(f"update_period must be between 0 and 999999, got {update_period}.")

        self._species = species
        self._sample_size_distribution = sample_size_distribution
        self._count_type = count_type
        self._gender = gender
        self._update_period = update_period

    def to_schema_dict(self, campaign: api_campaign) -> s2c.ReadOnlyDict:
        obj = s2c.get_class_with_defaults("idmType:VectorCounter", schema_json=campaign.get_schema())
        obj.Species = self._species
        obj.Count_Type = self._count_type
        obj.Gender = self._gender
        obj.Update_Period = self._update_period
        self._sample_size_distribution.set_intervention_distribution(obj, "Sample_Size")
        obj.pop("schema", None)
        obj.pop("explicits", None)
        return obj


class VectorSurveillanceEventCoordinator(BaseEventCoordinator):
    """
    The **VectorSurveillanceEventCoordinator** monitors vector populations by periodically
    sampling vectors and computing statistics (allele frequencies or genome fractions).
    Unlike most event coordinators, it does **not** distribute interventions. Instead, it
    delegates response logic to an embedded Python script, **dtk_vector_surveillance.py**,
    which must be placed in the simulation working directory.

    Sampling is controlled by coordinator-level trigger events: the coordinator begins
    periodic sampling when an event from ``start_trigger_condition_list`` is received,
    and stops when an event from ``stop_trigger_condition_list`` is received or
    ``duration`` expires.

    Embedded Python: dtk_vector_surveillance.py
        The **dtk_vector_surveillance.py** file must define a ``respond()`` function and
        may optionally define ``create_responder()`` and ``delete_responder()``.

        **respond(time, responder_id, coordinator_name, num_vectors_sampled,
        list_data_names, list_data_values)** -- Required. Called each time any
        VectorSurveillanceEventCoordinator in the simulation completes a sampling event.
        Must return a ``list[str]`` of coordinator-level event names to broadcast (or an
        empty list). These events can trigger other campaign events such as mosquito
        releases. The returned event names must correspond to events used in the campaign
        unrecognized events will cause the simulation to fail.

        Parameters passed to ``respond()``:

        * ``time`` (float) -- Simulation time in days when sampling occurred.
        * ``responder_id`` (int) -- Unique ID assigned to this responder at coordinator
          creation. IDs are assigned in order of coordinator creation.
        * ``coordinator_name`` (str) -- The **Coordinator_Name** of the coordinator that
          performed this sampling. Use this to differentiate between multiple coordinators,
          since all coordinators share the same ``respond()`` function.
        * ``num_vectors_sampled`` (int) -- Number of vectors actually sampled (may be less
          than requested if population is small).
        * ``list_data_names`` (list[str]) -- When ``count_type`` is ``ALLELE_FREQ``: allele
          names (e.g., ``["a0", "a1"]``). When ``GENOME_FRACTION``: genome strings
          (e.g., ``["X-a0:X-a0", "X-a0:X-a1"]``). Equivalent genomes under allele
          reordering are grouped together.
        * ``list_data_values`` (list[float]) -- Fractions corresponding to each entry in
          ``list_data_names``. For ``ALLELE_FREQ``: frequency at each allele's locus
          (accounts for two copies per diploid vector). For ``GENOME_FRACTION``: fraction of
          each genome in the sampled population.

        **create_responder(responder_id, coordinator_name)** -- Optional. Called once when
        each coordinator is created. Use to initialize per-coordinator state.

        **delete_responder(responder_id, coordinator_name)** -- Optional. Called when a
        coordinator expires (after ``duration`` elapses). Use for cleanup.

    .. important::

        The ``respond()`` function can return coordinator-level event names at
        runtime. These events are determined dynamically and **cannot** be
        auto-detected from the script. You must manually register any event
        names that ``respond()`` might return in **Custom_Coordinator_Events**
        in the simulation configuration. Failing to register them will cause
        the simulation to fail at runtime.

    Args:
        campaign (api_campaign, required):
            The campaign object.

        counter (VectorCounter, required):
            Sampling configuration specifying which species and gender to sample,
            how many vectors to sample (via a distribution), how often to sample,
            and what statistic to compute.

        survey_completed_event (str, optional):
            Coordinator-level event broadcast every time the coordinator completes a survey of the vector population.
            Default value: None (no event broadcast)

        duration (float, optional):
            The number of days the coordinator remains active after creation. After this
            many days, the coordinator unregisters and expires. A value of -1 keeps
            it running indefinitely.
            Minimum value: -1. Default value: -1.

        start_trigger_condition_list (list[str], required):
            A list of coordinator-level events that, when heard, start the coordinator's
            periodic sampling at the interval specified by the counter's ``update_period``.

        stop_trigger_condition_list (list[str], optional):
            A list of coordinator events that, when heard, stop sampling and prevent the
            responder from responding. The coordinator does not expire until ``duration``
            has elapsed.
            Default value: None (empty list)

        coordinator_name (str, optional):
            A descriptive name for this coordinator instance, useful in output reports
            such as ReportCoordinatorEventRecorder.csv and
            ReportSurveillanceEventRecorder.csv. EMOD does not enforce uniqueness.
            Assign unique names to each coordinator to make it easy to route logic in
            the ``respond()`` function.
            Default value: "VectorSurveillanceEventCoordinator"
    """

    def __init__(self,
                 campaign: api_campaign,
                 counter: VectorCounter,
                 start_trigger_condition_list: list[str],
                 survey_completed_event: str = None,
                 duration: float = None,
                 stop_trigger_condition_list: list[str] = None,
                 coordinator_name: str = None):
        super().__init__(campaign, 'VectorSurveillanceEventCoordinator')

        if not isinstance(counter, VectorCounter):
            raise ValueError(
                f"counter must be a VectorCounter instance, "
                f"got {type(counter).__name__}.")

        self._coordinator.Counter = counter.to_schema_dict(campaign)

        if not start_trigger_condition_list or not isinstance(start_trigger_condition_list, list):
            raise ValueError("start_trigger_condition_list must be a non-empty list of coordinator-level events.")
        self._coordinator.Start_Trigger_Condition_List = [campaign.set_listened_coordinator_event(t) for t in start_trigger_condition_list]

        if survey_completed_event is not None:
            responder = s2c.get_class_with_defaults("idmType:VectorResponder", schema_json=campaign.get_schema())
            responder.Survey_Completed_Event = campaign.set_broadcast_coordinator_event(survey_completed_event)
            responder.pop("schema", None)
            responder.pop("explicits", None)
            self._coordinator.Responder = responder

        if duration is not None:
            if duration < -1:
                raise ValueError(f"duration must be >= -1, got {duration}.")
            self._coordinator.Duration = duration

        if stop_trigger_condition_list:
            self._coordinator.Stop_Trigger_Condition_List = [campaign.set_listened_coordinator_event(t) for t in stop_trigger_condition_list]

        if coordinator_name is not None:
            self._coordinator.Coordinator_Name = coordinator_name

        campaign.implicits.append(
            partial(_validate_vector_sampling_type,
                    intervention_name="VectorSurveillanceEventCoordinator"))
