# OutbreakIndividualMalariaVarGenes


The **OutbreakIndividualMalariaVarGenes** intervention class is an individual-level intervention
that enables infecting people with an exact set of antigens. This can be helpful when
experimenting with the immune model, such as testing how a person’s immune system
reacts if they are reinfected by the same parasite. To use this intervention, set the
configuration parameters **Malaria_Model** to MALARIA_MECHINISTIC_MODEL and **Malaria_Strain_Model**
to FALCIPARUM_FIXED_STRAIN.

.. note::

    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    |EMOD_s| does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with |EMOD_s| will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not |EMOD_s| parameter names will be ignored by the
    model.

The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv("csv/campaign-outbreakindividualmalariavargenes.csv") }}

```json
{
    "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Number_Repetitions": 30,
        "Timesteps_Between_Repetitions": 150,
        "Target_Demographic": "Everyone",
        "Demographic_Coverage": 1.0,
        "Intervention_Config": {
            "class": "OutbreakIndividualMalariaVarGenes",
            "MSP_Type": 2,
            "IRBC_Type": [
                2, 75, 148, 221, 294, 367, 440, 513, 586, 659, 732, 805, 878, 951, 24, 97, 170,
                243, 316, 389, 462, 535, 608, 681, 754, 827, 900, 973, 46, 119, 192, 265, 338,
                411, 484, 557, 630, 703, 776, 849, 922, 995, 68, 141, 214, 287, 360, 433, 506, 579
            ],
            "Minor_Epitope_Type": [
                2, 0, 3, 3, 1, 2, 3, 3, 0, 1, 3, 2, 1, 3, 0, 1, 1, 2, 4, 0,
                1, 1, 0, 4, 0, 1, 1, 4, 4, 0, 2, 0, 4, 1, 2, 1, 1, 0, 1, 3, 3,
                1, 2, 4, 2, 4, 4, 3, 2, 4
            ]
        }
    }
}
```
