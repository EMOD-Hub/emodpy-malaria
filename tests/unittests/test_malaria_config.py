import unittest
from copy import deepcopy
import json
import os, sys

from emod_api.config import default_from_schema_no_validation as dfs

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

default_config = None  # is set in setUpClass()

import schema_path_file

from emodpy_malaria.malaria_config import set_team_defaults, add_species, set_max_larval_capacity

from emodpy_malaria.vector_config import \
    add_genes_and_alleles, \
    add_mutation, \
    add_insecticide_resistance


class TestMalariaConfig(unittest.TestCase):
    default_config = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.default_config = dfs.write_default_from_schema(schema_path_file.schema_path)  # default_config.json

    def setUp(self) -> None:
        self.is_debugging = False
        self.config = dfs.get_config_from_default_and_params(
            config_path='default_config.json',
            set_fn=self.set_malaria_config
        )
        self.config = set_team_defaults(self.config, schema_path_file)

    def set_malaria_config(self, config):
        config.parameters.Simulation_Type = "MALARIA_SIM"
        config.parameters.Infectious_Period_Constant = 0
        config.parameters.Enable_Demographics_Birth = 1
        config.parameters.Enable_Demographics_Reporting = 0
        config.parameters.Run_Number = 99
        config.parameters.Simulation_Duration = 60
        config.parameters.Enable_Demographics_Risk = 1

        return config

    def add_insecticide_resistance(self, schema_path_file, insecticide_name, species, combo,
                                   blocking=1.0, killing=1.0, larval_killing=1.0, repelling=1.0):
        add_insecticide_resistance(
            self.config,
            manifest=schema_path_file,
            insecticide_name=insecticide_name,
            species=species,
            allele_combo=combo,
            blocking=blocking,
            killing=killing,
            larval_killing=larval_killing,
            repelling=repelling
        )

    def tearDown(self) -> None:
        if self.is_debugging:
            with open(f'DEBUG_{self._testMethodName}.json', 'w') as outfile:
                debug_object = {}
                debug_object['config'] = self.config
                json.dump(debug_object, outfile, indent=4, sort_keys=True)

    def test_team_defaults(self):

        self.assertEqual(self.config.parameters.Vector_Species_Params, [])

        found_drug_names = []
        for mdp in self.config.parameters.Malaria_Drug_Params:
            found_drug_names.append(mdp['Name'])
        self.assertIn('Chloroquine', found_drug_names)
        self.assertIn('Artemether', found_drug_names)
        self.assertIn('Lumefantrine', found_drug_names)

    def test_add_resistance_new_insecticide(self):
        add_insecticide_resistance(self.config,
                                   schema_path_file,
                                   insecticide_name='Honey',
                                   species='arabiensis',
                                   allele_combo=[['X', '*']],
                                   killing=0.17,
                                   blocking=0.22,
                                   larval_killing=0.7,
                                   repelling=0.33)
        add_insecticide_resistance(self.config,
                                   schema_path_file,
                                   insecticide_name='Honey',
                                   species='funestus',
                                   allele_combo=[['X', 'Y']],
                                   killing=0.15,
                                   blocking=0.2,
                                   larval_killing=0.55,
                                   repelling=0.33)
        add_insecticide_resistance(self.config,
                                   schema_path_file,
                                   insecticide_name='Vinegar',
                                   species='arabiensis',
                                   allele_combo=[['X', 'Y']],
                                   killing=0.5,
                                   blocking=0.2,
                                   larval_killing=0.7,
                                   repelling=0.44)
        self.assertEqual(len(self.config.parameters.Insecticides), 2)
        for insecticide in self.config.parameters.Insecticides:
            if insecticide.Name == "Honey":
                self.assertEqual(len(insecticide.Resistances), 2)
                for resistance in insecticide.Resistances:
                    if resistance.Species == "arabiensis":
                        self.assertEqual(resistance.Allele_Combinations, [['X', '*']])
                        self.assertEqual(resistance.Larval_Killing_Modifier, 0.7)
                        self.assertEqual(resistance.Killing_Modifier, 0.17)
                        self.assertEqual(resistance.Blocking_Modifier, 0.22)
                    elif resistance.Species == "funestus":
                        if resistance.Species == "arabiensis":
                            self.assertEqual(resistance.Larval_Killing_Modifier, 0.55)
                            self.assertEqual(resistance.Killing_Modifier, 0.15)
                            self.assertEqual(resistance.Blocking_Modifier, 0.2)
            elif insecticide.Name == "Vinegar":
                self.assertEqual(len(insecticide.Resistances), 1)
                self.assertEqual(insecticide.Resistances[0].Species, "arabiensis")
                self.assertEqual(insecticide.Resistances[0].Repelling_Modifier, 0.44)

            else:
                raise ValueError(f"We should not be here, shouldn't have insecticide with name {insecticide.Name}.\n")

    def test_add_genes_and_alleles(self):
        add_species(self.config, schema_path_file, ["funestus", "arabiensis"])
        add_genes_and_alleles(self.config,
                    schema_path_file,
                    species="funestus",
                    alleles=[("a0", 0.5), ("a1", 0.35), ("a2", 0.15)])
        add_genes_and_alleles(self.config,
                    schema_path_file,
                    species="funestus",
                    alleles=[("b0", 0.90), ("b1", 0.1)])
        add_genes_and_alleles(self.config,
                    schema_path_file,
                    species="arabiensis",
                    alleles=[("c0", 0.66), ("c1", 0.1), ("c2", 0.24)])
        for species in self.config.parameters.Vector_Species_Params:
            if species.Name == "funestus":
                self.assertEqual(len(species.Genes), 2)
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "a2":
                            self.assertEqual(allele.Initial_Allele_Frequency, 0.15)
            elif species.Name == "arabiensis":
                self.assertEqual(len(species.Genes), 1)
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "c0":
                            self.assertEqual(allele.Initial_Allele_Frequency, 0.66)

    def test_add_genes_and_alleles_gender_gene(self):
        add_species(self.config, schema_path_file, ["funestus", "arabiensis"])
        add_genes_and_alleles(self.config,
                    schema_path_file,
                    species="funestus",
                    alleles=[("a0", 0.5, 1), ("a1", 0.35, 1), ("a2", 0.15)])
        add_genes_and_alleles(self.config,
                    schema_path_file,
                    species="funestus",
                    alleles=[("b0", 0.90), ("b1", 0.1)])
        add_genes_and_alleles(self.config,
                    schema_path_file,
                    species="arabiensis",
                    alleles=[("c0", 0.66), ("c1", 0.1), ("c2", 0.24)])
        for species in self.config.parameters.Vector_Species_Params:
            if species.Name == "funestus":
                self.assertEqual(len(species.Genes), 2)
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "a2":
                            self.assertEqual(gene.Is_Gender_Gene, 1)
                            self.assertEqual(allele.Initial_Allele_Frequency, 0.15)
            elif species.Name == "arabiensis":
                self.assertEqual(len(species.Genes), 1)
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "c0":
                            self.assertEqual(gene.Is_Gender_Gene, 0)
                            self.assertEqual(allele.Initial_Allele_Frequency, 0.66)

    def test_add_mutation(self):
        add_species(self.config, schema_path_file, ["funestus", "arabiensis"])
        add_genes_and_alleles(self.config,
                    schema_path_file,
                    species="funestus",
                    alleles=[("a0", 0.5), ("a1", 0.35), ("a2", 0.15)])
        add_genes_and_alleles(self.config,
                    schema_path_file,
                    species="funestus",
                    alleles=[("b0", 0.90), ("b1", 0.1)])
        add_genes_and_alleles(self.config,
                    schema_path_file,
                    species="arabiensis",
                    alleles=[("c0", 0.66), ("c1", 0.1), ("c2", 0.24)])
        add_mutation(self.config, schema_path_file, "arabiensis", mutate_from="c1", mutate_to="c2",
                     probability=0.04)
        add_mutation(self.config, schema_path_file, "arabiensis", mutate_from="c0", mutate_to="c1",
                     probability=0.02)
        add_mutation(self.config, schema_path_file, "funestus", mutate_from="a0", mutate_to="a1",
                     probability=0.023)
        for species in self.config.parameters.Vector_Species_Params:
            if species.Name == "funestus":
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "a2":
                            self.assertEqual(gene.Mutations[0].Mutate_From, "a0")
                            self.assertEqual(gene.Mutations[0].Mutate_To, "a1")
                            self.assertEqual(gene.Mutations[0].Probability_Of_Mutation, 0.023)
            elif species.Name == "arabiensis":
                for gene in species.Genes:
                    for allele in gene.Alleles:
                        if allele.Name == "c0":
                            self.assertEqual(len(gene.Mutations), 2)
                            for mutation in gene.Mutations:
                                if mutation.Mutate_From == "c0":
                                    self.assertEqual(mutation.Mutate_To, "c1")
                                    self.assertEqual(mutation.Probability_Of_Mutation, 0.02)
                                elif mutation.Mutate_From == "c1":
                                    self.assertEqual(mutation.Mutate_To, "c2")
                                    self.assertEqual(mutation.Probability_Of_Mutation, 0.04)


    def test_set_max_larval_capacity(self):
        add_species(self.config, schema_path_file, ["funestus", "arabiensis"])
        set_max_larval_capacity(self.config, "funestus", "TEMPORARY_RAINFALL", 123000)
        set_max_larval_capacity(self.config, "arabiensis", "TEMPORARY_RAINFALL", 654000)
        for species in self.config.parameters.Vector_Species_Params:
            if species.Name == "funestus":
                self.assertEqual(species.Habitats[0]["Habitat_Type"], "TEMPORARY_RAINFALL")
                self.assertEqual(species.Habitats[0]["Max_Larval_Capacity"], 123000)
            elif species.Name == "arabiensis":
                self.assertEqual(species.Habitats[0]["Habitat_Type"], "TEMPORARY_RAINFALL")
                self.assertEqual(species.Habitats[0]["Max_Larval_Capacity"], 654000)


if __name__ == '__main__':
    unittest.main()
