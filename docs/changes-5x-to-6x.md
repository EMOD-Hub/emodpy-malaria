# emodpy-malaria: Changes from 5.x to 6.0.2

**Version:** 5.2.1 → 6.0.2  
**emodpy dependency:** ~1.16 → ~3.3  
**emod-malaria:** ~2.35 (unchanged)

---

## 1. Version and Dependency Changes

| Item | 5.x | 6.0.2 |
|---|---|---|
| emodpy-malaria version | 5.2.1 | 6.0.2 |
| emodpy dependency | ~1.16 | ~3.3 |
| emod-malaria | ~2.35 | ~2.35 (unchanged) |

The top-level `__init__.py` now re-exports from `emodpy_malaria.campaign` and `emodpy_malaria.demographics`.

---

## 2. Campaign / Interventions (Major Rewrite)

### Removed: `emodpy_malaria/interventions/` (26 files, ~5,308 lines)

All files deleted:
- `common.py`, `bednet.py`, `usage_dependent_bednet.py`, `irs.py`, `spacespraying.py`
- `indoor_individual_emanator.py`, `outdoor_node_emanator.py`, `drug.py`, `drug_campaign.py`
- `adherentdrug.py`, `diag_survey.py`, `treatment_seeking.py`, `vaccine.py`, `ivermectin.py`
- `larvicide.py`, `larval_microsporidia.py`, `scale_larval_habitats.py`, `mosquitorelease.py`
- `sugartrap.py`, `outdoorrestkill.py`, `outbreak.py`, `malaria_challenge.py`, `inputeir.py`
- `vector_surveillance.py`, `community_health_worker.py`

### Added: `emodpy_malaria/campaign/` (8 files, ~5,996 lines)

| Module | Lines | Purpose |
|---|---|---|
| `individual_intervention.py` | 2,153 | All individual-level interventions: `AntimalarialDrug`, `SimpleBednet`, `MalariaDiagnostic`, `_RTSSVaccine`, `AdherentDrug`, `Ivermectin`, `UsageDependentBednet`, `IRSHousingModification`, etc. |
| `node_intervention.py` | 1,867 | All node-level interventions: `SpaceSpraying`, `Larvicides`, `MosquitoRelease`, `InputEIR`, `MalariaChallenge`, `ScaleLarvalHabitat`, `SugarTrap`, `OutdoorRestKill`, etc. |
| `intervention_systems.py` | 1,315 | Drug campaign orchestration (replaces `drug_campaign.py`): `CampaignType` enum, `DRUG_CODES`, MDA/SMC/MSAT builders |
| `event_coordinator.py` | 284 | `VectorSurveillanceEventCoordinator`, `VectorCounter`; re-exports emodpy coordinators |
| `waning_config.py` | 155 | Re-exports waning effect classes; adds malaria-specific `InsecticideWaningEffect` with internal K/RK/RBK mapping |
| `distributor.py` | 198 | `add_intervention_scheduled`, `add_intervention_triggered`, `add_broadcast_coordinator_event`, `add_vector_surveillance`, `add_community_health_worker` |
| `common.py` | 24 | Re-exports shared types from emodpy |

### Key Architecture Changes

- **Function-based → Class-based:** Old code used standalone functions returning raw dicts. New code uses OOP classes inheriting from emodpy's `IndividualIntervention` / `NodeIntervention` base classes.
- **26 files → 3 domain-grouped modules:** Individual interventions, node interventions, and intervention systems.
- **Delegation to emodpy:** Generic interventions (`BroadcastEvent`, `SimpleVaccine`, `DelayedIntervention`, `Outbreak`, etc.) are re-exported from emodpy, not duplicated.
- **Explicit waning configs:** Old code inferred waning class from parameter combinations. New code uses typed classes (`Constant`, `Box`, `Exponential`, `BoxExponential`, `Combo`).
- **Enum-based validation:** Uses enums from `emodpy_malaria.utils.emod_enum` (`DiagnosticType`, `HabitatType`, `VectorCountType`, etc.) instead of raw strings.
- **Import path change:** `emodpy_malaria.interventions.*` → `emodpy_malaria.campaign.*`

---

## 3. Configuration Modules

### malaria_config.py

**Removed functions (8 pass-through wrappers):** `set_species_param`, `add_species`, `add_blood_meal_mortality`, `add_insecticide_resistance`, `get_species_params`, `set_max_larval_capacity`, `add_microsporidia`, `configure_linear_spline` — these forwarded to `vector_config` and are now re-exported via `__all__` instead.

**Added:** `add_new_drug(config, manifest, drug: MalariaDrugTypeParameters, overwrite)` — type-safe drug creation.

**Changed:**
- `set_team_defaults`: string literals → enum members (`MalariaStrainModel`, `ParasiteSwitchType`, `InnateImmuneVariationType`)
- `set_team_drug_params`: CSV parsing rewritten to use `MalariaDrugTypeParameters` / `DoseFractionByAge` objects
- `set_parasite_genetics_params`: accepts `VarGeneRandomnessType` enum; new `sporozoites_per_oocyst: BaseDistribution` param
- `set_drug_param`: `value is None` check replaces `not value` (fixes 0/False bug)
- `add_drug_resistance`: uses `DrugModifier` class instead of raw dict

**Schema layer swap:** `emod_api.config.default_from_schema_no_validation` → `emod_api.schema_to_class`; `.parameters` accessor removed.

### vector_config.py

**Removed:** `configure_linear_spline` standalone function — replaced by `VectorHabitat` class.

**Added:**
- `VectorHabitat` — typed habitat config with `to_schema_dict()`
- `VectorSpeciesParameters` — full species config class with `from_preset()` classmethod

**Changed:** `add_species`, `add_genes_and_alleles`, `add_insecticide_resistance`, `set_max_larval_capacity`, `add_vector_migration` all gained type annotations and stricter required params. String enum values replaced by enum members.

### malaria_vector_species_params.py

Rewritten from procedural `if/elif` chains to module-level `VectorSpeciesParameters` / `VectorHabitat` instances stored in a `_SPECIES_DATA` dict, deep-copied on lookup. `BUILTIN_SPECIES` list exported. `species_params()` recommends `VectorSpeciesParameters.from_preset()`.

### New: drug_config.py (279 lines)

Three new classes:
- `DoseFractionByAge` — pediatric dosing
- `DrugModifier` — resistance modifier
- `MalariaDrugTypeParameters` — full drug PK/PD config with `to_schema_dict(manifest)` and `validate_value_range` bounds checking

---

## 4. Demographics

**Deleted:** `MalariaDemographics.py` (263 lines)

**Replaced by:**
- `malaria_demographics.py` (575 lines) — expanded `MalariaDemographics` class
- `malaria_node.py` (86 lines) — new `MalariaNode(Node)` subclass
- `__init__.py` — re-exports `MalariaDemographics`, `MalariaNode`, `AgeDistribution`, `FertilityDistribution`, `MortalityDistribution`

**Key changes:**
- Now extends `emodpy.demographics.demographics.Demographics` (was `emod_api.demographics.Demographics`)
- `__init__` signature changed: removed `init_prev`/`include_biting_heterogeneity`; added `default_node`/`set_defaults`
- Added: `from_file()`, `add_vector_migration()`, `add_weather()`, `set_risk_distribution()`, `set_innate_immune_distribution()`, `set_fertility_distribution()`, `set_initial_prevalence_distribution()`, `set_migration_heterogeneity()`
- Old factory functions (`from_csv`, `from_params`, `from_pop_csv`) removed; `from_template_node` retained
- `set_innate_immune_distribution()`: `distribution` parameter is `Optional[BaseDistribution]`; for `PYROGENIC_THRESHOLD_VS_AGE_INCREASING_AND_CYTOKINE_KILLING_INVERSE`, distribution must be `None` (Uniform(0,1) forced internally)
- `set_initial_prevalence_distribution()`: replaces inherited `set_prevalence_distribution()`; automatically enables `Enable_Initial_Prevalence`
- `set_migration_heterogeneity()`: replaces inherited `set_migration_heterogeneity_distribution()`; automatically sets `Migration_Model = FIXED_RATE_MIGRATION` and `Enable_Migration_Heterogeneity = 1`

---

## 5. Reporters

**Deleted:** `builtin.py` (2,221 lines)  
**Replaced by:** `reporters.py` (2,181 lines)

**Key changes:**
- Generic reporters now imported from `emodpy.reporters.common` instead of duplicated locally
- **Free functions → class constructors:** `add_report_vector_genetics(task, manifest, ...)` → `ReportVectorGenetics(reporters_object, ...)`
- No more `task`/`manifest` args — reporters take a `reporters_object` from emodpy
- **Removed:** `add_visualizations()`, all `add_*()` free functions, `SqlReportMalariaGenetics`, `ReportVectorStatsMalariaGenetics`, `MalariaSurveyJSONAnalyzer` (renamed to `MalariaSurveyAnalyzer`)
- **Added:** `ReportAntibodies`, `ReportFpgNewInfections`, `ReportSimpleMalariaTransmission`, `ReportNodeDemographicsMalariaGenetics`
- Enums `VectorState`, `DrugResistantAndHRPStatisticType` moved to `emodpy_malaria.utils.emod_enum`
- Uses `ReportFilter` from `emodpy.reporters.base` for filtering

---

## 6. Serialization (Modular Rewrite)

**Removed (475 lines):** `replace_genomes.py`, `replace_genomes_get_next_barcode.py`, `serialization_support.py`, `zero_infections.py`

**Added (1,128 lines):** Six private modules + public `__init__.py`:
- `_export.py` — export utilities
- `_genomes.py` — genome replacement logic
- `_infections.py` — infection zeroing
- `_inspect.py` — DTK file inspection
- `_population.py` — population data handling
- `_vectors.py` — vector data handling
- `__init__.py` — public API surface

---

## 7. Migration

- Conversion scripts moved from top-level into `migration_scripts/` subpackage
- New `vector_migration_data.py` (383 lines) with expanded vector migration data handling
- `vector_migration.py` slightly refactored
- New `__init__.py` for public exports
- `README.md` removed

---

## 8. Weather (Simplified)

**Removed:**
- `weather_request.py` (378 lines) — COMPS/SSMT remote-fetch logic
- `data_sources.py` (59 lines) — ERA5 source definitions

**Added:** `weather_config.py` (144 lines) — configuration helpers for weather setup

All remaining modules (`weather_data.py`, `weather_metadata.py`, `weather_set.py`, `weather_utils.py`, `weather_variable.py`, `__init__.py`) significantly refactored (net ~765 lines removed). Remote-fetch pipeline removed; focus is on local file operations.

---

## 9. New `utils/` Package (~823 lines)

| Module | Purpose |
|---|---|
| `config_utils.py` | `non_schema_checks()` for config validation; `validate_bins()` for bin-edge checks |
| `distributions.py` | Re-exports 11 distribution classes from `emodpy.utils.distributions` |
| `emod_enum.py` | Shared + malaria-specific enums: `DiagnosticType`, `HabitatType`, `VectorGender`, `MalariaStrainModel`, `EIRType`, `NonAdherenceOption`, etc. |
| `targeting_config.py` | Re-exports `AbstractTargetingConfig`, `HasIP`, `HasIntervention`; adds `IsPregnant` with validation |
| `serialization.py` | Burnin/pickup helpers: `configure_serialization_write()`, `configure_serialization_read()`, `get_burnin_sim_outpaths()` |

---

## 10. Plotting

**Added:** `plot_a_vs_b.py` (50 lines) and `xy_plot.py` (304 lines). Existing modules received minor refactoring.

---

## 11. Tests (Complete Overhaul)

**Removed (~17,544 lines):**
- `test_malaria_interventions.py` (3,264), `test_malaria_reporters.py` (1,057), `test_demog.py` (394), `test_treatment_seeking.py` (240), `test_campaign_common.py` (27)
- Entire `weather/` test directory (6 test modules, all data fixtures, notebooks, scenarios)
- `base_sim_test.py`, `doc_tests/`, CSV/binary test data

**Added/rewritten:**
- `test_interventions.py` (1,049), `test_node_interventions.py` (836), `test_reporters.py` (1,149)
- `test_malaria_demographics.py` (584), `test_campaign_distributor.py` (333)
- `test_vector_config.py` (936), `test_weather.py` (599), `test_targeting_config.py` (138)
- `test_config_utils.py` (378), `test_vector_migration.py` (498)
- `test_config_implicits.py` — validates config-level implicits for larval habitat, mosquito release genome, and genome locations
- `test_demographics_implicits.py` (273) — validates implicit config parameter setting for risk, innate immune, fertility, prevalence, weather, and migration heterogeneity distributions
- `test_serialization/` package (3 modules: `test_genomes.py`, `test_infections.py`, `test_inspect.py` — 364 total)
- `test_import.py` and `test_malaria_config.py` substantially rewritten
- `helpers.py` retained (37 lines)
- `tests/sim_tests/` — simulation-level test runner
- `tests/tutorials/test_tutorials.py` — tutorial integration tests

---

## 12. Examples

**Removed:** Entire `examples-container/` directory (31+ subdirectories, Snakemake orchestration, ~11,214 lines)

**Added:** Simpler `examples/` directory:
- `drug_campaign/` — 162-line example + manifest
- `most_interventions/` — 927-line comprehensive example + manifest + vector surveillance script
- `vector_migration_sweep/` — 144-line example + manifest

---

## 13. Tutorials

- All 7 existing tutorials rewritten/simplified
- New tutorial added: `tutorial_8_migration.py` (314 lines)
- All tutorials use `set_initial_prevalence_distribution()` (replaces old `set_prevalence_distribution()`)
- `comps_sif_file.id` removed; `manifest.py` updated (`burnin_serialize_years` reduced to 1 for faster test runs)

---

## 14. Documentation

**New pages:**
- `docs/emod/`: `model-properties.md`, `software-report-surveillance-event-recorder.md`, `software-serializing-data-access.md`, `vector-model-gene-drives.md`
- `docs/tutorials/`: `overview.md`, `setup.md`, `concepts.md`, `tutorial-8.md`, tutorial images

**Removed:** `vector-model-maternal-deposition.md`

**Updated:**
- `model-heterogeneity.md` — added innate immune variation section (~100 lines, formulas for all 5 variation types) and migration heterogeneity paragraph
- `model-migration.md` — added migration heterogeneity section (~25 lines)
- `software-serializing-change-campaign.md` — typo fix: `NodelLevelHealthTriggeredIV` → `NodeLevelHealthTriggeredIV`
- `software-serializing-change-demog.md` — reformatted `LarvalHabitatMultiplier` as admonition; fixed `InnateImmuneDistribution*` prerequisite (was `Enable_Demographics_Risk`, corrected to `Innate_Immune_Variation_Type`); simplified IndividualProperties section
- `config-enable-malaria.csv`, `config-infectivity-malaria.csv` — corrected `Enable_Initial_Prevalence` ("number" → "fraction", per-node draw semantics)
- `demo-simpledistro-malaria.csv` — clarified `PrevalenceDistributionFlag` as per-node draw
- `parameter-campaign-individual-bitingrisk.md` — minor wording clarification
- Campaign event coordinator CSVs/docs, serializing docs, vector genetics docs, all tutorial markdown pages

---

## Summary of Breaking Changes

1. **Import paths:** `emodpy_malaria.interventions.*` → `emodpy_malaria.campaign.*`
2. **Function → class API:** Standalone functions replaced by class constructors throughout (interventions, reporters)
3. **Schema layer:** `emod_api.config.default_from_schema_no_validation` → `emod_api.schema_to_class`; `.parameters` accessor removed
4. **String → enum:** All config string literals now require enum members from `utils.emod_enum`
5. **Raw dict → typed classes:** Drug params, waning effects, distributions, habitats now use typed class instances
6. **Demographics factory functions removed:** `from_csv`, `from_params`, `from_pop_csv` (`from_template_node` retained)
7. **Demographics distribution renames:** `set_prevalence_distribution()` → `set_initial_prevalence_distribution()`; `set_migration_heterogeneity_distribution()` → `set_migration_heterogeneity()`
8. **Reporter API:** `add_*(task, manifest, ...)` free functions → `Reporter(reporters_object, ...)` constructors
9. **Weather remote-fetch removed:** No more COMPS/SSMT weather request pipeline
10. **emodpy dependency:** ~1.16 → ~3.3 (major version bump)
11. **Required args tightened:** Several functions that defaulted to `None` now require explicit values
