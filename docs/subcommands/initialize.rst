Initialize
==========

The initialization method is responsible for creating the directory structure that will contain all of the log files.
It loads an initial template set from github and will create a default configuration file with all of the known default
settings provided.

Configuration
-------------

This command can be customized through command line arguments.

- ``-t <file/URL>`` or ``--templates <file/url>``

  Provides an override of the templates that are used to generate output formatted files.  The file or URL must be a
  zip file the contains all of the template files as well as a ``template.yaml`` file that contains details of how the
  template is to be rendered.

  DEFAULT: zip file containing `Autology Templates<https://github.com/MeerkatLabs/autology_templates>`_

- ``-o <directory>`` or ``--output-dir <directory>``

  Provides an override for where the contents of the log should be placed.

  DEFAULT: ``.`` (Current working directory)


Example Execution
-----------------

.. code-block:: sh

  autology init -t /tmp/autology_templates-master.zip -o ~/notes/
