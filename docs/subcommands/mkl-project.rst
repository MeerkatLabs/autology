MKL-Project
===========

Provides reports and functionality associated with the mkl-project plugin.

Configuration
-------------

This command is configured through command line arguments.

- ``-p`` or ``--project-list``

  Print out a list of all the projects that have been defined in the YAML and markdown files.  It will also print out
  the name associated with that project or a label showing that the project doesn't have a definition in the data set.

Example Execution
-----------------

To dump out the project list that has been defined:

.. code-block:: sh

  autology mkl-project -p
