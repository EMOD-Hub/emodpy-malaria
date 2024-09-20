import emod_api.serialization.SerializedPopulation as SerPop
import json


def write_out_humans_data(serialization_filename: str,
                          output_filename: str) -> None:
    """
    This function writes out human data into a json format file.
    Humans are separated by nodes.

    Args:
        serialization_filename: input file, should be the .dtk file created by EMOD
        output_filename: output file, will be in JSON format

    Returns:
        None
    """
    serialized_data = SerPop.SerializedPopulation(serialization_filename)
    human_data = {}
    for index, node in enumerate(serialized_data.nodes):
        human_data[f"Node {node.externalId}"] = node.individualHumans

    with open(output_filename, "w") as out_json:
        json.dump(human_data, out_json)
