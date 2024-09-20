#!/usr/bin/env python3

"""
Walk through weather scenarios: generating weather files, convert to csv and back to weather, update and save to file.
"""
from datetime import datetime, timedelta
from emodpy_malaria.weather import *

weather_dir1 = "output/demo1"           # both string and Path
weather_dir2 = Path("output/demo2")     # are supported
csv_file = Path(weather_dir1).joinpath("weather.csv")

print("\n---=| WEATHER REQUEST |=---\n")

# Request weather files
startdate = (datetime.today() - timedelta(180+365)).replace(day=1).strftime('%Y%j')
enddate= (datetime.today() - timedelta(180)).replace(day=1).strftime('%Y%j')
wr = generate_weather(platform="Calculon",
                      site_file="input/site_details.csv",
                      start_date=startdate,
                      end_date=enddate,
                      node_column="id",
                      id_reference="Custom user",
                      local_dir=weather_dir1)

assert wr.files_exist
print("Weather request files:")
print("\n".join(wr.files))

print("\n---=| WEATHER OBJECTS |=---\n")

# Load weather files into a weather set object
ws1 = WeatherSet.from_files(weather_dir1)

# List of all weather variables (just to show them all explicitly)
all_weather_variables = [WeatherVariable.AIR_TEMPERATURE,
                         WeatherVariable.RELATIVE_HUMIDITY,
                         WeatherVariable.RAINFALL,
                         WeatherVariable.LAND_TEMPERATURE]

# List of all weather variables is available in WeatherVariable
assert WeatherVariable.list() == all_weather_variables

# WeatherSet contains the list weather variables it contains
assert ws1.weather_variables == all_weather_variables

# WeatherSet is dictionary-like, it supports "items" and "values" methods
print("Data")
for v, wd in ws1.items():
    print(v.name)
    print(wd.data)
    print(wd.metadata.attributes_dict)


print("\n---=| CONVERSION & EDITING |=---\n")

# Convert weather files into csv and dataframe
df, wa = weather_to_csv(weather_dir=wr.local_dir, csv_file=csv_file)

# Convert csv back to a weather set object
ws2 = csv_to_weather(csv_data=csv_file, attributes=wa)

print(f"Original {WeatherVariable.AIR_TEMPERATURE.name} data")
wd2 = ws2[WeatherVariable.AIR_TEMPERATURE]
print(wd2.data)

# Update air temperate values and save
df["airtemp"] += 1.1
ws2 = csv_to_weather(csv_data=df, attributes=wa, weather_dir=weather_dir2)

print(f"\nUpdated {WeatherVariable.AIR_TEMPERATURE.name} data")
wd2 = ws2[WeatherVariable.AIR_TEMPERATURE]
print(wd2.data)

# Check all files exist
print("\nWeather set file names:")
for v, f in ws2.file_names.items():
    file_path = weather_dir2.joinpath(f)
    print(f"{v}: {str(file_path)}")
    assert file_path.is_file()

