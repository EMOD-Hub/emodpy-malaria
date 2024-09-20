"""
#!/usr/bin/python
"""
import json
import pandas as pd
import numpy as np

def do_something(output_path):
    # Do something arbitrary but demonstrative with InsertChart.json that extracts a single datum.
    icj = json.load( open (output_path + "/InsetChart.json" ) )["Channels"]
    #vectors = sum( icj["Adult Vectors"]["Data"] )
    vectors = np.sum( icj["Adult Vectors"]["Data"] ) # just gratuitous use of np even though not needed.
    print( f"Total number of mosquitoes was: {vectors}" )
    import os
    os.remove( output_path + "/InsetChart.json" )

def application( output_path ):
    #import pkg_resources
    #installed_packages = pkg_resources.working_set
    #installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
    #print(installed_packages_list)
    print( f"We can post-proc files in {output_path}." )

    do_something(output_path)

if __name__ == "__main__":
    application( "output" )
