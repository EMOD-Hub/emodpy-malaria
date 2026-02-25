import os
import json
import unittest
import emodpy_malaria.demographics.MalariaDemographics as MalariaDemographics
from emod_api.demographics.Node import Node
import emod_api.demographics.Demographics as ApiDemographics
import pandas as pd

from pathlib import Path
import sys
parent = Path(__file__).resolve().parent
sys.path.append(str(parent))


def delete_existing_file(filename):
    if os.path.isfile(filename):
        print(f'\tremove existing {filename}.')
        os.remove(filename)


class DemoTest(unittest.TestCase):
    def setUp(self) -> None:
        print(f"\n{self._testMethodName} started...")
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.out_folder = os.path.join(current_dir, 'demo_output')

    def check_for_unique_node_id(self, nodes):
        node_ids = list()
        for node in nodes:
            node_id = node['NodeID']
            if node_id not in node_ids:
                node_ids.append(node_id)
            else:
                return False
        return True

    def test_demo_basic_node(self):
        out_filename = os.path.join(self.out_folder, "demographics_basic_node.json")
        demog = MalariaDemographics.from_template_node()
        print(f"Writing out file: {out_filename}.")
        demog.generate_file(out_filename)
        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['Latitude'], 0)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['Longitude'], 0)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['InitialPopulation'], 1e6)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['FacilityName'], 1)
        self.assertEqual(demog_json['Nodes'][0]['NodeID'], 1)

    def test_demo_basic_node_2(self):
        out_filename = os.path.join(self.out_folder, "demographics_basic_node_2.json")
        lat = 1111
        lon = 999
        pop = 888
        name = 'test_name'
        forced_id = 777
        demog = MalariaDemographics.from_template_node(lat=lat, lon=lon, pop=pop, name=name, forced_id=forced_id)
        print(f"Writing out file: {out_filename}.")
        demog.generate_file(out_filename)
        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['Latitude'], lat)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['Longitude'], lon)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['InitialPopulation'], pop)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['FacilityName'], name)
        self.assertEqual(demog_json['Nodes'][0]['NodeID'], forced_id)
        # self.assertEqual(len(demog.implicits), 1)  # two more implicits again

    @staticmethod
    def demog_template_test(template, **kwargs):
        demog = MalariaDemographics.from_template_node()
        template(demog, **kwargs)
        return demog

    def test_set_risk_lowmedium(self):
        mean = 0.0
        sigma = 1.6
        demog = MalariaDemographics.from_template_node()
        demog.set_risk_lowmedium()
        # demog.SetHeteroRiskLognormalDist( mean, sigma )
        template_setting = {"RiskDistributionFlag": 5,
                            "RiskDistribution1": mean,
                            "RiskDistribution2": sigma}
        for key, value in template_setting.items():
            self.assertEqual(value, demog.raw['Defaults']['IndividualAttributes'][key])

        self.assertEqual(5, demog.raw['Defaults']['IndividualAttributes']['RiskDistributionFlag'])
        self.assertEqual(mean, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution1'])
        self.assertEqual(sigma, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution2'])
        # print(f"{demog.implicits}")
        # self.assertEqual(len(demog.implicits), 2)  # there are 4 implicits in this one??

    def test_set_risk_high(self):
        mean = 1
        demog = MalariaDemographics.from_template_node()
        demog.set_risk_high()
        # demog.SetHeteroRiskExponDist( mean )
        template_setting = {"RiskDistributionFlag": 3,
                            "RiskDistribution1": mean,
                            "RiskDistribution2": 0}
        for key, value in template_setting.items():
            self.assertEqual(value, demog.raw['Defaults']['IndividualAttributes'][key])

        self.assertEqual(3, demog.raw['Defaults']['IndividualAttributes']['RiskDistributionFlag'])
        self.assertEqual(mean, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution1'])
        self.assertEqual(0, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution2'])
        # self.assertEqual(len(demog.implicits), 2) # there are 4 implicits in this one??

    def test_from_csv(self):
        out_filename = os.path.join(self.out_folder, "demographics_from_csv.json")
        delete_existing_file(out_filename)
        id_ref = "from_csv_test"

        current_dir = os.path.dirname(os.path.realpath(__file__))
        input_file = os.path.join(current_dir, 'demo_data', 'demog_in.csv')
        demog = MalariaDemographics.from_csv(input_file, res=25 / 3600, id_ref=id_ref)
        self.assertEqual(demog.idref, id_ref)
        demog.SetDefaultProperties()
        demog.generate_file(out_filename)
        sorted_nodes = ApiDemographics.get_node_ids_from_file(out_filename)

        self.assertEqual(demog.idref, id_ref)
        self.assertGreater(len(sorted_nodes), 0)

        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)

        # Checking we can grab a node
        inspect_node = demog.get_node(demog.nodes[15].id)
        self.assertEqual(inspect_node.id, demog.nodes[15].id, msg=f"This node should have an id of {demog.nodes[15].id} but instead it is {inspect_node.id}")

        with self.assertRaises(ValueError):
            demog.get_node(161839)

        self.assertEqual(demog_json['Metadata']['IdReference'], id_ref)

        self.assertDictEqual(demog_json, demog.raw)

        import pandas as pd
        csv_df = pd.read_csv(input_file, encoding='iso-8859-1')

        pop_threshold = 25000  # hardcoded value
        csv_df = csv_df[(6 * csv_df['under5_pop']) >= pop_threshold]
        self.assertEqual(len(csv_df), len(demog_json['Nodes']))

        self.assertTrue(self.check_for_unique_node_id((demog.raw['Nodes'])))

    def test_from_csv_2(self):
        out_filename = os.path.join(self.out_folder, "demographics_from_csv_2.json")
        delete_existing_file(out_filename)

        current_dir = os.path.dirname(os.path.realpath(__file__))
        input_file = os.path.join(current_dir, "demo_data", "nodes.csv")
        demog = MalariaDemographics.from_csv(input_file, res=25 / 3600)
        demog.SetDefaultProperties()
        demog.generate_file(out_filename)
        sorted_nodes = ApiDemographics.get_node_ids_from_file(out_filename)

        self.assertGreater(len(sorted_nodes), 0)

        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')

        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)

        # Checking we can grab a node
        inspect_node = demog.get_node(demog.nodes[0].id)
        self.assertEqual(inspect_node.id, demog.nodes[0].id, msg=f"This node should have an id of {demog.nodes[0].id} "
                                                                 f"but instead it is {inspect_node.id}")

        id_reference = 'from_csv' # hardcoded value
        self.assertEqual(demog_json['Metadata']['IdReference'], id_reference)

        self.assertDictEqual(demog_json, demog.raw)

        import pandas as pd
        csv_df = pd.read_csv(input_file, encoding='iso-8859-1')

        # checking if we have the same number of nodes and the number of rows in csv file
        self.assertEqual(len(csv_df), len(demog_json['Nodes']))

        self.assertTrue(self.check_for_unique_node_id(demog.raw['Nodes']))
        for index, row in csv_df.iterrows():
            pop = int(row['pop'])
            lat = float(row['lat'])
            lon = float(row['lon'])
            node_id = int(row['node_id'])
            self.assertEqual(pop, demog.nodes[index].node_attributes.initial_population)
            self.assertEqual(lat, demog.nodes[index].node_attributes.latitude)
            self.assertEqual(lon, demog.nodes[index].node_attributes.longitude)
            self.assertEqual(node_id, demog.nodes[index].forced_id)

    def test_add_vector_species_from_csv(self):
        """
        Checks that add_initial_vectors_per_species_from_csv():
            does not accept a nonexistent csv path
            appropriately maps the node id to an array of species presence
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        csv_path = os.path.join(current_dir, "inputs", "species_vec.csv")
        bad_csv_path = os.path.join(current_dir, "inputs", "species_vec2.csv")
        output_file = os.path.join(current_dir, "demo_output", "vec_species_from_csv.csv")
        delete_existing_file(output_file)

        data = pd.read_csv(csv_path)

        # creates list of node_ids from csv
        nodes = [Node(100, 200, 500, forced_id=id, name=f"id_{id}") for id in list(data["node_id"])]

        # creates demographics object with only nodes from csv
        demog = MalariaDemographics.MalariaDemographics(nodes=nodes)
        demog.add_initial_vectors_per_species_from_csv(csv_path)

        demog.generate_file(output_file)
        with open(output_file, 'r') as demo_file:
            demog_dict = json.load(demo_file)

        # checks species values for each node from csv (dataframe) against generated file
        for node in demog_dict["Nodes"]:
            row = data[data["node_id"] == node["NodeID"]]
            columns = list(data.columns)
            columns.remove("node_id")

            for species in columns:
                node["NodeAttributes"]["InitialVectorsPerSpecies"][species]
                self.assertEqual(list(row[species])[0], node["NodeAttributes"]["InitialVectorsPerSpecies"][species])

        # tests that a bad csv path will yield ValueError
        bad_demog = MalariaDemographics.MalariaDemographics(nodes=nodes)
        with self.assertRaises(ValueError):
            bad_demog.add_initial_vectors_per_species_from_csv(bad_csv_path)

    def test_add_vector_species(self):
        """
        Tests that add_initial_vectors_per_species():
            Applies species to all nodes when none are specified
            Applies species to specified node when it is specified
            Applies species to several specified nodes as expected
            Does not accept invalid node ids
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        outfile = os.path.join(current_dir, "demo_output", "vec_with_id.json")
        outfile2 = os.path.join(current_dir, "demo_output", "vec_with_no_id.json")

        delete_existing_file(outfile)
        delete_existing_file(outfile2)

        # tests that specifying vec_species with no node ids is as expected
        vec_species = {"Mosquito": 200}
        demog_no_id = MalariaDemographics.from_template_node()
        demog_no_id.add_initial_vectors_per_species(init_vector_species=vec_species)
        demog_no_id.generate_file(outfile)

        with open(outfile, 'r') as demo_file:
            demog_no_id_dict = json.load(demo_file)

        self.assertEqual(demog_no_id_dict["Defaults"]["NodeAttributes"]["InitialVectorsPerSpecies"], vec_species)

        # tests that specifying vec species with node id list applies vec species
        # to that node as expected
        vec_species2 = {"Mosquito": 300}
        demog = MalariaDemographics.from_template_node(forced_id=5)
        demog.add_initial_vectors_per_species(init_vector_species=vec_species2, node_ids=[5])
        demog.generate_file(outfile2)
        with open(outfile2, 'r') as demo_file:
            demog_dict = json.load(demo_file)
        self.assertEqual(demog_dict["Nodes"][0]["NodeAttributes"]["InitialVectorsPerSpecies"], vec_species2)

        # tests that specifying vec species with node id list with >1 length applies vec species
        # to all nodes as expected
        nodes = [Node(100, 200, 500, forced_id=id, name=f"id_{id}") for id in range(5)]
        demog_with_nodes = MalariaDemographics.MalariaDemographics(nodes=nodes)
        demog_with_nodes.add_initial_vectors_per_species(init_vector_species=vec_species2, node_ids=[0, 1, 2, 3, 4])
        delete_existing_file(outfile)
        demog_with_nodes.generate_file(outfile)

        with open(outfile, 'r') as demo_file:
            demog_dict_nodes = json.load(demo_file)["Nodes"]

        for node in demog_dict_nodes:
            self.assertEqual(node["NodeAttributes"]["InitialVectorsPerSpecies"], vec_species2)

        # tests that invalid node id yields ValueError
        with self.assertRaises(ValueError):
            demog_with_nodes.add_initial_vectors_per_species(init_vector_species=vec_species2, node_ids=[6])

    def test_from_csv_bad_id(self):
        input_file = os.path.join('demo_data', 'demog_in_faulty.csv')

        with self.assertRaises(ValueError):
            MalariaDemographics.from_csv(input_file, res=25 / 3600)

    @unittest.skip("Known issue logged at https://github.com/InstituteforDiseaseModeling/emodpy-malaria/issues/620")
    def test_from_pop_csv(self):
        out_filename = os.path.join(self.out_folder, "demographics_from_pop_csv.json")
        delete_existing_file(out_filename)

        current_dir = os.path.dirname(os.path.realpath(__file__))
        input_file = os.path.join(current_dir, "demo_data", "nodes.csv")
        demog = MalariaDemographics.from_pop_csv(input_file)
        demog.SetDefaultProperties()
        demog.generate_file(out_filename)
        sorted_nodes = ApiDemographics.get_node_ids_from_file(out_filename)

        self.assertGreater(len(sorted_nodes), 0)

        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)

        # Checking we can grab a node
        inspect_node = demog.get_node(demog.nodes[0].id)
        self.assertEqual(inspect_node.id, demog.nodes[0].id,
                         msg=f"This node should have an id of {demog.nodes[0].id} but instead it is {inspect_node.id}")

        with self.assertRaises(ValueError):
            demog.get_node(161839)

        id_reference = 'No_Site'  # hardcoded value
        self.assertEqual(demog_json['Metadata']['IdReference'], id_reference)

        self.assertDictEqual(demog_json, demog.raw)

        # csv_df = pd.read_csv(input_file, encoding='iso-8859-1')
        # the following assertion fails, logged as https://github.com/InstituteforDiseaseModeling/emod-api/issues/367
        # self.assertEqual(len(csv_df), len(demog_json['Nodes']))

        self.assertTrue(self.check_for_unique_node_id(demog.raw['Nodes']))

    def test_from_params(self):
        out_filename = os.path.join(self.out_folder, "demographics_from_params.json")
        delete_existing_file(out_filename)

        totpop = 1e5
        num_nodes = 250
        frac_rural = 0.1
        demog = MalariaDemographics.from_params(tot_pop=totpop, num_nodes=num_nodes, frac_rural=frac_rural)
        demog.SetDefaultProperties()
        demog.generate_file(out_filename)

        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)

        id_reference = 'from_params'  # hardcoded value
        self.assertEqual(demog_json['Metadata']['IdReference'], id_reference)

        self.assertDictEqual(demog_json, demog.raw)

        self.assertEqual(num_nodes, len(demog_json['Nodes']))

        sum_pop = 0
        for node in demog_json['Nodes']:
            sum_pop += node['NodeAttributes']['InitialPopulation']
        # Todo: add this assertion back when #112 is fixed.
        # self.assertEqual(sum_pop, totpop)
        if sum_pop != totpop:
            print(f"Something went wrong, expected totpop is {totpop}, got {sum_pop} total population.")

        self.assertTrue(self.check_for_unique_node_id(demog.raw['Nodes']))

        # Todo: assert frac_rural after we figure out the definition of this parameter

    def test_add_larval_habitat_multiplier(self):
        out_filename = os.path.join(self.out_folder, "demographics_from_csv.json")
        delete_existing_file(out_filename)
        id_ref = "from_csv_test"
        node_id = 1793079799
        factor = 0.455
        species = "arabiensis"
        habitat_type = "TEMPORARY_RAINFALL"
        current_dir = os.path.dirname(os.path.realpath(__file__))
        input_file = os.path.join(current_dir, 'demo_data', 'demog_in.csv')
        demog = MalariaDemographics.from_csv(input_file, res=25 / 3600, id_ref=id_ref)
        import schema_path_file
        demog.add_larval_habitat_multiplier(schema=schema_path_file.schema_file, hab_type=habitat_type,
                                            multiplier=factor, species=species, node_id=node_id)
        demog.generate_file(out_filename)
        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)

        for node in demog_json['Nodes']:
            if node['NodeID'] == node_id:
                self.assertEqual(node['NodeAttributes']['LarvalHabitatMultiplier'][0]["Factor"], factor)
                self.assertEqual(node['NodeAttributes']['LarvalHabitatMultiplier'][0]["Species"], species)
                self.assertEqual(node['NodeAttributes']['LarvalHabitatMultiplier'][0]["Habitat"], habitat_type)
            else:
                self.assertNotIn("LarvalHabitatMultiplier", node['NodeAttributes'])


if __name__ == '__main__':
    unittest.main()
