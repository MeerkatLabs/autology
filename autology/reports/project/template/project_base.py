"""Template for the project log files."""
from autology.reports.models import Template
from autology.reports.timeline.template import template_start as timeline_start, template_end as timeline_end, \
    timeline_base


def template_start(project_id=None, **kwargs):
    """Start a new template."""

    # Make sure that project is defined in the list of activities
    activities = kwargs.setdefault('activities', [])
    if 'project' not in activities:
        activities.append('project')

    post = timeline_start(**kwargs)
    post.metadata['mkl-project'] = project_id

    return post


def template_end(post, **kwargs):
    """Post processing on the template after it has been saved by the user."""
    post = timeline_end(post, **kwargs)

    return post


project_base = Template(template_start, template_end,
                        'Inherits from timeline_base template, but also provides additional details about a project '
                        'that was being worked on while the note was open.',
                        dict([
                            ('mkl-project', 'Project identifier that the entry will be about')
                        ], **timeline_base.arguments))
