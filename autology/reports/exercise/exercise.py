"""
Process all of the content for the exercise details, and calculate the number of miles that have been done from all of
the gpx files that have been stored.
"""
from autology import topics, publishing
from autology.utilities import log_file
import gpxpy
import gpxpy.gpx
import pytz
import logging
from autology.reports.simple import SimpleReportPlugin

logger = logging.getLogger(__name__)
EXERCISE_ACTIVITY = 'exercise'
GPX_FILE = 'gpx_file'
GPX_DATA = 'gpx_data'

# Pointer to the report plugin provided by simple report plugin functionality.
_report_plugin = None


def register_plugin():
    """ Subscribe to the initialize method and add default configuration values to the settings object. """
    topics.Application.INITIALIZE.subscribe(_initialize)


def _initialize():
    """ Register for all of the required events that will be fired off by the main loop """
    global _report_plugin
    _report_plugin = TimelineReport()
    _report_plugin.initialize()


class TimelineReport(SimpleReportPlugin):

    def __init__(self):
        """Overridden to set the day and index template paths."""
        super().__init__('exercise', 'Exercise', 'List of all exercise related files')
        self.day_template_path = ['exercise', 'day']
        self.index_template_path = ['exercise', 'index']

    def test_activities(self, activities_list):
        """Overridden to process all of the log files that are passed in."""
        return EXERCISE_ACTIVITY in activities_list

    def _preprocess_entry(self, entry):
        """Currently only handling entries that contain data about gpx files."""
        if GPX_FILE in entry.metadata:
            # Need to find the file pointed to in the entry by finding
            gpx_file = log_file.find_file(entry.metadata[GPX_FILE])

            try:
                # This should check to see if the gpx file is valid or not, and if it's valid, then the gpx file should
                # be copied into place and a new markdown file should be created as well based on the start time of the
                # content.
                with open(gpx_file) as gpx_file_content:
                    gpx_data = gpxpy.parse(gpx_file_content)

                # Check to see if the gpx library can find a date, and use that value, otherwise must use the date value
                # provided by the arguments.
                # Arguments probably should always trump the file content.  In addition need to provide an end date time
                # as well.
                start_time, end_time = gpx_data.get_time_bounds()

                start_time = pytz.utc.localize(start_time)
                end_time = pytz.utc.localize(end_time)

                moving_time, stopped_time, moving_distance, stopped_distance, max_speed = gpx_data.get_moving_data()

                entry.metadata[GPX_DATA] = dict(speed=dict(max=max_speed, min=0, average=0),
                                                distance=gpx_data.length_3d(),
                                                time=end_time - start_time)

                # Copy the gpx file so that it can be referenced by the entry metadata
                output_url = publishing.copy_file(gpx_file, 'exercise', 'data_file', date=start_time, id=self.id,
                                                  file_name=gpx_file.name)
                entry.metadata['gpx_url'] = output_url

            except gpxpy.gpx.GPXXMLSyntaxException:
                logger.exception('Cannot import file: {}'.format(gpx_file))
