# DelayedIntervention


The **DelayedIntervention** intervention class introduces a delay between when the intervention is
distributed to the individual and when they receive the actual intervention. This is due to the
frequent occurrences of time delays as individuals seek care and receive treatment. This
intervention allows configuration of the distribution type for the delay as well as the fraction of
the population that receives the specified intervention.

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

{{ read_csv("csv/campaign-delayedintervention.csv") }}

```json
{
  "Campaign_Name": "Initial Seeding",
  "Events": [
    {
      "Event_Name": "Outbreak",
      "class": "CampaignEvent",
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Start_Day": 1,
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Target_Demographic": "Everyone",
        "Demographic_Coverage": 1.0,
        "Intervention_Config": {
          "class": "DelayedIntervention",
          "Delay_Period_Distribution": "CONSTANT_DISTRIBUTION",
          "Delay_Period_Constant": 25,
          "Actual_IndividualIntervention_Configs": [
            {
              "Outbreak_Source": "PrevalenceIncrease",
              "class": "OutbreakIndividual"
            }
          ]
        }
      }
    },
    {
      "Event_Name": "Outbreak",
      "class": "CampaignEvent",
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Start_Day": 50,
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Target_Demographic": "Everyone",
        "Demographic_Coverage": 1.0,
        "Intervention_Config": {
          "class": "DelayedIntervention",
          "Delay_Period_Distribution": "UNIFORM_DISTRIBUTION",
          "Delay_Period_Min": 15,
          "Delay_Period_Max": 30,
          "Actual_IndividualIntervention_Configs": [
            {
              "Outbreak_Source": "PrevalenceIncrease",
              "class": "OutbreakIndividual"
            }
          ]
        }
      }
    }
  ],
  "Use_Defaults": 1
}
```
