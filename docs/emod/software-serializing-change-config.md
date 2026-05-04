# Changing serialized configuration parameters


Not every parameter can be changed after the creation of serialized files. The following overview
is intended as high-level guidance for what changes can and cannot be made.


## Simulation parameters


### Cannot be changed


* **Simulation_Type** The type of simulation determines the parameters and the types of objects in the file.
* **Enable_Demographics_Builtin**
* **Default_Geography_Initial_Node_Population**
* **Default_Geography_Torus_Size**
* **Node_Grid_Size** This is not serialized; the value is loaded from the configuration file every time a simulation is created.
* **Enable_Interventions**
* **Campaign_Filename**
* **Load_Balance_Filename**  You must use the same number of cores that you used when you created the serialized file.  The nodes will be on the those same cores.
* **Malaria_Model**


### Can be changed


* **Simulation_Duration** This controls the number of days the simulation will run from the day it starts (when the executable begins executing).
* **Start_Time** It can be useful to set this parameter to the day that the file was serialized plus one timestep. For example, if you serialized the file on day 100 and your timestep was 5, setting Start_Time = 105 will make the appearance that the simulation started right where it left off.  It is also fine to have it start at 0.
* **Custom_Individual_Events**  You can easily add new events but must be careful when removing them. If an individual has a serialized intervention that emits the event that you delete, you should get an error de-serializing the file because the event is unknown.
* **Malaria_Drug_Params** These parameters are not serialized so they can be changed.  However, there are a few caveats:

    # If you have handed out drugs to people and the people have the drugs in them when you serialize, then you must have drugs in **Malaria_Drug_Params** with the same name.  When the people are de-serialized, the drug intervention will look for the drug parameters with the same name as when the person was serialized.
    # A person who had drugs when serialized will still be in that state when de-serialized.  The previous values created the person's current state; changing the parameters will not reverse the previous effects.
    # Given the person's state when serialized, the new parameters could cause weird effects depending on how the parameters are changed.  For example, if you shorten a delay significantly, the drug could suddenly have no remaining effect.

* **Serialized_Population_Reading_Type**
* **Serialized_Population_Writing_Type**
* **Serialized_Population_Path**
* **Serialized_Population_Filenames**
* **Enable_Random_Generator_From_Serialized_Population**


### Can be changed (but not recommended to change)


* **Simulation_Timestep** Usually not recommended, but you can change the duration of a single timestep. NOTE:  Malaria's timestep is fixed at one day.



## Individual parameters



### Can be changed


* **Enable_Aging** This parameters is not serialized and can be changed.  However, if it was enabled and you disable it, people will be frozen at whatever age they were during serialization.  Conversely, people will start aging when you enable it.  This could mean everyone is the same age.
* **Infection_Updates_Per_Timestep** This parameter is not serialized and can be changed.  However, it could impact some interventions like drugs.
* **Enable_Superinfection**
* **Max_Individual_Infections**
* **Age_Dependent_Biting_Risk_Type**
* **Newborn_Biting_Risk_Multiplier**


## Infection parameters



### Can be changed


* **Incubation_Period_Distribution** This parameter is not serialized and can be changed, including the extra parameters used in defining the distribution.
* **Infectious_Period_Distribution** This parameter is not serialized and can be changed, including the extra parameters used in defining the distribution.  (Note this parameter is not used in malaria simulations.)
* **Base_Infectivity** This parameter is not serialized and can be changed, including the extra parameters used in defining the distribution.  (Note this parameter is not used in malaria simulations.)
* **Malaria_Strain_Model** This parameter is not serialized and can be changed but it will only impact new infections.



Note that some of these parameters will impact infections that were serialized
immediately upon de-serialization while others will only impact new infections.

* **Antibody_IRBC_Kill_Rate**
* **Nonspecific_Antigenicity_Factor**
* **MSP1_Merozoite_Kill_Fraction**
* **Gametocyte_Stage_Survival_Rate**
* **Base_Gametocyte_Fraction_Male**
* **Base_Gametocyte_Production_Rate**
* **Antigen_Switch_Rate**
* **Merozoites_Per_Hepatocyte**
* **Merozoites_Per_Schizont**
* **RBC_Destruction_Multiplier**
* **Number_Of_Asexual_Cycles_Without_Gametocytes**


## Immunity


### Cannot be changed


When people are created, memory is allocated based on the value of these parameters.

* **Falciparum_MSP_Variants**
* **Falciparum_Nonspecific_Types**
* **Falciparum_PfEMP1_Variants**


### Can be changed


Note that people with existing infections when you de-serialize could have inconsistent clinical case
indications while adjusting to the new settings.

* **Clinical_Fever_Threshold_Low**
* **Clinical_Fever_Threshold_High**
* **Min_Days_Between_Clinical_Incidents**

Note that people with existing infections when you de-serialize could have inconsistent severe case
indications while adjusting to the new settings.

* **Anemia_Severe_Threshold**
* **Parasite_Severe_Threshold**
* **Fever_Severe_Threshold**
* **Anemia_Severe_Inverse_Width**
* **Parasite_Severe_Inverse_Width**
* **Fever_Severe_Inverse_Width**

Note that people with existing infections when you de-serialize could have inconsistent HRP2
behavior depending on how the parameters are set.

* **PfHRP2_Boost_Rate**
* **PfHRP2_Decay_Rate**

## Vectors


### Cannot be changed


* **Enable_Vector_Mortality**
* **Enable_Vector_Aging** There are objects created based on its value.
* **Vector_Sampling_Type** There are objects created based on its value.


### Can be changed


* **Insecticides** This not serialized so the value can be changed.  However, if you distributed an intervention that has an insecticide, removing it will cause an error.


### Special cases


* **x_Temporary_Larval_Habitat**  This parameter is used during initialization.  If you are de-serializing the habitats from the file, then this parameter is not used.  However, if you set **Serialization_Mask_Node_Read** to 16 so that you are not using the data in the file, the habitat is re-initialized and the parameter is used.  Please note that if all you do is set **Serialization_Mask_Node_Read** to 16, your results will be slightly different due to the re-initialization of the habitat.

* **Vector_Species_Params**

    * Cannot add/remove a species
    * Habitat - Cannot change Habitat parameters (but they may be masked).
    * Genes - Genes can be added but assume alleles in existing vectors are the first allele.  You can remove an gene if you remove all other references to it.  If an insecticide had resistance to the gene, you can change the insecticide so it is not referring to the gene.  However, you cannot remove an insecticide if it was used by an intervention that was serialized.
    * Alleles- alleles can be added but not removed.  You can replace the name of an allele.
    * Gene_To_Trait_Modifiers - These can be modified.  Just make sure that if you change genes or alleles that you update these as well.
    * Drivers - These can be modified.  Just make sure that if you change genes or alleles that you update these as well.
    * Other parameters - They can be modified but impact might take a generation of vectors.
