# OutdoorRestKill


The **OutdoorRestKill** intervention class imposes node-targeted mortality to a vector that is at
rest in an outdoor environment after a feed. This affects female vectors that have fed indoors and outdoors and males.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No. It will need to be redistributed when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target sub-groups using genomes or specific sexes.
*  **Time-based expiration:** No. It will continue to exist even if efficacy is zero.
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Outdoor Die After Feeding. Note that it is a node-level intervention but does not impact the other node-level probabilities.
*  **Vector effects:** Killing
*  **Vector sexes affected:** Males and meal-seeking females
*  **Vector life stage affected:** Adults


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

{{ read_csv("csv/campaign-outdoorrestkill.csv") }}

[link](../json/parameter-campaign-node-outdoorrestkill.json)
