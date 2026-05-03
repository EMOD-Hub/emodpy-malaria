# Infectivity and transmission


{% include "../reuse/config-infectivity.txt" %}

The malaria transmission model does not use many of the parameters provided by the generic simulation
type. Instead, *gametocyte* abundances and *cytokine* mediated infectiousness are
modeled explicitly. See [vector-model-transmission](vector-model-transmission.md) for more information.

{% include "../reuse/warning-case.txt" %}

{{ read_csv("csv/config-infectivity-malaria.csv") }}
