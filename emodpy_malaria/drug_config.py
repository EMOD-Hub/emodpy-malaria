from typing import Union

import emod_api.schema_to_class as s2c
from emodpy.utils import validate_value_range
from emodpy_malaria.utils.emod_enum import PKPDModel


class DoseFractionByAge:
    """
    Pediatric dosing fraction for a specific age cutoff. Children below
    **upper_age_in_years** receive **fraction_of_adult_dose** of the adult dose.

    Schema type: ``idmType:DoseFractionByAge``

    Args:
        upper_age_in_years (float): Age in years below which children receive a
            reduced dose.
            Minimum value: 0
            Maximum value: 125
        fraction_of_adult_dose (float): Fraction of the adult dose given to children
            below the specified age.
            Minimum value: 0
            Maximum value: 1
    """

    def __init__(self, upper_age_in_years: float, fraction_of_adult_dose: float):
        self._upper_age = validate_value_range(
            upper_age_in_years, "upper_age_in_years", min_value=0, max_value=125)
        self._fraction = validate_value_range(
            fraction_of_adult_dose, "fraction_of_adult_dose", min_value=0, max_value=1)

    @property
    def upper_age_in_years(self) -> float:
        return self._upper_age

    @property
    def fraction_of_adult_dose(self) -> float:
        return self._fraction

    def to_schema_dict(self, manifest):
        obj = s2c.get_class_with_defaults("idmType:DoseFractionByAge", schema_path=manifest.schema_file)
        obj.Upper_Age_In_Years = self._upper_age
        obj.Fraction_Of_Adult_Dose = self._fraction
        return obj


class DrugModifier:
    """
    Drug resistance modifier applied when a parasite genome matches the specified
    resistant string. Multiple matching modifiers are multiplied together.

    Schema type: ``idmType:DrugModifier``

    Args:
        drug_resistant_string (str): Nucleotide base letters (A, C, G, T) defining
            resistance at specific genome locations.
        pkpd_c50_modifier (float, optional): Multiplier applied to the drug's
            **Drug_PKPD_C50**.
            Minimum value: 0
            Maximum value: 1000
            Default value: 1.0
        max_irbc_kill_modifier (float, optional): Multiplier applied to the drug's
            **Max_Drug_IRBC_Kill**.
            Minimum value: 0
            Maximum value: 1000
            Default value: 1.0
    """

    def __init__(self, drug_resistant_string: str,
                 pkpd_c50_modifier: float = 1.0,
                 max_irbc_kill_modifier: float = 1.0):
        self._drug_resistant_string = drug_resistant_string
        self._pkpd_c50_modifier = validate_value_range(
            pkpd_c50_modifier, "pkpd_c50_modifier", min_value=0, max_value=1000)
        self._max_irbc_kill_modifier = validate_value_range(
            max_irbc_kill_modifier, "max_irbc_kill_modifier", min_value=0, max_value=1000)

    @property
    def drug_resistant_string(self) -> str:
        return self._drug_resistant_string

    @property
    def pkpd_c50_modifier(self) -> float:
        return self._pkpd_c50_modifier

    @property
    def max_irbc_kill_modifier(self) -> float:
        return self._max_irbc_kill_modifier

    def to_schema_dict(self, manifest):
        obj = s2c.get_class_with_defaults("idmType:DrugModifier", schema_path=manifest.schema_file)
        obj.Drug_Resistant_String = self._drug_resistant_string
        obj.PKPD_C50_Modifier = self._pkpd_c50_modifier
        obj.Max_IRBC_Kill_Modifier = self._max_irbc_kill_modifier
        return obj


class MalariaDrugTypeParameters:
    """
    Schema-backed malaria drug type configuration. Encapsulates all pharmacokinetic/
    pharmacodynamic parameters for a single antimalarial drug.

    Schema type: ``idmType:MalariaDrugTypeParameters``

    Args:
        name (str, required): Drug name. Must be unique across all configured drugs.
        pkpd_model (Union[PKPDModel, str], optional): PK/PD model type. Use
            ``PKPDModel.CONCENTRATION_VERSUS_TIME`` for full PK/PD modeling or
            ``PKPDModel.FIXED_DURATION_CONSTANT_EFFECT`` for simplified constant-effect
            modeling.
            Default value: ``FIXED_DURATION_CONSTANT_EFFECT``
        drug_cmax (float, optional): Maximum drug concentration after a treatment
            dose (mg/L). Only used when **pkpd_model** is
            ``CONCENTRATION_VERSUS_TIME``.
            Minimum value: 0
            Maximum value: 100000
            Default value: 1000
        drug_decay_t1 (float, optional): First-phase exponential decay rate (days).
            Minimum value: 0
            Maximum value: 100000
            Default value: 1
        drug_decay_t2 (float, optional): Second-phase exponential decay rate (days).
            Minimum value: 0
            Maximum value: 100000
            Default value: 1
        drug_vd (float, optional): Volume of distribution (L/kg). Only used when
            **pkpd_model** is ``CONCENTRATION_VERSUS_TIME``.
            Minimum value: 0
            Maximum value: 100000
            Default value: 10
        drug_pkpd_c50 (float, optional): Drug concentration at which killing rate is
            50% of maximum (mg/L). Only used when **pkpd_model** is
            ``CONCENTRATION_VERSUS_TIME``.
            Minimum value: 0
            Maximum value: 100000
            Default value: 100
        drug_fulltreatment_doses (int, optional): Number of doses in a full treatment
            course.
            Minimum value: 1
            Maximum value: 100000
            Default value: 3
        drug_dose_interval (float, optional): Days between doses.
            Minimum value: 0
            Maximum value: 100000
            Default value: 1
        drug_gametocyte02_killrate (float, optional): Kill rate for stage 0–2
            gametocytes.
            Minimum value: 0
            Maximum value: 100000
            Default value: 0
        drug_gametocyte34_killrate (float, optional): Kill rate for stage 3–4
            gametocytes.
            Minimum value: 0
            Maximum value: 100000
            Default value: 0
        drug_gametocytem_killrate (float, optional): Kill rate for mature gametocytes.
            Minimum value: 0
            Maximum value: 100000
            Default value: 0
        drug_hepatocyte_killrate (float, optional): Kill rate for hepatocytes
            (liver stage).
            Minimum value: 0
            Maximum value: 100000
            Default value: 0
        max_drug_irbc_kill (float, optional): Maximum kill rate for infected red
            blood cells.
            Minimum value: 0
            Maximum value: 100000
            Default value: 5
        bodyweight_exponent (float, optional): Exponent for body-weight-based dosing
            adjustment.
            Minimum value: 0
            Maximum value: 100000
            Default value: 0
        fractional_dose_by_upper_age (list[DoseFractionByAge], optional): Pediatric
            dosing fractions by age.
            Default value: []
        resistances (list[DrugModifier], optional): Drug resistance modifiers for
            parasite genetics simulations.
            Default value: []
    """

    def __init__(self,
                 name: str,
                 pkpd_model: Union[PKPDModel, str] = PKPDModel.FIXED_DURATION_CONSTANT_EFFECT,
                 drug_cmax: float = 1000,
                 drug_decay_t1: float = 1,
                 drug_decay_t2: float = 1,
                 drug_vd: float = 10,
                 drug_pkpd_c50: float = 100,
                 drug_fulltreatment_doses: int = 3,
                 drug_dose_interval: float = 1,
                 drug_gametocyte02_killrate: float = 0,
                 drug_gametocyte34_killrate: float = 0,
                 drug_gametocytem_killrate: float = 0,
                 drug_hepatocyte_killrate: float = 0,
                 max_drug_irbc_kill: float = 5,
                 bodyweight_exponent: float = 0,
                 fractional_dose_by_upper_age: list = None,
                 resistances: list = None):
        if not isinstance(pkpd_model, PKPDModel):
            try:
                pkpd_model = PKPDModel(pkpd_model)
            except ValueError:
                raise ValueError(
                    f"Invalid pkpd_model {pkpd_model!r}. "
                    f"Valid options: {list(PKPDModel)}")

        self._name = name
        self._pkpd_model = pkpd_model
        self._drug_cmax = validate_value_range(
            drug_cmax, "drug_cmax", min_value=0, max_value=100000)
        self._drug_decay_t1 = validate_value_range(
            drug_decay_t1, "drug_decay_t1", min_value=0, max_value=100000)
        self._drug_decay_t2 = validate_value_range(
            drug_decay_t2, "drug_decay_t2", min_value=0, max_value=100000)
        self._drug_vd = validate_value_range(
            drug_vd, "drug_vd", min_value=0, max_value=100000)
        self._drug_pkpd_c50 = validate_value_range(
            drug_pkpd_c50, "drug_pkpd_c50", min_value=0, max_value=100000)
        self._drug_fulltreatment_doses = validate_value_range(
            drug_fulltreatment_doses, "drug_fulltreatment_doses",
            min_value=1, max_value=100000, param_type=int)
        self._drug_dose_interval = validate_value_range(
            drug_dose_interval, "drug_dose_interval", min_value=0, max_value=100000)
        self._drug_gametocyte02_killrate = validate_value_range(
            drug_gametocyte02_killrate, "drug_gametocyte02_killrate",
            min_value=0, max_value=100000)
        self._drug_gametocyte34_killrate = validate_value_range(
            drug_gametocyte34_killrate, "drug_gametocyte34_killrate",
            min_value=0, max_value=100000)
        self._drug_gametocytem_killrate = validate_value_range(
            drug_gametocytem_killrate, "drug_gametocytem_killrate",
            min_value=0, max_value=100000)
        self._drug_hepatocyte_killrate = validate_value_range(
            drug_hepatocyte_killrate, "drug_hepatocyte_killrate",
            min_value=0, max_value=100000)
        self._max_drug_irbc_kill = validate_value_range(
            max_drug_irbc_kill, "max_drug_irbc_kill", min_value=0, max_value=100000)
        self._bodyweight_exponent = validate_value_range(
            bodyweight_exponent, "bodyweight_exponent", min_value=0, max_value=100000)
        self._fractional_dose_by_upper_age = fractional_dose_by_upper_age or []
        self._resistances = resistances or []

    @property
    def name(self) -> str:
        return self._name

    @property
    def pkpd_model(self) -> PKPDModel:
        return self._pkpd_model

    def to_schema_dict(self, manifest):
        mdp = s2c.get_class_with_defaults("idmType:MalariaDrugTypeParameters", schema_path=manifest.schema_file)
        mdp.Name = self._name
        mdp.PKPD_Model = self._pkpd_model.value
        mdp.Drug_Cmax = self._drug_cmax
        mdp.Drug_Decay_T1 = self._drug_decay_t1
        mdp.Drug_Decay_T2 = self._drug_decay_t2
        mdp.Drug_Vd = self._drug_vd
        mdp.Drug_PKPD_C50 = self._drug_pkpd_c50
        mdp.Drug_Fulltreatment_Doses = self._drug_fulltreatment_doses
        mdp.Drug_Dose_Interval = self._drug_dose_interval
        mdp.Drug_Gametocyte02_Killrate = self._drug_gametocyte02_killrate
        mdp.Drug_Gametocyte34_Killrate = self._drug_gametocyte34_killrate
        mdp.Drug_GametocyteM_Killrate = self._drug_gametocytem_killrate
        mdp.Drug_Hepatocyte_Killrate = self._drug_hepatocyte_killrate
        mdp.Max_Drug_IRBC_Kill = self._max_drug_irbc_kill
        mdp.Bodyweight_Exponent = self._bodyweight_exponent

        for dose_frac in self._fractional_dose_by_upper_age:
            mdp.Fractional_Dose_By_Upper_Age.append(
                dose_frac.to_schema_dict(manifest))

        for resistance in self._resistances:
            mdp.Resistances.append(
                resistance.to_schema_dict(manifest))

        return mdp
