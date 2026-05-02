============
Installation
============

Software prerequisites
======================

The following is required:

- Windows or Linux (Mac is loosely supported)
- Python 3.13 (but also supports 3.11–3.14)
- Docker (optional, but highly recommended — required to run EMOD locally on your computer)

Python
------

To verify you have the correct version, enter the following command:

.. code-block:: console

   python --version

You should see something similar to the following, and it should start with "3.13":

.. code-block:: doscon

   Python 3.13.2

If you do not get that, you may need to install Python 3.13. Download it from
`python.org <https://www.python.org/downloads/>`__ or contact your IT support.

Docker
------

How you plan to run EMOD determines whether you need Docker. If you are running
simulations on a **shared computing cluster** provided by your institution or
organization, you do not need Docker and can skip this section. If you are running
simulations on **your own computer**, you need Docker.

Installation may require administrative privileges. If you don't have them, you may
need IT support. Follow the instructions on the Docker website for your operating system:

- `Windows <https://docs.docker.com/desktop/setup/install/windows-install/>`__
- `Linux <https://docs.docker.com/desktop/setup/install/linux/>`__
- `Mac <https://docs.docker.com/desktop/setup/install/mac-install/>`__

.. warning::

   Installing Docker can require downloading close to one gigabyte of data. The first
   time you run EMOD locally it will download another half gigabyte.

Windows-specific setup
~~~~~~~~~~~~~~~~~~~~~~

Enable Developer Mode — required for Docker to work correctly:

   **Settings** → **Update & Security** → **For Developers** → select **Developer Mode**

Enable long file path support (only needed if your file paths exceed 255 characters).
This step may also require IT support:

   **Local Computer Policy** → **Computer Configuration** → **Administrative Templates**
   → **System** → **Filesystem** → enable **Win32 long paths**

Set up a virtual environment
============================

A :doc:`virtual environment <virtual_environments>` keeps emodpy-malaria's software
separate from other Python projects on your computer, preventing version conflicts.
You will want to do this for all of your new projects.

1. Create the virtual environment:

   .. code-block:: console

      python -m venv env

2. Activate the virtual environment:

   **Windows**:

   .. code-block:: doscon

      env\Scripts\activate.bat

   **Linux**:

   .. code-block:: bash

      source env/bin/activate

3. Ensure Python's package installer is up to date:

   .. code-block:: console

      python -m pip install pip --upgrade

.. toctree::
   :hidden:

   virtual_environments

Install emodpy-malaria
======================

Use the following command to install emodpy-malaria:

.. code-block:: console

   python -m pip install emodpy-malaria
