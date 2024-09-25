====================================
Troubleshooting |EMOD_s| simulations
====================================

If you encounter any of the following problems when attempting to run |EMOD_s| simulations, see the
information below to resolve the issue.

If you need assistance, you can contact support for help with solving issues. You can contact
|IDM_l| support at idmsupport@gatesfoundation.org. When submitting the issue, please include any error
information. 

See :doc:`emod:dev-debugging-overview` for troubleshooting issues when attempting to build |exe_s| or |linux_binary|.

.. contents:: Contents
   :local:

Exceptions
==========

Whenever |EMOD_s| encounters an error condition while running a simulation, it should throw an
exception. These exceptions are designed to help you diagnose any problems so that you can quickly
resolve the issue. You can find the exceptions code in the utils directory of the |EMOD_s| source
code within the files Exceptions.h and Exceptions.cpp.

Each exception will return, at a minimum, the following information:

* Exception type caught
* The filename where the exception occurred
* The line number in the file where the exception was thrown (which may not be exactly where the
  error actually occurred in the code)
* The function name where the exception was thrown

Specific exceptions may also return additional information in a message format. This message
(msg) may contain variable names or the values of those variables, the name of a file that
wasn't found, and other informational text regarding the nature of the problem. For example,
a file not found exception (FileNotFoundException) might look similar to the following::

    00:00:00 [0] [E] [Eradication] FileNotFoundException caught: msg = Could not find
    file ./Namawala_single_node_demographics.compiled.json, filename = NodeDemographics.cpp,
    lineNumber = 227

BadEnumInSwitchStatementException
---------------------------------

This exception is thrown when an enumeration value is not handled in the switch statement. In other
words, this exception signals that there is a problem with an enumeration value, typically stemming
from one of the configuration files, though this is not always the case.

It is possible the enumeration value is not a valid value (out of range of the numeric range of the
enumeration), or perhaps the string value is currently not implemented in the code (and should not
be used in configuration settings yet).

BadMapKeyException
------------------

This exception is thrown when there is a standard template library (STL) mapping error. Usually,
this occurs where spatial output channel names are specified in the configuration file
if an unrecognized channel name is used.

If you have not modified the |EMOD_s| source code or used an unrecognized channel name, this error
could signal an internal problem with the code. Contact idm@gatesfoundation.org.

CalculatedValueOutOfRangeException
----------------------------------

|EMOD_s| performs a large number of mathematical operations on parameter values. Therefore, it is
possible that, despite original parameter values being with range, the values resulting from these
multiple calculations may end up outside its valid range. For example, a probability value (range: 0
to 1.0) that after multiple calculations during a simulation now exceeds 1.0.

This exception is thrown when such a situation is detected. This exception only applies to numeric
or Boolean values, not enumeration values.

ConfigurationRangeException
---------------------------

This exception is thrown if a parameter value read from a configuration file is detected to be
outside its valid range. This exception is similar to the more general case OutOfRangeException.
However, this exception is only thrown if the out of range exception comes from a numeric or Boolean
value, not enumeration value, read from a configuration file.

DllLoadingException
-------------------

The |EMOD_s| architecture is modularized and can be built as a core |exe_s| along with a series of
custom reporter |modules|, as opposed to a single monolithic |exe_s|. This exception indicates that
|EMOD_s| couldn't load on of the |module| DLLs.

This situation could occur for several reasons:

* |EMOD_s| couldn't find the |module|
* Unresolved symbols were found (Windows)
* |EMOD_s| could not find the necessary symbol during the **GetProcAddress** call
* The custom reporter |modules| were built using a version of Visual Studio that is no longer
  supported. Rebuild the |modules| using |VS_supp|.

FactoryCreateFromJsonException
-------------------------------

|EMOD_s| implements class factories that instantiate objects at run time and use information from
JSON- based configuration information in the creation of these objects. The exception indicates
something is incorrect with the JSON information.

In particular, in some cases, the JSON information is nested into a hierarchy of information.
Therefore, as the factories are called to create the objects described by the outer layers of one of
these nested hierarchies, the factories do not have any knowledge yet of the inner layers of the
hierarchies. This inner information contains information the factory needs to complete the object
instantiation, but this information might not be correct. If that happens, then the factory will
throw this exception.

Campaign files often have this kind of nested hierarchical structure, so it's important to t verify
that the hierarchy is set up correctly. For example, if the class name were mistyped and |EMOD_s|
had no implementation of that class, this exception will be thrown.

FileIOException
---------------

This exception is generated if there is an unrecoverable problem loading data from a file. The data
might be corrupted or there may be a mismatch. For example, if the file format or configuration
information indicates that there should be ten values of some array and there are only nine included
in the file, then this exception would be thrown.

This exception is not the same as the exception thrown for a file that is not found. In this case,
the file is found and loaded, but there is a problem with the data in the file.

FileNotFoundException
---------------------

This exception is thrown if a file cannot be found. Possible causes might include a incorrectly
typed filename in the configuration file, a wrong path to the file, or even the path not being set
in the system environment leading to the system not finding a relative path to the file. One of the
most likely causes is that quotes are missing around the file name.

GeneralConfigurationException
-----------------------------

This exception is only thrown if a more specific exception cannot be used for the configuration
problem detected. This exception is likely thrown when there is very little information available
about the root problem.

For example, this exception might be thrown if a parameter name is invalid, such as using an older,
deprecated version of a parameter name.


IllegalOperationException
-------------------------

This exception is thrown if an illegal operation was detected. In most cases, a more specific
exception will be thrown rather than this more general one. This exception is likely thrown when
there is very little information available about the root problem. For example, when a utility
function error is detected, there is very sparse information available as to what may have led to
the error. As a result, calling a more specific exception with more context is not an option.

IncoherentConfigurationException
--------------------------------

This exception is thrown if mutually contradictory or incompatible configuration settings have been
detected. For example, if mutually exclusive parameters are set, the minimum parameter value is
greater than the maximum value, or two distribution axes are specified in a demographics file but
there is a mismatch with the number of axes scale factors included. The exception can also occur if
there isn't a corresponding mapping between an reference ID in the metadata of a demographics file
and its corresponding data file.


InitializationException
-----------------------

This exception is thrown if a problem with initialization was detected. In most cases, a more
specific exception will be thrown rather than this more general one. This exception is likely thrown
when there is very little information available about the root problem.

For example, if the very first part of a JSON file has corrupted or badly formatted data, this
exception may be thrown instead of the more expected file input/output exception, FileIOException.

InvalidInputDataException
-------------------------

This exception is thrown when a problem with an input file is detected. For example, if the
wrong data type was detected, such as a float being detected when a string is expected you would see
this exception thrown, or even, if a parameter has an invalid value even if the value is of the
correct type. As the input file most likely to have significant modifications, verify that the
demographics file is set up correctly.

MissingParameterFromConfigurationException
------------------------------------------

This exception occurs when required parameters are missing. Verify that you are not using deprecated
parameters and that all required parameters are specified (or set **Use_Defaults** to 1).

MPIException
------------

This exception is thrown if there is an MPI error. As such, these types of issues are related to
interfacing with MPI (and/or networking issues) and do not necessary imply something wrong with the
EMOD code or JSON files.

NotYetImplementedException
--------------------------

This exception is thrown if an attempt is made to execute code that is not yet implemented.
For example, there are areas of |EMOD_s| where placeholder enumeration values are defined but not
yet implemented.  If you specify a value like this, it is considered within a valid range, but this
exception will be thrown in response. Verify that any enumeration values use one of the available
values as described in the documentation and do not contain any typos.

NullPointerException
--------------------

This exception is thrown when a NULL pointer is detected in the code, or rather when a NULL pointer
- that should NOT be NULL - is used. When thrown at the application level, a NULL pointer exception
is usually caused by some sort of initialization error, for example, a file not being found.

As a result, in most cases, a more specific exception will be thrown before the code execution
reaches a point where this exception would occur. Therefore, this exception is uncommon and likely
thrown only when there is very little information available about the root problem.

OutOfRangeException
-------------------

This exception is thrown when a numeric or Boolean value is out of range. For example, if you index
an array outside of its valid range, this exception will be thrown. There are other situations where
more specific exceptions are thrown instead of this more general one. For example, when the numeric
or Boolean values are from a configuration file, but are detected to be out of range, the
ConfigurationRangeException is thrown. Likewise, if the value goes out of range as the result of a
calculation, the CalculatedValueOutOfRangeException is thrown instead.

QueryInterfaceException
-----------------------

The |EMOD_s| architecture is modularized and many components now implement **QueryInterface**. This
exception is thrown when a required interface is queried on an object and the object that returns
that the interface is not supported.

If you have not modified the |EMOD_s| source code and receive this error, it could signal an
internal problem with the code. Contact idm@gatesfoundation.org.

SerializationException
----------------------

This exception is thrown when there is a serialization (or de-serialization) issue. For example, if
data is being passed over the network (MPI) and the connection drops, then the serialization fails
and this exception is thrown.

|Centos| environment
====================

The following problems are specific to running simulations using the |linux_binary| on |Centos_supp|.

Regression test graphs differ when run on |Centos|
--------------------------------------------------

After you run regression simulations on |Centos| using runemod.sh in the Scripts directory, it plots
graphs from the simulation output data with a red line for the reference output and a blue line for
the new output. The reference output was created by running the simulation on Windows, which in some
cases may be slightly different than the output from |Centos|.

For simulations that plot a baseline, you can override the Windows reference output by modifying
runemod.sh to use output/InsetChart.linux.json as the output location. In that case, the red
reference plots should always be completely covered by the blue plots.

|linux_binary| cannot locate the input files
--------------------------------------------

If you chose not to have the PrepareLinuxEnvironment.sh script download the |EMOD_s| source code and
input files, you need to set up the environment variable, path and symlink that are needed
to run simulations on |Centos|. See :doc:`install-linux`.
