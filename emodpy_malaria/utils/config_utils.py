def validate_allele_combo(species_params, allele_combo):
    """
    Validate that a user provided an acceptable allele_combo
    where it is a two dimensional array of strings and the inner array has
    two elements where each element is an allele of the same gene.
    """
    if len(allele_combo) == 0:
        raise ValueError("allele_combo must define some alleles to target")

    for combo in allele_combo:
        if len(combo) != 2:
            raise ValueError(
                "Each combo in allele_combo must have two values - one for each chromosome, '*' is acceptable. \n")

    allele_names = []
    allele_names_in_combo = []
    for gene in species_params.Genes:
        for allele in gene["Alleles"]:
            allele_names.append(allele["Name"])

    for combo in allele_combo:
        for allele_name in combo:
            if allele_name != "X" and allele_name != "Y" and allele_name != "*":
                allele_names_in_combo.append(allele_name)

    for alnic in allele_names_in_combo:
        if alnic not in allele_names:
            raise ValueError(f"Allele name {alnic} submitted in one of the allele_combos is not found"
                             f" in the Genes parameter for {species_params.Name}.\n")

    return


def validate_mosquito_release_genome(config, released_species, released_genome, param_name):
    species_params = None
    for sp in config.parameters.Vector_Species_Params:
        if sp.Name == released_species:
            species_params = sp
            break
    if species_params is None:
        available = [sp.Name for sp in config.parameters.Vector_Species_Params]
        raise ValueError(
            f"MosquitoRelease uses released_species='{released_species}' but it is not "
            f"defined in config. Available species: {available}.")

    genes = list(species_params.Genes)
    has_explicit_gender_gene = any(gene.get("Is_Gender_Gene", 0) for gene in genes)
    expected_loci = len(genes) if has_explicit_gender_gene else len(genes) + 1

    if len(released_genome) != expected_loci:
        raise ValueError(
            f"'{param_name}' defines {len(released_genome)} loci but species "
            f"'{released_species}' expects {expected_loci} loci "
            f"({'with' if has_explicit_gender_gene else 'without'} an explicitly defined "
            f"gender gene in config). All loci must be specified.")

    for locus_idx, locus in enumerate(released_genome):
        for allele in locus:
            if allele == "":
                raise ValueError(
                    f"'{param_name}' contains an empty-string allele at locus index {locus_idx} "
                    f"for species '{released_species}'. Alleles must be non-empty strings.")
            if allele == "*":
                raise ValueError(
                    f"'{param_name}' contains a wildcard ('*') at locus index {locus_idx} "
                    f"for species '{released_species}'. Wildcards are not permitted in a released genome.")

    # Map each genome locus to its config gene; skip the implicit gender locus (X/Y only).
    genome_to_check = released_genome if has_explicit_gender_gene else released_genome[1:]
    for locus, gene in zip(genome_to_check, genes):
        valid_alleles = {allele["Name"] for allele in gene.get("Alleles", [])}
        gene_name = gene.get("Name", "?")
        for allele in locus:
            if allele in ("X", "Y"):
                continue
            if allele not in valid_alleles:
                raise ValueError(
                    f"'{param_name}' contains allele '{allele}' for gene '{gene_name}' "
                    f"of species '{released_species}' but it is not defined in config. "
                    f"Valid alleles for '{gene_name}': {sorted(valid_alleles)}.")

    return config


def validate_larval_habitat_defined(config, habitat, species):
    if str(habitat) == 'ALL_HABITATS':
        return config

    if species == 'ALL_SPECIES':
        for sp in config.parameters.Vector_Species_Params:
            for hab in sp.Habitats:
                if hab['Habitat_Type'] == habitat:
                    return config
        available = {
            sp.Name: [str(h['Habitat_Type']) for h in sp.Habitats]
            for sp in config.parameters.Vector_Species_Params
        }
        raise ValueError(
            f"LarvalHabitatMultiplierSpec uses habitat='{habitat}' but no species in "
            f"config has this habitat type defined. Defined habitats per species: {available}.")
    else:
        sp_params = None
        for sp in config.parameters.Vector_Species_Params:
            if sp.Name == species:
                sp_params = sp
                break
        if sp_params is None:
            available = [sp.Name for sp in config.parameters.Vector_Species_Params]
            raise ValueError(
                f"LarvalHabitatMultiplierSpec uses species='{species}' but it is not "
                f"defined in config. Available species: {available}.")
        for hab in sp_params.Habitats:
            if hab['Habitat_Type'] == habitat:
                return config
        available_habitats = [str(h['Habitat_Type']) for h in sp_params.Habitats]
        raise ValueError(
            f"LarvalHabitatMultiplierSpec uses habitat='{habitat}' for species "
            f"'{species}' but this habitat type is not defined for that species. "
            f"Defined habitats for '{species}': {available_habitats}.")


def validate_genome_locations_length(config, value, param_name, locations_attr):
    pg = getattr(config.parameters, 'Parasite_Genetics', None)
    if pg is None:
        return config
    locations = getattr(pg, locations_attr, None)
    if locations is None:
        return config
    expected = len(locations)
    got = len(value)
    if got != expected:
        kind = "characters" if isinstance(value, str) else "entries"
        raise ValueError(
            f"'{param_name}' has {got} {kind} but "
            f"Parasite_Genetics.{locations_attr} defines {expected} location(s). "
            f"These must match.")
    return config


def validate_insecticide_name(config, insecticide_name, intervention_name):
    defined_names = [ins.Name for ins in config.parameters.Insecticides]
    if insecticide_name not in defined_names:
        raise ValueError(
            f"{intervention_name} uses insecticide_name='{insecticide_name}' but it is not "
            f"defined in config. Defined insecticides: {defined_names}. "
            f"Use malaria_config.add_insecticide_resistance() in the config builder to define it.")
    return config


def validate_malaria_model(config, intervention_name):
    mm = config.parameters.Malaria_Model
    if mm != "MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS":
        raise ValueError(
            f"Config parameter 'Malaria_Model' is set to '{mm}' but "
            f"{intervention_name} requires "
            f"'MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS'. "
            f"Use malaria_config.set_parasite_genetics_defaults() to configure it.")
    return config


def validate_vector_sampling_type(config, intervention_name):
    vst = config.parameters.Vector_Sampling_Type
    if vst not in ("TRACK_ALL_VECTORS", "SAMPLE_IND_VECTORS"):
        raise ValueError(
            f"Config parameter 'Vector_Sampling_Type' is set to '{vst}' but "
            f"{intervention_name} requires 'TRACK_ALL_VECTORS' or 'SAMPLE_IND_VECTORS'.")
    return config


def validate_sugar_feeding_frequency(config):
    for sp in config.parameters.Vector_Species_Params:
        if sp.Vector_Sugar_Feeding_Frequency != "VECTOR_SUGAR_FEEDING_NONE":
            return config
    raise ValueError(
        "Config parameter 'Vector_Sugar_Feeding_Frequency' is set to "
        "'VECTOR_SUGAR_FEEDING_NONE' for all species but SugarTrap requires at "
        "least one species with a different value. Options: "
        "'VECTOR_SUGAR_FEEDING_ON_EMERGENCE_ONLY', "
        "'VECTOR_SUGAR_FEEDING_EVERY_FEED', "
        "'VECTOR_SUGAR_FEEDING_EVERY_DAY'.")


def validate_birth_rate_dependence(config):
    brd = config.parameters.Birth_Rate_Dependence
    valid = ("INDIVIDUAL_PREGNANCIES", "INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR")
    if brd not in valid:
        raise ValueError(
            f"Config parameter 'Birth_Rate_Dependence' is set to '{brd}' but "
            f"IsPregnant targeting requires '{valid[0]}' or '{valid[1]}'.")
    return config


def non_schema_checks(config):
    """
    Do additional voluntary checks for config consistency beyond what the schema validates.
    """
    p = config.parameters
    if hasattr(p, 'Simulation_Type') and p.Simulation_Type != 'MALARIA_SIM':
        raise ValueError(f"Simulation_Type must be 'MALARIA_SIM', got '{p.Simulation_Type}'")
    return


def validate_bins(bins: list, param_name: str, min_value: float = None, max_value: float = None) -> list:
    """
    Validate that a list of bin edges is in strictly ascending order and within optional bounds.

    Args:
        bins (list): List of numeric bin edges.
        param_name (str): Name of the parameter (for error messages).
        min_value (float): If set, all values must be >= this.
        max_value (float): If set, all values must be <= this.

    Returns:
        The validated list of bins.

    Raises:
        ValueError: If bins are not in ascending order or out of bounds.
    """
    if not bins:
        return bins
    for i in range(1, len(bins)):
        if bins[i] <= bins[i - 1]:
            raise ValueError(
                f"{param_name} must be in strictly ascending order, "
                f"but got {bins[i]} at index {i} after {bins[i - 1]} at index {i - 1}.")
    if min_value is not None and bins[0] < min_value:
        raise ValueError(
            f"{param_name} values must be >= {min_value}, but got {bins[0]}.")
    if max_value is not None and bins[-1] > max_value:
        raise ValueError(
            f"{param_name} values must be <= {max_value}, but got {bins[-1]}.")
    return bins
