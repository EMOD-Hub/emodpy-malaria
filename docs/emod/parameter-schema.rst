================
Parameter schema
================

A :term:`schema` defines all configuration and campaign parameters available in the installed
version of |EMOD_s|, for all simulation types. It includes parameter names, data types,
defaults, valid ranges, and short descriptions. Note that the schema does not include
demographics parameters. The schema is a JSON file and can be opened in any text editor.

In most cases, you will not need to work with the schema directly — |EMODPY_malaria| handles
all model configuration through its Python API and uses the schema internally.

If you do need access to the schema, the |EMOD_s| executable and its associated schema are
bundled in the ``emod_malaria`` package, which is installed automatically when you install
|EMODPY_malaria|. You can extract them using the ``emod_malaria.bootstrap`` module. Add the
following to your project and run it once:

.. code-block:: python

    if __name__ == "__main__":
        import emod_malaria.bootstrap as bootstrap
        import pathlib
        bootstrap.setup(pathlib.Path("executables"))

This will download and place the |EMOD_s| executable and schema files into an
``executables`` folder in your current directory.
