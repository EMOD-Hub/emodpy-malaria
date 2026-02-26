def set_config( config ):
    config.parameters.Enable_Demographics_Reporting = 0
    config.parameters.Enable_Maternal_Infection_Transmission = 0
    
    config.parameters.x_Base_Population =0.5
    config.parameters.Max_Individual_Infections = 10

    # MIGRATION
    config.parameters.Migration_Pattern = "SINGLE_ROUND_TRIPS"

    config.parameters.x_Regional_Migration = 0.03
    config.parameters.Regional_Migration_Roundtrip_Duration = 2
    config.parameters.Enable_Migration_Heterogeneity = 0 # this should be implicit

    return config
