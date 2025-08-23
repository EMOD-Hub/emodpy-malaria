# Run the Simple Example in Codespaces

This tutorial will guide you through the steps to run a simple example of
EMOD-Malaria within GitHub Codespaces.  Everything will be on the web so
you don't need to install anything at this time.

## Prerequisites

The followign instructions assume you have Codespaces started on the
emopdy-malaria repository.  To learn how to do this, please the
[Starting Codespaces Tutorial](tutorial_starting_codespaces.md)

## Run EMOD example

1. Execute the following command in the “terminal” window

    ```
    cd examples-container
    ```

    "cd" stands for _change directory_

    ![](media/tutorial_6_cd_examples_container.png)

    Notice that the line after executing the command says what folder you are in.
    In our case, the folder you are in should be:

    ```
    /workspaces/emodpy-malaria/examples-container
    ```
    
    Most of the following instructions are going to take place in this terminal window.

2. See what examples there are by executing the following command:
    ```
    ls
    ```

    "ls" stands for _list files/directories_

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

    This step “Pulling image docker-production-public…”  may take a few minutes,
    but will only happen once per codespace image.

    ![](media/tutorial_11_pull_image.png)

    When the simulation is done, you should see the following:

    ![](media/tutorial_12_python_example_done.png)

## View the results

Now that we have run EMOD, lets look at some data to see what happend in the simulations.

1. In the file browser on the left, click on the ">" next to the _examples-container_ folder
and continue navigating to the folder:

    ```
    examples-container > simple_example > results
    ```

2. Select the file name **Simple_Example.png".

    ![](media/tutorial_16_select_image.png)

## Understand the results

The [next "tutorial"](tutorial_interpret_results.md) explains what you are seeing in this image.

