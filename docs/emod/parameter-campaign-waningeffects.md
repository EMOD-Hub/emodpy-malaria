# Waning effect classes


The following classes are nested within interventions (both individual-level and node-level) to
indicate how their efficacy wanes over time. They can be used with several parameters including
**Blocking_Config**, **Killing_Config**, and **Waning_Config**. Note that waning effect parameters
do not control the overall duration of an intervention and are not assigned probabilistically.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
See the example below that uses a mix of different waning effect classes and the tables below that
describe all parameters that can be used with each waning effect class.

[link](../json/parameter-campaign-waningeffects-1.json)

## WaningEffectBox


The efficacy is held at a constant rate until it drops to zero after the user-defined duration.

[link](../json/parameter-campaign-waningeffects-2.json)

{{ read_csv("csv/campaign-waningeffectbox.csv") }}

## WaningEffectBoxExponential


The initial efficacy is held for a specified duration, then the efficacy decays at an exponential rate where the current effect is equal to **Initial_Effect** - dt/**Decay_Time_Constant**.

[link](../json/parameter-campaign-waningeffects-3.json)

{{ read_csv("csv/campaign-waningeffectboxexponential.csv") }}

## WaningEffectCombo


The **WaningEffectCombo** class is used within individual-level interventions and allows for specifiying a list of effects when the intervention only has one **WaningEffect** defined. These effects can be added or multiplied.

[link](../json/parameter-campaign-waningeffects-4.json)

{{ read_csv("csv/campaign-waningeffectconstant.csv") }}

## WaningEffectConstant


The efficacy is held at a constant rate.

[link](../json/parameter-campaign-waningeffects-5.json)

{{ read_csv("csv/campaign-waningeffectconstant.csv") }}

## WaningEffectExponential


The efficacy decays at an exponential rate where the current effect is equal to **Initial_Effect** - dt/**Decay_Time_Constant**.

[link](../json/parameter-campaign-waningeffects-6.json)

{{ read_csv("csv/campaign-waningeffectexponential.csv") }}

## WaningEffectMapCount


The **WaningEffectMapCount** class assigns a probability to a particular update of the effect. This
typically used with [parameter-campaign-individual-adherentdrug](parameter-campaign-individual-adherentdrug.md) so one can assign a
probability that a person takes a particular dose. The **Times** value should be integers starting
from 1 and increasing.

If the example below were used in **AdherentDrug**, the probability that the person took the first
dose would be 40%, 30% for the second dose, and so on.

[link](../json/parameter-campaign-waningeffects-7.json)

{{ read_csv("csv/campaign-waningeffectmapcount.csv") }}

## WaningEffectMapLinear


The efficacy decays based on the time since the start of the intervention. This change is defined
by a map of time to efficacy values in which the time between time/value points is linearly
interpolated. When the time since start reaches the end of the times in the map, the last value will
be used unless the intervention expires. If the time since start is less than the first value in the
map, the efficacy will be zero. This can be used to define the shape of a curve whose magnitude is
defined by the **Initial_Effect** multiplier.

[link](../json/parameter-campaign-waningeffects-8.json)

{{ read_csv("csv/campaign-waningeffectmaplinear.csv") }}

## WaningEffectMapLinearAge


Similar to **WaningEffectMapLinear**, except that the efficacy decays based on the age of the
individual who owns the intervention instead of the time since the start of the intervention.

[link](../json/parameter-campaign-waningeffects-9.json)

{{ read_csv("csv/campaign-waningeffectmaplinearage.csv") }}

## WaningEffectMapLinearSeasonal


Similar to **WaningEffectMapLinear**, except that the map will repeat itself every 365 days. That
is, the time since start will reset to zero once it reaches 365.  This allows you to simulate
seasonal effects.

[link](../json/parameter-campaign-waningeffects-10.json)

{{ read_csv("csv/campaign-waningeffectmaplinearseasonal.csv") }}

## WaningEffectMapPiecewise


Similar to **WaningEffectMapLinear**, except that the data is assumed to be constant between
time/value points (no interpolation). If the time since start falls between two points, the efficacy
of the earlier time point is used.

[link](../json/parameter-campaign-waningeffects-11.json)

{{ read_csv("csv/campaign-waningeffectmappiecewise.csv") }}

## WaningEffectRandomBox


The efficacy is held at a constant rate until it drops to zero after a user-defined duration. This
duration is randomly selected from an exponential distribution where **Expected_Discard_Time** is
the mean.

[link](../json/parameter-campaign-waningeffects-12.json)

{{ read_csv("csv/campaign-waningeffectrandombox.csv") }}
