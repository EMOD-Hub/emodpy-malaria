================
Parameter sweeps
================

Parameter sweeps iteratively update the values of parameters to exhaustively search through the
parameter space for a simulation. |EMOD_s| does not currently support automated parameter sweeps.
However, you can write your own code, such as a Python or MATLAB script, that iterates through the
values you want for a particular parameter. This topic describes how to perform a parameter sweep.

For example, you can run simulations using a Python script that uses the parameter values specified
in a JSON parameter sweep file to iteratively update the configuration or campaign parameter values.
The |IDM_s| test team performs parameter sweeps as part of regression testing. See the following
examples to see how this is implemented.

The following JSON example illustrates sweeping through configuration parameter values.

.. code-block:: json

    {
        "sweep" :
        {
            "path": "Vector/22_Vector_Garki_MultiCore_VectorMigration",
            "param_name" : "Run_Number",
            "param_values" : [ 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144 ]
        }
    }

The following Python example illustrates how to update the configuration file with the above values.
This is excerpted from the regression_test.py script in the Regression_ directory.

.. code-block:: python

    elif "sweep" in reglistjson:
        print( "Running sweep...\n" )
        param_name = reglistjson["sweep"]["param_name"]

        for param_value in reglistjson["sweep"]["param_values"]:
            os.chdir(ru.cache_cwd)
            sim_timestamp = str(datetime.datetime.now()).replace('-', '_' ).replace( ' ', '_' ).replace( ':', '_' ).replace( '.', '_' )
            if regression_id == None:
                regression_id = sim_timestamp

            configjson = ru.flattenConfig( os.path.join( reglistjson["sweep"]["path"], "param_overrides.json" ) )
            if configjson is None:
                print("Error flattening config.  Skipping " + simcfg["path"])
                ru.final_warnings += "Error flattening config.  Skipped " + simcfg["path"] + "\n"
                continue

            # override sweep parameter
            configjson["parameters"][param_name] = param_value

            campjson_file = open( os.path.join( reglistjson["sweep"]["path"],"campaign.json" ) )
            campjson = json.loads( campjson_file.read().replace( "u'", "'" ).replace( "'", '"' ).strip( '"' ) )
            campjson_file.close()
            configjson["campaign_json"] = str(campjson)

            report_fn = os.path.join( reglistjson["sweep"]["path"],"custom_reports.json" )
            if os.path.exists( report_fn ) == True:
                reportjson_file = open( report_fn )
                reportjson = json.loads( reportjson_file.read().replace( "u'", "'" ).replace( "'", '"' ).strip( '"' ) )
                reportjson_file.close()
                configjson["custom_reports_json"] = str(reportjson)
            else:
                configjson["custom_reports_json"] = None

            thread = runner.commissionFromConfigJson( sim_timestamp, configjson, reglistjson["sweep"]["path"], None, 'sweep' )
            ru.reg_threads.append( thread )
    else:
        print "Unknown state"
        sys.exit(0)

.. _Regression: https://github.com/InstituteforDiseaseModeling/EMOD/tree/master/Regression