from typing import List, Optional

from emod_api import campaign as api_campaign

from emodpy.campaign.distributor import add_intervention_scheduled, add_intervention_triggered, add_community_health_worker  # noqa: F401
from emodpy.campaign.distributor import add_broadcast_coordinator_event as _emodpy_add_broadcast_coordinator_event
from emodpy.campaign.event import create_campaign_event
from emodpy_malaria.campaign.event_coordinator import VectorSurveillanceEventCoordinator, VectorCounter


def add_broadcast_coordinator_event(campaign: api_campaign,
                                    broadcast_event: str,
                                    start_day: float,
                                    coordinator_name: str = "BroadcastCoordinatorEvent",
                                    cost_to_consumer: float = 0,
                                    event_name: str = None,
                                    node_ids: Optional[List[int]] = None) -> None:
    """
    Add a coordinator-level event broadcast to the campaign. This creates a
    :class:`~emodpy.campaign.event_coordinator.BroadcastCoordinatorEvent` coordinator that
    broadcasts a single coordinator event when the campaign event fires. It does **not**
    distribute interventions.

    This is useful for triggering coordinator-level event chains. For example, it can
    broadcast the start trigger for a
    :class:`~emodpy.campaign.event_coordinator.SurveillanceEventCoordinator` or a
    :class:`~emodpy_malaria.campaign.event_coordinator.VectorSurveillanceEventCoordinator`.

    Args:
        campaign (api_campaign, required):
            - The campaign object to which the event will be added. This should be an
              instance of the emod_api.campaign class.
        broadcast_event (str, required):
            - The name of the coordinator-level event to broadcast. Must be a non-empty
              string. The event must be defined in **Custom_Coordinator_Events** in the
              simulation configuration.
        start_day (float, required):
            - The simulation day when the event fires.
        coordinator_name (str, optional):
            - A descriptive name for this coordinator instance, useful in output reports
              such as :class:`~emodpy.reporters.common.ReportCoordinatorEventRecorder`.
            - Default value: "BroadcastCoordinatorEvent"
        cost_to_consumer (float, optional):
            - The unit cost per coordinator created.
            - Minimum value: 0. Maximum value: 3.40282e+38.
            - Default value: 0
        event_name (str, optional):
            - The name of the campaign event.
            - Defaults to None.
        node_ids (Optional[List[int]], optional):
            - A list of node IDs where the event will be applied.
            - If None, the event applies to all nodes.
            - Defaults to None.

    Returns:
        None, adds the configuration to the campaign.

    Example:
        >>> from emodpy_malaria.campaign.distributor import add_broadcast_coordinator_event
        >>> from emod_api import campaign as api_campaign
        >>> my_campaign = api_campaign
        >>> my_campaign.set_schema('path_to_schema.json')
        >>> add_broadcast_coordinator_event(
        ...     campaign=my_campaign,
        ...     broadcast_event="StartSurveillance",
        ...     start_day=1,
        ...     coordinator_name="TriggerSurveillance"
        ... )
    """
    _emodpy_add_broadcast_coordinator_event(
        campaign,
        broadcast_event=broadcast_event,
        start_day=start_day,
        coordinator_name=coordinator_name,
        cost_to_consumer=cost_to_consumer,
        event_name=event_name,
        node_ids=node_ids)


def add_vector_surveillance(campaign: api_campaign,
                            counter: VectorCounter,
                            start_trigger_condition_list: list[str],
                            start_day: float,
                            survey_completed_event: str = None,
                            duration: float = None,
                            stop_trigger_condition_list: list[str] = None,
                            coordinator_name: str = None,
                            event_name: str = None,
                            node_ids: Optional[List[int]] = None) -> None:
    """
    Add a vector surveillance event to the campaign. The coordinator periodically samples
    vectors and computes statistics (allele frequencies or genome fractions). It does **not**
    distribute interventions. Instead, response logic is delegated to an embedded Python
    script, **dtk_vector_surveillance.py**, which must be placed in the simulation working
    directory.

    Sampling is controlled by coordinator-level trigger events: the coordinator begins
    periodic sampling when an event from ``start_trigger_condition_list`` is received,
    and stops when an event from ``stop_trigger_condition_list`` is received or
    ``duration`` expires.

    Args:
        campaign (api_campaign, required):
            - The campaign object to which the event will be added. This should be an
              instance of the emod_api.campaign class.
        counter (VectorCounter, required):
            - Sampling configuration specifying which species and gender to sample,
              how many vectors to sample (via a distribution), how often to sample,
              and what statistic to compute.
        start_trigger_condition_list (list[str], required):
            - A list of coordinator-level events that, when heard, start the coordinator's
              periodic sampling at the interval specified by the counter's ``update_period``.
            - Cannot be an empty list.
        start_day (float, required):
            - The simulation day when the surveillance is distributed. The surveillance does
              not run until the coordinator hears an event from
              ``start_trigger_condition_list``, but this is the earliest it can start.
        survey_completed_event (str, optional):
            - Coordinator-level event broadcast every time the coordinator completes a
              survey of the vector population.
            - Default value: None (no event broadcast).
        duration (float, optional):
            - The number of days the coordinator remains active after creation. After this
              many days, the coordinator unregisters and expires. A value of -1 keeps it
              running indefinitely.
            - Minimum value: -1.
            - Default value: None (uses EMOD default: -1).
        stop_trigger_condition_list (list[str], optional):
            - A list of coordinator-level events that, when heard, stop sampling and prevent
              the responder from responding. The coordinator does not expire until
              ``duration`` has elapsed.
            - Default value: None (empty list).
        coordinator_name (str, optional):
            - A descriptive name for this coordinator instance, useful in output reports
              such as ReportCoordinatorEventRecorder.csv and
              ReportSurveillanceEventRecorder.csv.
            - Default value: None (uses EMOD default: "VectorSurveillanceEventCoordinator").
        event_name (str, optional):
            - The name of the campaign event.
            - Defaults to None.
        node_ids (Optional[List[int]], optional):
            - A list of node IDs where the event will be applied.
            - If None, the event applies to all nodes.
            - Defaults to None.

    Returns:
        None, adds the configuration to the campaign.

    .. important::

        The ``respond()`` function in **dtk_vector_surveillance.py** can return
        coordinator-level event names at runtime. These events are determined
        dynamically and **cannot** be auto-detected from the script. You must
        manually register any event names that ``respond()`` might return in
        **Custom_Coordinator_Events** in the simulation configuration. Failing
        to register them will cause the simulation to fail at runtime.

    Example:
        >>> from emodpy_malaria.campaign.distributor import add_vector_surveillance
        >>> from emodpy_malaria.campaign.event_coordinator import VectorCounter
        >>> from emodpy_malaria.utils.distributions import ConstantDistribution
        >>> from emod_api import campaign as api_campaign
        >>> my_campaign = api_campaign
        >>> my_campaign.set_schema('path_to_schema.json')
        >>> counter = VectorCounter(species="gambiae",
        ...                         sample_size_distribution=ConstantDistribution(100))
        >>> add_vector_surveillance(
        ...     campaign=my_campaign,
        ...     counter=counter,
        ...     start_trigger_condition_list=["StartSurveillance"],
        ...     start_day=1,
        ...     survey_completed_event="SurveyComplete",
        ...     duration=365,
        ...     coordinator_name="MySurveillance"
        ... )
    """
    coordinator = VectorSurveillanceEventCoordinator(
        campaign,
        counter=counter,
        start_trigger_condition_list=start_trigger_condition_list,
        survey_completed_event=survey_completed_event,
        duration=duration,
        stop_trigger_condition_list=stop_trigger_condition_list,
        coordinator_name=coordinator_name)

    event = create_campaign_event(campaign, coordinator=coordinator, event_name=event_name,
                                  node_ids=node_ids, start_day=start_day)

    campaign.add(event.to_schema_dict(campaign))
