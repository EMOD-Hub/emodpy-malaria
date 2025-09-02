from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emodpy_malaria.interventions.common import add_campaign_event

iv_name = "InputEIR"


def _input_eir(
        campaign,
        monthly_eir: list = None,
        daily_eir: list = None,
        scaling_factor: float = 1.0,
        intervention_name: str = iv_name
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
            intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
                others that use the same class. It’s possible to have multiple InputEIR interventions
                attached to a node if they have different Intervention_Name values.

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
    intervention.Scaling_Factor = scaling_factor
    intervention.Intervention_Name = intervention_name
    return intervention


def add_scheduled_input_eir(
        campaign,
        start_day: int = 1,
        node_ids: list = None,
        monthly_eir: list = None,
        daily_eir: list = None,
        age_dependence: str = "OFF",
        scaling_factor: float = 1.0,
        intervention_name: str = iv_name
):
    """
        Create a full CampaignEvent that distributes InputEIR to a population.

        Args:
            campaign: Passed in campaign (from emod_api.campaign)
            start_day: The day on which the monthly_eir cycle starts
            node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
                will get the intervention
            monthly_eir: An array of 12 elements that contain an entomological inoculation rate (EIR) for each month;
                Each value should be between 0 and 1000
            daily_eir: An array of 365 values where each value is the mean number of infectious bites experienced
                by an individual for that day of the year
            start_day: The day on which the monthly_eir cycle starts
            age_dependence: Determines how InputEIR depends on the age of the target. Options are "OFF", "LINEAR",
                "SURFACE_AREA_DEPENDENT"
            scaling_factor: A modifier that is multiplied by the EIR determined for the current day
            intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
                others that use the same class. It’s possible to have multiple InputEIR interventions
                attached to a node if they have different Intervention_Name values.

        Returns:
            Nothing
    """

    input_eir = _input_eir(campaign=campaign, monthly_eir=monthly_eir, daily_eir=daily_eir,
                           age_dependence=age_dependence, scaling_factor=scaling_factor,
                           intervention_name=intervention_name)

    add_campaign_event(campaign=campaign, start_day=start_day, node_ids=node_ids, node_intervention=input_eir)


def new_intervention_as_file(campaign, start_day: int = 0, monthly_eir: list = None, daily_eir: list = None,
                             filename: str = "InputEIR.json"):
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
    add_scheduled_input_eir(campaign=campaign, start_day=start_day, monthly_eir=monthly_eir, daily_eir=daily_eir)
    campaign.save(filename)
    return filename
