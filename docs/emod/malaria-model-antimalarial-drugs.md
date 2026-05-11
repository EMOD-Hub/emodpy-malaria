# Antimalarial drugs


Antimalarial drugs are a powerful tool for malaria control and elimination.  Modeling mass
antimalarial campaigns can elucidate how to most effectively deploy drug-based interventions and
quantitatively compare the effects of cure, prophylaxis, and transmission-blocking in suppressing
parasite prevalence.

Individuals in a simulation can receive antimalarial drugs as treatment for clinical or severe
malaria or during a *mass drug administration (MDA)* campaign. The following information
explains how to configure antimalarial drug parameters in a configuration file. For a complete list
of configuration parameters that are used in the malaria model, see the
[Configuration parameters](parameter-configuration.md).

To specify where, when, and to whom the antimalarial drugs are administered, you must use an
**AntiMalarialDrug**, **AdherentDrug**, or **MultiComboPackDrug** intervention in the campaign file.
See [Campaign parameters](parameter-campaign.md) for more information.




## Modeling a box profile of antimalaria drug pharmacokinetics


Pharmacokinetics (PK) of antimalarial drugs can be modeled with a box profile or with a double
exponential decay. Pharmacodynamics (PD) of antimalarial drugs are modeled as an on/off switch for
box PK or with a simple sigmoid for double exponential PK. If multiple drugs are given in a
treatment, each drug is considered independently for both PK and PD.

To model a box PK, set the parameter **PKPD\_Model** to FIXED\_DURATION\_CONSTANT\_EFFECT. Drugs
will have full killing efficacy for the duration set by **Drug\_Decay\_T1**. Dosing multiple times leads
to multiple pulses of drug killing if dose separation is longer than **Drug\_Decay\_T1**. If dose
separation (**Drug\_Dose\_Interval**) is shorter than **Drug\_Decay\_T1**, the box time is reset by each new
dose such that drug killing is switched off after time **Drug\_Decay\_T1** after the last dose.

![Modeling drug killing effects with a box profile. (A) A single dose of drug kills parasites at maximum efficacy for duration set by **Drug\_Decay\_T1**. (B) A drug given in multiple doses results in multiple parasite killing pulses of duration **Drug\_Decay\_T1** if the dose separation **Drug\_Dose\_Interval** is longer than **Drug\_Decay\_T1**. (C) If a drug’s dosing regimen results in doses taken before time **Drug\_Decay\_T1** has elapsed, the drug kills parasites at maximum efficacy the entire time between the first dose and time **Drug\_Decay\_T1** after the last dose.](../figures/vector-malaria/Antimalarial_Drugs__Box_PK_profile.png)

*Modeling drug killing effects with a box profile. (A) A single dose of drug kills parasites at maximum efficacy for duration set by **Drug\_Decay\_T1**. (B) A drug given in multiple doses results in multiple parasite killing pulses of duration **Drug\_Decay\_T1** if the dose separation **Drug\_Dose\_Interval** is longer than **Drug\_Decay\_T1**. (C) If a drug’s dosing regimen results in doses taken before time **Drug\_Decay\_T1** has elapsed, the drug kills parasites at maximum efficacy the entire time between the first dose and time **Drug\_Decay\_T1** after the last dose.*

The following example provides the syntax:

```json
{
    "Malaria_Drug_Params": [
        {
            "Name": "Artemether_Lumefantrine",
            "PKPD_Model": "FIXED_DURATION_CONSTANT_EFFECT",
            "Drug_Cmax": 1000,
            "Drug_Decay_T1": 1,
            "Drug_Decay_T2": 1,
            "Drug_Dose_Interval": 1,
            "Drug_Fulltreatment_Doses": 3,
            "Drug_Gametocyte02_Killrate": 2.3,
            "Drug_Gametocyte34_Killrate": 2.3,
            "Drug_GametocyteM_Killrate": 0,
            "Drug_Hepatocyte_Killrate": 0,
            "Drug_PKPD_C50": 100,
            "Drug_Vd": 10,
            "Max_Drug_IRBC_Kill": 4.61,
            "Bodyweight_Exponent": 0
        }
    ]
}
```

## Modeling a double exponential PK


To model a double exponential PK, set the parameter **PKPD\_Model** to CONCENTRATION\_VERSUS\_TIME.
The double exponential PK approximates a one- or two-compartment PK model. To model a drug with
1-compartment PK, set **Drug\_Decay\_T2** equal to **Drug\_Decay\_T1** (**Drug\_Vd** becomes
irrelevant). For PD, the **Drug\_PKPD\_C50** determines the drug concentrations where parasite
killing is effective (drug concentration > C50) and ineffective (drug concentration < C50). EMOD
sets the shape of the parasite killing curve based on parasite kill rate and C50. **Drug\_Cmax**,
**Drug\_Decay\_T1**, **Drug\_Decay\_T2**, **Drug\_Vd**, and **Drug\_PKPD\_C50** together determine
when the drug is effectively killing parasites. Changing each of these parameters will affect how
long the parasites are exposed to a strong killing effect. Adding additional doses will also
increase the duration of the parasite- killing window.

Children can be dosed with a fraction of the adult dose according to
**Fractional\_Dose\_By\_Upper\_Age**, where each dose fraction is paired with the maximum age of
children receiving that dose. Depending on specific PK characteristics of each drug, bodyweight may
affect the rate of drug clearance. In the double exponential PK model, bodyweight is directly
determined by age, and **Drug\_Cmax** is multiplied by the inverse of the bodyweight raised to the power
of **Bodyweight\_Exponent**. See the paper on drug PK and PD ([Mass campaigns with antimalarial drugs: a modelling comparison of artemether-lumefantrine and DHA-piperaquine with and without primaquine as tools for malaria control and elimination][gerardin-2015-mda-abstract]) for more details on how to set PK and
PD parameter values in EMOD.

![Modeling drug killing effects with a double exponential PK and sigmoid PD. (A) Two-compartment PK models include both distribution and elimination of drug. One-compartment models do not have a distribution phase. (B) A double exponential PK approximates the distribution and elimination phases of a two- compartment model. (C) Parasite killing is determined by drug concentration, **Drug\_PKPD\_C50**, and parasite stage- specific maximum kill rates. (D) PK and PD together determine the duration over which a dose of drug is effective.](../figures/vector-malaria/Antimalarial_Drugs_Concentration_vs_time_PK_profile.png)

*Modeling drug killing effects with a double exponential PK and sigmoid PD. (A) Two-compartment PK models include both distribution and elimination of drug. One-compartment models do not have a distribution phase. (B) A double exponential PK approximates the distribution and elimination phases of a two- compartment model. (C) Parasite killing is determined by drug concentration, **Drug\_PKPD\_C50**, and parasite stage- specific maximum kill rates. (D) PK and PD together determine the duration over which a dose of drug is effective.*

## Relevant IDM publications



### Antimalarial drugs


* Bellinger, *et al*., 2016. [Oral, ultra--long-lasting drug delivery: Application toward malaria elimination goals][bellinger-2016]. *Science Translational Medicine*.  8(365).

* Gerardin, Eckhoff and Wenger, 2015. [Mass campaigns with antimalarial drugs: a modeling comparison of
  artemether-lumefantrine and DHA-piperaquine with and without primaquine as tools for malaria control and
  elimination][gerardin-2015-mda].
  *BMC Infectious Diseases*. 15:144


### Vaccines


* Penny, *et al*., 2016. [Public health impact and cost-effectiveness of the RTS,S/AS01 malaria vaccine:
  a systematic comparison of predictions from four mathematical models][penny-2016].
  *The Lancet*. 387(100016): 367-375

* McCarthy, Wenger, Huynh and Eckhoff, 2015. [Calibration of an intrahost malaria model and parameter   ensemble evaluation of a pre-erythrocytic vaccine][mccarthy-2015].
  *Malaria Journal*. 14:6

* Wenger & Eckhoff, 2013. [A mathematical model of the impact of present and future malaria vaccines][wenger-2013]. *Malaria Journal*. 12:126

