# Larval habitat


Available larval habitat is a primary driver of local mosquito populations, and different mosquito
species can have different habitat preferences. Rainfall and humidity can strongly affect available
larval habitat, although this depends on the mosquito species and its particular habitat preference.
For example, *Anopheles funestus*, which prefers more semi-permanent larval habitat, exhibits
rainfall dependence, partly due to vegetation on edges of water and the interaction of rainfall with
agricultural schedules for crops such as rice. Further, preference can vary within species: *An. funestus*
exhibits differences in population responses to rainfall which are correlated with
chromosomal diversity.

In addition to available habitat, mosquito populations depend on larval development and mortality
rates. These in turn are affected by a variety of factors, including climate, short term weather,
and densities of other larvae.

In the present model, different models for larval habitat are developed for temporary, semi-
permanent, permanent, and human-driven habitats. The duration of larval development is a decreasing
function of temperature, and the present model utilizes an Arrhenius temperature-dependent rate
$a_1(a_2/T_K)$. In some cases, this temperature-dependent rate must be modified by local
larval density. Rainfall and temperature then combine through habitat creation and larval
development to create varying local patterns of distribution by larval instar, and larval mortality
and development duration determine pupal rates.


The creation of the habitat model is described in further detail in the articles
[Eckhoff, Malaria Journal 2011, 10:303][eckhoff-2011],
[Eckhoff, Malaria Journal 2012, 11:419][eckhoff-2012-mj], and
[Eckhoff, Am. J. Trop. Med. Hyg. 2013, 88(5)][eckhoff-2013].
The following sections provide information regarding specific larval habitat types and how to
configure these parameters in EMOD.

See [Larval configuration](parameter-configuration-larval.md) and [Vector lifecycle configuration](parameter-configuration-vector-lifecycle.md) parameters for more information on
configuring the various vector species.


## Modeling mosquito life cycles and larval habitat

The framework facilitates simulating multiple species of *Anopheles* mosquitoes simultaneously. This
allows for a mechanistic description of vector abundances through the effects of
climate and weather on different preferred larval habitats. Each species is configured separately
according to its ecological and behavioral preferences. For example, the female *An. arabiensis*
deposits eggs primarily in temporary, rainfall-driven habitat and has a higher propensity to feed
outdoors or on livestock. In contrast, *An. farauti* larvae live in brackish lagoons in the Solomon
Islands, where lagoons fill with rain, and larvae are washed out into the ocean due to excess rain.
The temporary rainfall relationship between larval habitat and rainfall cannot reproduce abrupt
(sub-week) changes in biting rates, and an additional rainfall-driven larval mortality term has been
implemented to capture the non-linear rain-to-habitat relationship.


![Vector abundance depends on larval habitat availability](../figures/vector-malaria/Vector_Transmission_abundance.png)

*Vector abundance depends on larval habitat availability*

![Larval habitat type determines how rainfall and temperature influence vector populations](../figures/vector-malaria/Vector_Transmission_larval_habitats.png)

*Larval habitat type determines how rainfall and temperature influence vector populations*


## Habitats

The parameter **Habitats**  is an array of JSON objects that contains one or more objects
that define a habitat. The user indicates the vector species, habitat type(s), and the array of scaling factors
used to determine the volume of that habitat needed for larvae to develop. Note that multiple species
may utilize the same habitat, with each species existing independently. The scaling factor
represents the number of larvae in a 1x1-degree area. The factor multiplicatively scales the
resulting weather or population dependent functional form. The following example shows how to use
this parameter, using *Anopheles funestus* as the vector and CONSTANT as the scaled habitat type.


```json
{
    "Vector_Species_Params": [
        {
            "Name": "funestus",
            "Habitats": [
                {
                    "Habitat_Type": "CONSTANT",
                    "Max_Larval_Capacity": 10000000.0
                }
            ],
            "Acquire_Modifier": 0.2
        }
    ]
}
```

The following are possible values for **Habitats**. They are described in detail below.

* TEMPORARY_RAINFALL
* WATER_VEGETATION
* CONSTANT
* BRACKISH_SWAMP
* HUMAN_POPULATION
* LINEAR_SPLINE



### Temporary rainfall


TEMPORARY_RAINFALL habitat corresponds to mosquitoes such as *Anopheles arabiensis* or
*Anopheles gambiae* which breed primarily in temporary puddles which are replenished by rainfall
and drain through evaporation and infiltration. We have developed a series of update equations for
the larval carrying capacity which scale the functional form for evaporation rates. This creates a
relationship in which evaporation and infiltration are higher when the weather is hot and dry.

The basic update equations appear in the article [Eckhoff, Malaria Journal 2011, 10:303][eckhoff-2011] and are as
follows: Temporary habitat $H_\text{temp}$ in a grid of diameter $D_\text{cell}$ increases with
rainfall $P_\text{rain}$ and decays with a rate $\tau_\text{temp}$ proportional to the
evaporation rate driven by temperature in Kelvin T and humidity RH:

$$H_{temp} += P_{rain}K_{temp}D^2_{cell} - H_{temp}\left(\frac{\Delta t}{\tau_{temp}}\right)$$

$$\frac{1}{\tau_{temp}} = \left(5.1\times 10^{11} Pa\right)\mathrm{e}^{-\frac{5628.1 K}{T}} k_{tempdecay}\sqrt{\frac{0.018kg / mol}{2\pi R T}}(1-RH)$$

in which $K_\text{temp}$ refers to species-specific maximum larval habitat capacity defined in **Vector_Species_Params**,
the exponential results from the *Clausius-Clayperon relation*, the root is from the
expression for vapor evaporation rates due to molecular mass given a partial pressure, and the
constant is the Clausius-Clayperon integration constant multiplied by a factor
$k_\text{tempdecay}$ to relate mass evaporation per unity area to habitat loss. Note that the R in the denominator
of the square root refers to the noble gas constant, and is neither a variable nor related to the relative humidity term RH.

Examining the two equations more closely, the first is a *time step* update equation, in which
available habitat is increased by a multiple of the rainfall in the past time step, scaled by the
size of the node in the simulation. For example, a 5 km square node will have 25 times the habitat
of a 1 km square node. Then existing habitat decays with a time constant defined by the second
equation. The basic functional form is based on an equation for evaporation rates, which is not
fully realistic in that it neglects boundary layer effects. However, we are looking for a rate of
habitat loss, not the rate of evaporation, and we also want to take infiltration into account.
The parameter $k_\text{tempdecay}$ converts raw evaporation rates in kg/m^2/s into habitat loss
per day.

The value of $k_\text{tempdecay}$ is initially chosen to set the habitat half-lives near 1 day for
hot and dry conditions and 2-3 weeks for more tropical conditions. The parameter
$k_\text{tempdecay}$ in the article [Eckhoff, Malaria Journal 2011, 10:303][eckhoff-2011] corresponds to
**Temporary_Habitat_Decay_Factor** in the simulation configuration file, and it applies to all local
species using temporary habitat. Each species in a given location can adjust the parameter
$K_\text{temp}$ from the paper, or equivalently the scaling factor value in **Habitats**
in the simulation configuration file (nested under the species name), to adjust the overall scaling
of the time series. So $K_\text{temp}$ is specific for each species, but $k_\text{tempdecay}$ is a
single value for all temporary habitat species in that location. Basically, the local weather and
$k_\text{tempdecay}$ set the overall time profile for larval habitat which can feed-forward into
adult population levels and biting rates. $k_\text{tempdecay}$ can be adjusted to achieve a best fit
for the time profile for a given location. Factors such as how sandy or clay-like the soil is will
affect this value. Once the time profile is correct, $K_\text{temp}$ can be adjusted to yield the
correct annual *entomological inoculation rate (EIR)* for that species.

The carrying capacity for TEMPORARY_RAINFALL is the number of larvae per [R * Degree$^2$]
where R is accumulated rainfall (in meters).


### Semi-permanent water vegetation

The second type of larval habitat, WATER_VEGETATION, is a semi-permanent habitat, which corresponds
to developing vegetation on the edges of semi-permanent habitat. This could be seen for swamp-like
or rice cultivation settings, in which the development of vegetation lags the rainfall and will be
closest to its peak towards the end of the rainy season. The decay is specified as a loss of habitat
per day, and this slower decay constant means that species with this habitat type will tend to have
a proportionately higher dry-season population relative to the temporary habitat species.

In the model, semi-permanent habitat increases with a constant $K_\text{semi} D_\text{cell}^2 P_\text{rain}$ and decays with a longer time constant $\tau_\text{semi}$
(**Semipermanent_Habitat_Decay_Rate** in the simulation configuration file): 

$$H_{semi} += P_{rain}K_{semi}D^2_{cell} - H_{semi}\Delta t\tau_{semi}$$

The parameter $K_\text{semi}$ is the maximum larval capacity in **Habitats** for species with a
**Habitats** of "WATER_VEGETATION". 
The values of $\tau_\text{semi}$ and  $K_\text{semi}$ 
can be fit to local data on vector abundance by species over time or to local data on
EIR to tailor a simulation to a specific setting.

The carrying capacity for WATER_VEGETATION is the number of larvae per [R * Degree$^2$]
where R is accumulated rainfall (in meters).


### Constant habitat


For habitat type CONSTANT, larval carrying capacity is constant throughout the year and does not
depend on weather. However, there will be a seasonal signal in adult population levels due to the
effects of temperature upon aquatic development times. For a given carrying capacity, a faster
development time will allow a local habitat to have a higher larval "through-put" with corresponding
impacts on the adult population. The scaling factor value in the **Habitats** parameter
is used to specify the carrying capacity per unit area $D_\text{cell}^2$. 

The carrying capacity for CONSTANT is the number of larvae per Degree$^2$.


### Brackish swamp


The BRACKISH_SWAMP habitat setting deals with the dynamics of how rain fills a brackish swamp, how
it decays and the associated parameter for rainfall-driven mortality threshold. This habitat type is
observable in the Solomon Islands where an entire larval generation is flushed away as a result of
the overflowing lagoon geography.  Since this is the case, the **TEMPORARY_RAINFALL** relationship
between larval habitat and rainfall cannot reproduce these abrupt changes (on 0 week timescales) of
biting rates. So, an additional rainfall-driven larval mortality term has been implemented that
captures the non-linear rain-to- habitat relationship. This habitat uses the same decay rate as the
semi-permanent water vegetation habitat.

The carrying capacity for BRACKISH_SWAMP is the number of larvae per Degree$^2$.



![Rainfall-driven mortality during swamp flushing](../figures/vector-malaria/Rainfall_Driven_Mortality_Flushing_of_Swamp.png)

*Rainfall-driven mortality during swamp flushing*

### Human population


The habitat type HUMAN_POPULATION scales with correlates of urban development, for example, water
that is available due to water pots in urban areas. This type is configured by multiplying the
number of people in the node’s population times the capacity value set in
**Habitats**.  Further, climate is not involved in setting
the capacity, as available water is not dependent on rainfall (it is instead dependent on human-provided
water sources).

The carrying capacity for HUMAN_POPULATION is the number of larvae per person.



### Linear spline


LINEAR_SPLINE is a user-customizable habitat type. Instead of specifying a given
habitat type, users may utilize data that tracks the number of larvae measured throughout the year(s)
to estimate the daily larval population using linear interpolation. In other words, this option
enables the user to use data collected from a specific site, or create data files to match a
particular location.  This option does not replace the climatological parameters, but it instead
adds a more flexible option in which you do not need climate data.

LINEAR_SPLINE has different syntax than the other habitat types, as the user is now required to
provide a distribution of the larval population. The following example provides the syntax for
configuring this habitat type:

```json
{
    "Vector_Species_Params": [
        {
            "Name": "funestus",
            "Habitats": [
                {
                    "Habitat_Type": "LINEAR_SPLINE",
                    "Capacity_Distribution_Number_Of_Years": 2,
                    "Capacity_Distribution_Over_Time": {
                        "Times": [0.0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5,
                                  212.917, 243.333, 273.75, 304.167, 334.583, 365.0,
                                  395.417, 425.833, 456.25, 486.667, 517.083, 547.5,
                                  577.917, 608.333, 638.75, 669.167, 699.583],
                        "Values": [0.0, 0.0, 0.0, 0.0, 0.2, 1.0, 1.0, 1.0, 0.5, 0.2,
                                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 1.0, 1.0, 1.0,
                                   0.5, 0.2, 0.0, 0.0]
                    },
                    "Max_Larval_Capacity": 10000000000.0
                }
            ]
        }
    ]
}
```

The LINEAR_SPLINE configuration specifies the day of year (in the **Times** array), larval value (in
the **Values** array), and larval capacity scaling number (**Max_Larval_Capacity**). The model
linearly interpolates the values to estimate the habitat availability for each vector species
without requiring climatological data. It is required that the first value under **Times** is equal
to zero.

The carrying capacity for LINEAR_SPLINE is the number of larvae per Degree$^2$.



## Modifying habitat availability


Ultimately, habitat is configured in order to create mosquito populations that realistically emulate
observed *entomological inoculation rate (EIR)*. Briefly, available habitat is directly related
to mosquito abundance, and mosquito abundance in turn is directly related to biting rate. In order
to calibrate the model there are several options for configuring habitat. You can first set habitat
parameters and modify them directly using the habitat scalar and decay rate. Then, after those
initial parameters are set, you can modify habitat with overall scaling parameters.


### Habitat scalars and decay rates


The following two figures demonstrate the effects of varying the habitat scalar
(**Habitats**) and the **Temporary_Habitat_Decay_Factor** ($k_\text{tempdecay}$)  for a
single species with temporary habitat. Changing the habitat scalar will scale the resulting adult
population size and biting rate by a similar factor.


![Effect of varying the habitat scalar, **Habitats**](../figures/vector-malaria/Vary_Habitat_Scalar.png){#hab-scalar-fig}

*Effect of varying the habitat scalar, **Habitats***

Lowering $k_\text{tempdecay}$ causes the resulting rainfall-driven habitat to decay at a slower
rate and thus increases $\tau_\text{temp}$.  A slower decay rate will result in higher
larval habitat on average, and higher resulting adult population biting rates.


![Effect of varying the decay rate, **Temporary_Habitat_Decay_Factor** ($k_\text{tempdecay}$)](../figures/vector-malaria/Vary_Temporary_Habitat_Scalar.png){#decay-rate-fig}

*Effect of varying the decay rate, **Temporary_Habitat_Decay_Factor** ($k_\text{tempdecay}$)*

These two parameters can be co-varied to produce an appropriate temporal profile. If rainfall is
constant, there is only one degree of freedom, as the habitat is always at equilibrium. The two
degrees of freedom become important when there is a distinct rainy season. For example, scaling
habitat produces the same ratio between biting rates in the wet season and dry season as seen in
[habitat scalar figure](#hab-scalar-fig).

However, when varying the decay rate, the ratio between habitats is different in the wet season
versus the dry season. As seen in the graph [decay rate variation](#decay-rate-fig), a
given ratio in rainy season will become exaggerated in the start of dry season (with a higher ratio
the drier the season), as the slower decay rate extends habitat longer into the dry season.



### Overall scaling


Often, it is desired to study a similar location, with the same species, temporal profile, etc., but
with a different annual *entomological inoculation rate (EIR)*. EIR depends not only on
climate, but on larval habitat availability as well. So as an alternative for modifying all  climate
and habitat parameters to change EIR, it is simpler to use the habitat scaling parameter,
**x_Temporary_Larval_Habitat** found in the configuration file. This parameter will scale all
habitat  parameters without changing the temporal dynamics, so that a new transmission is achieved
with the same ratios among the species, and same time profile. For example, setting
**x_Temporary_Larval_Habitat** to 0.1 would simulate low EIR (or a low transmission setting) by
reducing available habitat to 10%; a value of 1 could be used to  simulate high EIR (or a high
transmission setting), and there would be no reduction in available habitat.

An alternative to **x_Temporary_Larval_Habitat** is **LarvalHabitatMultiplier**.
**LarvalHabitatMultiplier** is a parameter in the demographics file, and can be applied to all
habitat types configured for the simulation, specific habitat types, or individual mosquito species
within particular habitat types in the Nodes array of the demographics file (see NodeAttributes in
[parameter-demographics](parameter-demographics.md)). The following example shows the syntax:


```json
{
    "Nodes": {
        "NodeID": 340461476,
        "NodeAttributes": {
            "LarvalHabitatMultiplier": [
                {
                    "Factor": 0.5,
                    "Habitat": "ALL_HABITATS",
                    "Species": "ALL_SPECIES"
                }
            ]
        }
    }
}
```

It should be noted that **LarvalHabitatMultiplier** enables habitat availability to be modified
independently for each species within a shared habitat. This is an upgrade over previous versions
of EMOD in which the modifier would be applied equally to all species within a shared habitat.


## Basic species configuration


For each species listed in **Vector_Species_Params**, a "VectorPopulation" object will be added to the
simulation at each node. Each species will be defined by parameters in the simulation configuration file 
for the vector ecology and behavior of the species. This allows for a mechanistic description of vector
abundances and behavior through the effects of climate and weather on different preferred larval
habitats.


The following example shows the syntax for configuring species parameters for *Anopheles arabiensis*.
Note that you would also need to configure parameters for *An. fuenstus* and *An. gambiae*, if you are
using a three species model as from the above example.

```json
{
    "Vector_Species_Params": [
        {
            "Name": "arabiensis",
            "Acquire_Modifier": 0.2,
            "Adult_Life_Expectancy": 20,
            "Anthropophily": 0.65,
            "Aquatic_Arrhenius_1": 84200000000,
            "Aquatic_Arrhenius_2": 8328,
            "Aquatic_Mortality_Rate": 0.1,
            "Days_Between_Feeds": 3,
            "Egg_Batch_Size": 100,
            "Habitats": [
                {
                    "Habitat_Type": "TEMPORARY_RAINFALL",
                    "Max_Larval_Capacity": 11250000000.0
                }
            ],
            "Immature_Duration": 2,
            "Indoor_Feeding_Fraction": 1,
            "Infected_Arrhenius_1": 117000000000,
            "Infected_Arrhenius_2": 8336,
            "Infected_Egg_Batch_Factor": 0.8,
            "Infectious_Human_Feed_Mortality_Factor": 1.5,
            "Male_Life_Expectancy": 10,
            "Temperature_Dependent_Feeding_Cycle": "NO_TEMPERATURE_DEPENDENCE",
            "Transmission_Rate": 0.5
        }
    ]
}
```

While the above example shows the mosquito residing in one habitat, it is worth noting that mosquitoes
can reside in multiple habitat types. This linear-combination of habitat types allows for greater
control over local vector ecology (especially during dry seasons as habitat availability may be
drastically different). The following example demonstrates the syntax to include several habitat types.

```json
{
    "Vector_Species_Params": [
        {
            "Name": "arabiensis",
            "Habitats": [
                {
                    "Habitat_Type": "TEMPORARY_RAINFALL",
                    "Max_Larval_Capacity": 11250000000.0
                },
                {
                    "Habitat_Type": "WATER_VEGETATION",
                    "Max_Larval_Capacity": 6000000000.0
                }
            ]
        }
    ]
}
```
