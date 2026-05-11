# MultiPackComboDrug


The **MultiPackComboDrug** intervention class is an individual-level intervention that explicitly
models which doses of anti-malarial pills are taken when. This intervention is similar to the
[AdherentDrug](parameter-campaign-individual-adherentdrug.md) class, but allows modeling pill packs that involve
multiple drugs with different dosing per drug.


!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv("csv/campaign-multipackcombodrug.csv", keep_default_na=False) }}

```json
{
    "class": "CampaignEvent",
    "Start_Day": 30,
    "Nodeset_Config": {
        "class": "NodeSetNodeList",
        "Node_List": [7]
    },
    "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Number_Repetitions": 1,
        "Timesteps_Between_Repetitions": 0,
        "Target_Demographic": "Everyone",
        "Demographic_Coverage": 1,
        "Intervention_Config": {
            "class": "MultiPackComboDrug",
            "Dont_Allow_Duplicates": 0,
            "Cost_To_Consumer": 1,
            "Dose_Interval": 12,
            "Doses": [
                ["TestDrugA", "TestDrugA", "TestDrugB"],
                ["TestDrugBA"],
                ["TestDrugA", "TestDrugB"],
                ["TestDrugBA"],
                ["TestDrugAB"],
                [],
                ["TestDrugAB"]
            ]
        }
    }
}
```

The **Doses** array allows the user to specify what drugs are taken in what dose.  **The Dose_Interval**
parameter is used to determine the number of days between these doses.  A dose can be specified to
have zero drugs.  For example, if we wanted to model a 7-day pill pack that involved two drugs where
the person gets two doses of DrugA on Day 0 and then one every other day for 7-days and DrugB was to
be taken every day for 4-days, we would configure it like the following:

```json
{
    "Dose_Interval": 1,
    "Doses": [
        ["DrugA", "DrugA", "DrugB"],
        ["DrugB"],
        ["DrugA", "DrugB"],
        ["DrugB"],
        ["DrugA"],
        [],
        ["DrugA"]
    ]
}
```

However, if DrugB was instead to be taken twice--once on Day 0 and once on Day 4, it would be configured
like the following:

```json
{
    "Dose_Interval": 2,
    "Doses": [
        ["DrugA", "DrugA", "DrugB"],
        ["DrugA"],
        ["DrugA", "DrugB"],
        ["DrugA"]
    ]
}
```
