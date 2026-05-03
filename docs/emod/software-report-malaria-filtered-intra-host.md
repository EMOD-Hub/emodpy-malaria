# ReportMalariaFilteredIntraHost


The malaria filtered intra-host report (ReportMalariaFilteredIntraHost.json) extends
[software-report-filtered-malaria](software-report-filtered-malaria.md) by replacing the standard InsetChart channels with a
focused set of within-host disease dynamics channels. It retains a small number of epidemiological
channels from the parent report and adds channels tracking infection stage distribution, cytokine
levels, MSP variant antibody fractions, and metrics on individuals carrying the maximum number of
simultaneous infections. Weather and vector channels are removed.


## Configuration


To generate this report, the following parameters must be configured in the custom_reports.json
file. All parameters are inherited from [software-report-filtered-malaria](software-report-filtered-malaria.md).

```
**Filename_Suffix**, string, NA, NA, (empty string), "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
**Start_Day**, float, 0, 3.40282e+38, 0, "The day of the simulation to start collecting data."
**End_Day**, float, 0, 3.40282e+38, 3.40282e+38, "The day of the simulation to stop collecting data."
**Node_IDs_Of_Interest**, array of integers, 0, 2.14748e+09, [], "Data will be collected for the nodes in this list. Empty list implies all nodes."
**Min_Age_Years**, float, 0, 9.3228e+35, 0, "Minimum age in years of people to collect data on."
**Max_Age_Years**, float, 0, 9.3228e+35, 9.3228e+35, "Maximum age in years of people to collect data on."
**Must_Have_IP_Key_Value**, string, NA, NA, (empty string), "A Key:Value pair that the individual must have in order to be included. Empty string means to not include IPs in the selection criteria."
**Must_Have_Intervention**, string, NA, NA, (empty string), "The name of the intervention that the person must have in order to be included. Empty string means to not include interventions in the selection criteria."
**Has_Interventions**, array of strings, NA, NA, [], "A channel is added to the report for each intervention name specified. The channel value is the fraction of the population that has that intervention."
**Include_30Day_Avg_Infection_Duration**, boolean, NA, NA, 1, "If set to true (1), the 30-Day Avg Infection Duration channel is included in the report.  See below for what the channel is."
```

```json
{
    "Reports": [
        {
            "class": "ReportMalariaFilteredIntraHost",
            "Filename_Suffix": "kids_400",
            "Start_Day": 0,
            "End_Day": 3.40282e+38,
            "Node_IDs_Of_Interest": [],
            "Min_Age_Years": 0,
            "Max_Age_Years": 10,
            "Must_Have_IP_Key_Value": "",
            "Must_Have_Intervention": "",
            "Has_Interventions": [],
            "Include_30Day_Avg_Infection_Duration": 1
        }
    ],
    "Use_Defaults": 1
}
```

## Channels


The following channels are included in the report.

```
30-day Avg Infection Duration, "A running average of the duration of each infection that cleared in the last 30 days (both naturally and due to drugs). Only included if **Include_30Day_Avg_Infection_Duration** is set to true."
Avg Cytokines, "The average cytokine level per person across the population."
Avg Num Infections, "The average number of infections, per person (infected people only) on that day. These are all the infections the individual has and may not be detectable by diagnostics. Note that this may not equal the number of infected people as people may have multiple infections."
Blood Smear Parasite Prevalence, "The fraction of the population that is detectable with the BLOOD_SMEAR_PARASITES version of **MalariaDiagnostic**. The detectability of the diagnostic is controlled by parameters **Report_Parasite_Smear_Sensitivity** and **Report_Detection_Threshold_Blood_Smear_Parasites**."
Campaign Cost, "The cost of campaigns cumulative up to that day (set by the **Cost_To_Consumer** parameter in each intervention)."
Fraction Infected, "The fraction of the statistical population that is currently infected."
Inf Frac-Stage 1 - Hepatocyte, "The fraction of all active infections currently in the hepatocyte stage."
Inf Frac-Stage 1 - Hepatocyte - New, "Of infections currently in the hepatocyte stage, the fraction that transitioned into that stage on this time step."
Inf Frac-Stage 2 - Asexual, "The fraction of all active infections currently in the asexual blood stage."
Inf Frac-Stage 2 - Asexual - New, "Of infections currently in the asexual stage, the fraction that transitioned into that stage on this time step."
Inf Frac-Stage 3 - Gametocytes Only, "The fraction of all active infections currently in the gametocyte-only stage (asexual parasites cleared)."
Inf Frac-Stage 3 - Gametocytes Only - New, "Of infections currently in the gametocyte-only stage, the fraction that transitioned into that stage on this time step."
Infection Duration Max, "The duration in days of the longest-running active infection across all individuals at this time step."
Max Inf-Avg Duration, "The average infection duration among individuals who are carrying the maximum allowed number of simultaneous infections."
Max Inf-Pop Fraction, "The fraction of currently infected individuals who are carrying the maximum allowed number of simultaneous infections."
New Clinical Cases, "The number of new clinical cases on that day. This channel is controlled by the **Clinical_Fever_Threshold_Low** and **Clinical_Fever_Threshold_High** parameters. The amount that an individual's fever is above normal must be greater than both of these values to be considered clinical."
New Infections, "The number of *individuals* who got infected on that day. Because an individual could receive multiple infections in a single day, this is not the number of *total new infections* on that day. The **Malaria_Model** parameter controls the number of new infections possible per person per day."
Statistical Population, "The total number of individuals in the simulation on that day."
True Prevalence, "The fraction of the population that is detectable with the TRUE_PARASITE_DENSITY version of **MalariaDiagnostic**. The detectability of the diagnostic is controlled by the parameter **Report_Detection_Threshold_True_Parasite_Density**."
Variant Fraction-MSP, "The average fraction of MSP1 antibody variants present per person across the population."
Variant Fraction-PfEMP1 Major, "The average of the fraction of variants of the PfEMP1 var genes that an individual has had. The parameter **Falciparum_PfEMP1_Variants** defines the total number of possible variants. This channel indicates the average fraction that an individual has seen of this total number. The greater the fraction the more that the population has developed antibodies to the parasite."
```

## Example


The following is a sample of ReportMalariaFilteredIntraHost.json with 3 time steps.

```json
{
    "Header": {
        "DateTime": "Mon Apr 13 23:49:19 2026",
        "DTK_Version": "2.33.0 jammy_jellyfish(26cf0505) Apr 13 2026 22:25:02",
        "Report_Type": "InsetChart",
        "Report_Version": "3.2",
        "Start_Time": 0,
        "Simulation_Timestep": 1,
        "Timesteps": 3,
        "Channels": 21
    },
    "Channels": {
        "30-day Avg Infection Duration": {
            "Units": "",
            "Data": [
                34.39166641235,
                30.69079017639,
                32.65899276733
            ]
        },
        "Avg Cytokines": {
            "Units": "",
            "Data": [
                0.05802467465401,
                0.0510664395988,
                0.05226223543286
            ]
        },
        "Avg Num Infections": {
            "Units": "",
            "Data": [
                2.253846168518,
                2.176470518112,
                2.152454853058
            ]
        },
        "Blood Smear Parasite Prevalence": {
            "Units": "",
            "Data": [
                0.3131749331951,
                0.2909482717514,
                0.3254310488701
            ]
        },
        "Campaign Cost": {
            "Units": "USD",
            "Data": [
                5172,
                5192,
                5216
            ]
        },
        "Fraction Infected": {
            "Units": "",
            "Data": [
                0.8423326015472,
                0.8426724076271,
                0.8340517282486
            ]
        },
        "Inf Frac-Stage 1 - Hepatocyte": {
            "Units": "",
            "Data": [
                0.1581342369318,
                0.1492361873388,
                0.1500600278378
            ]
        },
        "Inf Frac-Stage 1 - Hepatocyte - New": {
            "Units": "",
            "Data": [
                0.1079136654735,
                0.1417322903872,
                0.1599999964237
            ]
        },
        "Inf Frac-Stage 2 - Asexual": {
            "Units": "",
            "Data": [
                0.5961319804192,
                0.620446562767,
                0.6278511285782
            ]
        },
        "Inf Frac-Stage 2 - Asexual - New": {
            "Units": "",
            "Data": [
                0.04198473319411,
                0.06060606241226,
                0.05162524059415
            ]
        },
        "Inf Frac-Stage 3 - Gametocytes Only": {
            "Units": "",
            "Data": [
                0.245733782649,
                0.2303172796965,
                0.2220888286829
            ]
        },
        "Inf Frac-Stage 3 - Gametocytes Only - New": {
            "Units": "",
            "Data": [
                0.1851851791143,
                0.1224489808083,
                0.1405405402184
            ]
        },
        "Infection Duration Max": {
            "Units": "",
            "Data": [
                167,
                168,
                138
            ]
        },
        "Max Inf-Avg Duration": {
            "Units": "",
            "Data": [
                18.65841674805,
                19.48648643494,
                19.36666679382
            ]
        },
        "Max Inf-Pop Fraction": {
            "Units": "",
            "Data": [
                0.5179487466812,
                0.4731457829475,
                0.4651162922382
            ]
        },
        "New Clinical Cases": {
            "Units": "",
            "Data": [
                10,
                14,
                16
            ]
        },
        "New Infections": {
            "Units": "",
            "Data": [
                15,
                18,
                20
            ]
        },
        "Statistical Population": {
            "Units": "Population",
            "Data": [
                463,
                464,
                464
            ]
        },
        "True Prevalence": {
            "Units": "",
            "Data": [
                0.5572354197502,
                0.5517241358757,
                0.5431034564972
            ]
        },
        "Variant Fraction-MSP": {
            "Units": "",
            "Data": [
                0.515051305294,
                0.5143453478813,
                0.5150862336159
            ]
        },
        "Variant Fraction-PfEMP1 Major": {
            "Units": "",
            "Data": [
                0.2465250939131,
                0.2463604211807,
                0.2467168867588
            ]
        }
    }
}
```
