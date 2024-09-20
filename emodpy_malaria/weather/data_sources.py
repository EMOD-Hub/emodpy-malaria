"""
Data sources metadata, a temporarily snapshot of data sources config, in the future to be removed with a
weather service API offers this metadata.
"""

import json

_data_source_metadata = """ 
{    
    "defaults": {
        "name": "ERA5"
    },
    "data_sources": {
        "ERA5": {
            "weather_variables": ["AIR_TEMPERATURE", "RELATIVE_HUMIDITY", "RAINFALL", "LAND_TEMPERATURE"],
            "min_date": "19790101",
            "max_date": "20211231",
            "arc_seconds": [
                900
            ],
            "provenance": {
                "name": "ERA5 hourly data on single levels from 1979 to present",
                "description": "Reanalysis dataset, downloaded from Copernicus Climate Change Service (C3S) using cdsapi client, aggregated by day.",
                "url": "https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels"
            }
        },
        "ERA5-LAND": {
            "weather_variables": ["AIR_TEMPERATURE", "RELATIVE_HUMIDITY", "RAINFALL", "LAND_TEMPERATURE"],
            "min_date": "20010101",
            "max_date": "20211231",
            "arc_seconds": [
                360
            ],
            "provenance": {
                "name": "ERA5-Land hourly data from 1950 to present",
                "description": "Reanalysis dataset, downloaded from Copernicus Climate Change Service (C3S) using cdsapi client, aggregated by day.",
                "url": "https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land"
            }
        },
        "TAMSATv3": {
            "weather_variables": ["RAINFALL"],
            "min_date": "20000101",
            "max_date": "20171231",
            "arc_seconds": [
                120
            ],
            "provenance": {
                "name": " TAMSATv3 daily rainfall estimates at 4 km resolution from 1983-present for the African continent.",
                "description": "Daily totals in mm. Blended product: incorporates both ground-based and satellite observational data. Produced by the University of Reading.",
                "url": "http://www.tamsat.org.uk/"
            }
        }
    }
}
"""


def _get_data_source_metadata():
    return json.loads(_data_source_metadata)
