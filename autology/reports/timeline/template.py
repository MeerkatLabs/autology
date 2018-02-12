"""Simple template definition for a log file that contains start time, end time, location, and empty content."""
from datetime import datetime
import tzlocal

import frontmatter

from autology.utilities.log_file import MetaKeys, Entry
from autology.utilities.processors import markdown
from autology.reports.models import Template
import pkg_resources

PACKAGE_NAME = 'autology'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def template_start(start_time=None, end_time=None, location='home', activities=None, mime_type=markdown.MIME_TYPE,
                   **kwargs):
    """
    Start a new file template based on the content of the template definition.
    :param start_time: either a string or a date time object that contains the start time for an entry.
    :param end_time: either a string, date, or None that contains the end time for an entry.
    :param location: the location where the event takes place.
    :param activities: the list of activities that are defined for this entry.
    :param mime_type: mime type that will be used for the created entry
    """

    if start_time is None:
        start_time = tzlocal.get_localzone().localize(datetime.now())
    else:
        if type(start_time) is not datetime:
            start_time = tzlocal.get_localzone().localize(datetime.strptime(start_time, DATE_FORMAT))

    if end_time is not None and type(end_time) is not datetime:
        end_time = tzlocal.get_localzone().localize(datetime.strptime(end_time, DATE_FORMAT))

    if activities is None:
        activities = []

    _post = frontmatter.Post('', **{
        MetaKeys.TIME: start_time,
        MetaKeys.END_TIME: end_time,
        MetaKeys.LOCATION: location,
        MetaKeys.ACTIVITIES: activities,
        MetaKeys.AGENT_DEFINITION: {
            MetaKeys.Agent.NAME: PACKAGE_NAME,
            MetaKeys.Agent.VERSION: pkg_resources.require(PACKAGE_NAME)[0].version,
            MetaKeys.Agent.FILE_VERSION: '{}'.format(MetaKeys.CURRENT_FILE_VERSION)
        }
    })

    return Entry(start_time, mime_type, _post.metadata, _post.content, None, None)


def template_end(post, **kwargs):
    """
    Finish the manipulation of the metadata in the front matter before saving the contents to the storage engine.
    :param post: the post file that will be modified.
    """
    if not post.metadata[MetaKeys.END_TIME]:
        post.metadata[MetaKeys.END_TIME] = tzlocal.get_localzone().localize(datetime.now())
    else:
        # Need to set the timezone value for the post to be the current time zone.
        post.metadata[MetaKeys.END_TIME] = post.metadata[MetaKeys.END_TIME].astimezone(tzlocal.get_localzone())

    # Time value is currently stored in a different timezone, so make sure that it's set to the local timezone value
    # just as the end time is
    if MetaKeys.TIME in post.metadata:
        post.metadata[MetaKeys.TIME] = post.metadata[MetaKeys.TIME].astimezone(tzlocal.get_localzone())

    return post


timeline_base = Template(template_start, template_end,
                         'This template provides the base for all templates.  It contains all required fields.',
                         {'start_time': 'Date Time Value containing the start time of the entry, must be in the format'
                                        'of: {}'.format(DATE_FORMAT),
                          'end_time': 'Date Time Value containing the end time of the entry, must be in the format '
                                      'of :{}'.format(DATE_FORMAT),
                          'location': 'Location of tne entry, either a GPS uri, or keyword'
                          })
