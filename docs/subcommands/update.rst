Update
======

Updates the autology directory by updating the log files or the out generation templates that are defined.

Configuration
-------------

This command is configured through command line arguments.

- ``-f`` or ``--files``

  Indicate that the command will be responsible for modifying the log files.  It will walk through them and provide
  the contents to each of the updaters.  These updaters will look at the metadata information in the front matter to
  determine if the contents of the front matter need to be updated to match a new scheme.  Running this command
  multiple times shouldn't modify the data on any attempt after the first.

- ``-t`` or ``--templates``

  Indicate that the command is responsible for updating to the latest version of the template defined by the
  application.  Running this command without specifying a template to install will only install and update the base
  template.  If the base template version has already been installed, this command will do nothing.

- ``-T`` or ``--template-definition``

  Define the template that should be installed into the log directory.  This can be a URL that points to a zip file,
  a local zip file, or a local directory containing a template definition.

Example Execution
-----------------

To update the log files that are defined:

.. code-block:: sh

  autology update -f


To update the log files and the base template definition:

.. code-block:: sh

  autology update -f -t
