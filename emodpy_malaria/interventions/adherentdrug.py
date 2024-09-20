from emod_api import schema_to_class as s2c


def adherent_drug(campaign, cost: int = 1, doses: list = None, dose_interval: int = 1,
                  adherence_values: list = None,
                  non_adherence_options: list = None,
                  non_adherence_distribution: list = None, max_dose_consideration_duration: int = 40,
                  took_dose_event: str = "Took_Dose", intervention_name: str = None):
    """
        Configures adherent drug dictionary  using the **AdherentDrug** class, an individual-level
        intervention which extends the **AntimalarialDrug** class.

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        cost: Unit cost per drug.
        doses: Lists of drugs for each dose. For example,
            ``[["DrugA", DrugB"], ["DrugB"], [], ["DrugB"]]``. The empty list,
            ``[]``, indicates no drugs for that dose.
        dose_interval: Interval between doses of drugs, in days. Default is 1.
        adherence_values: A list defining WaningEffectMapCount waning effect's "Values",
            to be used to set the probability for a particular dose. Where the "Times"
            is the dose number inferred from 'doses' parameter and "Values" is the probably
            of that dose being successfully taken.
        non_adherence_options: List of enums to define what happens when the user
            is not adherent. If not defined then NEXT_UPDATE is used. Enum values are:
            ["STOP", "NEXT_UPDATE", "NEXT_DOSAGE_TIME", "LOST_TAKE_NEXT"].
        non_adherence_distribution: Non adherence probability value(s) assigned to
            the corresponding options in non_adherence_options. There must be one value
            in this list for each value in non_adherence_options. The sum of these
            values must equal 1.0.
        max_dose_consideration_duration: Maximum number of days that an individual
            will consider taking the doses of the drug.
        took_dose_event: Event that gets sent out every time a dose is taken.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it from
            others that use the same class. Default is AdeherentDrug_drug1_drug2 in alphabetical order.

    Returns:
    Configured **AdherentDrug** class dictionary
    """
    # built-in default so we can run this function by just putting in the config builder.
    waning_map = s2c.get_class_with_defaults("WaningEffectMapCount", campaign.schema_path)
    waning_map.Initial_Effect = 1

    if not doses:
        doses = [["Sulfadoxine", "Pyrimethamine", 'Amodiaquine'],
                 ['Amodiaquine'],
                 ['Amodiaquine']]

    inferred_times = [x + 1 for x in range(len(doses))]
    if not adherence_values:
        adherence_values = [1, 1, 1]

    # the default is for person to take everything every dose
    waning_map.Durability_Map.Times = inferred_times
    waning_map.Durability_Map.Values = adherence_values

    if len(adherence_values) != len(inferred_times):
        raise ValueError(f"Length of 'adherence_values' parameter ({len(adherence_values)}) does not match the "
                         f"length of 'doses' ({len(doses)}). These need to be the same as we are defining the "
                         f"probabilities of taking each dose.\n")

    if not non_adherence_options:
        non_adherence_options = ["NEXT_UPDATE"]
    if not non_adherence_distribution:
        non_adherence_distribution = [1]

    adherent_drug = s2c.get_class_with_defaults("AdherentDrug", campaign.schema_path)
    adherent_drug.Cost_To_Consumer = cost
    adherent_drug.Doses = doses
    adherent_drug.Dose_Interval = dose_interval
    adherent_drug.Adherence_Config = waning_map
    adherent_drug.Non_Adherence_Options = non_adherence_options
    adherent_drug.Non_Adherence_Distribution = non_adherence_distribution
    adherent_drug.Max_Dose_Consideration_Duration = max_dose_consideration_duration
    adherent_drug.Took_Dose_Event = campaign.get_send_trigger(took_dose_event, old=True)
    if not intervention_name:
        all_drugs = []
        for day in doses:
            for drug in day:
                all_drugs.append(drug)
        all_drugs = sorted(list(set(all_drugs)))
        intervention_name = "AdherentDrug"
        for drug in all_drugs:
            intervention_name = intervention_name + "_" + drug
    adherent_drug.Intervention_Name = intervention_name
    return adherent_drug
