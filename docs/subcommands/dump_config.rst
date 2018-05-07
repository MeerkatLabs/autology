Dump Config
===========

Dump the current configuration of the application to a yaml file.  This will contain both the default values and the
overridden values from any current ``config.yaml`` files that have been processed.

Configuration
-------------

This command is configured through command line arguments.

- ``-o <file_name>`` or ``--output <file_name>``

  Specify the output file for the configuration details

  Default: config.yaml

Example Execution
-----------------

.. code-block:: sh

  autology dump_config -o test_config.yaml
