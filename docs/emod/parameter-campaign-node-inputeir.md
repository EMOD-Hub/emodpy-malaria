# InputEIR


The **InputEIR** intervention class enables the Entomological Inoculation Rate (EIR) to be
configured either for each month or for each day of the year in a particular node. The EIR is the number of
infectious mosquito bites received in a night. This number is usually calculated by taking the number of mosquito
bites received  per night and multiplying them by the proportion of those bites that are positive for sporozoites.

Whether each individual actually becomes infected from the challenge is modified by individual-level
factors. Each person's probability of infection is scaled by a combined relative risk that accounts for:
* **Acquisition immunity** -- both naturally acquired immunity that develops over time through repeated
  exposure and any reduction from acquisition-blocking vaccines (e.g., **SimpleVaccine** with
  **Vaccine_Type** set to **AcquisitionBlocking**).
* **Age-dependent biting risk** -- if **Age_Dependent_Biting_Risk_Type** is enabled in the configuration,
  younger (smaller) individuals receive proportionally fewer bites.
* **Demographics-based risk** -- if **Enable_Demographics_Risk** is enabled, each individual's personal
  risk factor from the demographics file further scales their exposure.

Vector control interventions will not affect the EIR delivered by this intervention.

If vectors are  included when this class is implemented, this will add the EIR specified for that month or day in
addition to the EIR provided by the vectors. Note that the **Daily EIR channel** in the [InsetChart report](software-report-inset-chart.md)
will not be impacted by this intervention.

When distributing **InputEIR** to a node that already has an existing **InputEIR** intervention, the existing
intervention will be purged and replaced with the new intervention.

**Note**: **Age_Dependence** parameter has been removed from this intervention (EMOD v2.28, emod-malaria v0.77).
Age dependent biting risk is now controlled by the **Age_Dependent_Biting_Risk_Type parameter** in the config file, same as for vector biting.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No, it needs to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Does Not Apply
*  **Time-based expiration:** No.
*  **Purge existing:** Yes. Adding a new intervention of this class will overwrite an existing intervention of the same class.
*  **Vector killing contributes to:** Does Not Apply
*  **Vector effects:** Does Not Apply
*  **Vector sexes affected:** Does Not Apply
*  **Vector life stage affected:** Does Not Apply

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

{{ read_csv("csv/campaign-inputeir.csv", keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "Constant EIR challenge",
    "Events": [
        {
            "class": "CampaignEvent",
            "Event_Name": "Input EIR intervention",
            "Start_Day": 0,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Number_Repetitions": 1,
                "Intervention_Config": {
                    "class": "InputEIR",
                    "Monthly_EIR": [0.39, 0.19, 0.77, 0, 0, 0, 6.4, 2.2, 4.7, 3.9, 0.87, 0.58]
                }
            }
        }
    ]
}
```
