Sub-commands
============

Sub-commands provide a means of iterating over the data and providing some kind of functionality.  For example, the
``generator`` command will iterate over all of the files that are stored in the logs directory and translate that data
into a static HTML output containing dashboard information.

Registration
------------

Sub-commands are registered into the framework using the python entry point ``autology_commands``.  The method that is
provided is responsible for building up the ``argparse`` sub processor with the relevant flags.  One of the values
that must be added is the default called ``func``.  This is the method that will be called later with the results of
processing the arguments.

.. code-block:: python

  def register_command(subparser):
      """Register the subcommand with any additional arguments."""
      parser = subparser.add_parser('some_command', help='Command help')
      parser.set_defaults(func=_main)

      parser.add_argument('--foo', action='store_true', default=False)


  def _main(args):
      """Method that will be executed once arguments have been parsed."""
      print('args.foo: {}'.format(args.foo))

See Also
--------

- `ArgParse Documentation<https://docs.python.org/3.6/library/argparse.html>`_
- `Python Entry Points<https://stackoverflow.com/questions/774824/explain-python-entry-points/9615473#9615473>`_
