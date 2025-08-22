# Run the Simple Example in Codespaces

This tutorial will guide you through the steps to run a simple example of
EMOD-Malaria within GitHub Codespaces.  Everything will be on the web so
you don't need to install anything at this time.

## Prerequisites

The followign instructions assume you have Codespaces started on the
emopdy-malaria repository.  To learn how to do this, please the
[Starting Codespaces Tutorial](tutorial_starting_codespaces.md)

## Run an EMOD

1. Execute the following command in the “terminal” window

    ```
    cd examples-container
    ```

    ![](media/tutorial_6_cd_examples_container.png)

2. See what examples there are by executing the following command:
    ```
    ls
    ```

    ![](media/tutorial_7_ls.png)

3. Enter the “simple_example” directory by executing the following command:

    ```
    cd simple_example
    ```

    ![](media/tutorial_8_cd_simple_example.png)

4. See what files are in this directory by executing the following command:

    ```
    ls
    ```

    ![](media/tutorial_9_ls.png)

5. Run the example with the following command:

    ```
    python example.py
    ```

    ![](media/tutorial_10_python_example_start.png)

    This step “Pulling image docker-production-public…”  may take a few minutes.

    ![](media/tutorial_11_pull_image.png)

    When the simulation is done, you should see the following:

    ![](media/tutorial_12_python_example_done.png)

## View the results

Now that we have run EMOD, lets look at some data to see what happend in the simulations.

1. In the file browser on the left, click on the ">" next to the _examples-container_ folder.

    ![](media/tutorial_13_open_examples_container.png)

2. Next, click on the ">" next to the _simple_example_ folder.

    ![](media/tutorial_14_open_simple_example.png)

3. Next, click on the ">" next to the _results_ folder.

    ![](media/tutorial_15_open_results.png)

4. Select the file names **Simple_Example.png".

    ![](media/tutorial_16_select_image.png)

