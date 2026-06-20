# Tutorial 9: Weather files

Earlier tutorials used `CLIMATE_CONSTANT` mode, where every node receives the same air
temperature, rainfall, and relative humidity on every time step. Real simulations need
site-specific weather that varies over time — daily temperature swings, seasonal rainfall
patterns, and humidity gradients across nodes. This tutorial shows how to create and add weather data
to your EMOD simulation.

**File:** `tutorials/tutorial_9_weather.py`

## How EMOD uses weather

EMOD's `CLIMATE_BY_DATA` mode reads weather from binary files — one pair of files (`.bin` +
`.bin.json`) per weather variable. Three variables are required for malaria simulations:

| Variable | Unit | Effect on transmission                                                                                  |
|----------|------|---------------------------------------------------------------------------------------------------------|
| Air temperature | Celsius | Controls mosquito development rate, sporogony duration, adult mortality, temporary habitat evaportation |
| Rainfall | mm/day | Drives larval habitat availability for `TEMPORARY_RAINFALL` habitat types                               |
| Relative humidity | 0.0 -- 1.0 | Affects adult mosquito mortality                                                                        |

EMOD also requires a land temperature file, but does not use it for malaria. emodpy-malaria
handles this automatically by reusing the air temperature file for land temperature — you
never need to create or manage land temperature data separately.

## Weather data structure

Weather data is a time series of float values per node. If you have 3 nodes and 365 daily
time steps, each weather variable contains 3 x 365 = 1095 values. All three variables must
have the same nodes and the same number of time steps.

The `WeatherSet` class manages all three variables together and ensures they stay consistent.
Each individual variable's data is held in a `WeatherData` object.


## Getting real weather data

There are many sources of historical weather data suitable for EMOD simulations — ERA5
reanalysis, CHIRPS rainfall, NOAA GSOD station records, national meteorological services, and
others. Wherever you get your data, it will need to be converted into a DataFrame (or CSV)
with columns `node`, `step`, `airtemp`, `humidity`, and `rainfall` before emodpy-malaria can
use it. Each row represents one node at one time step. The node column holds the EMOD node ID
(matching your demographics), the step column holds a sequential integer (0, 1, 2, ...),
and the three weather columns hold the values in the units EMOD expects: Celsius for
temperature, mm/day for rainfall, and a fraction (0.0--1.0) for relative humidity.

Each step in the data corresponds to one update interval, which you specify via
`update_resolution` in `add_weather()`. The supported resolutions are:

| Resolution | Data points per year | Meaning |
|------------|---------------------|---------|
| `CLIMATE_UPDATE_YEAR` | 1 | One value per year — constant for the entire year |
| `CLIMATE_UPDATE_MONTH` | 12 | One value per month — constant for that month |
| `CLIMATE_UPDATE_WEEK` | 52 | One value per week — constant for that week |
| `CLIMATE_UPDATE_DAY` | 365 | One value per day (most common) |
| `CLIMATE_UPDATE_HOUR` | 8760 | One value per hour |

For example, if you have 12 data points per node and set
`update_resolution=ClimateUpdateResolution.CLIMATE_UPDATE_MONTH`, EMOD applies each value
for an entire month before advancing to the next. If your source data has different
resolutions for different variables — say daily temperature but monthly rainfall — set
`update_resolution` to the highest resolution (daily) and repeat the lower-resolution values
to fill every step. For monthly rainfall, fill each day's value into all 28--31 daily
steps for that month, dividing the monthly rainfall by the number of days to get mm/day.

## Creating weather from a DataFrame

The most common workflow is to start with tabular weather data — from a CSV file, a database
query, or a climate API — and convert it into EMOD weather files. The data must have columns
for node ID, time step, and each weather variable. This example creates synthetic weather 
data for two nodes over 30 days, with daily temperature, rainfall, and humidity values:

```python
import pandas as pd
from emodpy_malaria.weather import WeatherVariable, WeatherSet

# B a DataFrame with daily weather for two nodes over 30 days
rows = []
for node_id in [1, 2]:
    for step in range(30):
        rows.append({
            "node": node_id,
            "step": step,
            "airtemp": 25.0 + 3.0 * (node_id - 1) + 0.5 * (step % 7),
            "rainfall": max(0, 8.0 - 0.2 * step + 2.0 * (step % 10 < 3)),
            "humidity": 0.70 + 0.05 * (node_id - 1),
        })
df = pd.DataFrame(rows)
```

Convert the DataFrame to a `WeatherSet` by specifying which columns map to which variables:

```python
ws = WeatherSet.from_dataframe(
    df,
    node_column="node",
    step_column="step",
    weather_columns={
        WeatherVariable.AIR_TEMPERATURE: "airtemp",
        WeatherVariable.RAINFALL: "rainfall",
        WeatherVariable.RELATIVE_HUMIDITY: "humidity",
    },
    notes="ERA5 reanalysis, bilinear interpolation to node centroids, 2015-2020",
)
```

`node_column` and `step_column` identify the node and time-step columns. `weather_columns`
maps each `WeatherVariable` to the column name containing that variable's data. The optional
`notes` parameter is stored in the weather file metadata — use it to record where the
original data came from and how it was processed, so that anyone reading the files later can
trace their provenance. If your
columns are named `nodes`, `steps`, `airtemp`, `humidity`, and `rainfall`, the defaults will
detect them automatically and you can omit the column arguments.

## Creating weather from a CSV file

If your data is already in a CSV file, use `WeatherSet.from_csv()` instead. It takes the same
column arguments:

```python
ws = WeatherSet.from_csv(
    "my_weather_data.csv",
    node_column="node_id",
    step_column="day",
    weather_columns={
        WeatherVariable.AIR_TEMPERATURE: "temp_c",
        WeatherVariable.RAINFALL: "rain_mm",
        WeatherVariable.RELATIVE_HUMIDITY: "rh",
    },
)
```

## Adding weather to the simulation

Because weather is tied to demographics, we add weather to the simulation via the demographics object. 
`add_weather()` on the demographics object validates the weather data, writes the binary
files, and registers an implicit config function that sets EMOD's climate parameters at build
time. This follows the same pattern as `add_migration()` from
[Tutorial 8](tutorial-8.md).

```python
from emod_api.demographics.node import Node
from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
from emodpy_malaria.utils.distributions import ExponentialDistribution
from emodpy_malaria.utils.emod_enum import ClimateUpdateResolution

def build_demographics():
    nodes = [
        Node(lat=-2.0, lon=32.0, pop=5000, forced_id=1, name="Site_A"),
        Node(lat=-2.5, lon=32.5, pop=3000, forced_id=2, name="Site_B"),
    ]
    demog = MalariaDemographics(nodes=nodes, idref="tutorial_9")
    demog.set_birth_rate(40)
    demog.set_age_distribution(ExponentialDistribution(20))

    # Create weather (from DataFrame or CSV)
    ws = create_weather()

    demog.add_weather(
        data=ws,
        update_resolution=ClimateUpdateResolution.CLIMATE_UPDATE_DAY
    )

    return demog
```

File names are generated automatically from the variable name and the update resolution.
For example, with `CLIMATE_UPDATE_DAY` the files will be named `airtemp_daily.bin`,
`rainfall_daily.bin`, and `humidity_daily.bin`. You can prepend a prefix to all file names
with the `prefix` parameter:

```python
demog.add_weather(
    data=ws,
    prefix="era5_",
    update_resolution=ClimateUpdateResolution.CLIMATE_UPDATE_DAY
)
# Produces: era5_airtemp_daily.bin, era5_rainfall_daily.bin, era5_humidity_daily.bin
```

### What add_weather does

1. **Validates type** — `data` must be a `WeatherSet` instance.
2. **Checks variables** — The set must contain `AIR_TEMPERATURE`, `RAINFALL`, and
   `RELATIVE_HUMIDITY`.
3. **Validates nodes** — Weather data nodes must exactly match demographics nodes — no
   extra and no missing nodes are allowed.
4. **Sets IdReference** — The weather files' `IdReference` is set to the demographics
   `idref`. You do not need to set it on the `WeatherSet` yourself. 
5. **Writes binary files** — Three `.bin` / `.bin.json` file pairs are written to disk.
6. **Registers assets** — The files are added to the simulation's asset list.
7. **Sets config** — An implicit config function is registered that sets `Climate_Model`,
   filenames, offsets, scale factors, and stochasticity parameters when the task is built.

### Validation

Node validation prevents a common error: weather files with node IDs that do not match the
demographics. The weather data must contain exactly the same nodes as the demographics — no
extra nodes and no missing nodes. If there is a mismatch, `add_weather()` raises a
`ValueError`:

```
ValueError: Weather data nodes must exactly match demographics nodes. extra nodes in weather data: [3]
```

```
ValueError: Weather data nodes must exactly match demographics nodes. missing nodes in weather data: [2]
```

## Offsets, scale factors, and stochasticity

`add_weather()` accepts parameters that modify how EMOD applies the weather data at runtime.
These do not change the binary files — they are set in the EMOD config.

```python
demog.add_weather(
    data=ws,
    update_resolution=ClimateUpdateResolution.CLIMATE_UPDATE_DAY,
    air_temperature_offset=1.5,
    rainfall_scale_factor=0.8,
    air_temperature_variance=2.0,
    relative_humidity_variance=0.05,
    enable_rainfall_stochasticity=True
)
```

| Parameter | Type | Default | Effect |
|-----------|------|---------|--------|
| `prefix` | str | `""` | String prepended to each weather file name (e.g. `"era5_"`) |
| `update_resolution` | `ClimateUpdateResolution` | `CLIMATE_UPDATE_DAY` | How often EMOD reads new values from the weather files |
| `air_temperature_offset` | float | 0.0 | Additive offset (Celsius) applied to all air temperature values |
| `rainfall_scale_factor` | float | 1.0 | Multiplicative factor applied to all rainfall values |
| `relative_humidity_scale_factor` | float | 1.0 | Multiplicative factor applied to all relative humidity values |
| `air_temperature_variance` | float | 0.0 | Standard deviation (Celsius) for Gaussian noise on daily temperature |
| `relative_humidity_variance` | float | 0.0 | Standard deviation for Gaussian noise on daily humidity |
| `enable_rainfall_stochasticity` | bool | False | Draw daily rainfall from an exponential distribution with mean equal to the data value |

When any variance is non-zero or `enable_rainfall_stochasticity` is True,
`Enable_Climate_Stochasticity` is set automatically. You do not need to set it yourself.

These parameters are useful for sensitivity analysis — for example, testing how a +1.5 C
temperature increase or a 20% rainfall reduction affects transmission.

## Using constant climate

Not every simulation needs weather files. For simple experiments, constant climate avoids the
overhead of creating binary files. Use `set_climate_constant()` directly in your config
callback:

```python
from emodpy_malaria.weather import set_climate_constant

def build_config(config):
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    set_climate_constant(
        config,
        air_temperature=27.0,
        rainfall=10.0,
        relative_humidity=0.75
    )

    config.parameters.Simulation_Duration = 365
    config.parameters.Run_Number = 0
    return config
```

`set_climate_constant()` also supports stochasticity parameters:

```python
set_climate_constant(
    config,
    air_temperature=27.0,
    rainfall=10.0,
    relative_humidity=0.75,
    air_temperature_variance=2.0,
    enable_rainfall_stochasticity=True
)
```

## Config callback with weather files

When using `add_weather()`, the config callback does not need to set any climate parameters —
they are handled by the implicit function registered by `add_weather()`. Just make sure to
**not** call `set_climate_constant()` or manually set `Climate_Model`, as the implicit will
override it.

```python
def build_config(config):
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    # No climate config here — add_weather() handles it

    config.parameters.Simulation_Duration = 365
    config.parameters.Run_Number = 0
    return config
```

## Loading existing weather files

If you have EMOD weather files from a previous run or an external tool, load them with
`WeatherSet.from_files()`:

```python
ws = WeatherSet.from_files(
    dir_path="path/to/weather_files",
    prefix="dtk_15arcmin_",
)
```

`from_files()` looks for `.bin` files matching the prefix and known variable name patterns
(`airtemp`, `rainfall`, `humidity`). You can also specify exact filenames:

```python
ws = WeatherSet.from_files(
    dir_path="path/to/weather_files",
    file_names={
        WeatherVariable.AIR_TEMPERATURE: "my_airtemp.bin",
        WeatherVariable.RAINFALL: "my_rainfall.bin",
        WeatherVariable.RELATIVE_HUMIDITY: "my_humidity.bin",
    },
)
```

The loaded `WeatherSet` can be passed to `add_weather()` like any other.

## Converting between formats

The weather module provides convenience functions for converting between CSV and binary
formats:

```python
from emodpy_malaria.weather import csv_to_weather, weather_to_csv

# CSV → binary weather files
ws = csv_to_weather(
    "weather_data.csv",
    node_column="node",
    step_column="step",
    weather_dir="output/weather",
)

# Binary weather files → CSV + attributes
df, attributes = weather_to_csv(
    weather_dir="output/weather",
    csv_file="weather_roundtrip.csv",
)
```

## Weather files on disk

After `add_weather()` writes the files, you will see three pairs in the output directory:

```
airtemp.bin           # air temperature binary data
airtemp.bin.json      # air temperature metadata
rainfall.bin          # rainfall binary data
rainfall.bin.json     # rainfall metadata
humidity.bin          # relative humidity binary data
humidity.bin.json     # relative humidity metadata
```

The `.bin` file contains raw IEEE 754 float32 values — the time series for each node laid out
sequentially. The `.bin.json` file contains metadata including the `IdReference`, node count,
data value count, and a hex-encoded node offset string that maps each node ID to its byte
offset in the binary file.

## Putting it together

The complete tutorial script creates synthetic weather as a DataFrame, attaches it to a
two-node demographics, and runs the simulation:

```python
import numpy as np
import pandas as pd
import pathlib

import emod_malaria.bootstrap as dtk
from emod_api.demographics.node import Node
from emodpy.emod_task import EMODTask
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

from emodpy_malaria import malaria_config
from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
from emodpy_malaria.utils.distributions import ExponentialDistribution
from emodpy_malaria.utils.emod_enum import ClimateUpdateResolution
from emodpy_malaria.weather import WeatherVariable, WeatherSet

import manifest

sim_years = 3


def build_config(config):
    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    config.parameters.Simulation_Duration = sim_years * 365
    config.parameters.Run_Number = 0
    return config


def build_demographics():
    nodes = [
        Node(lat=-2.0, lon=32.0, pop=5000, forced_id=1, name="Site_A"),
        Node(lat=-2.5, lon=32.5, pop=3000, forced_id=2, name="Site_B"),
    ]
    demog = MalariaDemographics(nodes=nodes, idref="tutorial_9")
    demog.set_birth_rate(40)
    demog.set_age_distribution(ExponentialDistribution(20))

    # --- Create synthetic weather as a DataFrame ---
    n_steps = sim_years * 365
    day = np.arange(n_steps)
    rows = []
    for node_id in [1, 2]:
        for d in range(n_steps):
            rows.append({
                "node": node_id,
                "step": d,
                "airtemp": 22.0 + 5.0 * (node_id - 1) + 5.0 * np.sin(2 * np.pi * d / 365),
                "rainfall": max(0.0, (8.0 + 5.0 * (node_id - 1)) * np.sin(2 * np.pi * d / 365)),
                "humidity": 0.65 + 0.15 * (node_id - 1),
            })
    df = pd.DataFrame(rows)

    ws = WeatherSet.from_dataframe(
        df,
        node_column="node",
        step_column="step",
        weather_columns={
            WeatherVariable.AIR_TEMPERATURE: "airtemp",
            WeatherVariable.RAINFALL: "rainfall",
            WeatherVariable.RELATIVE_HUMIDITY: "humidity",
        },
    )

    demog.add_weather(
        data=ws,
        update_resolution=ClimateUpdateResolution.CLIMATE_UPDATE_DAY,
    )

    return demog


if __name__ == "__main__":
    platform = Platform("Container", job_directory="tutorial_9")
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)

    task = EMODTask.from_defaults(
        config_builder=build_config,
        schema_path=manifest.schema_file,
        demog_builder=build_demographics,
        campaign_builder=None,
    )

    experiment = Experiment.from_task(task, name="tutorial_9_weather")
    experiment.run(wait_until_done=True, platform=platform)
```

## Next

This tutorial covered site-specific weather for data-driven climate. For constant climate
simulations or quick prototyping, `set_climate_constant()` can be called directly in the
config callback without creating any weather files.
