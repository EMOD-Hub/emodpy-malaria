=====================================
Run a simulation using mpiexec
=====================================

The application mpiexec is used to run multi-node simulations in parallel. |exe_s| is "single
threaded", so it uses only one core for processing. If you run a simulation with multiple geographic
nodes using mpiexec instead of invoking |exe_s| directly, multiple copies of |exe_s| will be
running, with one copy per core processing data for a single node at a time. Message Passing
Interface (MPI) communicates between the cores when handling the migration of individuals from one
:term:`node` to another.

Although mpiexec can be used to run a simulation in parallel on your local computer, it is  more
often used to run complex simulations in parallel on an HPC cluster or several linked computers.
Mpiexec is part of the |HPC_SDK_supp| installed as a prerequisite for building |exe_s| from the
|EMOD_s| source code. 

See :doc:`emod:dev-install-overview` for more information.

.. note::

    If you get an error that the mpiexec command cannot be found, you must add the path to mpiexec to
    the PATH environment variable. For example, open Control Panel and add the path C:\\Program
    Files\\Microsoft HPC Pack 2012\\Bin to PATH.


Usage
=====

#.  Take note of the number of cores on your computer or cluster.

    If running locally, we recommend running mpiexec with one fewer cores than are available, so one
    core is reserved for the operating system. The simulation can be run on all available cores and
    will complete faster, but the desktop will not be responsive.

#.  Open a Command Prompt window and navigate to the directory that contains the configuration and
    campaign files for the simulation.

#.  Invoke |exe_s| using mpiexec as follows, replacing the number of cores, paths, and command options
    as necessary for your environment. See :doc:`software-simulation-cli` for more information about
    the command options available for use with |exe_s|.

    .. code-block:: none

        mpiexec -n 3 ..\Eradication.exe --config config.json --input-path ..\InputDirectory\Garki --output-path OutputGarki


Mpiexec will start multiple copies of |exe_s| as specified by ``-n``. Those instances will
communicate with each other via MPI. If all cores are on a single computational node or host, they
will use internal networking to carry the MPI packets.

You can also link together several computers with MPI using the mpiexec ``-host`` option. For
example, if you were using six cores on two computers, you could run three copies of |exe_s|
on the first computer, and three more could be run on the second computer. Again, this assumes that
each computer has at least three cores.

For more information about mpiexec, see MSDN_.

.. _MSDN: https://msdn.microsoft.com/en-us/library/cc947675
