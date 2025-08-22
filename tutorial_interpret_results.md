# Interpreting the results of Simple Example

At the end of the [Run Simple Example Tutorial](tutorial_run_simple_example.md), you generated
an image, results/Simple_Example.png.  This image shows 31 different time-based statistics
on the simulation.  The following will discuss many of these statistics so that you
can begin to get a feeling for the kinds of information you get get from EMOD about
your simulation.

## Prerequisites

This tutorial assumes you have run the examples-container/simple_example either on
Codespaces or locally.

## The InsetChart plot

EMOD's default report is called "InsetChart".  This report contains numerous statistics
over time.  The purpose of the report is to give you a quick overview of what is happening
in your simulation.  It is frequently helpful to this data all at once because it allows
you to easily cross reference with other statistics.  For example, if you looked at the
"Infected" data and saw no one is infected, you might also look at the "Statistical Population"
data to verify there are people.  If there were no people, you could assume that is why
no one is infected.

NOTE:  Sometimes a statistic in InsetChart is referred to as a "channel".

Your Simple_Example.png should look something like the following:

![](media/tutorial_17_understand_results.png)

## Weather information

InsetChart has four statistics on weather:
- Air Temperature
- Land Temperature
- Rainfall
- Relative Humidity

Below are these four statistics showing the value over time.  You will notice that these values
are constant over the 80 days of the simulation.  This is because the simulation was configured
to have constant weather.  This is a handy feature to use when you are trying to understand how
things work because you don't have to also adjust for how seasonality changes things.

![](media/tutorial_18_weather.png)

## Mosquitoes / Vectors

InsetChart also has four statistics that are directly related to the mosquitoes or vectors that
are in the simulation.  These are:
- Adult Vectors
- Daily Human Biting Rate
- Daily EIR
- Infectious Vectors

These plots are much more interesting with Adult Vectors growing over time while Infectious Vectors and Daily EIR don't get started until day 40.  Why do the plots have the shapes that they do?

EMOD is one of the only malaria models that includes the mosquitoes as its own set of agents.
EMOD models the mosquito through its life cycle from eggs to larve to adult and back again.
Please [EMOD Vector Biology](https://docs.idmod.org/projects/emodpy-malaria/en/latest/emod/vector-model-overview.html) for more information.

**Adult Vectors** - These are the adult, female mosquitoes.  Our scenario has three species and so starts out with 10,000 each at day 0 (30,000 total).  You see a rapid decline until about day 18,
because there are no new mosquitoes becoming adults.  We must wait for the eggs laid on day zero
to mature and become adults.  If we were to run this simulation longer, we would likely see the
number of mosquitoes leveling out once they have saturated the larval habitat.

**Infectious Vectors** - This is the fraction of **Adult Vectors** that are _infectious_.  This
means that these vectors bit a human, got gametocytes, the gametocytes became ocysts, and the ocysts
produced sporozoites.  This also took time, possibly the 22 days between when the new adults
started appearing on day 18 and the sporozoites developed.

**Daily Bites per Human** - This statistic is interesting because it shows how it declines
as the vector population declines and then suddenly takes off on day 18.  This is the same day
that our first eggs have matured.  The biting starts out very jagged because this group of
mosquitoes is biting every three days.  We see it because less jagged over time as number
of mosquitoes feeding each day starts to equal out.

**Daily EIR** - This statistic is showing the number of infectious bites delivered each day.
It is jagged like **Daily Bites per Human** because these mosquitoes delivering infectious
bites are probably from those first couple of initial new adults.

To avoid some of these vector start up issues as well as establish immunity in the population,
users will do a simulation "burn-in".  This is where they will run the simulation for many
years to let the vectors and immunity to stabilize.  When that simulation finishes, they have
it create a "serialized population file".  This file is then used for new simulations.
please see [Serializing Populaitons](https://docs.idmod.org/projects/emodpy-malaria/en/latest/emod/software-serializing-pops.html) for more information.

![](media/tutorial_19_vectors.png)

## Demographic statistics

InsetChart includes three statistics on the demographics:
- Statistical Population
- Births
- Disease Deaths

**Statistical Population** - This statistic shows the number of human agents in the simulation
at each time step.  It changes as agents are born and die.  In our case, we see one of the
simulations increase twice.  If we look at the **Births** statistic, we see those births for that
simulation.

**Births** - This statistic shows the cumulative number of people born at each time step.
As noted above, we see one simulation had two births and those people show up in the 
**Statistical Population**.

**Disease Deaths** - This shows the number of people that died at each time step due to
malaria.  Most users do not model disease death in EMOD due to the lack of data to calibrate
to.  Hence, in this case, we see no disease deaths.

![](media/tutorial_20_demographics.png)

## Prevalence, incidence, and immunity

Unlike the real world, simulation lets us know what is going on in the entire population.
For example, the following statistics tell us about the prevalence and immunity status of
the whole population.
- Infected
- New Infections
- Variant Fraction - PfEMP1 Major

**Infected** - This is the fraction of the total population that is infected (has parasites
at any stage during their time within a human).  In this scenario, we see that about 20% of
the population is infected at the beginning and at about day 40, it jumps up to close to 100%.

**New Infections** - This is the number of people receiving a new infection on that time step.
In this plot, we see a bunch of new infections, a large spike around day 40, and then it declines.
The first spike is our initial set of infections and the large spike is due that large group
of infectious vectors biting most of our population.

**Variant Fraction - PfEMP1 Major** - This is more complicated to explain than we have room
for here, but think of this statistic as showing you the amount of antibodies that the agents
have developed against the parasite.  In our plot, we see that the people start off with no
immunity, but it really takes off once people start getting infected.  See the section on
[Malaria infection and immune model](https://docs.idmod.org/projects/emodpy-malaria/en/latest/emod/malaria-model-infection-immunity.html)
for more information.

![](media/tutorial_21_prevalence.png)

## Clinical and severe cases

One measure of malaria is when people's symptoms become significant enough that something
is done about it.  This requires EMOD to model fever for each infected agent.  The InsetChart
plot has two statistics showing the number of cases detected each time step.
- New Clinical Cases
- New Severe Cases

**New Clinical Cases** - People don't usually seek treatment for malaria until their fever
has been high enough and long enough to cause concern.  This is what we call a "clinical case".
In our plot, you will notice two peaks: one at about day 18 which is about 18 days after the
initial round of infections.  You see a second peak at about day 58 which is about 18 days after
the peak of new infections on day 40.

**New Severe Cases** - Excessive fever or anemia can lead to severe cases and are rare in this
short amount of time.  We had one simulation with one severe case.

To learn more about how symptoms are modeled in EMOD, please see [Malaria symptoms and diagnostics](
https://docs.idmod.org/projects/emodpy-malaria/en/latest/emod/malaria-model-symptoms-diagnosis.html).

![](media/tutorial_22_cases.png)

## Diagnostics

Most of the other statistics in InsetChart show prevalence if you could sample the entire
population with a particular diagnostic.  Below is a sample of those statistics:
- Blood Smear Parasite Prevalence
- PCR Gametocyte Prevalence
- PfHRP2 Prevalence
- Fever Prevalence

The thing to notice about these is how **Blood Smear Parasite Prevalence** and **PfHRP2 Prevlance**
might have detected that people had malaria before people started developing high fevers,
**Fever Prevalence**.  When we compare those three with **PCR Gametocyte Prevalence**, we
see the delay it takes for the parasites to be come gametocytes and the people to become
infectious.

![](media/tutorial_23_diagnostics.png)

For more on InsetChart, please our [documetation](https://docs.idmod.org/projects/emodpy-malaria/en/latest/emod/software-report-inset-chart.html).

