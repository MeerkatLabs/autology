"""Template for the project log files."""
from autology.reports.models import Template
from autology.reports.timeline.template import template_start as timeline_start, template_end as timeline_end


def register_template():
    description = 'Inherits from timeline_base template, but also provides additional details about a project that ' \
                  'was being worked on while the note was open.'
    return Template('project_base', template_start, template_end, description)


def template_start(**kwargs):
    """Start a new template."""
    post = timeline_start(**kwargs)
    post.metadata['mkl-project'] = None
    post.meatdata['activities'].append('project')

    return post


def template_end(post, **kwargs):
    """Post processing on the template after it has been saved by the user."""
    post = timeline_end(post, **kwargs)

    return post
