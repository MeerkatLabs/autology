Index Report
============

This plugin is responsible for providing the main page of the output.  It consists of the collation
of all of the reports that were generated.  It fetches these by listening to the
``autology.topics.Reporting.REGISTER_REPORT`` topic.

Configuration Details
---------------------

This plugin is not configurable.

Inputs
------

This plugin only receives inputs from the ``REGISTER_REPORT`` topic.

Generated Reports
-----------------

Index
~~~~~

Contains all reports that were reported during execution.

Template Path Definition
++++++++++++++++++++++++

- index
  - index

Publishing Context Values
+++++++++++++++++++++++++

The following values will be used when creating the index report.

- ``stats``

  Dictionary containing the following values

  - ``generated_date``

      python datetime object for when the generate command finished processing all of the files.

  - ``execution_time``

      float containing the total number of seconds between the Processing.BEGIN and Processing.END topics were
      published.

  - ``start_time``

      python datetime object for when the Processing.BEGIN topic was published.

  - ``end_time``

      python datetime object for when the Processing.END topic was published.

  - ``processed_files``

      Number of total files that were processed during the generate command

  - ``num_days``

      The number of days that were processed as part of the log files

- ``reports``

  List of ``autology.reports.models.Report`` objects that were published to this report definition

  Reports contain the following fields:

  - ``name``

     Title of the report.

  - ``description``

     Brief description of the report

  - ``url``

     URL location of where the reports output will be stored
