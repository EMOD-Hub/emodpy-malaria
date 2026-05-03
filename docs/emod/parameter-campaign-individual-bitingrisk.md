# BitingRisk


The **BitingRisk** class allows you to adjust the relative risk that the person is bitten by a
vector. As an intervention, it allows you to target specific groups at specific times during the
simulation.

The relative biting rate can be initially set by setting **Enable_Demographic_Risk** to 1 and then
configuring **IndividualAttributes**, **RiskDistributionFlag**, **RiskDistributionParam1**, and
**RiskDistributionParam2**. This will give each new person their own relative risk.

The relative biting rate can be thought of as having two parts: the relative risk value and the age
dependent value. Age dependence is set using the  **Age_Dependent_Biting_Risk_Type** parameter.
These two values (from age dependence and relative risk) are multiplied to get the resulting rate,
which is then used to control how much contagion is deposited from an infectious individual and the
probability that an infection is acquired.

This intervention expires. To reset it, distribute another **BitingRisk** intervention that sets it
back to the original value. Note that this is a *relative* biting rate. For example, giving everyone
a value of 10 is the same as giving everyone a value of 1. This intervention is used to indicate
some individuals are more likely to be bitten than others.


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

{{ read_csv("csv/campaign-bitingrisk.csv") }}

```json
{
  "Intervention_Config": {
    "class": "BitingRisk",
    "Risk_Distribution": "CONSTANT_DISTRIBUTION",
    "Risk_Constant": 0.1
  }
}
```
