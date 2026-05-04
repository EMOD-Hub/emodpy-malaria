# Tutorial 1: Run your first simulation

This tutorial introduces the core building blocks of every emodpy-malaria script by running a
simple malaria simulation with no interventions. You will see how to configure simulation
parameters, define a human population, and run an experiment on the Container platform.

If you have not already read [EMOD input files](concepts.md), do that first — it introduces the
configuration, demographics, campaign, and report concepts used in every tutorial.

**File:** `tutorials/tutorial_1_intro.py`

## Obtaining the EMOD executable

The `if __name__ == "__main__"` block calls `emod_malaria.bootstrap.setup()` before running the
experiment. This downloads the EMOD executable and schema from the `emod_malaria` package into
the `tutorials/download/` directory.

```python
import emod_malaria.bootstrap as dtk
dtk.setup(pathlib.Path(manifest.eradication_path).parent)
```

Paths used throughout the tutorials are defined in `manifest.py`.

## Config callback: set_param_fn

`set_param_fn` is passed to `EMODTask` and called when building `config.json`. It receives a
config object and returns it after making changes.

```python
def set_param_fn(config):
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae", "arabiensis", "funestus"])

    config.parameters.Simulation_Duration = sim_years * 365
    config.parameters.Run_Number = 0
    return config
```

`set_team_defaults()` applies the malaria team's standard parameter set — a large collection of
validated defaults that gives a working malaria simulation without needing to set every parameter
individually.

`add_species()` adds the three *Anopheles* vector species present at most African sites. Each
species gets its own transmission parameters and habitat.

`Simulation_Duration` is in days, so `sim_years * 365` converts years to days.

## Demographics callback: build_demog

`build_demog` builds the demographics file that describes the simulated human population.

```python
def build_demog():
    demog = Demographics.from_template_node(lat=-3.2, lon=37.9, pop=1000,
                                            name="Tutorial_Site")
    demog.SetEquilibriumVitalDynamics()
    demog.SetAgeDistribution(Distributions.AgeDistribution_SSAfrica)
    return demog
```

`from_template_node()` creates a single-node population of 1000 people.

`SetEquilibriumVitalDynamics()` sets birth and death rates equal so the population size stays
roughly stable over the simulation.

`SetAgeDistribution()` initializes the population with a realistic age structure for
sub-Saharan Africa rather than starting everyone at the same age.

## Platform

The `Platform` specifies where simulations run. The tutorial includes commented-out blocks for
all three supported platforms — uncomment the one that matches your environment:

```python
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

## EMODTask

`EMODTask.from_default2()` assembles the simulation task from the callbacks and the paths to
the EMOD executable and schema:

```python
task = emod_task.EMODTask.from_default2(
    config_path="config.json",
    eradication_path=manifest.eradication_path,
    campaign_builder=None,
    schema_path=manifest.schema_file,
    ep4_custom_cb=None,
    param_custom_cb=set_param_fn,
    demog_builder=build_demog,
    plugin_report=None
)
```

`campaign_builder=None` means no interventions are added — the population runs under baseline
transmission only. Campaigns are introduced in Tutorial 3.

## Running the experiment

`SimulationBuilder` manages parameter sweeps across simulations. Tutorial 1 runs a single
simulation by sweeping `Run_Number` over just one value:

```python
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

Each simulation directory is where EMOD runs. If a simulation fails, check `stderr.txt` and
`stdout.txt` in that directory to diagnose the problem. The output report files are also in
that directory — Tutorial 2 introduces a more convenient way to retrieve them.

## Next

[Tutorial 2](tutorial-2.md) adds output reports, downloads them, and plots the results.
