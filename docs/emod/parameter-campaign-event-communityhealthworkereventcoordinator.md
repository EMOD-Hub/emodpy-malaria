# CommunityHealthWorkerEventCoordinator


The **CommunityHealthWorkerEventCoordinator** coordinator class is used to model a health care worker's ability
to distribute interventions to the nodes and individual in their coverage area. This coordinator
distributes a limited number of interventions per day, and can create a backlog of individuals or
nodes requiring the intervention. For example, individual-level interventions could be distribution
of drugs  and node-level interventions could be spraying houses with insecticide.

.. note::

    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    |EMOD_s| does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with |EMOD_s| will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not |EMOD_s| parameter names will be ignored by the
    model.

The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv("csv/campaign-communityhealthworkereventcoordinator.csv") }}

```json
{
  "Events": [
    {
      "class": "CampaignEvent",
      "Start_Day": 1,
      "Nodeset_Config": {
        "class": "NodeSetNodeList",
        "Node_List": [
          2,
          3,
          4
        ]
      },
      "Event_Coordinator_Config": {
        "class": "CommunityHealthWorkerEventCoordinator",
        "Duration": 400,
        "Distribution_Rate": 25,
        "Waiting_Period": 10,
        "Days_Between_Shipments": 25,
        "Amount_In_Shipment": 250,
        "Max_Stock": 1000,
        "Initial_Amount_Distribution": "CONSTANT_DISTRIBUTION",
        "Initial_Amount_Constant": 500,
        "Target_Demographic": "Everyone",
        "Demographic_Coverage": 1.0,
        "Property_Restrictions": [],
        "Target_Residents_Only": 0,
        "Trigger_Condition_List": [
          "NewInfectionEvent"
        ],
        "Intervention_Config": {
          "class": "SimpleVaccine",
          "Cost_To_Consumer": 10.0,
          "Vaccine_Take": 1,
          "Vaccine_Type": "AcquisitionBlocking",
          "Waning_Config": {
            "class": "WaningEffectBox",
            "Initial_Effect": 1,
            "Box_Duration": 200
          }
        }
      }
    }
  ]
}
```
