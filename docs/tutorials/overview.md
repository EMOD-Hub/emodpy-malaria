# emodpy-malaria Tutorials

These tutorials walk through the core emodpy-malaria workflow step by step, from running a single simulation to calibrating transmission and evaluating intervention impact against a population with a realistic history of infections and immunity. Each tutorial builds directly on the previous one — the Python script for each tutorial is a clean diff of the last, so the diff itself is the lesson.

## Prerequisites

Before starting, complete the [setup](setup.md) page to install dependencies and confirm your environment is working.

If you are new to EMOD, read [EMOD input files](concepts.md) for a brief overview of the configuration, demographics, campaign, and report concepts used throughout the tutorials.

The tutorials run on the **Container platform** by default (Docker, works locally or in Codespaces). Each script also shows commented-out COMPS and SLURM platform blocks if you are going to run on a cluster.

## Tutorials

| # | Title | What you'll learn |
|---|-------|-------------------|
| [1](tutorial-1.md) | Run your first simulation | EMODTask, demographics, config callbacks, running an experiment |
| [2](tutorial-2.md) | Reports | MalariaSummaryReport, downloading results, plotting InsetChart |
| [3](tutorial-3.md) | Interventions | Campaign files, treatment seeking, ITNs, comparing scenarios |
| [4](tutorial-4.md) | Seasonality | LINEAR_SPLINE habitat, multi-year runs, seasonal transmission patterns |
| [5](tutorial-5.md) | Sweep parameters | SimulationBuilder, cross-product sweeps, parametrized campaigns |
| [6](tutorial-6.md) | Calibration | CalibManager, OptimTool, scoring simulations against reference data |
| [7](tutorial-7.md) | Serialization | Burnin to build immunity, serialized population files, pickup with interventions |

## Tutorial scripts

All Python scripts live in the `tutorials/` directory alongside this documentation:

```
tutorials/
    manifest.py               shared paths and platform settings
    tutorial_1_intro.py
    tutorial_2_reports.py
    tutorial_3_interventions.py
    tutorial_4_seasonality.py
    tutorial_5_sweep.py
    tutorial_6_calibration.py
    tutorial_6_reference_pfpr.csv
    tutorial_7_burnin.py
    tutorial_7_pickup.py
```

Tutorials 1–6 can be run independently — each script is self-contained. Tutorial 7 has two
values that must be carried forward from earlier tutorials: `CALIBRATED_LOG10_X_LARVAL_HABITAT`
from Tutorial 6 (a default is provided so you can run without it) and `BURNIN_EXP_ID` in the
pickup script, which requires the burnin to have been run first.
