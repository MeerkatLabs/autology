Generator Subcomand
===================

This command walks through the contents of the logs directory and publishes the contents of each file to an output
directory.

Configuration
-------------

The configuration of this tool is done through the configuration of the plugins.  They are documented separately.

Extending
---------

This command's functionality is extended by adding additional reports to the framework.  Each of the files that is
processed will be published to the ``autology.topics.Processing.PROCESS_FILE`` topic.  Additional topics are provided
for beginning the processing, ending the processing and then for each day when it starts and finishes.

Example Execution
-----------------

.. code-block:: sh

  autology generate


See Also
--------

- `Extending Reports<../extending/reports.md>`_
- `Autology Topics<../../autology/topics.py>`_
