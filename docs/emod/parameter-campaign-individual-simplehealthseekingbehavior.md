# SimpleHealthSeekingBehavior


The **SimpleHealthSeekingBehavior** intervention class models the time delay that typically occurs
between when an individual experiences onset of symptoms and when they seek help from a health care
provider. Several factors may contribute to such delays including accessibility, cost, and trust in
the health care system. This intervention models this time delay as an exponential process; at every
time step, the model draws randomly to determine if the individual will receive the specified
intervention. As an example, this intervention can be nested in a **NodeLevelHealthTriggeredIV** so
that when an individual is infected, he or she receives a **SimpleHealthSeekingBehavior**,
representing that the individual will now seek care. The individual subsequently seeks care with an
exponentially distributed delay and ultimately receives the specified intervention.

{% include "../reuse/warning-case.txt" %}

{% include "../reuse/campaign-example-intro.txt" %}

{{ read_csv("csv/campaign-simplehealthseekingbehavior.csv") }}

```json
{
     "Use_Defaults": 1,
     "Events": [{
          "class": "CampaignEvent",
          "Event_Name": "Drugs after TB activation",
          "Nodeset_Config": {
               "class": "NodeSetAll"
          },
          "Start_Day": 9125,
          "Event_Coordinator_Config": {
               "class": "StandardInterventionDistributionEventCoordinator",
               "Number_Repetitions": 1,
               "Target_Demographic": "Everyone",
               "Demographic_Coverage": 1,
               "Intervention_Config": {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Trigger_Condition_List": ["NewInfectionEvent"],
                    "Actual_IndividualIntervention_Config": {
                         "class": "SimpleHealthSeekingBehavior",
                         "Event_Or_Config": "Config",
                         "Tendency": 0.0015,
                         "Actual_IndividualIntervention_Config": {
                              "class": "AntiTBDrug",
                              "Cost_To_Consumer": 90,
                              "Drug_Type": "FirstLineCombo",
                              "Durability_Profile": "FIXED_DURATION_CONSTANT_EFFECT",
                              "Primary_Decay_Time_Constant": 180,
                              "Remaining_Doses": 1,
                              "Secondary_Decay_Time_Constant": 0
                         }
                    }
               }
          }
     }]
}
```
