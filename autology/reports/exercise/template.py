"""Template for the project log files."""
import pathlib

import gpxpy
import pytz
import tzlocal
import logging

from autology.reports.models import Template
from autology.utilities import log_file
from autology.reports.timeline.template import template_start as timeline_start, template_end as timeline_end, \
    timeline_base

logger = logging.getLogger(__name__)


def gpx_template_start(gpx_file=None, **kwargs):
    """Start a new template."""

    # Make sure that exercise is defined in the activities field
    activities = kwargs.setdefault('activities', [])
    if 'exercise' not in activities:
        activities.append('exercise')

    # If the gpx file field is defined, load up the gpx file and populate the kwargs with the files start and end times
    if gpx_file:
        gpx_file = pathlib.Path(gpx_file)
        gpx_values = _process_gpx_file(gpx_file)
        kwargs.update(gpx_values)

    post = timeline_start(**kwargs)

    if gpx_file:
        post.metadata['gpx_file'] = str(gpx_file)
    else:
        post.metadata['gpx_file'] = None

    return post


def gpx_template_end(post, **kwargs):
    """Post processing on the template after it has been saved by the user."""
    post = timeline_end(post, **kwargs)

    if post.metadata['gpx_file']:
        gpx_file_path = pathlib.Path(post.metadata['gpx_file'])

        if gpx_file_path.exists():
            log_directory, relative_path = log_file.insert_file(post.date, gpx_file_path, gpx_file_path.read_text())
            post.metadata['gpx_file'] = str(relative_path)

    return post


def _process_gpx_file(file=None):
    """Inject the provided file into the date requested."""

    if file is None:
        logger.error('Cannot handle null file')
        return

    try:
        # This should check to see if the gpx file is valid or not, and if it's valid, then the gpx file should be
        # copied into place and a new markdown file should be created as well based on the start time of the content.
        with file.open() as gpx_file:
            _gpx_data = gpxpy.parse(gpx_file)

        # Check to see if the gpx library can find a date, and use that value, otherwise must use the date value
        # provided by the arguments.
        # Arguments probably should always trump the file content.  In addition need to provide an end date time as
        # well.
        start_time, end_time = _gpx_data.get_time_bounds()

        if start_time:
            start_time = pytz.utc.localize(start_time).astimezone(tzlocal.get_localzone())

        if end_time:
            end_time = pytz.utc.localize(end_time).astimezone(tzlocal.get_localzone())

        return dict(start_time=start_time, end_time=end_time, gpx_file=str(gpx_file))
    except gpxpy.gpx.GPXXMLSyntaxException:
        logger.exception('Cannot import file: {}'.format(file))


gpx_data = Template(gpx_template_start, gpx_template_end,
                    'Inherits from timeline base but provides the means of linking in gpx files for displaying maps, '
                    'and activities.',
                    dict([
                        ('gpx_file', 'Path to GPX File')
                    ], **timeline_base.arguments))
