import emod_api.config.default_from_schema_no_validation as dfs


def species_params(manifest, species: str = None):
    """
        Returns configured species parameters based on species name

    Args:

        manifest: file that contains path to the schema file
        species: species, configuration for which, we will be adding to the simulation.

    Returns:
        Configured species parameters

    """

    # generic
    vsp = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorSpeciesParameters"])
    vsp.parameters.Anthropophily = 0.65
    vsp.parameters.Name = "gambiae"
    vsp.parameters.Acquire_Modifier = 0.8
    vsp.parameters.Adult_Life_Expectancy = 20
    vsp.parameters.Aquatic_Arrhenius_1 = 84200000000
    vsp.parameters.Aquatic_Arrhenius_2 = 8328
    vsp.parameters.Aquatic_Mortality_Rate = 0.1
    vsp.parameters.Days_Between_Feeds = 3
    vsp.parameters.Egg_Batch_Size = 100
    vsp.parameters.Immature_Duration = 2
    vsp.parameters.Indoor_Feeding_Fraction = 0.95
    vsp.parameters.Infected_Arrhenius_1 = 117000000000
    vsp.parameters.Infected_Arrhenius_2 = 8336
    vsp.parameters.Infected_Egg_Batch_Factor = 0.8
    vsp.parameters.Infectious_Human_Feed_Mortality_Factor = 1.5
    vsp.parameters.Male_Life_Expectancy = 10
    vsp.parameters.Transmission_Rate = 0.9
    vsp.parameters.Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_NONE"
    # adding habitats
    lht = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
    lht.parameters.Habitat_Type = "WATER_VEGETATION"
    lht.parameters.Max_Larval_Capacity = 20000000
    # end adding larval capacity
    vsp.parameters.Habitats = [lht.parameters]

    builtin_species_list = ["gambiae", "arabiensis", "funestus", "fpg_gambiae", "minimus", "dirus"]  # please update if more species is added
    if species == "gambiae":  # same as generic species
        return vsp.parameters
    elif species == "arabiensis":
        # default arabiensis
        vsp.parameters.Name = "arabiensis"
        vsp.parameters.Indoor_Feeding_Fraction = 0.5
        # replacing habitats
        lht1 = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
        lht1.parameters.Habitat_Type = "TEMPORARY_RAINFALL"
        lht1.parameters.Max_Larval_Capacity = 800000000
        lht2 = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
        lht2.parameters.Habitat_Type = "CONSTANT"
        lht2.parameters.Max_Larval_Capacity = 80000000
        # end adding larval capacity
        vsp.parameters.Habitats = [lht1.parameters, lht2.parameters]
        return vsp.parameters
    elif species == "funestus":
        vsp.parameters.Name = "funestus"
        # replacing habitats
        lht1 = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
        lht1.parameters.Habitat_Type = "TEMPORARY_RAINFALL"
        lht1.parameters.Max_Larval_Capacity = 800000000
        lht2 = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
        lht2.parameters.Habitat_Type = "CONSTANT"
        lht2.parameters.Max_Larval_Capacity = 80000000
        # end adding larval capacity
        vsp.parameters.Habitats = [lht1.parameters, lht2.parameters]
        return vsp.parameters
    elif species == "fpg_gambiae":  # from Jon Russel's sims, still called "gambiae"
        vsp.parameters.Acquire_Modifier = 0.8
        vsp.parameters.Indoor_Feeding_Fraction = 0.5
        vsp.parameters.Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_EVERY_DAY"
        # replacing habitats
        lht = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
        lht.parameters.Habitat_Type = "LINEAR_SPLINE"
        lht.parameters.Max_Larval_Capacity = 316227766.01683795
        lht.parameters.Capacity_Distribution_Number_Of_Years = 1
        # adding larval capacity
        cdot = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:InterpolatedValueMap"])
        cdot.parameters.Times = [0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167,
                                 334.583]
        cdot.parameters.Values = [3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8, 6.5, 2.6, 2.1]
        lht.parameters.Capacity_Distribution_Over_Time = cdot.parameters
        # end adding larval capacity
        vsp.parameters.Habitats = [lht.parameters]
        return vsp.parameters
    elif species == "minimus":  # from Monique Ambrose's sims
        vsp.parameters.Anthropophily = 0.5
        vsp.parameters.Name = "minimus"
        vsp.parameters.Acquire_Modifier = 0.8
        vsp.parameters.Adult_Life_Expectancy = 25
        vsp.parameters.Egg_Batch_Size = 70
        vsp.parameters.Indoor_Feeding_Fraction = 0.6
        vsp.parameters.Transmission_Rate = 0.8
        # adding habitats
        lht1 = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
        lht1.parameters.Habitat_Type = "WATER_VEGETATION"
        lht1.parameters.Max_Larval_Capacity = 2e7
        lht2 = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
        lht2.parameters.Habitat_Type = "LINEAR_SPLINE"
        lht2.parameters.Max_Larval_Capacity = 3e7
        lht2.parameters.Capacity_Distribution_Number_Of_Years = 1
        # adding larval capacity
        cdot = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:InterpolatedValueMap"])
        cdot.parameters.Times = [0, 1, 245, 275, 364]
        cdot.parameters.Values = [0.2, 0.2, 0.7, 3, 3]
        lht2.parameters.Capacity_Distribution_Over_Time = cdot.parameters
        # end adding larval capacity
        vsp.parameters.Habitats = [lht1.parameters, lht2.parameters]
        return vsp.parameters
    elif species == "dirus":  # dirus for Monique Ambrose's sims
        vsp.parameters.Anthropophily = 0.5
        vsp.parameters.Name = "dirus"
        vsp.parameters.Adult_Life_Expectancy = 30
        vsp.parameters.Egg_Batch_Size = 70
        vsp.parameters.Indoor_Feeding_Fraction = 0.01
        vsp.parameters.Transmission_Rate = 0.8
        # adding habitats
        lht1 = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
        lht1.parameters.Habitat_Type = "CONSTANT"
        lht1.parameters.Max_Larval_Capacity = 1e7
        lht2 = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:VectorHabitat"])
        lht2.parameters.Habitat_Type = "TEMPORARY_RAINFALL"
        lht2.parameters.Max_Larval_Capacity = 7e7
        # end adding larval capacity
        vsp.parameters.Habitats = [lht1.parameters, lht2.parameters]
        return vsp.parameters
    else:
        return builtin_species_list
