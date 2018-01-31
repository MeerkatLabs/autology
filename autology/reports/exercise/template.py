"""Template for the project log files."""
from autology.reports.models import Template
from autology.reports.timeline.template import template_start as timeline_start, template_end as timeline_end


def register_template():
    return Template('gpx_base', gpx_template_start, gpx_template_end,
                    'Inherits from timeline base but provides the means of linking in gpx files for displaying maps, '
                    'and activities.')


def gpx_template_start(**kwargs):
    """Start a new template."""
    post = timeline_start(**kwargs)
    post.metadata['gpx_file'] = '{}'.format(kwargs.pop('gpx_file', None))
    post.metadata['activities'].append('exercise')

    return post


def gpx_template_end(post, **kwargs):
    """Post processing on the template after it has been saved by the user."""
    post = timeline_end(post, **kwargs)

    return post
