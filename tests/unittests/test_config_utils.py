import unittest
import pytest
from types import SimpleNamespace
from emodpy_malaria.utils.config_utils import validate_mosquito_release_genome


def _make_config(species_list):
    """Build a minimal config stub for validate_mosquito_release_genome.

    species_list: list of dicts:
        {"name": str, "genes": [{"name": str, "is_gender": bool, "alleles": [str, ...]}]}
    """
    def _make_gene(g):
        gene = {"Name": g["name"], "Alleles": [{"Name": a} for a in g["alleles"]]}
        if g.get("is_gender"):
            gene["Is_Gender_Gene"] = 1
        return gene

    def _make_species(s):
        sp = SimpleNamespace()
        sp.Name = s["name"]
        sp.Genes = [_make_gene(g) for g in s["genes"]]
        return sp

    params = SimpleNamespace()
    params.Vector_Species_Params = [_make_species(s) for s in species_list]
    config = SimpleNamespace()
    config.parameters = params
    return config


@pytest.mark.unit
class TestValidateMosquitoReleaseGenome(unittest.TestCase):

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _gambiae_config_implicit_gender(self):
        """One autosomal gene, gender gene is implicit (not in config)."""
        return _make_config([{
            "name": "gambiae",
            "genes": [
                {"name": "driver_gene", "alleles": ["a0", "a1", "a2"]},
            ]
        }])

    def _gambiae_config_explicit_gender(self):
        """Explicit gender gene + one autosomal gene."""
        return _make_config([{
            "name": "gambiae",
            "genes": [
                {"name": "gender", "is_gender": True, "alleles": ["X", "Y"]},
                {"name": "driver_gene", "alleles": ["a0", "a1", "a2"]},
            ]
        }])

    def _two_autosomal_config(self):
        """Implicit gender gene + two autosomal genes."""
        return _make_config([{
            "name": "arabiensis",
            "genes": [
                {"name": "gene_A", "alleles": ["a0", "a1"]},
                {"name": "gene_B", "alleles": ["b0", "b1"]},
            ]
        }])

    # ------------------------------------------------------------------
    # Species lookup
    # ------------------------------------------------------------------

    def test_species_not_in_config_raises(self):
        config = self._gambiae_config_implicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "funestus",
                                             [["X", "X"], ["a0", "a0"]],
                                             "released_genome")
        self.assertIn("funestus", str(ctx.exception))
        self.assertIn("gambiae", str(ctx.exception))

    # ------------------------------------------------------------------
    # Locus count — implicit gender gene
    # ------------------------------------------------------------------

    def test_valid_genome_implicit_gender(self):
        config = self._gambiae_config_implicit_gender()
        result = validate_mosquito_release_genome(config, "gambiae",
                                                  [["X", "X"], ["a0", "a1"]],
                                                  "released_genome")
        self.assertIs(result, config)

    def test_too_few_loci_implicit_gender_raises(self):
        config = self._gambiae_config_implicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "X"]],
                                             "released_genome")
        self.assertIn("1 loci", str(ctx.exception))
        self.assertIn("2", str(ctx.exception))

    def test_too_many_loci_implicit_gender_raises(self):
        config = self._gambiae_config_implicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "X"], ["a0", "a0"], ["a0", "a0"]],
                                             "released_genome")
        self.assertIn("3 loci", str(ctx.exception))

    # ------------------------------------------------------------------
    # Locus count — explicit gender gene
    # ------------------------------------------------------------------

    def test_valid_genome_explicit_gender(self):
        config = self._gambiae_config_explicit_gender()
        result = validate_mosquito_release_genome(config, "gambiae",
                                                  [["X", "Y"], ["a0", "a0"]],
                                                  "released_genome")
        self.assertIs(result, config)

    def test_too_few_loci_explicit_gender_raises(self):
        config = self._gambiae_config_explicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "Y"]],
                                             "released_genome")
        self.assertIn("1 loci", str(ctx.exception))

    def test_too_many_loci_explicit_gender_raises(self):
        config = self._gambiae_config_explicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "Y"], ["a0", "a0"], ["a0", "a0"]],
                                             "released_genome")
        self.assertIn("3 loci", str(ctx.exception))

    # ------------------------------------------------------------------
    # Multiple autosomal genes
    # ------------------------------------------------------------------

    def test_valid_genome_two_autosomal_genes(self):
        config = self._two_autosomal_config()
        result = validate_mosquito_release_genome(config, "arabiensis",
                                                  [["X", "X"], ["a0", "a1"], ["b0", "b1"]],
                                                  "released_genome")
        self.assertIs(result, config)

    def test_wrong_locus_count_two_autosomal_genes_raises(self):
        config = self._two_autosomal_config()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "arabiensis",
                                             [["X", "X"], ["a0", "a1"]],
                                             "released_genome")
        self.assertIn("2 loci", str(ctx.exception))
        self.assertIn("3", str(ctx.exception))

    # ------------------------------------------------------------------
    # Allele validation
    # ------------------------------------------------------------------

    def test_invalid_allele_raises(self):
        config = self._gambiae_config_implicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "X"], ["a0", "INVALID"]],
                                             "released_genome")
        self.assertIn("INVALID", str(ctx.exception))
        self.assertIn("driver_gene", str(ctx.exception))
        self.assertIn("gambiae", str(ctx.exception))

    def test_invalid_allele_second_locus_raises(self):
        config = self._two_autosomal_config()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "arabiensis",
                                             [["X", "Y"], ["a0", "a1"], ["b0", "WRONG"]],
                                             "released_genome")
        self.assertIn("WRONG", str(ctx.exception))
        self.assertIn("gene_B", str(ctx.exception))

    def test_x_and_y_always_valid_implicit_gender(self):
        """X and Y at the gender locus should never raise even though they are
        not in the config genes (implicit gender gene)."""
        config = self._gambiae_config_implicit_gender()
        result = validate_mosquito_release_genome(config, "gambiae",
                                                  [["X", "Y"], ["a0", "a1"]],
                                                  "released_genome")
        self.assertIs(result, config)

    def test_x_and_y_valid_in_explicit_gender_gene(self):
        config = self._gambiae_config_explicit_gender()
        result = validate_mosquito_release_genome(config, "gambiae",
                                                  [["X", "Y"], ["a2", "a0"]],
                                                  "released_genome")
        self.assertIs(result, config)

    # ------------------------------------------------------------------
    # param_name appears in error messages
    # ------------------------------------------------------------------

    def test_param_name_in_error_wrong_locus_count(self):
        config = self._gambiae_config_implicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "X"]],
                                             "released_mate_genome")
        self.assertIn("released_mate_genome", str(ctx.exception))

    def test_param_name_in_error_invalid_allele(self):
        config = self._gambiae_config_implicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "X"], ["BAD", "a0"]],
                                             "released_mate_genome")
        self.assertIn("released_mate_genome", str(ctx.exception))

    # ------------------------------------------------------------------
    # Multiple species in config
    # ------------------------------------------------------------------

    def test_correct_species_selected_from_multiple(self):
        config = _make_config([
            {"name": "gambiae", "genes": [{"name": "gA", "alleles": ["g0", "g1"]}]},
            {"name": "arabiensis", "genes": [{"name": "aA", "alleles": ["a0", "a1"]}]},
        ])
        # valid for arabiensis, would be invalid for gambiae (wrong allele names)
        result = validate_mosquito_release_genome(config, "arabiensis",
                                                  [["X", "X"], ["a0", "a1"]],
                                                  "released_genome")
        self.assertIs(result, config)

    def test_allele_from_wrong_species_raises(self):
        config = _make_config([
            {"name": "gambiae", "genes": [{"name": "gA", "alleles": ["g0", "g1"]}]},
            {"name": "arabiensis", "genes": [{"name": "aA", "alleles": ["a0", "a1"]}]},
        ])
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "X"], ["a0", "a1"]],
                                             "released_genome")
        self.assertIn("a0", str(ctx.exception))
        self.assertIn("gambiae", str(ctx.exception))

    # ------------------------------------------------------------------
    # Edge cases: empty inputs
    # ------------------------------------------------------------------

    def test_empty_genome_raises(self):
        config = self._gambiae_config_implicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [],
                                             "released_genome")
        self.assertIn("0 loci", str(ctx.exception))
        self.assertIn("2", str(ctx.exception))

    def test_empty_species_list_raises(self):
        config = _make_config([])
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "X"], ["a0", "a0"]],
                                             "released_genome")
        self.assertIn("gambiae", str(ctx.exception))

    # ------------------------------------------------------------------
    # Species with no autosomal genes (only implicit gender)
    # ------------------------------------------------------------------

    def test_species_with_no_genes_expects_one_locus(self):
        config = _make_config([{"name": "minimal", "genes": []}])
        result = validate_mosquito_release_genome(config, "minimal",
                                                  [["X", "X"]],
                                                  "released_genome")
        self.assertIs(result, config)

    def test_species_with_no_genes_wrong_locus_count_raises(self):
        config = _make_config([{"name": "minimal", "genes": []}])
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "minimal",
                                             [["X", "X"], ["a0", "a0"]],
                                             "released_genome")
        self.assertIn("2 loci", str(ctx.exception))
        self.assertIn("1", str(ctx.exception))

    # ------------------------------------------------------------------
    # Implicit gender locus: alleles are NOT validated
    # ------------------------------------------------------------------

    def test_arbitrary_tokens_at_implicit_gender_locus_are_valid(self):
        """The implicit gender locus is skipped during allele validation."""
        config = self._gambiae_config_implicit_gender()
        result = validate_mosquito_release_genome(config, "gambiae",
                                                  [["FOO", "BAR"], ["a0", "a1"]],
                                                  "released_genome")
        self.assertIs(result, config)

    # ------------------------------------------------------------------
    # Explicit gender locus: non-X/Y alleles ARE validated
    # ------------------------------------------------------------------

    def test_invalid_allele_at_explicit_gender_locus_raises(self):
        """With an explicit gender gene, alleles other than X/Y must be in the gene's allele list."""
        config = self._gambiae_config_explicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "NOTXY"], ["a0", "a0"]],
                                             "released_genome")
        self.assertIn("NOTXY", str(ctx.exception))
        self.assertIn("gender", str(ctx.exception))

    # ------------------------------------------------------------------
    # Allele used at the wrong autosomal gene's locus
    # ------------------------------------------------------------------

    def test_allele_from_wrong_autosomal_gene_raises(self):
        """b0/b1 are valid for gene_B but not for gene_A; using them at gene_A's locus should raise."""
        config = self._two_autosomal_config()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "arabiensis",
                                             [["X", "X"], ["b0", "b1"], ["b0", "b1"]],
                                             "released_genome")
        self.assertIn("b0", str(ctx.exception))
        self.assertIn("gene_A", str(ctx.exception))

    # ------------------------------------------------------------------
    # Homozygous pair (both alleles identical)
    # ------------------------------------------------------------------

    def test_homozygous_allele_pair_valid(self):
        config = self._gambiae_config_implicit_gender()
        result = validate_mosquito_release_genome(config, "gambiae",
                                                  [["X", "X"], ["a2", "a2"]],
                                                  "released_genome")
        self.assertIs(result, config)

    # ------------------------------------------------------------------
    # Error message includes valid alleles list
    # ------------------------------------------------------------------

    def test_error_message_includes_valid_alleles_for_gene(self):
        config = self._gambiae_config_implicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "X"], ["a0", "BAD"]],
                                             "released_genome")
        error = str(ctx.exception)
        self.assertIn("a0", error)
        self.assertIn("a1", error)
        self.assertIn("a2", error)

    # ------------------------------------------------------------------
    # Empty-string alleles
    # ------------------------------------------------------------------

    def test_empty_string_allele_at_autosomal_locus_raises(self):
        config = self._gambiae_config_implicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", "X"], ["a0", ""]],
                                             "released_genome")
        self.assertIn("empty", str(ctx.exception))
        self.assertIn("released_genome", str(ctx.exception))

    def test_empty_string_allele_at_implicit_gender_locus_raises(self):
        config = self._gambiae_config_implicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["", "X"], ["a0", "a1"]],
                                             "released_genome")
        self.assertIn("empty", str(ctx.exception))
        self.assertIn("0", str(ctx.exception))

    def test_empty_string_allele_at_explicit_gender_locus_raises(self):
        config = self._gambiae_config_explicit_gender()
        with self.assertRaises(ValueError) as ctx:
            validate_mosquito_release_genome(config, "gambiae",
                                             [["X", ""], ["a0", "a0"]],
                                             "released_genome")
        self.assertIn("empty", str(ctx.exception))

