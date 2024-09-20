# replace+genomes.py
# -----------------------------------------------------------------------------
# DanB 4/7/2021
# -----------------------------------------------------------------------------
import time
import os
import argparse
import numpy
import emod_api.serialization.SerializedPopulation as SerPop
from pathlib import Path
import importlib


class Genome:
    """Represent a single genome
    """
    def convert_char_to_int(ch):
        if ch == 'A':
            return 0
        elif ch == 'C':
            return 1
        elif ch == 'G':
            return 2
        elif ch == 'T':
            return 3
        else:
            raise Exception("Unknown character ch=" + ch)

    def create_genome(barcode_str, allele_root_id):
        g = Genome()
        g.barcode_str = barcode_str
        g.hash_code = 17    # must match value in C++ code, see file ParasiteGnome.cpp
        g.barcode_hash_code = 17    # must match value in C++ code, see file ParasiteGnome.cpp

        for ch in barcode_str:
            val = Genome.convert_char_to_int(ch)
            g.nucleotides.append(val)
            g.allele_roots.append(allele_root_id)
            g.barcode_hash_code = numpy.int32(31 * g.barcode_hash_code + val)
            g.hash_code = numpy.int32(31 * g.hash_code + val)
            g.hash_code = numpy.int32(31 * g.hash_code + allele_root_id)

        return g

    def __init__(self):
        self.hash_code = numpy.int32(0)
        self.barcode_hash_code = numpy.int32(0)
        self.allele_roots = []
        self.nucleotides = []
        self.barcode_str = ""

    @property
    def barcode(self):
        return self.barcode_str

    @property
    def hashcode(self):
        return self.hash_code

    def set_allele_roots(self, root):
        if len(self.allele_roots) > 0:
            raise Exception("Allele Roots already set")

        for val in self.nucleotides:
            self.allele_roots.append(root)

    def to_dtk_dict(self):
        dtk_dict = {}
        dtk_dict["m_pInner"] = {}
        dtk_dict["m_pInner"]["__class__"] = "ParasiteGenomeInner"
        dtk_dict["m_pInner"]["m_HashCode"] = int(self.hash_code)
        dtk_dict["m_pInner"]["m_BarcodeHashcode"] = int(self.barcode_hash_code)
        dtk_dict["m_pInner"]["m_NucleotideSequence"] = self.nucleotides
        dtk_dict["m_pInner"]["m_AlleleRoots"] = self.allele_roots

        return dtk_dict

    def to_dtk_map_entry(self):
        dtk_map_entry = {}
        dtk_map_entry["key"] = int(self.hash_code)
        dtk_map_entry["value"] = {}
        dtk_map_entry["value"] = self.to_dtk_dict()["m_pInner"]
        return dtk_map_entry


def print_hashcodes(ser_pop):
    for genome in ser_pop.dtk.simulation["ParasiteGenetics"]["m_ParasiteGenomeMap"]:
        print(genome.key)

    for node in ser_pop.nodes:
        for person in node["individualHumans"]:
            print("------------ " + str(person["suid"]["id"]) + " -----------------")
            for infection in person["infections"]:
                print(infection["infection_strain"]["m_Genome"]["m_pInner"]["m_HashCode"])

        for vector_pop in node["m_vectorpopulations"]:
            for vector in vector_pop["AdultQueues"]:
                print("------------ VECTOR " + str(vector["m_ID"]) + " -----------------")
                for oocyst in vector["m_OocystCohorts"]:
                    print("oocyst-male=" + str(oocyst["m_MaleGametocyteGenome"]["m_pInner"]["m_HashCode"])
                          + "--- "
                          + "oocyst-female=" + str(oocyst["m_pStrainIdentity"]["m_Genome"]["m_pInner"]["m_HashCode"]))
                for sporo in vector["m_SporozoiteCohorts"]:
                    print("sporo-male=" + str(sporo["m_MaleGametocyteGenome"]["m_pInner"]["m_HashCode"])
                          + "--- "
                          + "sporo-female=" + str(sporo["m_pStrainIdentity"]["m_Genome"]["m_pInner"]["m_HashCode"]))


def get_next_genome(next_barcode_fn, allele_root_id, ser_pop_genome_map, cache_genome_map):
    barcode_str = next_barcode_fn()
    key = barcode_str + "-" + str(allele_root_id)

    if key in cache_genome_map:
        genome = cache_genome_map[key]
    else:
        genome = Genome.create_genome(barcode_str, allele_root_id)
        cache_genome_map[key] = genome
        ser_pop_genome_map.append(genome.to_dtk_map_entry())

    dtk_genome_obj = genome.to_dtk_dict()
    # print(genome.barcode + "=" + str(genome.hashcode))
    return dtk_genome_obj


def replace_genomes(input_file, next_barcode_fn, output_file):
    """
    Replaces genomes in infected individuals and vectors.
    Args:
        input_file (): Input serialized population file
        next_barcode_fn (): Function that return the next barcode. The function is called once for every infection of an
         individual and once for every vector in the vector population.
        output_file (): Output file with replaced genomes.

    Returns:
        Nothing
    """
    if not os.path.exists(input_file):
        raise Exception(f"Couldn't find specified input file: {input_file}.")
    if next_barcode_fn is None:
        raise Exception("You must provide a function that returns the next barcode string")

    pop = SerPop.SerializedPopulation(input_file)
    ser_pop_genome_map = pop.dtk.simulation["ParasiteGenetics"]["m_ParasiteGenomeMap"]
    ser_pop_genome_map.clear()

    cache_genome_map = {}

    for node in pop.nodes:
        tic1 = time.perf_counter()
        for person in node["individualHumans"]:
            # print("------------ " + str(person["suid"]["id"]) + " -----------------")
            for infection in person["infections"]:
                next_genome = get_next_genome(next_barcode_fn, person["suid"]["id"], ser_pop_genome_map, cache_genome_map)
                length_barcode = len(infection["infection_strain"]["m_Genome"]["m_pInner"]["m_NucleotideSequence"])
                assert length_barcode == len(next_genome["m_pInner"]["m_NucleotideSequence"]), f"New barcode has wrong length."
                infection["infection_strain"]["m_Genome"] = next_genome

        tic2 = time.perf_counter()
        print(f"{tic2 - tic1:0.4f}")

        for vector_pop in node["m_vectorpopulations"]:
            print(len(vector_pop["AdultQueues"]))
            tic1 = time.perf_counter()
            for vector in vector_pop["AdultQueues"]["collection"]:
               # print("------------ VECTOR " + str(vector["m_ID"]) + " -----------------")
                for oocyst in vector["m_OocystCohorts"]:
                    genome_oocyst = get_next_genome(next_barcode_fn, -999, ser_pop_genome_map, cache_genome_map)
                    length_oocyst_barcode = len(oocyst["m_MaleGametocyteGenome"]["m_pInner"]["m_NucleotideSequence"])
                    assert len(genome_oocyst["m_pInner"]["m_NucleotideSequence"]) == length_oocyst_barcode, f"New barcode has wrong length."
                    oocyst["m_MaleGametocyteGenome"] = genome_oocyst

                    genome_oocyst = get_next_genome(next_barcode_fn, -999, ser_pop_genome_map, cache_genome_map)
                    length_oocyst_barcode = len(oocyst["m_pStrainIdentity"]["m_Genome"]["m_pInner"]["m_NucleotideSequence"])
                    assert len(genome_oocyst["m_pInner"]["m_NucleotideSequence"]) == length_oocyst_barcode, f"New barcode has wrong length."
                    oocyst["m_pStrainIdentity"]["m_Genome"] = genome_oocyst

                for sporo in vector["m_SporozoiteCohorts"]:
                    genome_sporo = get_next_genome(next_barcode_fn, -999, ser_pop_genome_map, cache_genome_map)
                    length_sporo_barcode = len(sporo["m_MaleGametocyteGenome"]["m_pInner"]["m_NucleotideSequence"])
                    assert len(genome_sporo["m_pInner"]["m_NucleotideSequence"]) == length_sporo_barcode, f"New barcode has wrong length."
                    sporo["m_MaleGametocyteGenome"] = genome_sporo

                    genome_sporo = get_next_genome(next_barcode_fn, -999, ser_pop_genome_map, cache_genome_map)
                    length_sporo_barcode = len(sporo["m_pStrainIdentity"]["m_Genome"]["m_pInner"]["m_NucleotideSequence"])
                    assert len(genome_sporo["m_pInner"]["m_NucleotideSequence"]) == length_sporo_barcode, f"New barcode has wrong length."
                    sporo["m_pStrainIdentity"]["m_Genome"] = genome_sporo

            tic2 = time.perf_counter()
            print(f"{tic2 - tic1:0.4f}")

    pop.write(output_file)


def test_replace_genomes(input_fn, get_next_barcode):
    if not os.path.exists(input_fn):
        raise Exception(f"Couldn't find specified input file: {input_fn}.")

    pop = SerPop.SerializedPopulation(input_fn)

    for node in pop.nodes:
        for person in node["individualHumans"]:
            for infection in person["infections"]:
                genome_as_int = list(map(Genome.convert_char_to_int, get_next_barcode()))
                assert infection["infection_strain"]["m_Genome"]["m_pInner"]["m_NucleotideSequence"] == genome_as_int

        for vector_pop in node["m_vectorpopulations"]:
            for vector in vector_pop["AdultQueues"]["collection"]:
                for oocyst in vector["m_OocystCohorts"]:
                    genome_as_int = list(map(Genome.convert_char_to_int, get_next_barcode()))
                    assert oocyst["m_MaleGametocyteGenome"]["m_pInner"]["m_NucleotideSequence"] == genome_as_int
                    genome_as_int = list(map(Genome.convert_char_to_int, get_next_barcode()))
                    assert oocyst["m_pStrainIdentity"]["m_Genome"]["m_pInner"]["m_NucleotideSequence"] == genome_as_int

                for sporo in vector["m_SporozoiteCohorts"]:
                    genome_as_int = list(map(Genome.convert_char_to_int, get_next_barcode()))
                    assert sporo["m_MaleGametocyteGenome"]["m_pInner"]["m_NucleotideSequence"] == genome_as_int
                    genome_as_int = list(map(Genome.convert_char_to_int, get_next_barcode()))
                    assert sporo["m_pStrainIdentity"]["m_Genome"]["m_pInner"]["m_NucleotideSequence"] == genome_as_int


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace genomes.", epilog="E.g. python replace_genomes.py -i state-00050.dtk -o low_eir_no_DR.dtk -m replace_genomes_get_next_barcode -f get_next_barcode")
    parser.add_argument("-i", "--input_file", type=Path, required=True, help="Serialized population file.")
    parser.add_argument("-o", "--output_file", type=Path, required=True, help="Serialized population output file.")
    parser.add_argument("-m", "--module", type=str, default="replace_genomes_get_next_barcode", help="Module that contains the function to generate the barcodes.")
    parser.add_argument("-f", "--get_next_barcode_func", type=str, default="get_next_barcode", help="Name of the function that returns the barcodes")
    args = parser.parse_args()

    try:
        user_defined_mod = importlib.import_module(args.module)
    except ModuleNotFoundError as err:
        print(err)
        print("Current working directory:", os.getcwd())
        exit(-1)

    replace_genomes(args.input_file, eval("user_defined_mod." + args.get_next_barcode_func), args.output_file)

    # importlib.reload(user_defined_mod)  # reimport module to reinitialize variables in module containing function to get next barcode
    # test_replace_genomes(args.output_file, eval("user_defined_mod." + args.get_next_barcode_func))