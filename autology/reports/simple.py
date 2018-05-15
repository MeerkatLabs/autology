"""
Simple plugin that will allow for an easy means of registering activity logging.  Functionality is used by the timeline
plugin.
"""
from datetime import datetime, time

from collections import namedtuple

from autology import topics
from autology.configuration import add_default_configuration, get_configuration
from autology.publishing import publish
from autology.reports.models import Report
from autology.utilities.log_file import MetaKeys
from autology.utilities.processors import markdown as md_loader

DayReport = namedtuple('DayReport', 'date entries prev next')

_defined_plugins = []


def register_plugin():
    """
    Subscribe to the initialize method and add default configuration values to the settings object.
    :return:
    """
    topics.Application.INITIALIZE.subscribe(_initialize)

    # TODO: Update to be a bit more configurable, change activities to definitions, then allow for activities to be
    # defined as part of the definition.
    add_default_configuration('simple', {
        'activities': []
    })


def _initialize():
    """
    Look in the configuration and create a new SimpleReportPlugin for all of the activities that are defined.
    :return:
    """
    for config in get_configuration().simple.activities:
        plugin = SimpleReportPlugin(config.id, config.name, config.description)
        plugin.initialize()
        _defined_plugins.append(plugin)


class SimpleReportPlugin:
    day_template_path = ['simple', 'day']
    index_template_path = ['simple', 'index']

    def __init__(self, _id, _name, _description):
        # The content that is stored for each individual day
        self._day_content = None
        self._previous_content = None

        # Dates that have been collected
        self._reports = []
        self.id = _id
        self.name = _name
        self.description = _description

    def initialize(self):
        """
        Register for all of the required events that will be fired off by the main loop
        :return:
        """
        topics.Processing.DAY_START.subscribe(self._start_day_processing)
        topics.Processing.PROCESS_FILE.subscribe(self._data_processor)
        topics.Processing.DAY_END.subscribe(self._end_day_processing)
        topics.Processing.END.subscribe(self._end_processing)

    def _start_day_processing(self, date):
        """
        Event handler that will be notified when a day's files are starting to be processed.  This doesn't mean that
        there were actually files processed for this date, just that the date was started.
        :param date: the day that is being processed.
        :return:
        """

        # Store off the current date value, and copy the current date report to previous date report if there is any
        # content to copy off (based on the num_entries in the report).
        if self._day_content and self._day_content.entries:
            self._previous_content = self._day_content

        self._day_content = DayReport(datetime.combine(date=date, time=time.min), [], None, None)

    def test_activities(self, activities_list):
        return self.id in activities_list

    def _data_processor(self, entry):
        """
        Checks to see if the data can be processed and stores any data required locally.
        :param entry:
        :return:
        """
        if entry.mime_type is not md_loader.MIME_TYPE:
            return

        activities_list = entry.metadata.get(MetaKeys.ACTIVITIES, [])
        if self.test_activities(activities_list):
            self._preprocess_entry(entry)
            self._day_content.entries.append(entry)

            # Since there is an entry that will be displayed for this day, can now see if the previous entry should be
            # published or not.
            if self._previous_content:
                # Set current report's previous to the previous content
                self._day_content = self._day_content._replace(prev=self._previous_content)

                # Prepare previous content for publishing
                self._previous_content = self._previous_content._replace(next=self._day_content)
                self._publish_report(self._previous_content)

                # Reset so that it isn't published multiple times
                self._previous_content = None

    def _preprocess_entry(self, entry):
        """
        Process the entry before storing it in the day content for the value.
        :param entry:
        :return:
        """
        pass

    def _end_day_processing(self, date=None):
        """Publish the content of the collated day together."""
        pass

    def _publish_report(self, report):
        sorted(report.entries, key=lambda x: x.metadata[MetaKeys.TIME])
        publish(*self.day_template_path, report=report, id=self.id, name=self.name, description=self.description)
        self._reports.append(report)

    def _end_processing(self):
        """All of the input files have been processed, so now need to build the master input value."""
        # Check to see if there is still a current_content or a previous_content that needs to be published
        if self._previous_content:
            self._publish_report(self._previous_content)
        elif self._day_content:
            self._publish_report(self._day_content)

        # Iterate through all of the values and count entries per day so can determine a decent legend value
        if self._reports:
            max_entries = len(max(self._reports, key=lambda x: len(x.entries)).entries)
            max_year = max(self._reports, key=lambda x: x.date).date.year
            min_year = min(self._reports, key=lambda x: x.date).date.year
        else:
            max_entries = 0
            max_year = min_year = datetime.now().year

        publish(*self.index_template_path, reports=self._reports, max_entries=max_entries, max_year=max_year,
                min_year=min_year, id=self.id, name=self.name, description=self.description)
        topics.Reporting.REGISTER_REPORT.publish(report=Report(self.name, self.description, self.index_template_path,
                                                               {'id': self.id}))
