# Demographics overlay files


You can specify multiple demographics files, which function as a "base layer" file and one
or more "overlay" files that override the base layer configuration. Overlay files can change the
value of parameters already specified in the base layer or add new parameters. Support for multiple
demographics layers allows for the following scenarios:

* Separating different sets of parameters and values into individual layers (for example, to separate
  those that are useful for specific diseases into different layers)
* Adding new parameters for a simulation into a new layer for easier prototyping
* Overriding certain parameters of interest in a new layer
* Overriding certain parameters for a particular sub-region
* Simulating subsets of a larger region for which input files have been constructed


To use an overlay file:

1. Select the demographics file to use as the base layer file. All nodes to be included in the simulation
    must be listed in this file.
1. In the metadata, make note of the **IdReference** value.

    You may change this value if you desire, but all input files for a simulation must have the
    same **IdReference** value. For more information about this parameter and the structure of
    demographics files in general, see [parameter-demographics](parameter-demographics.md).

1. Create one or more overlay files. Keep the following things in mind:

    * In the metadata, the value for **IdReference** must match the value in the base layer file and
      all other input files except configuration and campaign.
    * Any nodes listed in an overlay but not in the base layer will not be simulated.
    * If the demographics files include any JSON array elements, the entire array is overridden.
      You cannot add or remove individual elements in an array using an overlay file.
    * Overriding a parameter value on a node will not affect the other parameter values applied to
      that node.
    * Values set in the **Defaults** section of an overlay will be applied to all nodes listed in
      that file, not all nodes in the entire simulation. Therefore, an overlay file that includes a
      **Defaults** section but no **Nodes** section will not have any effect.

1. Place all demographics files in the directory where the other input files are stored.

1. In the *configuration file*, set **Demographics_Filenames** to an array that contains a
    comma-delimited list of demographics files, listing the base layer file first.

An example base layer demographics file and an overlay file is below. You can see that the overlay
adds the **TransmissionMatrix** for Heterogeneous Intra-Node Transmission (HINT) to only three of the five nodes (which correspond to
Washington state counties).

```json
{
    "Metadata": {
        "Author": "ewenger",
        "NodeCount": 5,
        "Tool": "table_to_demographics.py",
        "IdReference": "SampleContent",
        "DateCreated": "2013-08-01 15:37:16.853000"
    },
    "Defaults": {
        "NodeAttributes": {
            "BirthRate_DESCRIPTION": "Replacement of stable age distribution: Birth_Rate_Dependence=DEMOGRAPHIC_DEP_RATE (i.e. 14-45 year-old PossibleMothers)",
            "BirthRate": 0.00017675,

            "Airport": 0,
            "Region": 1,
            "Altitude": 0,
            "Seaport": 0
        },
        "IndividualAttributes": {

            "AgeDistribution_DESCRIPTION": "Box between age 0 and 60 years: Age_Initialization_Distribution_Type=DISTRIBUTION_SIMPLE",
            "AgeDistributionFlag": 1,
            "AgeDistribution1": 0,
            "AgeDistribution2": 21900,

            "PrevalenceDistribution_DESCRIPTION": "No initial infections",
            "PrevalenceDistributionFlag": 0,
            "PrevalenceDistribution1": 0,
            "PrevalenceDistribution2": 0,

            "RiskDistributionFlag": 0,
            "RiskDistribution1": 1,
            "RiskDistribution2": 0,

            "SusceptibilityDistributionFlag": 0,
            "SusceptibilityDistribution1": 1,
            "SusceptibilityDistribution2": 0,

            "MigrationHeterogeneityDistributionFlag": 0,
            "MigrationHeterogeneityDistribution1": 1,
            "MigrationHeterogeneityDistribution2": 0,

            "MortalityDistribution_DESCRIPTION": "WA state (1999-2010).  Source: wonder.cdc.gov",
            "MortalityDistribution": {
                "NumDistributionAxes": 2,
                "AxisNames": [ "gender", "age" ],
                "AxisUnits": [ "male=0,female=1", "years" ],
                "AxisScaleFactors": [ 1, 365 ],
                "NumPopulationGroups": [ 2, 15 ],
                "PopulationGroups": [
                    [ 0, 1 ],
                    [ 0, 1, 2.5, 7.5, 12.5, 17.5, 22.5, 30, 40, 50, 60, 70, 80, 90, 120 ]
                ],
                "ResultUnits": "annual deaths per 1000 individuals",
                "ResultScaleFactor": 0.00000273972602739726027397260273973,
                "ResultValues": [
                    [ 4.8, 0.2, 0.1, 0.2, 0.5, 1.1, 1.1, 1.7, 4.1, 9.2, 19.8, 53.7, 154.2, 1000, 1000 ],
                    [ 4.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.5, 1.1, 2.6, 5.5, 14.3, 40.1, 129.3, 1000, 1000 ]
                ]
            }
        }
    },
    "Nodes": [
        {
            "County": "Adams",
            "NodeAttributes": {
                "Latitude": 47.1274,
                "InitialPopulation": 19200,
                "Longitude": -118.38
            },
            "NodeID": 1
        },
        {
            "County": "Asotin",
            "NodeAttributes": {
                "Latitude": 46.3393,
                "InitialPopulation": 21800,
                "Longitude": -117.0482
            },
            "NodeID": 2
        },
        {
            "County": "Benton",
            "NodeAttributes": {
                "Latitude": 46.2068,
                "InitialPopulation": 183400,
                "Longitude": -119.7689
            },
            "NodeID": 3
        },
        {
            "County": "Chelan",
            "NodeAttributes": {
                "Latitude": 47.4235,
                "InitialPopulation": 73600,
                "Longitude": -120.3103
            },
            "NodeID": 4
        },
        {
            "County": "Clallam",
            "NodeAttributes": {
                "Latitude": 48.1181,
                "InitialPopulation": 72350,
                "Longitude": -123.4307
            },
            "NodeID": 5
        }
    ]
}
```

```json
{
    "Metadata": {
        "Author": "cwiswell",
        "NodeCount": 10,
        "Tool": "table_to_demographics.py",
        "IdReference": "SampleContent",
        "DateCreated": "2013-08-01 15:37:16.853000"
    },
    "Defaults": {
        "IndividualProperties": [
            {
                "Property": "Accessibility",
                "Values": [ "VaccineTake", "VaccineRefuse"],
                "Initial_Distribution": [ 0.85, 0.15],
                "TransmissionMatrix": {
                    "Route": "Contact",
                    "Matrix": [
                        [1.1, 0.3],
                        [0.3, 5.0]
                    ]
                }
            },
            {
                "Property": "Age_Bin",
                "Age_Bin_Edges_In_Years": [ 0, 5, 13, -1 ],
                "TransmissionMatrix": {
                    "Route": "Contact",
                    "Matrix": [
                        [1.4, 1.0, 1.0],
                        [1.0, 2.5, 0.7],
                        [1.0, 0.7, 1.0]
                    ]
                }
            }
        ]
    },
    "Nodes": [
        {
            "NodeID": 1
        },
        {
            "NodeID": 3
        },
        {
            "NodeID": 5
        }
    ]
}
```
