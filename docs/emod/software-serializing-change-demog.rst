===========================================
Changing serialized demographics parameters
===========================================

.. need to edit, fix headers, etc

Not every parameter can be changed after the creation of serialized files. The following overview
is intended as high-level guidance for what changes can and cannot be made.

Population-level parameters
===========================

Cannot be changed
-----------------

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


Can be changed
--------------
* **Enable_Disease_Mortality**


NodeAttributes
==============

Cannot be changed
-----------------

* **InitialPopulation**
* **InitialVectorsPerSpecies**
* **LarvalHabitatMultiplier** This is read but not used.  Both the **LarvalHabitatMultiplier** and the **x_Temporary_Larval_Habitat** are applied when a habitat is created at the beginning of a simulation.  When the habitat is serialized, it is stored with the results of these multipliers.  If you are reading from a serialized file and **Serialization_Mask_Node_Read** = 0, then you ignore both **LarvalHabitatMultiplier** and **x_Temporary_Larval_Habitat** settings and just use what was stored in the serialized file.  If **Serialization_Mask_Node_Read** = 16, then we create new habitats and ignore what is in the serialized file.  We do use the **x_Temporary_Larval_Habitat** setting to adjust the habitat, but it is a known issue that we don't also use **LarvalHabitatMultiplier**.

Can be changed
--------------

* **Altitude**
* **BirthRate**
* **Latitude**
* **Longitude**
* **NodePropertyValues**
* **Airport**
* **Region**
* **Seaport**


IndividualAttributes
====================

Cannot be changed
-----------------

* **AgeDistributionFlag**, **AgeDistribution1**, **AgeDistribution2**
* **SusceptibilityDistributionFlag**, **SusceptibilityDistribution1**, **SusceptibilityDistribution2**
* **PrevalenceDistributionFlag**, **PrevalenceDistribution1**, **PrevalenceDistribution2**


Can be changed (with dependencies)
----------------------------------

* **FertilityDistribution**: If **Birth_Rate_Dependence** was serialized with the value INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR, then you can change this distribution.
* **MigrationHeterogeneityDistributionFlag**, **MigrationHeterogeneityDistribution1**, **MigrationHeterogeneityDistribution2**: These values can be can be changed if **Enable_Migration_Heterogeneity** is set to 1 in config.json.
* **MortalityDistributionFlag, MortalityDistribution1, MortalityDistribution2**: These can be changed if **Enable_Natural_Mortality** was serialized as true/on.  Which distribution is used depends on the serialized value of **Death_Rate_Dependence**.
* **RiskDistributionFlag, RiskDistribution1, RiskDistribution2**: These can be changed if **Enable_Demographics_Risk** was serialized as true/on, however - the new parameters will only be applied to newborns.  Existing individuals will retain their risk values from the serialized file.


IndividualProperties
====================

Cannot be changed
-----------------

* **Remove value from existing key**  You cannot remove an existing value from a key if the population that has been serialized has this value.

Can be changed
--------------

* **Add new value to existing key**
* **Change Initial_Distribution** You can change the **Initial_Distribution** if you just want to change the likelihood that a newborn will have a specific **IndividualProperties** value.  It will not impact the how the **IndividualProperties** values are distributed in the population that is serialized.


Special cases
-------------

* **Add/Remove IP/Key** Some may be changed, but it is not recommended.  It is best practices to not add or remove **IndividualProperties** values unless you also update the serialized file.  However, if you remove a value and do not ever reference it in the simulation that is running from the serialized file, the simulation may run without errors.  If you add values and don't add them to the people in the serialized file, then you should not reference it until all the people that came from the serialized file have died.





