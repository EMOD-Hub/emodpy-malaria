# Tutorial 1: Run your first simulation

This tutorial introduces the core building blocks of every emodpy-malaria script by running a
simple malaria simulation with no interventions. You will see how to configure simulation
parameters, define a human population, and run an experiment on the Container platform.

If you have not already read [EMOD input files](concepts.md), do that first — it introduces the
configuration, demographics, campaign, and report concepts used in every tutorial.

**File:** `tutorials/tutorial_1_intro.py`

## EMOD executable and schema

The `if __name__ == "__main__"` block calls `emod_malaria.bootstrap.setup()` before running the
experiment. This extracts the EMOD executable and schema from the `emod_malaria` package into
the `tutorials/download/` directory. 

```python title="tutorial_1_intro.py, lines 178–180"
import emod_malaria.bootstrap as dtk
dtk.setup(pathlib.Path(manifest.eradication_path).parent)
```

Paths used throughout the tutorials are defined in `manifest.py`.

## Config callback: build_config

`build_config` is passed to `EMODTask` and called when building `config.json`. It receives a
config object and returns it after making changes.

```python title="tutorial_1_intro.py, lines 43–61"
def build_config(config):
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Simulation_Duration = sim_years * 365
    config.parameters.Run_Number = 0
    return config
```

`set_team_defaults()` applies the malaria team's standard parameter set — a large collection of
validated defaults that gives a working malaria simulation without needing to set every parameter
individually.

`add_species()` adds pre-configured species parameters for three *Anopheles* vector species
present at most African sites.

`Simulation_Duration` is in days, so `sim_years * 365` converts years to days.

## Demographics callback: build_demog

`build_demographics` builds the demographics file that describes the simulated human population.

```python title="tutorial_1_intro.py, lines 64–77"
def build_demographics():
    from emodpy_malaria.demographics import MalariaDemographics as Demographics
    from emodpy_malaria.utils.distributions import UniformDistribution
    from emodpy_malaria.utils.emod_enum import BirthRateDependence

    demog = Demographics.from_template_node(lat=-3.2, lon=37.9, pop=1000,
                                            name="Tutorial_Site")
    demog.set_birth_rate(40, birth_rate_dependence=BirthRateDependence.POPULATION_DEP_RATE)
    demog.set_age_distribution(UniformDistribution(0, 60))
    return demog
```

`from_template_node()` creates a single-node population of 1000 people.

`set_birth_rate(40, birth_rate_dependence=BirthRateDependence.POPULATION_DEP_RATE)` sets the
birth rate to 40 births per 1000 people per year, a representative value for sub-Saharan
Africa. The `birth_rate_dependence` parameter controls how EMOD interprets the rate value —
`POPULATION_DEP_RATE` means births scale with node population.

`set_age_distribution(UniformDistribution(0, 60))` initializes the population with ages
uniformly distributed between 0 and 60 years rather than starting everyone at the same age.

## Platform

The `Platform` specifies where simulations run. The tutorial includes commented-out blocks for
all three supported platforms — uncomment the one that matches your environment:

```python title="tutorial_1_intro.py, lines 135–148"
# Container platform — runs EMOD in a Docker container locally or in Codespaces
platform = Platform("Container", job_directory=manifest.job_dir,
                    docker_image=manifest.plat_image)

# COMPS platform — runs on IDM's COMPS cluster
# platform = Platform("Calculon", node_group="idm_48cores", priority="Normal")

# SLURM platform — runs on a SLURM cluster
# platform = Platform("SLURM_LOCAL",
#                     job_directory=manifest.job_dir,
#                     time="02:00:00",
#                     partition="cpu_short",
#                     mail_user="you@example.org",
#                     ...)
```

## Report callback: build_reports

By default, EMOD produces no report output other than its standard logging (`stdout.txt`).
To get simulation data you can analyze, you need to add at least one reporter.
**InsetChart** is the most basic overview report — it records simulation-wide averages per
time step across channels like population size, infection prevalence, daily biting rate, and
many other statistics.

```python title="tutorial_1_intro.py, lines 80–84"
def build_reports(reporters):
    from emodpy_malaria.reporters.reporters import InsetChart
    reporters.add(InsetChart(reporters))
    return reporters
```

The callback receives a `Reporters` object, adds reporter instances to it, and returns it.
Here we add a single `InsetChart` reporter with default settings, which writes
`InsetChart.json` to the simulation output folder.

!!! note
    Reports are covered in much more detail in [Tutorial 2](tutorial-2.md), which adds
    additional reporters, downloads the results, and shows how to plot them.

## EMODTask

`EMODTask.from_defaults()` assembles the simulation task from the callbacks and the paths to
the EMOD executable and schema:

```python title="tutorial_1_intro.py, lines 150–157"
task = EMODTask.from_defaults(
    eradication_path=manifest.eradication_path,
    schema_path=manifest.schema_path,
    config_builder=build_config,
    campaign_builder=None,
    demographics_builder=build_demographics,
    report_builder=build_reports
)
```

`campaign_builder=None` means no interventions are added — the population runs under baseline
transmission only. Campaigns are introduced in Tutorial 3.

## Running the experiment

`SimulationBuilder` manages parameter sweeps across simulations. Tutorial 1 runs a single
simulation by sweeping `Run_Number` over just one value:

```python title="tutorial_1_intro.py, lines 165–169"
builder = SimulationBuilder()
builder.add_sweep_definition(sweep_run_number, [0])

experiment = Experiment.from_builder(builder, task, name="tutorial_1_intro")
experiment.run(wait_until_done=True, platform=platform)
```

`wait_until_done=True` pauses Python here until all simulations finish. Tutorial 5 covers
sweeping over multiple values to run parameter studies.

When using the Container platform, simulations run inside `tutorial_output/`. Inside that
directory you will find an experiment folder named after the experiment and its unique ID:

```
tutorial_output/
  e_tutorial_1_intro_949f773e-d09e-4212-80b3-3e7c10a4e16c/
    551dfe56-f2f8-4831-9f15-b7c0ac529557/   ← simulation 1
```

Each folder under the `e_tutorial_1_intro*` directory is one simulation run with its inputs
and outputs.

!!! note
    Every simulation produces `stdout.txt` and `stderr.txt` in its output folder. These are
    the standard logging files for EMOD and are the first place to look when debugging issues
    — they contain initialization messages, warnings, and error details that help identify
    what went wrong.

## Downloading and plotting results

After the experiment succeeds, `DownloadAnalyzer` copies `InsetChart.json` from each
simulation into a local `tutorial_1_results/` directory:

```python title="tutorial_1_intro.py, lines 97–102"
filenames = ["output/InsetChart.json"]
analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

manager = AnalyzeManager(platform=platform, analyzers=analyzers)
manager.add_item(experiment)
manager.analyze()
```

Then `plot_inset_chart()` reads the downloaded files and produces an overview plot with all
InsetChart channels over time:

```python title="tutorial_1_intro.py, lines 107–110"
from emodpy_malaria.plotting.plot_inset_chart import plot_inset_chart
plot_inset_chart(dir_name=output_path,
                 title="Tutorial 1 - InsetChart",
                 output=output_path)
```

The resulting image is saved to `tutorial_1_results/`.

## Next

[Tutorial 2](tutorial-2.md) adds more reports (MalariaSummaryReport, DemographicsSummary),
covers report filtering, and shows how to plot different report types.
