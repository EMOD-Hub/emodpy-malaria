from emodpy_malaria.serialization import serialization_support


# This example assumes that burnin_create_parasite_genetics/example has been ran
# We will be looking at the population of the generated file.
serialization_support.write_out_humans_data("serialization_files/output/state-00050.dtk",
                                            output_filename="humans_data.json")