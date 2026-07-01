# Changing serialized demographics parameters

Not every parameter can be changed after the creation of serialized files. The following overview
is intended as high-level guidance for what changes can and cannot be made.

See also: [Serializing populations](software-serializing-pops.md),
[Serialized population file format](software-serialized.md),
[Working with serialized data](software-serializing-data-access.md).

## Population-level parameters


### Cannot be changed


* **Age_Initialization_Distribution_Type**
* **Birth_Rate_Boxcar_Forcing**
* **Birth_Rate_Dependence**
* **Birth_Rate_Time_Dependence**
* **Birth_Rate_Sinusoidal**
* **Death_Rate_Dependence**
* **Enable_Birth**
* **Enable_Demographics_Risk**
* **Enable_Initial_Prevalence**
* **Enable_Natural_Mortality**
* **Enable_Vital_Dynamics**
* **Population_Scale_Type**
* **x_Base_Population**
* **x_Birth**
* **x_Other_Mortality**


### Can be changed

* **Enable_Disease_Mortality**


## NodeAttributes


### Cannot be changed


* **InitialPopulation**
* **InitialVectorsPerSpecies**
* **LarvalHabitatMultiplier**

!!! note
	We discourage use of **LarvalHabitatMultiplier** due to its deserialization issues.

    **LarvalHabitatMultiplier** is read but not used at deserialization time.
    Both **LarvalHabitatMultiplier** and **x_Temporary_Larval_Habitat** are applied when a
    habitat is created at the beginning of a simulation. When the habitat is serialized, it is
    stored with the results of these multipliers already applied.

    - If **Serialization_Mask_Node_Read** = 0, both **LarvalHabitatMultiplier** and
      **x_Temporary_Larval_Habitat** are ignored and the values from the serialized file are
      used as-is.
    - If **Serialization_Mask_Node_Read** = 16, new habitats are created from configuration
      parameters and the serialized habitat data is ignored. The **x_Temporary_Larval_Habitat**
      setting is used to adjust the new habitat, but it is a known issue that
      **LarvalHabitatMultiplier** is not also applied in this case.

### Can be changed


* **Altitude**
* **BirthRate**
* **Latitude**
* **Longitude**
* **NodePropertyValues**
* **Airport**
* **Region**
* **Seaport**


## IndividualAttributes


### Cannot be changed


* **AgeDistributionFlag**, **AgeDistribution1**, **AgeDistribution2**
* **SusceptibilityDistributionFlag**, **SusceptibilityDistribution1**, **SusceptibilityDistribution2**
* **PrevalenceDistributionFlag**, **PrevalenceDistribution1**, **PrevalenceDistribution2**


### Can be changed (with dependencies)


* **FertilityDistribution**: If **Birth_Rate_Dependence** was serialized with the value INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR, then you can change this distribution.
* **MigrationHeterogeneityDistributionFlag**, **MigrationHeterogeneityDistribution1**, **MigrationHeterogeneityDistribution2**: These values can be changed if **Enable_Migration_Heterogeneity** is set to 1 in config.json.
* **MortalityDistributionFlag**, **MortalityDistribution1**, **MortalityDistribution2**: These can be changed if **Enable_Natural_Mortality** was serialized as true/on. Which distribution is used depends on the serialized value of **Death_Rate_Dependence**.
* **RiskDistributionFlag**, **RiskDistribution1**, **RiskDistribution2**: These can be changed if **Enable_Demographics_Risk** was serialized as true/on, however the new parameters will only be applied to newborns. Existing individuals will retain their risk values from the serialized file.
* **InnateImmuneDistributionFlag**, **InnateImmuneDistribution1**, **InnateImmuneDistribution2**: These can be changed if **Innate_Immune_Variation_Type** was serialized as a value other than NONE, however the new parameters will only be applied to newborns. Existing individuals will retain their innate immune values from the serialized file.


## IndividualProperties


### Cannot be changed


* **Remove value from existing key**: You cannot remove an existing value from a key if the serialized population contains individuals with this value.

### Can be changed


* **Add new value to existing key**
* **Change Initial_Distribution**: You can change the **Initial_Distribution** to change the likelihood that a newborn will have a specific **IndividualProperties** value. It will not change how **IndividualProperties** values are distributed in the serialized population.


### Not recommended


* **Add/Remove IP/Key**: It is best practice to not add or remove **IndividualProperties** keys unless you also update the serialized file. However, if you remove a value and do not reference it in the simulation running from the serialized file, the simulation may run without errors. If you add values and don't add them to individuals in the serialized file, you should not reference them until all individuals from the serialized file have died.
