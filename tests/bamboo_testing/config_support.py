import emod_api.config.default_from_schema_no_validation as dfs

from emodpy_malaria import malaria_config as malconf


def set_config(config):
    # config.parameters.Acquisition_Blocking_Immunity_Decay_Rate = 0
    config.parameters.Acquisition_Blocking_Immunity_Duration_Before_Decay = 0
    config.parameters.Infectious_Period_Constant = 0
    config.parameters.Enable_Birth = 1
    # config.parameters.Enable_Coinfection = 1
    config.parameters.Enable_Demographics_Birth = 1
    config.parameters.Enable_Demographics_Reporting = 0
    # config.parameters.Migration_Model = "NO_MIGRATION"
    # config.parameters.Mortality_Blocking_Immunity_Decay_Rate = 0
    # config.parameters.Mortality_Blocking_Immunity_Duration_Before_Decay = 270
    config.parameters.Run_Number = 99
    config.parameters.Simulation_Duration = 60
    config.parameters.Enable_Demographics_Risk = 1
    config.parameters.Enable_Maternal_Infection_Transmission = 0
    config.parameters.Enable_Natural_Mortality = 0
    # config.parameters.Report_Event_Recorder = 1
    # config.parameters.Custom_Individual_Events = ["Received_Treatment"]
    config.parameters.Report_Event_Recorder_Events = ["ReceivedTreatment", "NewInfectionEvent", "NewClinicalCase",
                                                      "NewSevereCase"]
    config.parameters.x_Base_Population = 0.1
    # Must make sure mosquitos are not dying from anything but vaccine
    config.parameters.Human_Feeding_Mortality = 0
    # config.parameters.Report_Vector_Genetics = 1

    return config


def set_param_fn(config, manifest, set_config_fn, duration=365, whokill="Male"):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config.parameters.Simulation_Type = "MALARIA_SIM"
    import emodpy_malaria.malaria_config as conf
    config = conf.set_team_defaults(config, manifest)
    conf.add_species(config, manifest, ["gambiae"])
    config = set_config_fn(config)

    lhm = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
    lhm.parameters.Max_Larval_Capacity = 0  # no egs allowed
    lhm.parameters.Habitat_Type = "TEMPORARY_RAINFALL"
    conf.get_species_params(config, "gambiae").Habitats.append(lhm.parameters)

    # Important for a "clean" test
    species_params = config.parameters.Vector_Species_Params[0]
    species_params.Adult_Life_Expectancy = 730
    species_params.Egg_Batch_Size = 0

    config.parameters.Base_Rainfall = 150
    config.parameters.Simulation_Duration = duration
    config.parameters.Climate_Model = "CLIMATE_CONSTANT"
    config.parameters.Enable_Disease_Mortality = 0
    config.parameters.Egg_Saturation_At_Oviposition = "SATURATION_AT_OVIPOSITION"
    config.parameters.Enable_Vector_Species_Report = 1
    config.parameters.pop("Serialized_Population_Filenames")

    # Vector Genetics
    if whokill == "Male":
        malconf.add_insecticide_resistance(config, manifest, "everybody_wants_some", "gambiae", [["X", "X"]])
        malconf.add_insecticide_resistance(config, manifest, "everybody_wants_some", "gambiae",
                                           allele_combo=[["X", "Y"]],
                                           killing=0.0)
    elif whokill == "Female":
        malconf.add_insecticide_resistance(config, manifest, "everybody_wants_some", "gambiae", [["X", "Y"]])
        malconf.add_insecticide_resistance(config, manifest, "everybody_wants_some", "gambiae",
                                           allele_combo=[["X", "X"]],
                                           killing=0.0)

    elif whokill == "All":
        malconf.add_insecticide_resistance(config, manifest, "everybody_wants_some", "gambiae", [["X", "Y"]],
                                           killing=0.0)
        malconf.add_insecticide_resistance(config, manifest, "everybody_wants_some", "gambiae",
                                           allele_combo=[["X", "X"]],
                                           killing=0.0)

    elif whokill == "Mixed":
        malconf.add_insecticide_resistance(config, manifest, "everybody_wants_some", "gambiae", [["X", "Y"]],
                                           killing=1.0)
        malconf.add_insecticide_resistance(config, manifest, "everybody_wants_some", "gambiae", [["X", "X"]],
                                           killing=0.6)

    return config
