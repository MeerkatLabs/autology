Jinja2 Publishing Plugin
========================

The default publishing functionality is provided by Jinja2.  For details on how to configure templates see `Template
Documentation<../templates/configuring.md>`_.

Configuration Details
---------------------

All of the configuration details for jinja are placed in the ``publishing`` section of ``config.yaml``.

.. code-block:: yaml

  # JINJA2 Configuration details
  publishing:
    # Location where all of the output files will be placed after rendering content
    output: output

    # Location where the jinja templates are located on the file system.
    templates: templates

    # URL prefix that will be used inside templates.  This is useful in case the output of the
    # application is not located in the root of the webserver.
    url_root: '/'


Common Context Values
---------------------

All publishing contexts are provided details about the site object that is also defined in the ``config.yaml`` file.  It
is provided under a site key in the context list.  This key is useful for providing site wide configuration values such
as CSS and Javascript definitions that should be included on each page that is rendered.
