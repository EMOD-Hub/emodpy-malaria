# convert_json_to_bin.py
# -----------------------------------------------------------------------------
# This script converts a JSON formatted txt file to an EMOD binary-formatted migration file.
# It also creates the required metadata file.
#
# The JSON file allows the user to specify different rates for different ages
# and genders.
#
# The output binary file has one or two Gender Data sections depending on whether
# the JSON file has different data for each gender.  Each Gender Data section has
# one Age Data section for each age specified in the JSON file.  Each Age Data
# section has one Node Data section for each node that individuals can migrate
# from.  Each Node Data section has one chunk of data
#    [1-unint32_t (4-bytes) plus 1-double (8-bytes)]
# for each destination where each Node Data section has DestinationsPerNode chunks.
# In other words, each Node Data section is 12-bytes times DestinationsPerNode
# -----------------------------------------------------------------------------


import collections
import datetime
import json
import os
import struct
import sys
from enum import Enum

# -----------------------------------------------------------------------------
# Age Limits
# -----------------------------------------------------------------------------
AGE_Min = 0.0
AGE_Max = 125.0


# -----------------------------------------------------------------------------
# CheckAge
# -----------------------------------------------------------------------------
def check_age(age):
    if age < AGE_Min:
        print(f"Invalid age={age} < {AGE_Min}")
        exit(-1)

    if age > AGE_Max:
        print(f"Invalid age={age} > {AGE_Max}")
        exit(-1)


# -----------------------------------------------------------------------------
# CheckAgeArray
# -----------------------------------------------------------------------------
def check_ages_array(ages_years):
    errmsg = JSON_AgesYears + " must be an array of ages in years and in increasing order."
    if len(ages_years) == 0:
        print(errmsg)
        exit(-1)

    prev = 0.0
    for age in ages_years:
        check_age(age)
        if age < prev:
            print(errmsg)
            exit(-1)
        prev = age


# -----------------------------------------------------------------------------
# Enum Types
# -----------------------------------------------------------------------------
class GenderDataType(Enum):
    SAME_FOR_BOTH_GENDERS = "SAME_FOR_BOTH_GENDERS"
    ONE_FOR_EACH_GENDER = "ONE_FOR_EACH_GENDER"
    VECTOR_MIGRATION_BY_GENETICS = "VECTOR_MIGRATION_BY_GENETICS"


class InterpolationTypes(Enum):
    LINEAR_INTERPOLATION = "LINEAR_INTERPOLATION"
    PIECEWISE_CONSTANT = "PIECEWISE_CONSTANT"


class MigrationTypes(Enum):
    LOCAL_MIGRATION = "LOCAL_MIGRATION"
    AIR_MIGRATION = "AIR_MIGRATION"
    REGIONAL_MIGRATION = "REGIONAL_MIGRATION"
    SEA_MIGRATION = "SEA_MIGRATION"


# -----------------------------------------------------------------------------
# CheckGenderDataType
# -----------------------------------------------------------------------------
def check_gender_data_type(gdt):
    if gdt not in GenderDataType:
        print(f"Invalid GenderDataType = {gdt}, valid GenderDataTypes are: "
              f"{GenderDataType.SAME_FOR_BOTH_GENDERS}, {GenderDataType.ONE_FOR_EACH_GENDER}, "
              f"{GenderDataType.VECTOR_MIGRATION_BY_GENETICS} (only for vector migration).")
        exit(-1)


# -----------------------------------------------------------------------------
# CheckInterpolationType
# -----------------------------------------------------------------------------
def check_interpolation_type(interp_type):
    if interp_type not in InterpolationTypes:
        print(f"Invalid InterpolationType = {interp_type}, valid InterpolationTypes are: "
              f"{InterpolationTypes.LINEAR_INTERPOLATION}, {InterpolationTypes.PIECEWISE_CONSTANT}.")
        exit(-1)


# -----------------------------------------------------------------------------
# CheckMigrationType
# -----------------------------------------------------------------------------
def check_migration_type(mig_type):
    if mig_type not in MigrationTypes:
        print(f"Invalid MigrationType = {mig_type}, valid MigrationTypes are: "
              f"{MigrationTypes.LOCAL_MIGRATION}, {MigrationTypes.REGIONAL_MIGRATION},"
              f"{MigrationTypes.SEA_MIGRATION}, {MigrationTypes.AIR_MIGRATION}.")
        exit(-1)


# -----------------------------------------------------------------------------
# JSON Element Names
# -----------------------------------------------------------------------------
# NOTE: The indention below indicates where the tag is used in the JSON

JSON_IdRef = "IdReference"
JSON_InterpType = "Interpolation_Type"
JSON_GenderDataType = "Gender_Data_Type"
JSON_AgesYears = "Ages_Years"
JSON_NodeData = "Node_Data"
JSON_ND_FromNodeId = "From_Node_ID"
JSON_ND_RateData = "Rate_Data"
JSON_RD_ToNodeId = "To_Node_ID"
JSON_RD_RatesBoth = "Avg_Num_Trips_Per_Day_Both"
JSON_RD_RatesMale = "Avg_Num_Trips_Per_Day_Male"
JSON_RD_RatesFemale = "Avg_Num_Trips_Per_Day_Female"


# -----------------------------------------------------------------------------
# CheckInJson
# -----------------------------------------------------------------------------
def check_in_json(fn, data, key):
    if key not in data:
        print(f"Could not find {key} in file {fn}.")
        exit(-1)


# -----------------------------------------------------------------------------
# CheckRatesSize
# -----------------------------------------------------------------------------
def check_rates_size(num_ages, rd_data, key):
    if len(rd_data[key]) != num_ages:
        print(
            f"{JSON_AgesYears} has {num_ages} values and one of the {key} has {len(rd_data[key])} values. "
            f" They must have the same number.")
        exit(-1)


# -----------------------------------------------------------------------------
# ReadJson
# -----------------------------------------------------------------------------
def read_json(json_fn):
    json_file = open(json_fn, 'r')
    json_data = json.load(json_file)
    json_file.close()

    check_in_json(json_fn, json_data, JSON_IdRef)
    check_in_json(json_fn, json_data, JSON_InterpType)
    check_in_json(json_fn, json_data, JSON_GenderDataType)
    check_in_json(json_fn, json_data, JSON_AgesYears)
    check_in_json(json_fn, json_data, JSON_NodeData)

    check_interpolation_type(json_data[JSON_InterpType])
    check_gender_data_type(json_data[JSON_GenderDataType])
    check_ages_array(json_data[JSON_AgesYears])

    if len(json_data[JSON_NodeData]) == 0:
        print(f"{JSON_NodeData} has no elements so there would be no migration data.")
        exit(-1)

    num_ages = len(json_data[JSON_AgesYears])

    for nd_data in json_data[JSON_NodeData]:
        check_in_json(json_fn, nd_data, JSON_ND_FromNodeId)
        check_in_json(json_fn, nd_data, JSON_ND_RateData)

        if len(nd_data[JSON_ND_RateData]) == 0:
            print(f"{JSON_ND_RateData} has no elements so there would be no migration data.")
            exit(-1)

        for rd_data in nd_data[JSON_ND_RateData]:
            check_in_json(json_fn, rd_data, JSON_RD_ToNodeId)

            if json_data[JSON_GenderDataType] == GenderDataType.ONE_FOR_EACH_GENDER.value:
                check_in_json(json_fn, rd_data, JSON_RD_RatesMale)
                check_in_json(json_fn, rd_data, JSON_RD_RatesFemale)

                check_rates_size(num_ages, rd_data, JSON_RD_RatesMale)
                check_rates_size(num_ages, rd_data, JSON_RD_RatesFemale)
            else:
                check_in_json(json_fn, rd_data, JSON_RD_RatesBoth)

                check_rates_size(num_ages, rd_data, JSON_RD_RatesBoth)

    return json_data


# -----------------------------------------------------------------------------
# SummaryData
# -----------------------------------------------------------------------------
class SummaryData:
    def __init__(self, node_count, offset_str, max_destinations_per_node):
        self.num_nodes = node_count
        self.offset_str = offset_str
        self.max_destinations_per_node = max_destinations_per_node


# -----------------------------------------------------------------------------
# GetSummaryData
# -----------------------------------------------------------------------------
def get_summary_data(json_data):
    from_node_id_list = []

    # -------------------------------------------------------------------------
    # Find the list node that individuals can migrate from
    # Also find the maximum number of nodes that one can go to from a give node.
    # This max is used in determine the layout of the binary data.
    # -------------------------------------------------------------------------
    max_destinations = 0
    for node_data in json_data[JSON_NodeData]:
        from_node_id_list.append(int(node_data[JSON_ND_FromNodeId]))
        destinations = len(node_data[JSON_ND_RateData])
        if destinations > max_destinations:
            max_destinations = destinations

    print(f"max_destinations = {max_destinations}")

    # -------------------------------------------------------------------
    # Create NodeOffsets string
    # This contains the location of each From Node's data in the bin file
    # -------------------------------------------------------------------
    offset_str = ""
    nodecount = 0

    for from_node_id in from_node_id_list:
        offset_str += '%0.8X' % from_node_id
        offset_str += '%0.8X' % (nodecount * max_destinations * 12)  # 12 -> sizeof(uint32_t) + sizeof(double)
        nodecount += 1

    return SummaryData(nodecount, offset_str, max_destinations)


# -----------------------------------------------------------------------------
# WriteBinFile
# -----------------------------------------------------------------------------
def write_bin_file(bin_fn, json_data, summary):
    bin_file = open(bin_fn, 'wb')

    if json_data[JSON_GenderDataType] == GenderDataType.ONE_FOR_EACH_GENDER.value:
        write_bin_file_gender(bin_file, json_data, summary, JSON_RD_RatesMale)
        write_bin_file_gender(bin_file, json_data, summary, JSON_RD_RatesFemale)
    else:
        write_bin_file_gender(bin_file, json_data, summary, JSON_RD_RatesBoth)

    bin_file.close()


# -----------------------------------------------------------------------------
# WriteBinFileGender
# -----------------------------------------------------------------------------
def write_bin_file_gender(bin_file, json_data, summary, rates_key):
    for age_index in range(len(json_data[JSON_AgesYears])):
        for node_data in json_data[JSON_NodeData]:
            array_id = []
            array_rt = []

            # Initialize with zeros
            for i in range(summary.max_destinations_per_node):
                array_id.append(0)
                array_rt.append(0)

            # Populate arrays with data
            index = 0
            for rate_data in node_data[JSON_ND_RateData]:
                array_id[index] = int(rate_data[JSON_RD_ToNodeId])
                array_rt[index] = rate_data[rates_key][age_index]
                index += 1

            # Format data into binary
            bin_data_id = struct.pack('I' * len(array_id), *array_id)
            bin_data_rt = struct.pack('d' * len(array_rt), *array_rt)

            bin_file.write(bin_data_id)
            bin_file.write(bin_data_rt)


# -----------------------------------------------------------------------------
# WriteMetadataFile
# -----------------------------------------------------------------------------
def write_metadata_file(metadata_fn, mig_type, json_data, rate_data):
    output_json = collections.OrderedDict([])

    output_json["Metadata"] = {}
    output_json["Metadata"]["IdReference"] = json_data[JSON_IdRef]
    output_json["Metadata"]["DateCreated"] = datetime.datetime.now().ctime()
    output_json["Metadata"]["Tool"] = os.path.basename(sys.argv[0])
    output_json["Metadata"]["DatavalueCount"] = rate_data.max_destinations_per_node
    output_json["Metadata"]["MigrationType"] = mig_type
    output_json["Metadata"]["GenderDataType"] = json_data[JSON_GenderDataType]
    output_json["Metadata"]["InterpolationType"] = json_data[JSON_InterpType]
    output_json["Metadata"]["AgesYears"] = json_data[JSON_AgesYears]
    output_json["Metadata"]["NodeCount"] = rate_data.num_nodes
    output_json["NodeOffsets"] = rate_data.offset_str

    with open(metadata_fn, 'w') as file:
        json.dump(output_json, file, indent=4)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("\nUsage: %s [input-json] [output-bin] [migration-type]" % os.path.basename(sys.argv[0]))
        exit(0)

    json_fn = sys.argv[1]
    bin_fn = sys.argv[2]
    mig_type = sys.argv[3]

    metadata_fn = bin_fn + ".json"

    check_migration_type(mig_type)

    json_data = read_json(json_fn)

    summary = get_summary_data(json_data)

    write_bin_file(bin_fn, json_data, summary)
    write_metadata_file(metadata_fn, mig_type, json_data, summary)

    print(f"Finished converting {json_fn} to {bin_fn} and {metadata_fn}")
