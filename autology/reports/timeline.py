"""
Timeline report that will process all of the files into a timeline in order to be published to the log.
"""
import datetime

import frontmatter
import pathlib

from autology.reports.models import Report
from autology import topics
from autology.publishing import publish
from autology.utilities import log_file as log_file_utils

# The current date that is being processed.
_current_date = datetime.date.today()

# The content that is stored for each individual day
_day_content = []

# Dates that have been collected
_dates = []

# Default template definitions
TIMELINE_TEMPLATE_PATH = pathlib.Path('timeline', 'timeline_report.html')
DAY_TEMPLATE_PATH = pathlib.Path('timeline', 'day.html')


def register_plugin():
    """
    Subscribe to the initialize method and add default configuration values to the settings object.
    :return:
    """
    topics.Application.INITIALIZE.subscribe(_initialize)


def _initialize():
    """
    Register for all of the required events that will be fired off by the main loop
    :return:
    """
    topics.Processing.DAY_START.subscribe(_start_day_processing)
    topics.Processing.PROCESS_FILE.subscribe(_data_processor)
    topics.Processing.DAY_END.subscribe(_end_day_processing)
    topics.Processing.END.subscribe(_end_processing)


def _start_day_processing(date=None):
    """
    Event handler that will be notified when a day's files are starting to be processed.
    :param date: the day that is being processed.
    :return:
    """
    global _day_content, _current_date
    _day_content = []
    _current_date = date
    _dates.append(date)


def _data_processor(file, date):
    """
    Checks to see if the data can be processed and stores any data required locally.
    :param file:
    :return:
    """
    if file.suffix != '.md':
        return

    entry = frontmatter.load(file)
    entry_date = log_file_utils.get_start_time(date, entry.metadata, file)

    _day_content.append((entry_date, entry))


def _end_day_processing(date=None):
    """Publish the content of the collated day together."""
    publish(DAY_TEMPLATE_PATH, "{:04d}{:02d}{:02d}.html".format(_current_date.year, _current_date.month,
                                                                _current_date.day),
            entries=sorted(_day_content, key=lambda x: x[0]))


def _end_processing():
    publish(TIMELINE_TEMPLATE_PATH, 'timeline_report.html', dates=_dates)
    topics.Reporting.REGISTER_REPORT.publish(report=Report('Timeline', 'List of all report files',
                                                           'timeline_report.html'))
