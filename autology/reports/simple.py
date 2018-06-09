"""
Simple plugin that will allow for an easy means of registering activity logging.  Functionality is used by the timeline
plugin.
"""
from datetime import datetime, time

from collections import namedtuple

from autology import topics
from autology.configuration import add_default_configuration, get_configuration
from autology.publishing import publish, find_template, TemplateLookupError
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
        'definitions': []
    })


def _initialize():
    """
    Look in the configuration and create a new SimpleReportPlugin for all of the activities that are defined.
    :return:
    """
    for config in get_configuration().simple.definitions:
        plugin = SimpleReportPlugin(config.id, config.name, config.description, config.activities)
        plugin.initialize()
        _defined_plugins.append(plugin)


class SimpleReportPlugin:

    def __init__(self, id, name, description, activities=None):
        """
        Initialize the report plugin.
        :param id: identifier for the report
        :param name: human readable name for the report
        :param description: description for the report
        :param activities: activities associated with this report type.
        """
        # The content that is stored for each individual day
        self._day_content = None
        self._previous_content = None

        # Dates that have been collected
        self._reports = []
        self.id = id
        self.name = name
        self.description = description

        if activities:
            self.activities = activities
        else:
            self.activities = [self.id]

        # Define template definitions so that they are looked up on first usage.
        self._day_template = None
        self._index_template = None

    def initialize(self):
        """
        Register for all of the required events that will be fired off by the main loop
        :return:
        """
        topics.Processing.BEGIN.subscribe(self._begin_processing)
        topics.Processing.DAY_START.subscribe(self._start_day_processing)
        topics.Processing.PROCESS_FILE.subscribe(self._data_processor)
        topics.Processing.DAY_END.subscribe(self._end_day_processing)
        topics.Processing.END.subscribe(self._end_processing)
        topics.Processing.PREPROCESS_FILE.subscribe(self._preprocess_entry)

    def _begin_processing(self):
        """Record the report that is being generated regardless of whether it has data or not."""
        topics.Reporting.REGISTER_REPORT.publish(report=Report(self.name, self.description, self.index_template_path(),
                                                               {'id': self.id}))

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
        """
        Test to see if activities will require that the entry be processed.  This is done by seeing if any of the
        activities in the activities_list parameter are contained in the activities defined in the definition.
        :param activities_list: activities associated with this entry
        :return: if the entry should be processed or not
        """
        overlap_test = [a for a in activities_list if a in self.activities]
        return len(overlap_test) > 0

    def _test_entry(self, entry):
        """Test to see if the entry should be processed or not.  Current implementation tests the activities list."""
        activities_list = entry.metadata.get(MetaKeys.ACTIVITIES, [])
        return self.test_activities(activities_list)

    def _preprocess_entry(self, entry):
        """Check to see if the entry should be preprocessed by this report, and then pre-process it."""
        if self._test_entry(entry):
            self.preprocess_entry(entry)

    def _data_processor(self, entry):
        """
        Checks to see if the data can be processed and stores any data required locally.
        :param entry:
        :return:
        """
        if entry.mime_type is not md_loader.MIME_TYPE:
            return

        if self._test_entry(entry):
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

    def preprocess_entry(self, entry):
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
        publish(*self.day_template_path(), report=report, id=self.id, name=self.name, description=self.description)
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

        publish(*self.index_template_path(), reports=self._reports, max_entries=max_entries, max_year=max_year,
                min_year=min_year, id=self.id, name=self.name, description=self.description)

    def index_template_path(self):
        """Retrieve the index template path for this report."""

        if not self._index_template:
            self._index_template = [self.id, 'index']
            try:
                find_template(*self._index_template)
            except TemplateLookupError:
                self._index_template = ['simple', 'index']

        return self._index_template

    def day_template_path(self):
        """Retrieve the day template path for this report."""
        if not self._day_template:
            self._day_template = [self.id, 'day']
            try:
                find_template(*self._day_template)
            except TemplateLookupError:
                self._day_template = ['simple', 'day']

        return self._day_template

