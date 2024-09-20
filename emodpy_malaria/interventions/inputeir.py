from emod_api import schema_to_class as s2c
from emod_api.interventions import utils



def new_intervention(
        campaign,
        monthly_eir: list = None,
        daily_eir: list = None,
        age_dependence: str = "OFF",
        scaling_factor: float = 1.0
):
    """
        Create the InputEIR intervention itself that will be nestled inside an event coordinator.

        Args:
            campaign:  Passed in campaign (from emod_api.campaign)
            monthly_eir: An array of 12 elements that contain an entomological inoculation rate (EIR) for each month;
                Each value should be between 0 and 1000
            daily_eir: An array of 365 values where each value is the mean number of infectious bites experienced
                by an individual for that day of the year
            age_dependence: Determines how InputEIR depends on the age of the target. Options are "OFF", "LINEAR",
                "SURFACE_AREA_DEPENDENT"
            scaling_factor: A modifier that is multiplied by the EIR determined for the current day

        Returns:
            InputEIR intervention
    """
    if (monthly_eir is None and daily_eir is None) or (monthly_eir is not None and daily_eir is not None):
        raise ValueError("Please define either monthly_eir or daily_eir for this intervention (but not both).\n")

    intervention = s2c.get_class_with_defaults("InputEIR", campaign.schema_path)

    if daily_eir:
        if len(daily_eir) != 365:
            raise ValueError(f"daily_eir array needs to have 1 element per day of the year (i.e., 365).")
        if any(i > 1000 for i in daily_eir):
            raise ValueError(f"All daily_eir array elements need to be <= 1000.")
        if any(i < 0 for i in daily_eir):
            raise ValueError(f"All daily_eir array elements need to be positive.")
        intervention.Daily_EIR = daily_eir
        intervention.EIR_Type = "DAILY"
    else:
        if len(monthly_eir) != 12:
            raise ValueError(f"monthly_eir array needs to have 1 element per month (i.e., 12).")
        if any(i > 1000 for i in monthly_eir):
            raise ValueError(f"All monthly_eir array elements need to be <= 1000.")
        if any(i < 0 for i in monthly_eir):
            raise ValueError(f"All monthly_eir array elements need to be positive.")
        intervention.Monthly_EIR = monthly_eir
        intervention.EIR_Type = "MONTHLY"
    intervention.Age_Dependence = age_dependence
    intervention.Scaling_Factor = scaling_factor
    return intervention


def InputEIR(
        campaign,
        monthly_eir: list = None,
        daily_eir: list = None,
        start_day: int = 1,
        node_ids: list = None,
        age_dependence: str = "OFF",
        scaling_factor: float = 1.0
):
    """
        Create a full CampaignEvent that distributes InputEIR to a population.

        Args:
            campaign: Passed in campaign (from emod_api.campaign)
            monthly_eir: An array of 12 elements that contain an entomological inoculation rate (EIR) for each month;
                Each value should be between 0 and 1000
            daily_eir: An array of 365 values where each value is the mean number of infectious bites experienced
                by an individual for that day of the year
            start_day: The day on which the monthly_eir cycle starts
            node_ids: Nodes to which this intervention is applied
            age_dependence: Determines how InputEIR depends on the age of the target. Options are "OFF", "LINEAR",
                "SURFACE_AREA_DEPENDENT"
            scaling_factor: A modifier that is multiplied by the EIR determined for the current day

        Returns:
            Campaign event to be added to campaign (from emod_api.camapign)
    """

    # First, get the objects
    event = s2c.get_class_with_defaults("CampaignEvent", campaign.schema_path)
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", campaign.schema_path)
    if coordinator is None:
        print("s2c.get_class_with_defaults returned None. Maybe no schema.json was provided.")
        return ""

    intervention = new_intervention(campaign, monthly_eir, daily_eir, age_dependence, scaling_factor)
    coordinator.Intervention_Config = intervention
    coordinator.pop("Node_Property_Restrictions")

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    event.Start_Day = float(start_day)
    event.Nodeset_Config = utils.do_nodes(campaign.schema_path, node_ids)

    return event


def new_intervention_as_file(campaign, start_day: int = 0, monthly_eir: list = None, daily_eir: list = None, filename: str = None):
    """
        Create an InputEIR intervention as its own file.

        Args:
            campaign: Passed in campaign (from emod_api.campaign)
            start_day: The day on which the monthly_eir cycle starts
            monthly_eir: An array of 12 elements that contain an entomological inoculation rate (EIR) for each month;
                Each value should be between 0 and 1000
            daily_eir: An array of 365 values where each value is the mean number of infectious bites experienced
                by an individual for that day of the year
            filename: filename used for the file created

        Returns:
            The filename of the file created
    """
    campaign.add(InputEIR(campaign=campaign, monthly_eir=monthly_eir, daily_eir=daily_eir, start_day=start_day), first=True)
    if filename is None:
        filename = "InputEIR.json"
    campaign.save(filename)
    return filename


def add_InputEIR(campaign,
                 monthly_eir: list = None,
                 daily_eir: list = None,
                 start_day: int = 1,
                 node_ids: list = None,
                 age_dependence: str = "OFF",
                 scaling_factor: float = 1.0
                 ):
    """
    Wrapper that creates a full CampaignEvent that distributes InputEIR to a population AND adds it to the campaign.

    Args:
        campaign: Passed in campaign (from emod_api.campaign)
        monthly_eir: An array of 12 elements that contain an entomological inoculation rate (EIR) for each month;
            Each value should be between 0 and 1000
        daily_eir: An array of 365 values where each value is the mean number of infectious bites experienced
            by an individual for that day of the year
        start_day: The day on which the monthly_eir cycle starts
        node_ids: Nodes to which this intervention is applied
        age_dependence: Determines how InputEIR depends on the age of the target. Options are "OFF", "LINEAR",
            "SURFACE_AREA_DEPENDENT"
        scaling_factor: A modifier that is multiplied by the EIR determined for the current day
    """

    campaign_event = InputEIR(campaign=campaign,
                              monthly_eir=monthly_eir,
                              daily_eir=daily_eir,
                              start_day=start_day,
                              node_ids=node_ids,
                              age_dependence=age_dependence,
                              scaling_factor=scaling_factor)
    campaign.add(campaign_event)
