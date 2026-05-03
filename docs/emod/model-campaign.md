# Creating campaigns


You define the initial disease outbreak and interventions used to combat it for a simulation
through a JSON-formatted campaign file, typically called campaign.json. It is hierarchically
organized into logical groups of parameters that can have multiple levels of nesting. It contains
an **Events** array of campaign events, each of which contains a JSON object describing the event
coordinator, which in turn contains a nested JSON object describing the intervention. Campaign
events determine *when* and *where* an intervention is distributed, event coordinators determine
*who* receives the intervention, and interventions determine *what* is actually distributed. For
example, a vaccination or diagnostic test.

Interventions can be targeted to particular nodes or individuals, based on age or other
characteristics. Additionally, you can structure campaigns to guide individuals through complex
health care systems. For example, administering a second-line treatment only after the preferred
treatment has proven ineffective for an individual.

For some interventions, there can be a very complex hierarchical structure, including recursion.
This framework enables rigorous testing of possible control strategies to determine which events or
combination of events will best aid in the elimination of disease for specific geographic locations.

## Multiple interventions


When creating multiple interventions, either of the same type or different types, they will
generally be distributed independently without regard to whether a person has already received another
intervention.

For example, say you create two **SimpleBednet** interventions and both interventions
have **Demographic_Coverage** set to 0.5 (50% demographic coverage). This value is the probability
that each individual in the target population will receive the intervention. It does not guarantee
that the exact fraction of the target population set by **Demographic_Coverage** receives the
intervention.

By default, each individual in the simulation will have a 50% chance of receiving a bednet in both
of the distributions and the two distributions will be independent. Therefore, each individual has a
75% chance of receiving at least one bednet. Please note, individuals can only have one bednet at a time,
and receiving a second bednet will replace the first one, which is not necessarily true for other interventions.

![howto-multiple.png](../images/general/howto-multiple.png)

## Campaign file overview


For the interventions to take place, the campaign file must be in the same directory as the
*configuration file* and you must set the configuration parameters **Enable_Interventions** to
1 and **Campaign_Filename** to the name of the campaign file. When you run a simulation, you must
have a single campaign file.

Although you can create campaign files entirely from scratch, it is easier to use the provided Python
packages to create the JSON files.

The following is an example of campaign file that has two events (SimpleVaccine and Outbreak) that
occur in all nodes at day 1 and day 30, respectively. Each event contains an event coordinator that
describes who receives the intervention (everyone, with the vaccine repeated three times) and the
configuration for the intervention itself. Note that the nested JSON elements have been organized to
best illustrate their hierarchy, but that many files in the Regression directory list the parameters
within the objects differently. See [parameter-campaign](parameter-campaign.md) for more information on the structure
of these files and available parameters for this simulation type.

```json
{
    "Campaign_Name": "Vaccine",
    "Default_Campaign_Path": "defaults/generic-default-campaign.json",
    "Use_Defaults": 1,
    "Events":
    [
        {
            "VACCINATION": "BEGIN",
            "Event_Name": "SimpleVaccine",
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Day": 1,
            "class": "CampaignEvent",
            "Event_Coordinator_Config": {
                "Demographic_Coverage": 0.5,
                "Number_Repetitions": 3,
                "Target_Demographic": "Everyone",
                "Timesteps_Between_Repetitions": 7,
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "Cost_To_Consumer": 10,
                    "Waning_Config": {
                        "class": "WaningEffectMapLinear",
                        "Initial_Effect" : 1.0,
                        "Expire_At_Durability_Map_End" : 0,
                        "Durability_Map" : {
                            "Times"  : [   0,  30,  60,  90, 120 ],
                            "Values" : [ 0.9, 0.3, 0.9, 0.6, 1.0 ]
                        }
                    },
                    "Vaccine_Take": 1,
                    "Vaccine_Type": "AcquisitionBlocking",
                    "class": "SimpleVaccine"
                }
            },
            "VACCINATION": "END"
        },
        {
            "Event_Name": "Outbreak",
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Day": 30,
            "class": "CampaignEvent",
            "Event_Coordinator_Config": {
                "Demographic_Coverage": 0.001,
                "Target_Demographic": "Everyone",
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "Antigen": 0,
                    "Genome": 0,
                    "Outbreak_Source": "PrevalenceIncrease",
                    "class": "OutbreakIndividual"
                }
            }
        }
    ]
}
```



For a complete list of campaign parameters that are available to use with this simulation type and
more detail about the campaign file structure, see [parameter-campaign](parameter-campaign.md). For more information about
JSON, see [parameter-overview](parameter-overview.md).


