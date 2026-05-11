# Waning effect classes


The following classes are nested within interventions (both individual-level and node-level) to
indicate how their efficacy wanes over time. They can be used with several parameters including
**Blocking_Config**, **Killing_Config**, and **Waning_Config**. Note that waning effect parameters
do not control the overall duration of an intervention and are not assigned probabilistically.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
See the example below that uses a mix of different waning effect classes and the tables below that
describe all parameters that can be used with each waning effect class.

```json
{
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
                "Number_Repetitions": -1,
                "Timesteps_Between_Repetitions": 60,
                "Intervention_Config": {
                    "class": "SimpleBednet",
                    "Cost_To_Consumer": 5,
                    "Usage_Config": {
                        "class": "WaningEffectRandomBox",
                        "Initial_Effect": 1.0,
                        "Expected_Discard_Time": 60
                    },
                    "Blocking_Config": {
                        "class": "WaningEffectExponential",
                        "Decay_Time_Constant": 150,
                        "Initial_Effect": 0.5
                    },
                    "Killing_Config": {
                        "class": "WaningEffectConstant",
                        "Initial_Effect": 1.0
                    }
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```

## WaningEffectBox


The efficacy is held at a constant rate until it drops to zero after the user-defined duration.

```json
{
    "Intervention_Config": {
        "Blocking_Config": {
            "Box_Duration": 3650,
            "Initial_Effect": 0,
            "class": "WaningEffectBox"
        }
    }
}
```

{{ read_csv("csv/campaign-waningeffectbox.csv", keep_default_na=False) }}

## WaningEffectBoxExponential


The initial efficacy is held for a specified duration, then the efficacy decays at an exponential rate where the current effect is equal to **Initial_Effect** - dt/**Decay_Time_Constant**.

```json
{
    "Intervention_Config": {
        "Reduction_Config": {
            "class": "WaningEffectBoxExponential",
            "Box_Duration": 100,
            "Decay_Time_Constant": 150,
            "Initial_Effect": 0.1
        }
    }
}
```

{{ read_csv("csv/campaign-waningeffectboxexponential.csv", keep_default_na=False) }}

## WaningEffectCombo


The **WaningEffectCombo** class is used within individual-level interventions and allows for specifiying a list of effects when the intervention only has one **WaningEffect** defined. These effects can be added or multiplied.

```json
{
    "class": "WaningEffectCombo",
    "Add_Effects": 1,
    "Expires_When_All_Expire": 0,
    "Effect_List": [
        {
            "class": "WaningEffectMapLinear",
            "Initial_Effect": 1.0,
            "Expire_At_Durability_Map_End": 1,
            "Durability_Map": {
                "Times": [0.0, 1.0, 2.0],
                "Values": [0.2, 0.4, 0.6]
            }
        },
        {
            "class": "WaningEffectBox",
            "Initial_Effect": 0.5,
            "Box_Duration": 5.0
        }
    ]
}
```

{{ read_csv("csv/campaign-waningeffectcombo.csv", keep_default_na=False) }}

## WaningEffectConstant


The efficacy is held at a constant rate.

```json
{
    "Intervention_Config": {
        "class": "SimpleBednet",
        "Killing_Config": {
            "class": "WaningEffectConstant",
            "Initial_Effect": 1.0
        }
    }
}
```

{{ read_csv("csv/campaign-waningeffectconstant.csv", keep_default_na=False) }}

## WaningEffectExponential


The efficacy decays at an exponential rate where the current effect is equal to **Initial_Effect** - dt/**Decay_Time_Constant**.

```json
{
    "Intervention_Config": {
        "class": "SimpleBednet",
        "Blocking_Config": {
            "class": "WaningEffectExponential",
            "Decay_Time_Constant": 150,
            "Initial_Effect": 0.5
        }
    }
}
```

{{ read_csv("csv/campaign-waningeffectexponential.csv", keep_default_na=False) }}

## WaningEffectMapCount


The **WaningEffectMapCount** class assigns a probability to a particular update of the effect. This
typically used with [AdherentDrug](parameter-campaign-individual-adherentdrug.md) so one can assign a
probability that a person takes a particular dose. The **Times** value should be integers starting
from 1 and increasing.

If the example below were used in **AdherentDrug**, the probability that the person took the first
dose would be 40%, 30% for the second dose, and so on.

```json
{
    "Intervention_Config": {
        "class": "AdherentDrug",
        "Waning_Config": {
            "class": "WaningEffectMapCount",
            "Initial_Effect": 1.0,
            "Durability_Map": {
                "Times": [1.0, 2.0, 3.0, 4.0],
                "Values": [0.4, 0.3, 0.2, 0.1]
            }
        }
    }
}
```

{{ read_csv("csv/campaign-waningeffectmapcount.csv", keep_default_na=False) }}

## WaningEffectMapLinear


The efficacy decays based on the time since the start of the intervention. This change is defined
by a map of time to efficacy values in which the time between time/value points is linearly
interpolated. When the time since start reaches the end of the times in the map, the last value will
be used unless the intervention expires. If the time since start is less than the first value in the
map, the efficacy will be zero. This can be used to define the shape of a curve whose magnitude is
defined by the **Initial_Effect** multiplier.

```json
{
    "Intervention_Config": {
        "class": "ControlledVaccine",
        "Waning_Config": {
            "class": "WaningEffectMapLinear",
            "Reference_Timer": 0,
            "Initial_Effect": 1.0,
            "Expire_At_Durability_Map_End": 1,
            "Durability_Map": {
                "Times": [0, 120, 240, 360],
                "Values": [0.7, 0.8, 1.0, 0.0]
            }
        }
    }
}
```

{{ read_csv("csv/campaign-waningeffectmaplinear.csv", keep_default_na=False) }}

## WaningEffectMapLinearAge


Similar to **WaningEffectMapLinear**, except that the efficacy decays based on the age of the
individual who owns the intervention instead of the time since the start of the intervention.

```json
{
    "class": "WaningEffectMapLinearAge",
    "Initial_Effect": 1,
    "Durability_Map": {
        "Times": [1, 2, 5, 7],
        "Values": [1, 0.75, 0.5, 0.25]
    }
}
```

{{ read_csv("csv/campaign-waningeffectmaplinearage.csv", keep_default_na=False) }}

## WaningEffectMapLinearSeasonal


Similar to **WaningEffectMapLinear**, except that the map will repeat itself every 365 days. That
is, the time since start will reset to zero once it reaches 365.  This allows you to simulate
seasonal effects.

```json
{
    "Intervention_Config": {
        "class": "UsageDependentBednet",
        "Usage_Config_List": [
            {
                "class": "WaningEffectMapLinearSeasonal",
                "Initial_Effect": 1.0,
                "Durability_Map": {
                    "Times": [0.0, 20.0, 21.0, 30.0, 31.0, 365.0],
                    "Values": [1.0, 1.0, 0.0, 0.0, 1.0, 1.0]
                }
            }
        ]
    }
}
```

{{ read_csv("csv/campaign-waningeffectmaplinearseasonal.csv", keep_default_na=False) }}

## WaningEffectMapPiecewise


Similar to **WaningEffectMapLinear**, except that the data is assumed to be constant between
time/value points (no interpolation). If the time since start falls between two points, the efficacy
of the earlier time point is used.

```json
{
    "Intervention_Config": {
        "class": "SimpleVaccine",
        "Waning_Config": {
            "class": "WaningEffectMapPiecewise",
            "Initial_Effect": 1.0,
            "Reference_Timer": 0,
            "Expire_At_Durability_Map_End": 0,
            "Durability_Map": {
                "Times": [10, 30, 50],
                "Values": [0.9, 0.1, 0.6]
            }
        }
    }
}
```

{{ read_csv("csv/campaign-waningeffectmappiecewise.csv", keep_default_na=False) }}

## WaningEffectRandomBox


The efficacy is held at a constant rate until it drops to zero after a user-defined duration. This
duration is randomly selected from an exponential distribution where **Expected_Discard_Time** is
the mean.

```json
{
    "Intervention_Config": {
        "class": "SimpleBednet",
        "Cost_To_Consumer": 5,
        "Usage_Config": {
            "class": "WaningEffectRandomBox",
            "Initial_Effect": 1.0,
            "Expected_Discard_Time": 60
        }
    }
}
```

{{ read_csv("csv/campaign-waningeffectrandombox.csv", keep_default_na=False) }}
