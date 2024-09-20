=======
Install
=======

Follow the steps below to install |EMODPY_malaria|.

    .. note::

        Currently, an IDM VPN connection is required to run the example.

#.  Open a command prompt and create a virtual environment in any directory you choose. The
    command below names the environment "v-emodpy-malaria", but you may use any desired name::

        python -m venv v-emodpy-malaria

#.  Activate the virtual environment:

    * For Windows, enter the following::

        v-emodpy-malaria\Scripts\activate

    * For Linux, enter the following:: 

        source v-emodpy-malaria/bin/activate


#.  Install |EMODPY_malaria| packages::

        pip install emodpy_malaria

    If you are on Linux, also run::

        pip install keyrings.alt

#.  Open a command prompt and clone the |EMODPY_malaria| GitHub repository to a local directory using the following command::

        git clone https://github.com/InstituteforDiseaseModeling/emodpy-malaria.git

#.  Verify installation by running the included Python example, ``example.py``, located in /examples/start_here::

        python example.py

    Upon completion you can view the results in |COMPS_s|.

#.  When you are finished, deactivate the virtual environment by entering the following at a command prompt::

        deactivate
