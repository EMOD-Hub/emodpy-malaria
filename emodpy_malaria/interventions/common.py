"""
This module contains functionality common to many interventions.
"""

import emod_api.interventions.utils as utils
from emod_api import schema_to_class as s2c

schema_path=None

###
### Malaria
###

def MalariaDiagnostic(
        camp,
        Diagnostic_Type="BLOOD_SMEAR_PARASITES",
        Measurement_Sensitivity=0,
        Detection_Threshold=0
    ):
    """
    Add a malaria diagnostic intervention to your campaign. This is equivalent
    to :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`. 

    Args:
        camp: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention 
            will be added. 
        Measurement_Sensitivity: The setting for **Measurement_Sensitivity**
            in :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`.
        Detection_Threshold: The setting for **Detection_Threshold** in 
            :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`. 
        Diagnostic_Type: The setting for **Diagnostic_Type** in 
            :doc:`emod-malaria:parameter-campaign-individual-malariadiagnostic`.
            In addition to the accepted values listed there, you may also set
            TRUE_INFECTION_STATUS, which calls 
            :doc:`emod-malaria:parameter-campaign-individual-standarddiagnostic`
            instead.
    Returns:
      The diagnostic intervention event.
    """
    # Shares lots of code with Standard. Not obvious if code minimization maximizes readability.
    import emod_api.interventions.common as emodapi_com
    global schema_path 
    schema_path = camp.schema_path if camp is not None else schema_path
    # First, get the objects

    if Diagnostic_Type == "TRUE_INFECTION_STATUS":
        if Measurement_Sensitivity != 0 or Detection_Threshold != 0:
            raise ValueError( f"MalariaDiagnostic invoked with 'TRUE_INFECTION_STATUS' and non-default values of either sensitivity or threshold params (or both). Those params are not used for TRUE_INFECTION_STATUS." )
        intervention = emodapi_com.StandardDiagnostic( camp )
    else:
        intervention = s2c.get_class_with_defaults( "MalariaDiagnostic", schema_path )
        intervention.Measurement_Sensitivity = Measurement_Sensitivity 
        intervention.Detection_Threshold = Detection_Threshold 
        intervention.Diagnostic_Type = Diagnostic_Type 

    return intervention


def AntimalarialDrug( camp, Drug_Type, ctc=1.0 ):
    """
    Add an antimalarial drug intervention to your campaign. This is equivalent to
    :doc:`emod-malaria:parameter-campaign-individual-antimalarialdrug`.

    Args:
        camp: The :py:obj:`emod_api:emod_api.campaign` object to which the intervention will be added. 
        Drug_Type: The name of the drug to distribute in a drugs intervention.
            Possible values are contained in **Malaria_Drug_Params**. 
        ctc: The cost to consumer.

    Returns:
      The antimalarial drug intervention event.
    """
    global schema_path 
    schema_path = camp.schema_path if camp is not None else schema_path
    intervention = s2c.get_class_with_defaults( "AntimalarialDrug", schema_path )
    intervention.Drug_Type = Drug_Type 
    intervention.Cost_To_Consumer = ctc
    return intervention


def triggered_campaign_delay_event( camp, start_day, trigger, delay, intervention, ip_targeting=None, coverage=1.0, target_age_min=0, target_age_max=125.0 ):
    """
        Create and return a campaign event that responds to a trigger after a delay with an intervention.

        Args:
            camp: emod_api.campaign object with schema_path set.
            start_day: When to start.
            trigger: E.g., "NewInfection".
            delay: Dictionary of 1 or 2 params that are the literal Delay_Distribution parameters, 
                but without the distribution, which is inferred. E.g., { "Delay_Period_Exponential": 5 }.
            intervention: List of 1 or more valid intervention dictionaries to be distributed together. 
            ip_targeting: Optional Individual Properties required for someone to receive the intervntion(s).
            coverage: Optional percentage coverage of target population. Defaults to all (100%).
            target_age_min: Optional minimum age (in years). Defaults to 0.
            target_age_max: Optional maximum age (in years). Defaults to 125.

        Returns:
            Campaign event.

    """
    import emod_api.interventions.common as comm
    delay_iv = comm.DelayedIntervention( camp, Configs=[intervention], Delay_Dict = delay )
    event = comm.TriggeredCampaignEvent( camp, Start_Day=start_day, Event_Name="triggered_delayed_intervention", Triggers=[ camp.get_recv_trigger( trigger, old=True ) ], Intervention_List=[delay_iv], Property_Restrictions=ip_targeting, Demographic_Coverage=coverage, Target_Age_Min=target_age_min*365, Target_Age_Max=target_age_max*365 )

    return event


