"""
Timeline report that will process all of the files into a timeline in order to be published to the log.
"""

from collections import namedtuple

from autology import topics
from autology.reports.simple import SimpleReportPlugin

# The content that is stored for each individual day
_day_content = []

# Dates that have been collected
_dates = []

_report_plugin = None

DayReport = namedtuple('DayReport', 'date url num_entries')


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
    global _report_plugin
    _report_plugin = TimelineReport()
    _report_plugin.initialize()


class TimelineReport(SimpleReportPlugin):

    def __init__(self):
        """Overridden to set the day and index template paths."""
        super().__init__('timeline', 'Timeline', 'List of all report files')
        self.day_template_path = ['timeline', 'day']
        self.index_template_path = ['timeline', 'index']

    def test_activities(self, activities_list):
        """Overridden to process all of the log files that are passed in."""
        return True
