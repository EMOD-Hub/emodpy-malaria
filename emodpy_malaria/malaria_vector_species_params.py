import emod_api.schema_to_class as s2c

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
    vsp = s2c.get_class_with_defaults( "idmType:VectorSpeciesParameters", schema_path=manifest.schema_file)
    vsp.Anthropophily = 0.65
    vsp.Name = "gambiae"
    vsp.Acquire_Modifier = 0.8
    vsp.Adult_Life_Expectancy = 20
    vsp.Aquatic_Arrhenius_1 = 84200000000
    vsp.Aquatic_Arrhenius_2 = 8328
    vsp.Aquatic_Mortality_Rate = 0.1
    vsp.Days_Between_Feeds = 3
    vsp.Egg_Batch_Size = 100
    vsp.Immature_Duration = 2
    vsp.Indoor_Feeding_Fraction = 0.95
    vsp.Infected_Arrhenius_1 = 117000000000
    vsp.Infected_Arrhenius_2 = 8336
    vsp.Infected_Egg_Batch_Factor = 0.8
    vsp.Infectious_Human_Feed_Mortality_Factor = 1.5
    vsp.Male_Life_Expectancy = 10
    vsp.Transmission_Rate = 0.9
    vsp.Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_NONE"
    # adding habitats
    lht = s2c.get_class_with_defaults( "idmType:VectorHabitat", schema_path=manifest.schema_file)
    lht.Habitat_Type = "WATER_VEGETATION"
    lht.Max_Larval_Capacity = 20000000
    # end adding larval capacity
    vsp.Habitats = [lht]

    builtin_species_list = ["gambiae", "arabiensis", "funestus", "fpg_gambiae", "minimus", "dirus"]  # please update if more species is added
    if species == "gambiae":  # same as generic species
        return vsp
    elif species == "arabiensis":
        # default arabiensis
        vsp.Name = "arabiensis"
        vsp.Indoor_Feeding_Fraction = 0.5
        # replacing habitats
        lht1 = s2c.get_class_with_defaults( "idmType:VectorHabitat", schema_path=manifest.schema_file)
        lht1.Habitat_Type = "TEMPORARY_RAINFALL"
        lht1.Max_Larval_Capacity = 800000000
        lht2 = s2c.get_class_with_defaults( "idmType:VectorHabitat", schema_path=manifest.schema_file)
        lht2.Habitat_Type = "CONSTANT"
        lht2.Max_Larval_Capacity = 80000000
        # end adding larval capacity
        vsp.Habitats = [lht1, lht2]
        return vsp
    elif species == "funestus":
        vsp.Name = "funestus"
        # replacing habitats
        lht1 = s2c.get_class_with_defaults( "idmType:VectorHabitat", schema_path=manifest.schema_file)
        lht1.Habitat_Type = "TEMPORARY_RAINFALL"
        lht1.Max_Larval_Capacity = 800000000
        lht2 = s2c.get_class_with_defaults( "idmType:VectorHabitat", schema_path=manifest.schema_file)
        lht2.Habitat_Type = "CONSTANT"
        lht2.Max_Larval_Capacity = 80000000
        # end adding larval capacity
        vsp.Habitats = [lht1, lht2]
        return vsp
    elif species == "fpg_gambiae":  # from Jon Russel's sims, still called "gambiae"
        vsp.Acquire_Modifier = 0.8
        vsp.Indoor_Feeding_Fraction = 0.5
        vsp.Vector_Sugar_Feeding_Frequency = "VECTOR_SUGAR_FEEDING_EVERY_DAY"
        # replacing habitats
        lht = s2c.get_class_with_defaults( "idmType:VectorHabitat", schema_path=manifest.schema_file)
        lht.Habitat_Type = "LINEAR_SPLINE"
        lht.Max_Larval_Capacity = 316227766.01683795
        lht.Capacity_Distribution_Number_Of_Years = 1
        # adding larval capacity
        cdot = s2c.get_class_with_defaults( "idmType:InterpolatedValueMap", schema_path=manifest.schema_file)
        cdot.Times = [0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167,
                                 334.583]
        cdot.Values = [3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8, 6.5, 2.6, 2.1]
        lht.Capacity_Distribution_Over_Time = cdot
        # end adding larval capacity
        vsp.Habitats = [lht]
        return vsp
    elif species == "minimus":  # from Monique Ambrose's sims
        vsp.Anthropophily = 0.5
        vsp.Name = "minimus"
        vsp.Acquire_Modifier = 0.8
        vsp.Adult_Life_Expectancy = 25
        vsp.Egg_Batch_Size = 70
        vsp.Indoor_Feeding_Fraction = 0.6
        vsp.Transmission_Rate = 0.8
        # adding habitats
        lht1 = s2c.get_class_with_defaults( "idmType:VectorHabitat", schema_path=manifest.schema_file)
        lht1.Habitat_Type = "WATER_VEGETATION"
        lht1.Max_Larval_Capacity = 2e7
        lht2 = s2c.get_class_with_defaults( "idmType:VectorHabitat", schema_path=manifest.schema_file)
        lht2.Habitat_Type = "LINEAR_SPLINE"
        lht2.Max_Larval_Capacity = 3e7
        lht2.Capacity_Distribution_Number_Of_Years = 1
        # adding larval capacity
        cdot = s2c.get_class_with_defaults( "idmType:InterpolatedValueMap", schema_path=manifest.schema_file)
        cdot.Times = [0, 1, 245, 275, 364]
        cdot.Values = [0.2, 0.2, 0.7, 3, 3]
        lht2.Capacity_Distribution_Over_Time = cdot
        # end adding larval capacity
        vsp.Habitats = [lht1, lht2]
        return vsp
    elif species == "dirus":  # dirus for Monique Ambrose's sims
        vsp.Anthropophily = 0.5
        vsp.Name = "dirus"
        vsp.Adult_Life_Expectancy = 30
        vsp.Egg_Batch_Size = 70
        vsp.Indoor_Feeding_Fraction = 0.01
        vsp.Transmission_Rate = 0.8
        # adding habitats
        lht1 = s2c.get_class_with_defaults( "idmType:VectorHabitat", schema_path=manifest.schema_file)
        lht1.Habitat_Type = "CONSTANT"
        lht1.Max_Larval_Capacity = 1e7
        lht2 = s2c.get_class_with_defaults( "idmType:VectorHabitat", schema_path=manifest.schema_file)
        lht2.Habitat_Type = "TEMPORARY_RAINFALL"
        lht2.Max_Larval_Capacity = 7e7
        # end adding larval capacity
        vsp.Habitats = [lht1, lht2]
        return vsp
    else:
        return builtin_species_list
