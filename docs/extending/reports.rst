Reports
=======

Reports are functionality components that are used by the ```generate`` command.  They gather data by subscribing to a
collection of events and then use that to publish output using the publisher.  When finished they can register a report
entry point with the ```index`` report that will add links to the main page of the output log.

Registration
------------

Reports are registered with the application through entry points.  Reports use the ```autology_reports`` entry point to
register an initialization method.  This method should only be used to subscribe to the ```autology.topics.Application``
events that are published and to define the default configuration values for the report.  The configuration file isn't
loaded until all of the plugins have had their content registered.

The ```topics.Application.INITIALIZE`` topic is published before the sub-command starts executing.

.. code-block:: python

  from autology.configuration import add_default_configuration, get_configuration
  from autology import topics


  def report_initialization():
    topics.Application.INITIALIZE.subscribe(_process_configuration)

    add_default_configuration('my_key', {
      "some_key": "some_value",
      "other_key": False
    })

  def _process_configuration():
    configuration = get_configuration()

    # Do something with the configuration details
    print('my_key.some_key value: {}'.format(configuration.my_key.some_key))


Generation Workflow
-------------------

The generator will publish several events that can be subscribed to.  These are documented in the
``autology.topics.Processing`` object to include the parameters that are provided.  Examples of reports are defined in
the `project<../../autology/reports/project/project.py>`_ and `timeline<../../autology/reports/timeline/timeline.py>`_
report modules.

See Also
--------

- `Python Entry Points<https://stackoverflow.com/questions/774824/explain-python-entry-points/9615473#9615473>`_
- `Autology Topics<../../autology/topics.py>`_
