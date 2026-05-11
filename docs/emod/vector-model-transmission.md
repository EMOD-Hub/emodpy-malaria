# Vector transmission model


The *vector model* can be run in one of two modes: as a *cohort model* or as an
*individual mosquito model* (see [Vector model overview](vector-model-overview.md) for more information). The
vector model inherits the same human-infection model structure from the generic simulation type:
uninfected, latent incubation, infectious, multiple immune variables, and super-infection. However,
the transmission of infections is not between individual humans, but rather via the human-to-vector
and vector-to-human pathways. The model is a closed-loop feeding cycle where a successful vector
(mosquito) feeds (both indoors and outdoors), mates, then produce eggs which become larva and then
adult mosquitoes.

For example, vector blood-feeding branches into various probabilities that are calculated once per
*time step*. These calculations are based on species parameters and aggregated vector
interventions (see [feeding decision tree](#tree-movie)).

Vector transmission can be thought of in terms of vector ecology, and in the EMOD framework is
comprised of several components:

1. [Vector tracking](#vector-tracking-and-the-mosquito-life-cycle),

1. Mosquito behavior, which involves [feeding](#modeling-feeding-cycle-outcomes).

1. Transmission of malaria-causing *Plasmodium* parasites between humans and mosquitoes
    (see [transmission](#transmission-between-humans-and-vectors)).

For a complete list of configuration parameters that are used in the malaria model, see the
[parameter-configuration](parameter-configuration.md).


## Vector tracking and the mosquito life-cycle

Populations are tracked as cohorts throughout the full mosquito life-cycle:

* From eggs to larvae with a temperature-dependent development period
  preceding emergence

* A brief immature phase including sugar-feeding and mating

* Repeating multi-day *gonotrophic* cycles during which mosquitoes may be
  exposed to infection

* A temperature-dependent latency for sporogony

Life-cycle progression is modulated through a set of required species-specific parameters.

![Vector life cycle](../figures/vector-malaria/Vector_Transmission_life_cycle.png)

*Vector life cycle*


## Modeling feeding cycle outcomes

Adult vectors enter a cycle of host-seeking, feeding, and egg-laying that continues until death.
Successful vector blood-feeding branches into various probabilities that are calculated once per
*time step*. These calculations are based on species parameters (for example, *An. arabiensis*
has a higher propensity to feed outdoors or on livestock) and aggregated vector interventions.

Various feeding cycle outcomes are calculated from branching trees of conditional probabilities, and
individual interventions modulate the probability of choosing between branches. Feeding cycle
outcomes include:

* Death before, during, or after feeding

* Host unavailable

* Successful human feed

The allocation of mosquitoes to feeding-cycle outcomes is based on end-state probabilities that have
been aggregated over the individual humans in the simulation.

Multiple simultaneous interventions can target various branches in the vector feeding tree. For
example, when both *indoor residual spraying (IRS)* and *insecticide-treated nets (ITN)*
are applied against indoor host-seeking mosquitoes, IRS can discourage mosquitoes from entering the
house and kill mosquitoes before feeding. The fraction of mosquitoes that survive can be blocked by
the ITN, which may also kill a subset of the blocked fraction. Those mosquitoes who survive the
feeding attempt may be killed by IRS post-feed. This is how deterrent and toxic effects of multiple
interventions can be represented simultaneously.

To interact with these parameters and visualize the workings of this microsolver, see the decision
tree visualization below:

<iframe src="https://institutefordiseasemodeling.github.io/UnityVisualization/" height="680" width="1000"></iframe>[](){#tree-movie}

To get started, press the play button. You can also pause the visualization at any time.  Parameters
in blue are vector species parameters, while parameters in  green are types of campaign
interventions. Information on these parameters can be found in [parameter-configuration](parameter-configuration.md) and
[parameter-campaign](parameter-campaign.md). The two pink points on the tree illustrate when transmission of malaria
parasites is possible.

When the simulation starts, the initial mosquito population is set at 100 individuals. The starting
population for day two has an initial seeding of 50 mosquitoes, and also  includes all mosquitoes
that either live without feeding or feed and oviposit.  The simulation includes parameters that
determine the lifespan of mosquitoes and the time it takes for oviposited eggs to hatch and mature
to adulthood. As time progresses, the population will be comprised of only mosquitoes that are
generated through the oviposition cycle in the model.

The counters on the right side of the visualization keep track of current and total mosquitoes that
have "spawned" (generated in the simulation), died, lived without feeding, and fed and oviposited.

As an example, let's simulate *Anopheles gambiae*.  Set **Life_Expectancy** to 10 (most are thought
to live approximately 1-2 weeks in nature), **Egg_to_Adult** to 5 (this is their minimum duration in
the aquatic phase), **Days_between_Feeds** to 3, and **Anthropophily** and
**Indoor_Feeding_Fraction** to 0.8. These mosquitoes prefer to primarily feed on humans, and
preferentially feed indoors. Now, by changing the interventions, you can see how effective
interventions (or combinations of interventions) need to be in order to  disrupt (and reduce)
mosquito feeding and oviposition. Note that the slider bars for interventions range from 0 - 1, with
1 conferring 100% effectiveness. When mosquito ecology is sufficiently disrupted, malaria
transmission can be controlled.  You can also manipulate the species parameters to see how mosquito
ecology impacts the need for particular types of interventions.

If you are interested in simulating other mosquito species, more information on their relevant attributes
can be found in the articles [Made-to-measure malaria vector control strategies: rational design
based on insecticide properties and coverage of blood resources for mosquitoes][killeen-2014], by Killeen *et al*.,
2014, *Malaria Journal* 13:146, and [A global bionomic database for the dominant vectors of human malaria][massey-2016], by Massey *et al*., 2016, *Nature*.


## Transmission between humans and vectors

Transmission between humans and vectors can only occur when mosquitoes successfully feed on humans
(see Modeling feeding cycle outcomes).


### Microsporidia and transmission interference

The standard vector transmission model has been extended with a
[microsporidia endosymbiont model](vector-model-microsporidia.md) that captures how
microsporidia infections in mosquitoes interfere with *Plasmodium* acquisition and transmission.
Microsporidia-infected vectors have reduced probability of becoming infected with malaria when
feeding on infectious humans and reduced probability of transmitting malaria when feeding on
susceptible humans, with both effects configurable as time-dependent modifiers. The model tracks
vertical and horizontal microsporidia transmission through the mosquito population, enabling
evaluation of symbiont-based biocontrol strategies alongside conventional vector control
interventions such as IRS and ITNs.

See [Microsporidia](vector-model-microsporidia.md) for full details on transmission mechanisms, phenotypic
effects, configuration parameters, and associated interventions.


## Relevant IDM publications

* Eckhoff, 2013. [Mathematical models of within-host and transmission dynamics to determine effects of   malaria interventions in a variety of transmission settings][eckhoff-2013-ncbi].
  *Am J Trop Med Hyg*. 88(5):817-27

* Eckhoff, 2011. [A malaria transmission-directed model of mosquito life cycle and ecology][eckhoff-2011].
  *Malaria Journal*. 10:303
