# Tutorial 3: Interventions

This tutorial adds two interventions that represent a standard malaria control package:
treatment-seeking care and insecticide-treated nets (ITNs). It introduces the campaign file
and shows how to compare scenarios with and without interventions.

**File:** `tutorials/tutorial_3_interventions.py`

## The campaign file

The campaign file defines what interventions to distribute, to whom, and when. In emodpy-malaria
a `build_campaign()` function constructs this file and is passed to `EMODTask` via
`campaign_builder=`:

```python
task = EMODTask.from_defaults(
    ...,
    campaign_builder=build_campaign,   # previously None
    ...
)
```

## Interventions

`build_campaign()` builds the campaign using the class-based intervention API. Each
intervention is instantiated as an object and distributed via `add_intervention_triggered()`
or `add_intervention_scheduled()`:

```python
def build_campaign():
    campaign.set_schema(manifest.schema_path)

    if use_treatment_seeking:
        clinical_drug = AntimalarialDrug(campaign, drug_type="Artemether")
        clinical_diag = MalariaDiagnostic(
            campaign,
            diagnostic_type=DiagnosticType.FEVER,
            positive_diagnosis=clinical_drug
        )
        add_intervention_triggered(
            campaign,
            intervention_list=[clinical_diag],
            triggers_list=["NewClinicalCase"],
            start_day=365
        )

    if use_itn:
        bednet = SimpleBednet(
            campaign,
            repelling_config=Exponential(initial_effect=0.6, decay_rate=1.0/730),
            blocking_config=Exponential(initial_effect=0.9, decay_rate=1.0/730),
            killing_config=Exponential(initial_effect=0.1, decay_rate=1.0/1460)
        )
        add_intervention_scheduled(
            campaign,
            intervention_list=[bednet],
            start_day=365,
            target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.5)
        )

    return campaign
```

**Treatment seeking** uses `MalariaDiagnostic` to detect clinical cases and `AntimalarialDrug`
as the positive diagnosis action. The diagnostic and drug are wrapped together — when the
diagnostic fires on a `NewClinicalCase` event, it distributes the drug to positive cases.
Both interventions start on day 365, giving the population one year to reach a baseline before
any control begins.

**ITN distribution** uses `SimpleBednet` with waning effect configurations for repelling,
blocking, and killing. `Exponential` waning effects decay over time — the `decay_rate`
controls how quickly effectiveness drops. `TargetDemographicsConfig` sets the coverage to 50%.

## Comparing scenarios

Two boolean flags at the top of the script control which interventions are active:

```python
use_treatment_seeking = True
use_itn = True
```

Toggle these and re-run to compare each intervention separately against the no-intervention
baseline. Each combination writes to its own output directory:

| `use_treatment_seeking` | `use_itn` | Output directory |
|---|---|---|
| True | True | `tutorial_3_results` |
| True | False | `tutorial_3_results_ts` |
| False | True | `tutorial_3_results_itn` |
| False | False | `tutorial_3_results_no_interventions` |

## Plotting with a baseline reference

`plot_results()` looks for `tutorial_2_results/` from the previous tutorial and, if found,
uses it as the no-intervention reference (plotted in red) so the intervention impact is
visible directly. If you are starting here without having run Tutorial 2, the plot will still
work — the reference line simply will not appear.

```python
reference = None
if os.path.exists("tutorial_2_results"):
    t2_files = get_filenames(dir_or_filename="tutorial_2_results",
                             file_prefix="InsetChart", file_extension="json")
    if t2_files:
        reference = t2_files[0]

plot_inset_chart(dir_name=output_path,
                 reference=reference,
                 title="Tutorial 3 - InsetChart",
                 output=output_path)
```

Treatment seeking reduces the fraction of people infected; ITNs reduce the daily biting rate
and vector population. Running each combination separately lets you see each effect in
isolation.

## Example output

**Both interventions** (`use_treatment_seeking = True`, `use_itn = True`)

![Tutorial 3 - both interventions](images/tutorial-3/Tutorial_3_-_InsetChart.png)

**Treatment seeking only** (`use_treatment_seeking = True`, `use_itn = False`)

![Tutorial 3 - treatment seeking only](images/tutorial-3/Tutorial_3_ts_-_InsetChart.png)

**ITN only** (`use_treatment_seeking = False`, `use_itn = True`)

![Tutorial 3 - ITN only](images/tutorial-3/Tutorial_3_itn_-_InsetChart.png)

**No interventions** (`use_treatment_seeking = False`, `use_itn = False`)

![Tutorial 3 - no interventions](images/tutorial-3/Tutorial_3_none-_InsetChart.png)

## Next

[Tutorial 4](tutorial-4.md) introduces seasonal transmission by replacing the constant larval
habitat with a LINEAR_SPLINE.
