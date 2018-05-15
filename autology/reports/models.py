"""Models related to the definition of reports."""

from collections import namedtuple

# report definition object used when notifying the report listener that a new report has been defined.
Report = namedtuple('Report', 'name description path path_context')

# Template definition used to register the input template files for the logs.
Template = namedtuple('Template', 'start end description arguments')
