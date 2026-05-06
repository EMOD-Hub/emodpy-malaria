# Setup

The tutorials are Python scripts in the `tutorials/` directory of the emodpy-malaria repository. Before running them, prepare your environment using one of the two options below.

=== "Local"

    ### Prerequisites

    - Python 3.11 or later — see [virtual environments](../virtual_environments.md) for instructions
    - [Docker Desktop](https://www.docker.com/products/docker-desktop) — required by the Container platform used in the tutorials to run EMOD locally

    ### Steps

    1. Open a terminal, navigate to the directory where you want to clone the repository, and run:

        ```
        git clone https://github.com/EMOD-Hub/emodpy-malaria.git
        cd emodpy-malaria
        ```

    2. Create and activate a virtual environment inside the `emodpy-malaria` directory — follow the
       [virtual environments](../virtual_environments.md) guide.

    3. Install emodpy-malaria in editable mode:

        ```
        pip install -e .
        ```

    4. Start Docker (Docker Desktop on Mac/Windows, or ensure the Docker Engine service is running on Linux).

    5. Navigate to the `tutorials/` directory:

        ```
        cd tutorials
        ```

    6. Verify your setup by running Tutorial 1:

        ```
        python tutorial_1_intro.py
        ```

        If it completes successfully, your environment is ready and you can proceed to the tutorials.

    The first time you run a tutorial, `emod_malaria.bootstrap.setup()` extracts the EMOD
    executable and schema to the `tutorials/download/` directory.

=== "Codespaces"

    GitHub Codespaces provides a browser-based development environment with Docker and all
    dependencies pre-configured by the `.devcontainer` setup in this repository.

    !!! warning "Codespaces can cost money"
        GitHub gives each user 120 core-hours per month for free. Beyond that, charges apply.
        See the [GitHub billing documentation](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)
        for details. Closing the browser tab does **not** stop your Codespace — make sure to
        stop or delete it when you are done to avoid unnecessary charges.

    ### Steps

    1. Open the [emodpy-malaria repository](https://github.com/EMOD-Hub/emodpy-malaria) on GitHub.

    2. Click the **Code** button, select the **Codespaces** tab, and click **+** to create a
       new codespace on `main`.

    3. Wait for the container to build and for the post-creation `setup.sh` script to finish.
       The script automatically runs `pip install -e .` to install all dependencies. To check
       if setup is complete, open a terminal and run `pip freeze` — if no packages appear,
       setup is still running.

    4. In the terminal, navigate to the `tutorials/` directory:

        ```
        cd tutorials
        ```

    5. Verify your setup by running Tutorial 1:

        ```
        python tutorial_1_intro.py
        ```

        If it completes successfully, your environment is ready and you can proceed to the tutorials.

    The first time you run a tutorial, `emod_malaria.bootstrap.setup()` extracts the EMOD
    executable and schema to the `tutorials/download/` directory.

    ### Stopping and deleting a Codespace

    To avoid charges, stop or delete your Codespace when you are done:

    1. Go to the repository page on GitHub.
    2. Click **Code** → **Codespaces** tab.
    3. Find your Codespace, click the **...** ellipsis, and select **Stop Codespace** or **Delete**.

## Platform notes

**Container (default)**
: Runs EMOD inside a Docker container on your local machine or in Codespaces. No credentials or
cluster access required. Docker must be running (Docker Desktop on Mac/Windows, or Docker Engine on Linux).

**COMPS** *(IDM-only)*
: Requires IDM network access. A `comps_sif_file.id` file is included in the `tutorials/`
directory with the AssetCollection ID of the EMOD Singularity image. Contact your COMPS
administrator if you encounter access problems.

**SLURM**
: Set `slurm_sif_path` in `manifest.py` to the full path of the EMOD `.sif` file on your
cluster, and update the `mail_user` and `partition` fields in the `Platform("SLURM_LOCAL", ...)`
block inside each tutorial script.
