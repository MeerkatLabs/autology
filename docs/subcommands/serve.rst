Serve
=====

Creates a simple HTTPServer that will display the contents of the output directory after the content has been generated
by the generate command.  This command should only be used for developing new templates, and should not be used in
production.

Configuration
-------------

This command is configured through command line arguments.

- ``-p <int>`` or ``--port <int>``

  Specify the port that the web server will be listening on

  Default: 8080

Example Execution
-----------------

.. code-block:: sh

  autology serve -p 9000
