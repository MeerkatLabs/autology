Log File Templates
==================

Log file templates provide the definitions that are used by the ```make_note`` command.  Currently they are implemented to
be used only as front matter definitions of the markdown files.

Template Methods
----------------

The templates are implemented as a ``name`` and two methods, ```start`` and ```end``.  A named tuple has been defined in
```autology.reports.models.Template``.  The two methods must be stateless as they can be called at any time.

.. code-block:: python

  import frontmatter


  def start():
      """Return a newly created frontmatter post object that can be written out to a file"""
      return frontmatter.Post('', meta='data', definition={})


  def end(post):
      """Modify the content of the post object provided."""
      post.metadata['some_key'] = False

      return post


Registration
------------

Templates are registered into the system using python entry points.  Specifically the group ```autology_templates``.  The
method registered here must return a ```Template`` object or a list of templates.

.. code-block:: python

  from autology.reports.models import Template

  def register_template():
    return Template(name='dummy_template', start, end)


See Also
--------

- `Python Entry Points<https://stackoverflow.com/questions/774824/explain-python-entry-points/9615473#9615473>`_
- `Python FrontMatter Library<https://pypi.python.org/pypi/python-frontmatter/0.4.2>`_
