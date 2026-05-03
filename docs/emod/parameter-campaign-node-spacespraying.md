# SpaceSpraying


The **SpaceSpraying** intervention class implements node-level vector control by spraying pesticides
outdoors. This intervention targets specific habitat types, and imposes a mortality rate on all
targeted (both immature and adult male and female) mosquitoes. All mosquitoes have daily mortality
rates; mortality for adult females due to spraying is independent of whether or not they are
feeding.

At a glance:

*  **Distributed to:** Nodes
*  **Serialized:** No. You need to redistribute when starting from a serialized file.
*  **Uses insecticides:** Yes. It can target sub-groups using genomes, especially if you want to target specific sexes.
*  **Time-based expiration:** No
*  **Purge existing:** Yes and No. Adding a new intervention of this class will overwrite any existing intervention of the same class with the same **Intervention_Name**. If **Intervention_Name** is different, both interventions will coexist and their efficacies will combine 1-(1-prob1)*(1-prob2) etc.
*  **Vector killing contributes to:** Die Without Attempting To Feed & Die Before Attempting Human Feed
*  **Vector effects:** Killing
*  **Vector sexes affected:** Males and females
*  **Vector life stage affected:** Adult and immature



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

{{ read_csv("csv/campaign-spacespraying.csv") }}

[link](../json/parameter-campaign-node-spacespraying.json)
