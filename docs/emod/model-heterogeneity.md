# Adding heterogeneity


One of the benefits of an agent-based model like EMOD over compartmental models is that the
model can be configured to capture heterogeneity in population demographics, migration patterns,
disease transmissibility, climate, interventions, and more. This heterogeneity can affect the
overall course of the disease outbreak and campaign interventions aimed at controlling it.


## Demographics


Built-in demographics options are available for running EMOD simulations, or you can create
customized demographics files to represent particular locations. It is generally 
recommended that you create a demographics file instead of using built-in demographics. 

Every individual within the simulation has a variety of attributes, represented by continuous or
discrete state variables. Some are static throughout life, and others dynamically change
through the course of the simulation, through response either to aging or to simulation events (such
as infection). Static attributes are assigned upon instantiation (simulation initialization or birth
after the beginning of the simulation) and include gender, time of birth, time of non-disease death, etc. Dynamic attributes include disease state, history of interventions, and more. 

## Vital dynamics


Vital dynamics within EMOD are derived from fertility and mortality tables that
are passed to the model as input. Input demographic data can be used to construct a cumulative
probability distribution function (CDF) of death date based on individuals' birth dates. Then, in
the model, individual agents will be sampled stochastically from this CDF using an inverse transform
of this distribution. Female agents similarly sample the age at next childbirth, if any, upon
instantiation and birth of a previous child. Pregnancy is not linked to relationship status,
although newly born individuals are linked to a mother. The fertility rate changes by simulation
year and female age, and the range for available estimates depends on input data. Values outside of
this range can be chosen by "clamping," or choosing the nearest value within the range. Clamping was
also used when necessary to determine the non-disease mortality rate, which varies by gender, age, and
simulation year.

For more information on the demographics file, see [Demographics file](software-demographics.md).

## Individual and node properties


One of the most powerful and flexible features of EMOD is the ability to assign properties to
nodes or individuals that can then be used to target interventions or move individuals through a
health care system. For example, you might assign various degrees of risk, socioeconomic status,
intervention status, and more. In the generic, environmental, typhoid, airborne, and TBHIV simulation types, these
properties can be leveraged to add heterogeneity in transmission based on the property values
assigned to each individual. For example, you might configure higher transmission among school-age
children. 

## Innate immune variation

Individuals in a population differ in their innate immune responses to malaria. EMOD can model
this heterogeneity by drawing a per-individual innate immunity modifier (*v*) from a distribution
configured in the demographics file
(**InnateImmuneDistributionFlag**/**InnateImmuneDistribution1**/**InnateImmuneDistribution2**).
The modifier persists for the individual's lifetime.

The **Innate_Immune_Variation_Type** configuration parameter controls how the drawn value is
interpreted. In the formulas below, *v* is the drawn value, **Pyrogenic_Threshold** and
**Fever_IRBC_Kill_Rate** are configuration parameters, and *age* is the individual's age in
years.

### `NONE` (default)

No innate immune variation. The distribution is ignored; all individuals use the configured
**Pyrogenic_Threshold** and **Fever_IRBC_Kill_Rate** directly.

### `PYROGENIC_THRESHOLD`

The drawn value scales the individual's pyrogenic threshold — the IRBC/µL density at which
fever is triggered:

```
individual_pyrogenic_threshold = v × Pyrogenic_Threshold
```

Higher values mean the individual tolerates higher parasite loads before becoming febrile.
Bounded by **Pyrogenic_Threshold_Min** and **Pyrogenic_Threshold_Max**.

### `CYTOKINE_KILLING`

The drawn value scales the individual's cytokine-mediated parasite killing rate:

```
individual_kill_rate = v × Fever_IRBC_Kill_Rate
```

Higher values produce a stronger innate killing response.

### `PYROGENIC_THRESHOLD_VS_AGE_CONCAVE`

The pyrogenic threshold starts at `v × Pyrogenic_Threshold` and changes with age, reflecting
acquired tolerance. The threshold is recalculated every 3 months:

```
base = v × Pyrogenic_Threshold

if age < 2 years:
    threshold = base + 0.035 × base × age
else:
    threshold = base × 0.965 × exp(-0.09 × (age - 2)) + base × 0.1
```

For young children, the threshold increases linearly. After age 2, it decays exponentially
toward 10% of the base value (the asymptotic tolerance level for adults). Bounded by
**Pyrogenic_Threshold_Min** and **Pyrogenic_Threshold_Max**.

### `PYROGENIC_THRESHOLD_VS_AGE_INCREASING_AND_CYTOKINE_KILLING_INVERSE`

Both the pyrogenic threshold and cytokine killing rate are modified. The distribution
should be Uniform(0, 1) because the cytokine formula assumes *v* is in that range.

**Pyrogenic threshold** increases with age:

```
base = v × Pyrogenic_Threshold
threshold = base × 10^(0.132 × age)
```

Capped at **Pyrogenic_Threshold_Max**. Once the cap is reached, the threshold remains fixed.

**Cytokine killing rate** varies inversely with *v*:

```
individual_kill_rate = Fever_IRBC_Kill_Rate × (2 - v)
```

Individuals with a higher pyrogenic threshold (more tolerant of fever) have a lower cytokine
killing rate, and vice versa.

### Related parameters

| Parameter | Description |
|---|---|
| **Pyrogenic_Threshold** | Base IRBC/µL level at which innate inflammatory response is half-maximal (default: 1000) |
| **Pyrogenic_Threshold_Min** | Floor for calculated pyrogenic threshold (default: 0.1) |
| **Pyrogenic_Threshold_Max** | Ceiling for calculated pyrogenic threshold (default: 100000) |
| **Fever_IRBC_Kill_Rate** | Maximum IRBC kill rate from innate inflammatory response (default: 0.15) |

See [Immunity configuration](parameter-configuration-immunity.md) for the full parameter list.

To configure innate immune variation in emodpy-malaria, use
[MalariaDemographics.set_innate_immune_distribution()](https://emod.idmod.org/emodpy-malaria/autoapi/emodpy_malaria/demographics/MalariaDemographics/).
This method automatically sets **Innate_Immune_Variation_Type** at task build time.

For more details on the innate immune response model, see
[Infection and immunity](malaria-model-infection-immunity.md#innate-immune-response).


## Transmission


In EMOD, transmission can only happen within a geographic node, and the population is "well-mixed" in each node. Heterogeneous transmission is modeled through biologically
mechanistic parameters that control aspects of the simulation such as parasite density, symptom
severity, mosquito bites, and more. 

See [Infectivity configuration](parameter-configuration-infectivity.md) parameters for more information on configuring transmission in
this simulation type. Because HINT cannot be used with this simulation type, the parameter
**Enable_Heterogeneous_Intranode_Transmission** in the configuration file must be set to 0
(zero).

## Migration


EMOD can also simulate human and vector migration, which can be important in the transmission of
many diseases. You can assign different characteristics to each geographic *node* to control
how the disease spreads.

When **Enable_Migration_Heterogeneity** is enabled, each individual receives a personal migration
rate multiplier drawn from a distribution configured in the demographics file
(**MigrationHeterogeneityDistributionFlag/Distribution1/Distribution2**). This multiplier persists
for the individual's lifetime, creating realistic variation where some individuals are frequent
travelers and others rarely leave their home node. This heterogeneity applies only to human
migration; vector migration rates are controlled separately through habitat, food, and stay-put
modifiers.

For more information, see [Geographic migration](model-migration.md).

For more information on how you can target campaign interventions to individuals or locations based
on certain criteria, see [model-campaign](model-campaign.md).

