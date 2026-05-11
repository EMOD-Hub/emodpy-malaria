# Cascade of care


Some diseases, such as HIV, have a complex sequential cascade of care that individuals must
navigate. For example, going from testing to diagnosis, receiving medical counseling, taking
antiretroviral therapy, and achieving viral suppression. Other life events, such as pregnancy,
migration, relationship changes, or diagnostic criteria may trigger different medical interventions.

Health care in EMOD can be applied to individuals, such as through a vaccination campaign, or be
sought out by various triggering events including birth, pregnancy, or symptoms. A potential problem
created by this structure is that an individual could end up in care multiple times. For example, an
individual might have an antenatal care (ANC) visit and, in the same time step, seek health care for
AIDS symptoms, both leading to HIV testing and staging.

To avoid this situation, you can configure interventions using the InterventionStatus individual
property in the demographics file (see [NodeProperties and IndividualProperties](parameter-demographics.md:nodeproperties-and-individualproperties) for more information). In the
demographics file, create as many property values as necessary to describe the care cascade. For
example, undiagnosed, positive diagnosis, on therapy, lost to care, etc.

In the campaign file, set up your *event coordinator* as you typically would, using
**Target_Demographic**, **Property_Restrictions_Within_Node**, and other available parameters to
target the desired individuals. See [Targeted interventions](model-targeted-interventions.md) for more information on
targeting interventions and [Event coordinators](parameter-campaign-event-coordinators.md) for all available
event coordinators.

Then, in the intervention itself, you can add any properties that should prevent someone who would
otherwise qualify for the intervention from receiving it. For example, someone who has already
received a positive diagnosis would be prevented from receiving a diagnostic test if they sought out
medical care for symptoms. You can also add the new property that should be assigned to the
individual if they receive the intervention.

The following example shows a simplified example with two interventions, a diagnostic event and
distribution of medication. The demographics file defines intervention status values for having
tested positive and for being on medication.


```json
{
    "Use_Defaults": 1,
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "Everyone",
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "class": "SimpleDiagnostic",
                    "Disqualifying_Properties": [
                        "InterventionStatus:OnMeds"
                    ],
                    "New_Property_Value": "InterventionStatus:TestPositive",
                    "Base_Sensitivity": 1.0,
                    "Base_Specificity": 1.0,
                    "Cost_To_Consumer": 0,
                    "Days_To_Diagnosis": 5.0,
                    "Dont_Allow_Duplicates": 0,
                    "Event_Or_Config": "Event",
                    "Positive_Diagnosis_Event": "NewInfectionEvent",
                    "Intervention_Name": "Diagnostic_Sample",
                    "Treatment_Fraction": 1.0
                }
            }
        },
        {
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Trigger_Condition_List": [
                        "NewInfectionEvent"
                    ],
                    "Disqualifying_Properties": [
                        "InterventionStatus:OnMeds"
                    ],
                    "New_Property_Value": "InterventionStatus:OnMeds",
                    "Demographic_Coverage": 1.0,
                    "Actual_IndividualIntervention_Config": {
                        "class": "ARTBasic",
                        "Viral_Suppression": 1,
                        "Days_To_Achieve_Viral_Suppression": 1000000
                    }
                }
            }
        }
    ]
}
```
