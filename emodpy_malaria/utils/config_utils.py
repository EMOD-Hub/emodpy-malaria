def non_schema_checks(config):
    """
    Do additional voluntary checks for config consistency. There's no real fixed list for what
    should be here.
    """
    p = config.parameters
    if p.Report_HIV_ByAgeAndGender:
        if p.Report_HIV_ByAgeAndGender_Start_Year > (p.Base_Year + (p.Simulation_Duration / 365.0)):
            raise ValueError("'Report HIV By Age And Gender' doesn't start before the simulation ends.")
        if p.Report_HIV_ByAgeAndGender_Start_Year < p.Base_Year:
            raise ValueError("'Report HIV By Age And Gender' starts before the simulation.")
    if p.Report_HIV_Infection:
        if p.Report_HIV_Infection_Start_Year > (p.Base_Year + (p.Simulation_Duration / 365.0)):
            raise ValueError("'Report HIV Infection' doesn't start before the simulation ends.")
        if p.Report_HIV_Infection_Start_Year < p.Base_Year:
            raise ValueError("'Report HIV Infection' starts before the simulation.")
    return
