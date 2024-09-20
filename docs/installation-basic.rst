=============================
|EMODPY_malaria| installation
=============================

Follow the steps below to install |EMODPY_malaria|.

    .. note::

        Currently, VPN connection is required to run the example.

#.  Open a command prompt and create a virtual environment in any directory you choose. The
    command below names the environment "v-emodpy-malaria", but you may use any desired name::

        python -m venv v-emodpy-malaria

#.  Activate the virtual environment:

    .. container:: os-code-block

        .. container:: choices

            * Windows
            * Linux

        .. container:: windows

            Enter the following::

                v-emodpy-malaria\Scripts\activate

        .. container:: linux

            Enter the following::

                source v-emodpy-malaria/bin/activate

#.  Install |EMODPY_malaria| packages::

        pip install emodpy_malaria

    If you are on Python 3.6, also run::

        pip install dataclasses

    If you are on Linux, also run::

        pip install keyrings.alt

#.  Open a command prompt and clone the |EMODPY_malaria| GitHub repository to a local directory using the following command::

        git clone https://github.com/InstituteforDiseaseModeling/emodpy-malaria.git

#.  Verify installation by running the included Python example, ``example.py``, located in /examples/start_here::

        python example.py

    Upon completion you can view the results in |COMPS_s|.

#.  When you are finished, deactivate the virtual environment by entering the following at a command prompt::

        deactivate
