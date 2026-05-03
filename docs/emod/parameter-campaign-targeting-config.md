# Targeting_Config classes


The following classes can be used to enhance the selection of people when distributing interventions.
Most event coordinators and node-level interventions that distribute interventions to people have a
parameter called **Targeting_Config**.  This allows you to not only target individuals based on their
gender, age, and **IndividualProperties** (See [demo-properties](#demo-properties) parameters for more information),
but also on things such as whether or not they have a particular intervention or are in a relationship.

{% include "../reuse/warning-case.txt" %}

Below is a simple example where we want to distribute a vaccine to 20% of the people that do not
already have the vaccine on the 100th day of the simulation.

```json
{
    "class": "CampaignEvent",
    "Start_Day": 100,
    "Nodeset_Config": {
        "class": "NodeSetAll"
    },
    "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Target_Demographic": "Everyone",
        "Demographic_Coverage": 0.2,
        "Targeting_Config": {
            "class": "HasIntervention",
            "Is_Equal_To": 0,
            "Intervention_Name": "MyVaccine"
        },
        "Intervention_Config": {
            "class": "SimpleVaccine",
            "Intervention_Name" : "MyVaccine",
            "Cost_To_Consumer": 1,
            "Vaccine_Take": 1,
            "Vaccine_Type": "AcquisitionBlocking",
            "Waning_Config": {
                "class": "WaningEffectConstant",
                "Initial_Effect" : 1.0
            }
        }
    }
}
```

Below is a slightly more complicated example where we want to distribute a diagnostic to people
that are either high risk or have not been vaccinated.

```json
{
    "class": "CampaignEvent",
    "Start_Day": 100,
    "Nodeset_Config": {
        "class": "NodeSetAll"
    },
    "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Target_Demographic": "Everyone",
        "Demographic_Coverage": 0.2,
        "Targeting_Config": {
            "class" : "TargetingLogic",
            "Logic" : [
                [
                    {
                        "class": "HasIntervention",
                        "Is_Equal_To": 0,
                        "Intervention_Name": "MyVaccine"
                    }
                ],
                [
                    {
                        "class": "HasIP",
                        "Is_Equal_To": 1,
                        "IP_Key_Value": "Risk:HIGH"
                    }
                ]
            ]
        },
        "Intervention_Config": {
            "class": "SimpleDiagnostic",
            "Treatment_Fraction": 1.0,
            "Base_Sensitivity": 1.0,
            "Base_Specificity": 1.0,
            "Event_Or_Config": "Event",
            "Positive_Diagnosis_Event": "TestedPositive"
        }
    }
}
```

## HasIntervention


This determines whether or not the individual has an intervention with the given name.  This will only
work for interventions that persist like **SimpleVaccine** and **DelayedIntervention**.  It will not work for
interventions like **BroadcastEvent** since it does not persist.

### Configuration


```
**Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
**Intervention_Name**, string, NA, NA, """""", "The name of the intervention the person should have.  This cannot be an empty string but should be either the name of the class or the name given to the intervention of interest using the parameter Intervention_Name.  EMOD does not verify that this name exists."
```

### Example


Select the person if they do NOT have the MyVaccine intervention.

```json
"Targeting_Config": {
    "class": "HasIntervention",
    "Is_Equal_To": 0,
    "Intervention_Name": "MyVaccine"
}
```

## HasIP


This determines if the person has a particular value of a particular **IndividualProperties** (IP).
This is especially needed when determining if a partner has a particular IP (see **HasRelationship**).

### Configuration


```
**IP_Key_Value**, string, NA, NA, """""", "An **IndividualProperties** Key:Value pair where the key/property name and one of its values is separated by a colon (':')."
**Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
```

### Example


Select the person if their **Risk** property is HIGH.

```json
"Targeting_Config": {
    "class": "HasIP",
    "Is_Equal_To": 1,
    "IP_Key_Value": "Risk:HIGH"
}
```

## TargetingLogic


In some cases, the you need to logically combine multiple restrictions.  In these situations,
you should use the **TargetingLogic** class where you can "and" and "or" the different questions.

NOTE: Each element is independent and is being asked of the individual in question.  For questions
that are about a partner of the individual, all of the qualifiers for that partner must be in the
element.  This will ensure that there is one partner that has all of the qualifications.  Otherwise,
you could have a situation where one partner satisfies one qualification and another partner
satisfies a different one, but no partner has all of the qualifications.


### Configuration


```
**Logic**, 2D array of JSON objects, NA, NA, [], "This is a two-dimensional array of JSON objects.  The elements of the inner array will be AND'd together while the arrays themselves will be OR'd.  This is similar to **Property_Restrictions_Within_Node**.  This array and the inner arrays cannot be empty."
```

### Example

Select the person if they do not have the MyVaccine intervention OR do not have their **Risk** property set to HIGH.
Notice that **Logic** 2x1 where the first dimention contains two arrays with one JSON object.  These two
arrays are OR'd together.

```json
"Targeting_Config": {
    "class" : "TargetingLogic",
    "Logic" : [
        [
            {
                "class": "HasIntervention",
                "Is_Equal_To": 0,
                "Intervention_Name": "MyVaccine"
            }
        ],
        [
            {
                "class": "HasIP",
                "Is_Equal_To": 0,
                "IP_Key_Value": "Risk:HIGH"
            }
        ]
    ]
}
```

Select the person if they do not have the MyVaccine intervention AND do not have their **Risk** property set to HIGH.
Notice that **Logic** is 1x2 where the first dimension contains a single array with two JSON objects.  These two
objects are AND'd together.

```json
"Targeting_Config": {
    "class" : "TargetingLogic",
    "Logic" : [
        [
            {
                "class": "HasIntervention",
                "Is_Equal_To": 0,
                "Intervention_Name": "MyVaccine"
            },
            {
                "class": "HasIP",
                "Is_Equal_To": 0,
                "IP_Key_Value": "Risk:HIGH"
            }
        ]
    ]
}
```
