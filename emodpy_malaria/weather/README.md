# Weather (Climate)
This submodule provides features for working with weather input files used by EMOD. 

## Getting Started
Below examples illustrate the simplest way to use Weather API for weather files scenarios.

```python
import tempfile
from pathlib import Path

from emodpy_malaria.weather import *

# ---| Request weather files |--- 

# Request weather time series from 2015 to 2016, for nodes listed in a .csv file
wr = generate_weather(platform="SLURMStage",
                      site_file="tests/unittests/weather/ssmt/sites.csv",
                      start_date=2015,
                      end_date=2016,
                      node_column="nodes",
                      local_dir=tempfile.mkdtemp())   

# Generated weather files are downloaded into a local dir, if specified. 
print("\n".join(wr.files))


# ---| Convert to a dataframe |--- 

# Convert weather files to a dataframe and weather attributes
df, wa = weather_to_csv(weather_dir=wr.local_dir)     
print(df.head())


# ---| Modify and save |---

# Modify weather data (for example)
df["airtemp"] += 1.1    
print(df.head())

# Generate modified weather files (see "Weather Objects" section
weather_dir = tempfile.mkdtemp()
ws = csv_to_weather(csv_data=df, attributes=wa, weather_dir=weather_dir)
print(list(Path(weather_dir).glob("*")))
```

# Weather Objects
This section shows Weather API objects and methods you can use to work with weather files.

Examples will demonstrate use of the following classes:
- WeatherData 
  - Represents time series of a single weather variable (like air temperature).
  - Generates a .bin file.
- WeatherMetadata 
  - Represents metadata (attributes, node/time-series counts, node offsets).
  - Generates  .bin.json file.
- WeatherSet 
  - Represents time series for all weather variables. 
  - Encapsulates WeatherData and WeatherMetadata objects, one pair for each weather variable.
  - Generates all weather files by calling WeatherData and WeatherMetadata methods

## Create Weather Files Locally
  
### From Array 
This example shows how to create an 'air temperature' weather file. Time series are specified using a 2x3 Numpy array:
- 2 time series, one for each node (rows)
- 3 values in each time series (columns)

Node ids and metadata is auto-generated in this case. Nodes are enumerated (1, 2) and metadata is using default values. 
```python
import tempfile
from pathlib import Path

from emodpy_malaria.weather import *

# ---| Create |---

# Instantiate a weather data object (representing air_temperature).
wd = WeatherData(data=np.array([
                          [20.1, 20.2, 20.3], 
                          [20.4, 20.5, 20.6]]))

# Save time series to a file (node ids are auto generated).
weather_dir = tempfile.mkdtemp()
wd.to_file(Path(weather_dir).joinpath("dtk_air_temperature.bin"))
print(list(Path(weather_dir).glob("*")))
 

# ---| Inspect |---

# Use properties and methods to inspect weather objects:

# Access weather time series array (type was converted to np.float32, as required by EMOD). 
print(wd.data)
# [[20.1 20.2 20.3]
#  [20.4 20.5 20.6]]

# Access data as a dictionary of node ids and weather time series arrays.
print(wd.to_dict())
# {1: array([20.1, 20.2, 20.3], dtype=float32), 2: array([20.4, 20.5, 20.6], dtype=float32)}

# Access metadata
wm = wd.metadata

# Node offset dictionary.
print(wm.node_offsets)
# {1: 0, 2: 12}

# Node offset string. 
print(wm.node_offset_str)
# '0000000a00000000000000140000000c'

# Key attributes.
print(wm.id_reference)
# 'Default'

# Metadata attribute dictionary. 
print(wm.attributes_dict)
# {'DateCreated': '2022-03-07', 'IdReference': 'Default', 'datavalue_count': 3 ...}
```
### From Dictionary
This example shows how to create a weather file and explicitly specify node ids, weather time series and metadata attributes.
```python
from emodpy_malaria.weather import *

# Specify node ids and weather time series
data = {
    10: [20.1, 20.2, 20.3],
    20: [20.4, 20.5, 20.6]
}

# Specify basic metadata (recommended, optional).
meta = WeatherAttributes(start_year=2001,
                         end_year=2010,
                         provenance="Weather unittest file.")

# Initialize a weather data object.
wd = WeatherData.from_dict(node_series=data, attributes=meta)

print(wd.to_dict(), wd.metadata.node_offset_str)
```

### From CSV (Single Weather File)
This example shows how to create a weather file from a .csv file containing the following columns:
- "ids": containing node ids
- "time": containing time steps for each time series. 
- "data": containing weather time series values.

```python
from emodpy_malaria.weather import *

# Load data from a csv file  
data_path = "tests/unittests/weather/case_csv/data.csv"
wd = WeatherData.from_csv(data_path)

# Load data from a csv file and specify columns and metadata 
info = DataFrameInfo(node_column="nodes",
                     step_column = "steps",
                     value_column = "data")

meta = WeatherAttributes(start_year=2001, 
                         end_year=2010, 
                         provenance="Weather unittest file.")

wd = WeatherData.from_csv(file_path=data_path, info=info, attributes=meta)

print(wd.to_dict(), wd.metadata.node_offset_str)
```

### From a CVS (All Weather Files)
This example shows a way to create all weather files required by EMOD from a single csv file using WeatherSet class.  
In this case each weather variable has a separate column, as specified in the weather_columns dictionary. 
```python
import tempfile
from pathlib import Path

from emodpy_malaria.weather import *

weather_columns = {
    WeatherVariable.AIR_TEMPERATURE: "temp",
    WeatherVariable.RELATIVE_HUMIDITY: "humid",
    WeatherVariable.RAINFALL: "rain",
    WeatherVariable.LAND_TEMPERATURE: "land"
}
 
meta = WeatherAttributes(start_year=2001, 
                         end_year=2010, 
                         provenance="Weather unittest file.")

ws = WeatherSet.from_csv(file_path="tests/unittests/weather/case_csv/data_all.csv",                  
                         node_column="node",
                         step_column="step",
                         weather_columns=weather_columns,
                         attributes=meta)

# Access individual weather files
wd = ws[WeatherVariable.AIR_TEMPERATURE]

# Create all three weather files
weather_dir = tempfile.mkdtemp()
ws.to_files(dir_path=weather_dir)
print(list(Path(weather_dir).glob("*")))
```

## Requesting Weather Files
Request and download weather files:
```python
from emodpy_malaria.weather import *

# Request weather files
wa = WeatherArgs(site_file="tests/unittests/weather/ssmt/sites.csv",
                 start_date=2015001,
                 end_date=2015007,
                 node_column="nodes",
                 id_reference="something")

wr: WeatherRequest = WeatherRequest(platform="SLURMStage")
wr.generate(weather_args=wa, request_name="ERA5 custom request")
wr.download()

print(f"Weather asset collection id: {wr.data_id}")
print(f"Files are downloaded in dir: {wr.local_dir}")  # same as out_dir

# Convert weather data to a dataframe
ws = WeatherSet.from_files(dir_path=wr.local_dir)
df = ws.to_dataframe()
print(df.head())
```

## Examples

For more usage examples see: 
- [Examples](../../examples/weather/)
- [Unit-tests](../../tests/unittests/weather/) 


## Feature Overview  

### Working with individual weather files   
- Create from numpy arrays and weather metadata.  
- Specify metadata or use defaults
- Auto generate node ids (if not provided)
- Calculate node offsets and node/time-series counts
- Optimize numpy array storage by storing distinct arrays and assigning node offset.
- Conversions (from/to): 
  - Dictionary (nodes-weather time series)
  - Pandas DataFrames (can specify columns names or use defaults)
  - CSV file (can specify columns names or use defaults)
  - EMOD weather files

### Working with a set of weather files
- Encapsulates all weather data and metadata files.
- Creating multiple weather files from a single .csv or dataframe
- Specifying weather file name prefix/suffix 
  - to select a subset of weather files
  - or to work with weather files with using custom name schema 
- Conversions (from/to):
  - Pandas DataFrames (can specify columns names or use defaults)
  - CSV file (can specify columns names or use defaults)
  - EMOD weather files

### Requesting weather files
- Submit COMPS SSMT requests to generate weather files.
- Specify temporal scope by specifying start/end time (formats: year, date, year-day).
- Specify spatial scope via a csv file containing node coordinates.
- Download generated files.
- Generate files only if given dir doesn't already contain those files.