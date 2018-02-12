"""Template for the project log files."""
import pathlib

from autology.reports.models import Template
from autology.reports.timeline.template import template_start as timeline_start, template_end as timeline_end, \
    timeline_base
from autology.utilities.log_file import rebuild_entry
from autology.utilities.processors import yaml


def template_start(yaml_file=None, **kwargs):
    """Start a new template."""

    # Make sure that project is defined in the list of activities
    activities = kwargs.setdefault('activities', [])
    if 'project' not in activities:
        activities.append('project')

    post = timeline_start(mime_type=yaml.MIME_TYPE, **kwargs)

    # Read in the contents of the yaml file and set them as the content of the post
    if yaml_file:
        yaml_file = pathlib.Path(yaml_file)
        if yaml_file.exists():
            post = rebuild_entry(post, content=yaml_file.read_text())
        else:
            raise FileNotFoundError('Could not find file: {}'.format(yaml_file))

    return post


def template_end(post, **kwargs):
    """Post processing on the template after it has been saved by the user."""
    post = timeline_end(post, **kwargs)

    return post


project_yaml = Template(template_start, template_end,
                        'Inherits from timeline_base template, but provides a means of specifying a file that should '
                        'be used as the yaml content to follow.',
                        dict([
                            ('yaml_file', 'YAML file that contains all of the content that should be stored in the '
                                          'documents provided.')
                        ], **timeline_base.arguments))
