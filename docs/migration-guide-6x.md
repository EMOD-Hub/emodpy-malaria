# Migration Guide: emodpy-malaria 5.x → 6.x

**Versions:** 5.2.x → 6.0.3  
**emodpy dependency:** ~1.16 → ~3.3  
**emod-malaria:** ~2.35 (unchanged)

This guide walks through every breaking change using concrete before/after code.
For the complete inventory of what was added, removed, and restructured, see the
[changelog](changes-5x-to-6x.md).

---

## Design Philosophy

The 6.x API reflects several deliberate design shifts:

1. **Separation of concerns.** Intervention *definition* (what the intervention
   is) is separated from *distribution* (how/when/to whom it is given). In 5.x,
   `add_itn_scheduled` conflated both.

2. **Explicit over implicit.** Waning effects, drug types, and distribution
   classes are now visible in the code rather than inferred from parameter
   combinations.

3. **Composability.** The generic `add_intervention_scheduled` /
   `add_intervention_triggered` distributors work with *any* intervention class,
   so learning the distribution pattern once applies everywhere.

4. **Type safety.** Enums, typed config classes, and distribution objects catch
   errors at construction time rather than at EMOD runtime.

5. **Consistency.** The same `TargetDemographicsConfig` / `RepetitionConfig` /
   `ReportFilter` objects are reused across all interventions and reporters,
   replacing ad-hoc parameter lists that varied per function.

---

## At a Glance

| Area | 5.x pattern | 6.x pattern |
|---|---|---|
| Interventions | Free functions in 26 files under `interventions/` | OOP classes in 3 modules under `campaign/` |
| Waning effects | Flat float params, class inferred internally | Explicit typed classes (`waning.Exponential(...)`) |
| Distribution | Bundled into each intervention function | Generic `add_intervention_scheduled()` / `add_intervention_triggered()` |
| Demographics | PascalCase methods, `emod_api` distributions | snake_case methods, typed distribution classes |
| Reporters | Free functions taking `task` + `manifest` | Class constructors taking a `reporters` object |
| Task creation | `EMODTask.from_default2(param_custom_cb=...)` | `EMODTask.from_defaults(config_builder=...)` |
| Config values | Raw string literals | Enum members from `utils.emod_enum` |
| Schema layer | `emod_api.config.default_from_schema_no_validation`, `config.parameters.X` | `emod_api.schema_to_class`, `config.X` |

---

## 1. Dependencies

```
pip install "emodpy-malaria>=6.0.3"
```

emodpy-malaria 6.x requires **emodpy ~3.3** (was ~1.16). Update your
`requirements.txt` or `pyproject.toml` accordingly.

---

## 2. EMODTask Creation

The entry point for building a simulation changed from `from_default2` to
`from_defaults`, with renamed and restructured parameters.

| 5.x parameter | 6.x parameter | Notes |
|---|---|---|
| `config_path="config.json"` | *(removed)* | No longer needed |
| `param_custom_cb=` | `config_builder=` | Renamed |
| `demog_builder=` | `demographics_builder=` | Renamed |
| `ep4_custom_cb=` | *(removed)* | |
| `plugin_report=` | `report_builder=` | Now a first-class builder callback |

Reports are no longer bolted on after task creation. Instead, you pass a
`report_builder` callback that receives a `reporters` object (see
[Section 7](#7-reporters)).

### 5.x

```python
import emodpy.emod_task as emod_task

task = emod_task.EMODTask.from_default2(
    config_path="config.json",
    eradication_path=manifest.eradication_path,
    campaign_builder=build_campaign,
    schema_path=manifest.schema_path,
    ep4_custom_cb=None,
    param_custom_cb=build_config,
    demog_builder=build_demog,
    plugin_report=None
)

# Reports added AFTER task creation
add_reporters(task)
```

### 6.x

```python
from emodpy.emod_task import EMODTask

task = EMODTask.from_defaults(
    eradication_path=manifest.eradication_path,
    schema_path=manifest.schema_path,
    config_builder=build_config,
    campaign_builder=build_campaign,
    demographics_builder=build_demographics,
    report_builder=build_reports
)
```

---

## 3. Campaign Builder Signature

The `build_campaign` function now **receives** the campaign object as an
argument instead of importing and creating it internally.

### 5.x

```python
def build_campaign():
    import emod_api.campaign as campaign
    campaign.set_schema(manifest.schema_path)
    # ... add interventions ...
    return campaign
```

### 6.x

```python
def build_campaign(campaign):
    campaign.set_schema(manifest.schema_path)
    # ... add interventions ...
    return campaign
```

---

## 4. Interventions: Bednets (ITN)

The old monolithic `add_itn_scheduled()` bundled the intervention definition,
waning effect configuration, and distribution logic into a single call with ~20
parameters. The new API separates these into distinct, composable steps.

| Concept | 5.x | 6.x |
|---|---|---|
| Import path | `emodpy_malaria.interventions.bednet` | `emodpy_malaria.campaign.individual_intervention` |
| API style | Single function (`add_itn_scheduled`) | Class (`SimpleBednet`) + generic distributor |
| Waning effects | Flat floats: `blocking_initial_effect=0.9, blocking_decay_time_constant=7300` | Typed objects: `waning.Exponential(initial_effect=0.9, decay_time_constant=200)` |
| Coverage | `demographic_coverage=0.5` (flat param) | `TargetDemographicsConfig(demographic_coverage=0.5)` |
| Repetition | `repetitions=1` (flat param) | `RepetitionConfig(...)` object |
| Broadcast event | `receiving_itn_broadcast_event="Received_ITN"` | Add a `BroadcastEvent` to `intervention_list` |

#### Available waning effect classes

The old API inferred the waning class from parameter combinations (e.g., if
`box_duration > 0` and `decay_time_constant > 0`, it used `WaningEffectBoxExponential`).
The new API makes this explicit:

| Class | When to use |
|---|---|
| `waning.Constant(initial_effect)` | Effect never decays |
| `waning.Exponential(initial_effect, decay_time_constant)` | Exponential decay from day 0 |
| `waning.Box(initial_effect, box_duration)` | Constant for a fixed duration, then drops to 0 |
| `waning.BoxExponential(initial_effect, box_duration, decay_time_constant)` | Constant, then exponential decay |
| `waning.Combo(effects_list)` | Combine multiple waning effects |

### 5.x

```python
from emodpy_malaria.interventions.bednet import add_itn_scheduled

add_itn_scheduled(
    campaign,
    start_day=365,
    demographic_coverage=0.5,
    receiving_itn_broadcast_event="Received_ITN"
)
```

Waning effects were controlled through flat parameters with internally inferred
waning classes:

```python
add_itn_scheduled(
    campaign,
    start_day=365,
    demographic_coverage=0.5,
    blocking_initial_effect=0.9,
    blocking_box_duration=0,
    blocking_decay_time_constant=7300,
    killing_initial_effect=0.6,
    killing_box_duration=0,
    killing_decay_time_constant=7300,
    repelling_initial_effect=0.3,
    repelling_box_duration=0,
    repelling_decay_time_constant=4000
)
```

### 6.x

```python
from emodpy_malaria.campaign.individual_intervention import SimpleBednet
from emodpy_malaria.campaign.distributor import add_intervention_scheduled
from emodpy.campaign.common import TargetDemographicsConfig, RepetitionConfig
import emodpy_malaria.campaign.waning_config as waning

# Step 1: Define the intervention with explicit waning effects
bednet = SimpleBednet(
    campaign,
    blocking_config=waning.Exponential(initial_effect=0.9, decay_time_constant=200),
    killing_config=waning.Exponential(initial_effect=0.1, decay_time_constant=300),
    repelling_config=waning.Exponential(initial_effect=0.3, decay_time_constant=400),
)

# Step 2: Distribute it
add_intervention_scheduled(
    campaign,
    intervention_list=[bednet],
    start_day=5,
    repetition_config=RepetitionConfig(
        infinite_repetitions=True,
        timesteps_between_repetitions=361
    ),
    target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.5)
)
```

---

## 5. Interventions: Treatment Seeking

The convenience function `add_treatment_seeking()` -- which accepted a list
of trigger/coverage dicts -- has been replaced by explicit drug classes and
the generic triggered-distribution mechanism.

| Concept | 5.x | 6.x |
|---|---|---|
| Import path | `emodpy_malaria.interventions.treatment_seeking` | `emodpy_malaria.campaign.individual_intervention` + `emodpy_malaria.campaign.distributor` |
| Drug definition | Implicit (default artemether-lumefantrine) | Explicit: `AntimalarialDrug(campaign, drug_type="Artemether")` |
| Trigger/coverage | Single dict list: `targets=[{"trigger": ..., "coverage": ...}]` | Separate calls per trigger with `TargetDemographicsConfig` |
| Multi-drug regimen | Not directly supported in `add_treatment_seeking` | Pass list: `intervention_list=[drug1, drug2]` |
| Age targeting | `"agemin": 0, "agemax": 5` inside target dict | `TargetDemographicsConfig(target_age_max=40)` |

### 5.x

```python
from emodpy_malaria.interventions.treatment_seeking import add_treatment_seeking

add_treatment_seeking(
    campaign,
    start_day=365,
    targets=[
        {"trigger": "NewClinicalCase", "coverage": 0.7},
        {"trigger": "NewSevereCase",   "coverage": 0.9}
    ]
)
```

### 6.x

```python
from emodpy_malaria.campaign.individual_intervention import AntimalarialDrug
from emodpy_malaria.campaign.distributor import add_intervention_triggered
from emodpy.campaign.common import TargetDemographicsConfig

# Clinical case management: artemether at 70% coverage
clinical_drug = AntimalarialDrug(campaign, drug_type="Artemether")
add_intervention_triggered(
    campaign,
    intervention_list=[clinical_drug],
    triggers_list=["NewClinicalCase"],
    start_day=60,
    target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.7)
)

# Severe case management: two drugs at 90% coverage, age-targeted
severe_drugs = [
    AntimalarialDrug(campaign, drug_type="Chloroquine"),
    AntimalarialDrug(campaign, drug_type="Lumefantrine")
]
add_intervention_triggered(
    campaign,
    intervention_list=severe_drugs,
    triggers_list=["NewSevereCase"],
    start_day=40,
    target_demographics_config=TargetDemographicsConfig(
        demographic_coverage=0.9,
        target_age_max=40
    )
)
```

---

## 6. Demographics

The demographics module moved from a CamelCase filename with PascalCase methods
to a package with snake_case methods and typed distribution classes.

| Concept | 5.x | 6.x |
|---|---|---|
| Import | `import emodpy_malaria.demographics.MalariaDemographics` | `from emodpy_malaria.demographics import MalariaDemographics` |
| Vital dynamics | `demog.SetEquilibriumVitalDynamics()` | `demog.set_birth_rate(40, birth_rate_dependence=BirthRateDependence.POPULATION_DEP_RATE)` |
| Age distribution | `demog.SetAgeDistribution(Distributions.AgeDistribution_SSAfrica)` | `demog.set_age_distribution(UniformDistribution(0, 60))` |
| Initial prevalence | Constructor param: `init_prev=0.2` | `demog.set_initial_prevalence_distribution(UniformDistribution(0, 0.2))` |
| Biting heterogeneity | Constructor param: `include_biting_heterogeneity=True` | `demog.set_risk_distribution(...)` (explicit method) |
| Distributions | Pre-defined constants from `emod_api` | Typed classes: `UniformDistribution`, `ExponentialDistribution`, etc. |
| Naming convention | PascalCase (`SetAgeDistribution`) | snake_case (`set_age_distribution`) |

### Removed factory methods

- `from_csv()`, `from_params()`, `from_pop_csv()` — use `from_template_node()` or `from_file()` instead

### New distribution methods with automatic config implicits

| Method | Config implicit |
|---|---|
| `set_risk_distribution()` | `Enable_Demographics_Risk = 1` |
| `set_innate_immune_distribution()` | `Innate_Immune_Variation_Type` |
| `set_fertility_distribution()` | `Birth_Rate_Dependence` |
| `set_initial_prevalence_distribution()` | `Enable_Initial_Prevalence = 1` |
| `set_migration_heterogeneity()` | `Migration_Model = FIXED_RATE_MIGRATION`, `Enable_Migration_Heterogeneity = 1` |

`set_innate_immune_distribution()` accepts `Optional[BaseDistribution]` — for
`PYROGENIC_THRESHOLD_VS_AGE_INCREASING_AND_CYTOKINE_KILLING_INVERSE`, pass
`distribution=None` (Uniform(0,1) is forced internally).

### Renamed methods

| 5.x | 6.x |
|---|---|
| `set_prevalence_distribution()` | `set_initial_prevalence_distribution()` |
| `set_migration_heterogeneity_distribution()` | `set_migration_heterogeneity()` |

### 5.x

```python
import emodpy_malaria.demographics.MalariaDemographics as Demographics
import emod_api.demographics.PreDefinedDistributions as Distributions

demog = Demographics.from_template_node(
    lat=-3.2, lon=37.9, pop=1000, name="Tutorial_Site"
)
demog.SetEquilibriumVitalDynamics()
demog.SetAgeDistribution(Distributions.AgeDistribution_SSAfrica)
```

### 6.x

```python
from emodpy_malaria.demographics import MalariaDemographics as Demographics
from emodpy_malaria.utils.distributions import UniformDistribution
from emodpy_malaria.utils.emod_enum import BirthRateDependence

demog = Demographics.from_template_node(
    lat=-3.2, lon=37.9, pop=1000, name="Tutorial_Site"
)
demog.set_birth_rate(40, birth_rate_dependence=BirthRateDependence.POPULATION_DEP_RATE)
demog.set_age_distribution(UniformDistribution(0, 60))
demog.set_initial_prevalence_distribution(UniformDistribution(0, 0.2))
```

---

## 7. Reporters

Reporters moved from free functions that take `task` and `manifest` to class
constructors that take a `reporters` object. They are now added via a
`report_builder` callback passed to `EMODTask.from_defaults()`.

| Concept | 5.x | 6.x |
|---|---|---|
| Import path | `emodpy_malaria.reporters.builtin` | `emodpy_malaria.reporters.reporters` |
| API style | Free functions: `add_malaria_summary_report(task, manifest, ...)` | Classes: `MalariaSummaryReport(reporters, ...)` |
| When added | After `EMODTask` creation | Via `report_builder=` callback in `EMODTask.from_defaults()` |
| Filtering | Flat params: `start_day=`, `end_day=`, `filename_suffix=` | `ReportFilter(start_day=, end_day=, filename_suffix=)` |
| Enable flags | Manual: `task.config.parameters.Enable_Default_Reporting = 1` | Automatic when reporter class is added |

### 5.x

```python
from emodpy_malaria.reporters.builtin import add_malaria_summary_report

def add_reporters(task):
    """Called AFTER EMODTask is created."""
    task.config.parameters.Enable_Default_Reporting = 1
    task.config.parameters.Enable_Demographics_Reporting = 1
    add_malaria_summary_report(
        task, manifest,
        start_day=1,
        end_day=sim_years * 365,
        reporting_interval=30,
        age_bins=[0.25, 5, 115],
        max_number_reports=sim_years * 13,
        filename_suffix="monthly",
        pretty_format=True
    )
```

### 6.x

```python
from emodpy_malaria.reporters.reporters import (
    MalariaSummaryReport, DemographicsReport, ReportVectorStats, InsetChart
)
from emodpy.reporters.base import ReportFilter

def build_reports(reporters):
    """Passed as report_builder= to EMODTask.from_defaults()."""
    reporters.add(MalariaSummaryReport(
        reporters,
        reporting_interval=30,
        age_bins=[0.25, 5, 115],
        max_number_reports=sim_years * 13,
        report_filter=ReportFilter(
            start_day=1,
            end_day=sim_years * 365,
            filename_suffix="monthly"
        )
    ))
    reporters.add(InsetChart(reporters))
    reporters.add(DemographicsReport(reporters))
    reporters.add(ReportVectorStats(
        reporters,
        species_list=["gambiae", "arabiensis", "funestus"],
        stratify_by_species=True
    ))
    return reporters
```

---

## 8. Configuration

### Enums replace string literals

Config functions that previously accepted raw strings now expect enum members
from `emodpy_malaria.utils.emod_enum`.

```python
# 5.x
config.parameters.Malaria_Strain_Model = "FALCIPARUM_RANDOM_STRAIN"

# 6.x
from emodpy_malaria.utils.emod_enum import MalariaStrainModel
config.parameters.Malaria_Strain_Model = MalariaStrainModel.FALCIPARUM_RANDOM_STRAIN
```

Common enums: `DiagnosticType`, `HabitatType`, `VectorGender`,
`MalariaStrainModel`, `EIRType`, `NonAdherenceOption`,
`InnateImmuneVariationType`, `VectorCountType`, `BirthRateDependence`.

### Schema layer

The underlying schema-to-config mechanism changed:

```python
# 5.x
import emod_api.config.default_from_schema_no_validation as dfs
fpg = dfs.schema_to_config_subnode(manifest.schema_file, ["idmTypes", "idmType:ParasiteGenetics"])
fpg.parameters.Var_Gene_Randomness_Type = "ALL_RANDOM"

# 6.x
import emod_api.schema_to_class as s2c
fpg = s2c.get_class_with_defaults("idmType:ParasiteGenetics", schema_path=manifest.schema_file)
fpg.Var_Gene_Randomness_Type = VarGeneRandomnessType.ALL_RANDOM
```

Note the removal of `.parameters` — in 6.x, attributes are set directly on the
config object.

### Drug parameters use typed classes

```python
# 5.x — raw dict
drug_params = {"Cmax": 100, "Vd": 10, "PKPD_Model": "CONCENTRATION_VERSUS_EFFICACY"}

# 6.x — typed class
from emodpy_malaria.drug_config import MalariaDrugTypeParameters, DoseFractionByAge

drug = MalariaDrugTypeParameters(
    Name="CustomDrug",
    Cmax=100,
    Vd=10,
    PKPD_Model=PKPDModel.CONCENTRATION_VERSUS_EFFICACY,
    Fractional_Dose_By_Upper_Age=[
        DoseFractionByAge(upper_age=3, fraction=0.25),
        DoseFractionByAge(upper_age=6, fraction=0.5),
    ]
)
```

---

## 9. Weather

The remote-fetch pipeline (COMPS/SSMT weather requests) has been removed.
If your code used `weather_request.py` or `data_sources.py`, you will need to
fetch weather data externally and use the local file operations provided by
`weather_config.py` and the remaining weather modules.

---

## 10. New Utilities Package

6.x introduces `emodpy_malaria.utils/` with commonly needed helpers:

| Module | What it provides |
|---|---|
| `emod_enum.py` | Enums: `DiagnosticType`, `HabitatType`, `VectorGender`, `MalariaStrainModel`, `BirthRateDependence`, etc. |
| `distributions.py` | Distribution classes: `UniformDistribution`, `ExponentialDistribution`, `GaussianDistribution`, etc. |
| `targeting_config.py` | Targeting helpers: `HasIP`, `HasIntervention`, `IsPregnant` |
| `config_utils.py` | `non_schema_checks()` for config validation |
| `serialization.py` | Burnin/pickup: `configure_serialization_write()`, `configure_serialization_read()` |

---

## 11. Tutorial 3 — Complete Side-by-Side

Below is the full `build_campaign` function from Tutorial 3 in both versions,
showing the complete transformation pattern.

### 5.x — `build_campaign()`

```python
def build_campaign():
    import emod_api.campaign as campaign
    from emodpy_malaria.interventions.treatment_seeking import add_treatment_seeking
    from emodpy_malaria.interventions.bednet import add_itn_scheduled

    campaign.set_schema(manifest.schema_path)

    add_treatment_seeking(
        campaign,
        start_day=365,
        targets=[
            {"trigger": "NewClinicalCase", "coverage": 0.7},
            {"trigger": "NewSevereCase",   "coverage": 0.9}
        ]
    )

    add_itn_scheduled(
        campaign,
        start_day=365,
        demographic_coverage=0.5,
        receiving_itn_broadcast_event="Received_ITN"
    )

    return campaign
```

### 6.x — `build_campaign(campaign)`

```python
def build_campaign(campaign):
    from emodpy_malaria.campaign.individual_intervention import (
        AntimalarialDrug, SimpleBednet
    )
    from emodpy_malaria.campaign.distributor import (
        add_intervention_scheduled, add_intervention_triggered
    )
    from emodpy.campaign.common import TargetDemographicsConfig, RepetitionConfig
    import emodpy_malaria.campaign.waning_config as waning

    campaign.set_schema(manifest.schema_path)

    # Treatment: clinical cases
    clinical_drug = AntimalarialDrug(campaign, drug_type="Artemether")
    add_intervention_triggered(
        campaign,
        intervention_list=[clinical_drug],
        triggers_list=["NewClinicalCase"],
        start_day=60,
        target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.7)
    )

    # Treatment: severe cases
    severe_drugs = [
        AntimalarialDrug(campaign, drug_type="Chloroquine"),
        AntimalarialDrug(campaign, drug_type="Lumefantrine")
    ]
    add_intervention_triggered(
        campaign,
        intervention_list=severe_drugs,
        triggers_list=["NewSevereCase"],
        start_day=40,
        target_demographics_config=TargetDemographicsConfig(
            demographic_coverage=0.9, target_age_max=40
        )
    )

    # Bednets: 50% coverage, annual distribution
    bednet = SimpleBednet(
        campaign,
        blocking_config=waning.Exponential(initial_effect=0.9, decay_time_constant=200),
        killing_config=waning.Exponential(initial_effect=0.1, decay_time_constant=300),
        repelling_config=waning.Exponential(initial_effect=0.3, decay_time_constant=400),
    )
    add_intervention_scheduled(
        campaign,
        intervention_list=[bednet],
        start_day=5,
        repetition_config=RepetitionConfig(
            infinite_repetitions=True, timesteps_between_repetitions=361
        ),
        target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.5)
    )

    return campaign
```

---

## Import Path Reference

Complete mapping from 5.x to 6.x import paths:

| 5.x import | 6.x import |
|---|---|
| `emodpy_malaria.interventions.bednet` | `emodpy_malaria.campaign.individual_intervention` |
| `emodpy_malaria.interventions.treatment_seeking` | `emodpy_malaria.campaign.individual_intervention` + `emodpy_malaria.campaign.distributor` |
| `emodpy_malaria.interventions.drug` | `emodpy_malaria.campaign.individual_intervention` |
| `emodpy_malaria.interventions.drug_campaign` | `emodpy_malaria.campaign.intervention_systems` |
| `emodpy_malaria.interventions.irs` | `emodpy_malaria.campaign.individual_intervention` |
| `emodpy_malaria.interventions.vaccine` | `emodpy_malaria.campaign.individual_intervention` |
| `emodpy_malaria.interventions.diag_survey` | `emodpy_malaria.campaign.individual_intervention` |
| `emodpy_malaria.interventions.larvicide` | `emodpy_malaria.campaign.node_intervention` |
| `emodpy_malaria.interventions.mosquitorelease` | `emodpy_malaria.campaign.node_intervention` |
| `emodpy_malaria.interventions.spacespraying` | `emodpy_malaria.campaign.node_intervention` |
| `emodpy_malaria.interventions.scale_larval_habitats` | `emodpy_malaria.campaign.node_intervention` |
| `emodpy_malaria.interventions.outbreak` | `emodpy_malaria.campaign.individual_intervention` |
| `emodpy_malaria.interventions.common` | `emodpy_malaria.campaign.common` |
| `emodpy_malaria.reporters.builtin` | `emodpy_malaria.reporters.reporters` |
| `emodpy_malaria.demographics.MalariaDemographics` | `emodpy_malaria.demographics` |
| `emod_api.demographics.PreDefinedDistributions` | `emodpy_malaria.utils.distributions` |
| `config.parameters.X` | `config.X` |
| `MalariaSurveyJSONAnalyzer` | `MalariaSurveyAnalyzer` |
| `set_prevalence_distribution()` | `set_initial_prevalence_distribution()` |
| `set_migration_heterogeneity_distribution()` | `set_migration_heterogeneity()` |
| `from_csv()` / `from_params()` | `from_template_node()` / `from_file()` |
