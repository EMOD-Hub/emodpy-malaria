# Configuration file


The primary means of configuring the disease simulation is the *configuration file*. This
required file is a *JSON (JavaScript Object Notation)* formatted file that is typically named
config.json. The configuration file controls many different aspects of the simulation. For example,

* The names of the *campaign file* and other *input files* to use
* How to use additional demographics, climate, and migration data (such as enabling features or scaling values)
* General disease attributes such as infectivity, immunity, mortality, and so on
* Attributes specific to the disease type being modeled, such as infectivity and mortality
* The reports to output from the simulation


Although you can create configuration files entirely from scratch, it is often easier to start from
an existing configuration file and modify it to meet your needs or use the provided Python packages
to create configuration files.


For a complete list of configuration parameters that are available to use with this simulation type,
see [parameter-configuration](parameter-configuration.md). For more information about JSON, see [parameter-overview](parameter-overview.md).


## Configuration files


A configuration file is a single-depth JSON file with configuration parameters
listed alphabetically. This is the configuration file format required by EMOD.

However, there may be some hierarchical elements in the flattened version. For example,
**Vector_Species_Params** and **Malaria_Drug_Params** have nested JSON objects.

Below is an example of a flattened configuration file:

```json
{
  "parameters": {
    "Age_Initialization_Distribution_Type": "DISTRIBUTION_SIMPLE",
    "Base_Infectivity": 0.3,
    "Climate_Model": "CLIMATE_OFF",
    "Config_Name": "1_Generic_MinimalConfig",
    "Custom_Reports_Filename": "",
    "Default_Geography_Initial_Node_Population": 100,
    "Default_Geography_Torus_Size": 3,
    "Enable_Default_Reporting": 1,
    "Enable_Demographics_Builtin": 1,
    "Enable_Demographics_Reporting": 0,
    "Enable_Demographics_Risk": 0,
    "Enable_Disease_Mortality": 0,
    "Enable_Heterogeneous_Intranode_Transmission": 0,
    "Enable_Immunity": 0,
    "Enable_Initial_Prevalence": 0,
    "Enable_Initial_Susceptibility_Distribution": 0,
    "Enable_Interventions": 0,
    "Enable_Maternal_Infection_Transmission": 0,
    "Enable_Maternal_Protection": 0,
    "Enable_Property_Output": 0,
    "Enable_Skipping": 0,
    "Enable_Spatial_Output": 0,
    "Enable_Superinfection": 0,
    "Enable_Susceptibility_Scaling": 0,
    "Enable_Vital_Dynamics": 0,
    "Geography": "NONE",
    "Incubation_Period_Constant": 3,
    "Incubation_Period_Distribution": "CONSTANT_DISTRIBUTION",
    "Individual_Sampling_Type": "TRACK_ALL",
    "Infection_Updates_Per_Timestep": 1,
    "Infectious_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
    "Infectious_Period_Exponential": 7,    
    "Listed_Events": [],
    "Load_Balance_Filename": "",
    "Maternal_Infection_Transmission_Probability": 0,
    "Migration_Model": "NO_MIGRATION",
    "Node_Grid_Size": 0.042,
    "Number_Basestrains": 1,
    "Number_Substrains": 1,
    "Population_Density_Infectivity_Correction": "CONSTANT_INFECTIVITY",
    "Population_Scale_Type": "USE_INPUT_FILE",
    "Report_Event_Recorder": 0,
    "Run_Number": 1,
    "Simulation_Duration": 180,
    "Simulation_Timestep": 1,
    "Simulation_Type": "GENERIC_SIM",
    "Start_Time": 0,
    "Symptomatic_Infectious_Offset": 0
  }
}
```
