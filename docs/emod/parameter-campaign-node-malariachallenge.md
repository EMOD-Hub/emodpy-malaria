# MalariaChallenge


The **MalariaChallenge** intervention class is a node-level intervention similar to
[Outbreak](parameter-campaign-node-outbreak.md). However, instead of distributing infections, it distributes
malaria challenges by either tracking numbers of sporozoites or infectious mosquito bites.

Whether each individual actually becomes infected from the challenge is modified by individual-level
factors. Each person's probability of infection is scaled by a combined relative risk that accounts for:
* **Acquisition immunity** -- both naturally acquired immunity that develops over time through repeated
  exposure and any reduction from acquisition-blocking vaccines (e.g., **SimpleVaccine** with
  **Vaccine_Type** set to **AcquisitionBlocking**).
* **Age-dependent biting risk** -- if **Age_Dependent_Biting_Risk_Type** is enabled in the configuration,
  younger (smaller) individuals receive proportionally fewer bites.
* **Demographics-based risk** -- if **Enable_Demographics_Risk** is enabled, each individual's personal
  risk factor from the demographics file further scales their exposure.

Vector control interventions will not affect the infections delivered by this intervention.

If vectors are  included when this class is implemented, this will add the infections specified for that month or day in
addition to the infections provided by the vectors. Note that the **Daily EIR channel** in the [InsetChart report](software-report-inset-chart.md) will not be impacted by this intervention.

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

{{ read_csv("csv/campaign-malariachallenge.csv", keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Events": [
        {
            "class": "CampaignEvent",
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Day": 40,
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "MalariaChallenge",
                    "Challenge_Type": "InfectiousBites",
                    "Coverage": 1.0,
                    "Infectious_Bite_Count": 2,
                    "Sporozoite_Count": 3
                }
            }
        }
    ]
}
```
