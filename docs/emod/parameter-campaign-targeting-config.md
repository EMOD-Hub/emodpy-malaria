# Targeting_Config classes


The following classes can be used to enhance the selection of people when distributing interventions.
Most event coordinators and node-level interventions that distribute interventions to people have a
parameter called **Targeting_Config**.  This allows you to not only target individuals based on their
gender, age, and **IndividualProperties** (See [NodeProperties and IndividualProperties](parameter-demographics.md:nodeproperties-and-individualproperties) parameters for more information),
but also on things such as whether or not they have a particular intervention or are in a relationship.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.
Below is a simple example where we want to distribute a vaccine to 20% of the people that do not
already have the vaccine on the 100th day of the simulation.

[link](../json/parameter-campaign-targeting-config-1.json)

Below is a slightly more complicated example where we want to distribute a diagnostic to people
that are either high risk or have not been vaccinated.

[link](../json/parameter-campaign-targeting-config-2.json)

## HasIntervention


This determines whether or not the individual has an intervention with the given name.  This will only
work for interventions that persist like **SimpleVaccine** and **DelayedIntervention**.  It will not work for
interventions like **BroadcastEvent** since it does not persist.

### Configuration


```
**Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
**Intervention_Name**, string, NA, NA, """""", "The name of the intervention the person should have.  This cannot be an empty string but should be either the name of the class or the name given to the intervention of interest using the parameter Intervention_Name.  EMOD does not verify that this name exists."
```

### Example


Select the person if they do NOT have the MyVaccine intervention.

[link](../json/parameter-campaign-targeting-config-3.json)

## HasIP


This determines if the person has a particular value of a particular **IndividualProperties** (IP).
This is especially needed when determining if a partner has a particular IP (see **HasRelationship**).

### Configuration


```
**IP_Key_Value**, string, NA, NA, """""", "An **IndividualProperties** Key:Value pair where the key/property name and one of its values is separated by a colon (':')."
**Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
```

### Example


Select the person if their **Risk** property is HIGH.

[link](../json/parameter-campaign-targeting-config-4.json)

## TargetingLogic


In some cases, the you need to logically combine multiple restrictions.  In these situations,
you should use the **TargetingLogic** class where you can "and" and "or" the different questions.

NOTE: Each element is independent and is being asked of the individual in question.  For questions
that are about a partner of the individual, all of the qualifiers for that partner must be in the
element.  This will ensure that there is one partner that has all of the qualifications.  Otherwise,
you could have a situation where one partner satisfies one qualification and another partner
satisfies a different one, but no partner has all of the qualifications.


### Configuration


```
**Logic**, 2D array of JSON objects, NA, NA, [], "This is a two-dimensional array of JSON objects.  The elements of the inner array will be AND'd together while the arrays themselves will be OR'd.  This is similar to **Property_Restrictions_Within_Node**.  This array and the inner arrays cannot be empty."
```

### Example

Select the person if they do not have the MyVaccine intervention OR do not have their **Risk** property set to HIGH.
Notice that **Logic** 2x1 where the first dimention contains two arrays with one JSON object.  These two
arrays are OR'd together.

[link](../json/parameter-campaign-targeting-config-5.json)

Select the person if they do not have the MyVaccine intervention AND do not have their **Risk** property set to HIGH.
Notice that **Logic** is 1x2 where the first dimension contains a single array with two JSON objects.  These two
objects are AND'd together.

[link](../json/parameter-campaign-targeting-config-6.json)
