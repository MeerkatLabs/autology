"""
Provide an injector for the exercise report.  This will create a new file associated with a gpx file that is provided,
it will give details about the gpx file based on calculations that are provided.
"""
from autology.utilities import injectors, log_file
from autology.reports.exercise import template
import pathlib
import gpxpy
import gpxpy.gpx
import frontmatter
import pytz
import tzlocal


def register_injector():
    injectors.register_injector('gpx_file', handle_injection)


def handle_injection(file=None, start_time=None, end_time=None):
    """Inject the provided file into the date requested."""

    if file is None:
        print('Cannot handle null file')
        return

    injection_file = pathlib.Path(file)

    try:
        # This should check to see if the gpx file is valid or not, and if it's valid, then the gpx file should be
        # copied into place and a new markdown file should be created as well based on the start time of the content.
        with open(file) as gpx_file:
            gpx_data = gpxpy.parse(gpx_file)

        # Check to see if the gpx library can find a date, and use that value, otherwise must use the date value
        # provided by the arguments.
        # Arguments probably should always trump the file content.  In addition need to provide an end date time as
        # well.
        if start_time is None or end_time is None:
            start_time, end_time = gpx_data.get_time_bounds()

            if start_time:
                start_time = pytz.utc.localize(start_time)
            if end_time:
                end_time = pytz.utc.localize(end_time)

        _inject_gpx_file(injection_file, start_time, end_time)
    except gpxpy.gpx.GPXXMLSyntaxException:
        print('Cannot import file: {}'.format(file))


def _inject_gpx_file(file_component, start_time, end_time):
    """Add project template metadata to the file_component and then copy it into place into the directory structure."""

    if start_time is None or end_time is None:
        print('Cannot import file: {} because start_time ({}) or end_time ({}) is unknown'.format(file_component,
                                                                                                  start_time, end_time))
        return

    start_time = start_time.astimezone(tzlocal.get_localzone())
    end_time = end_time.astimezone(tzlocal.get_localzone())

    # GPX File format requires that all times are in UTC.
    file_location = injectors.insert_file(start_time, file_component, file_component.read_text())
    print('Importing file: {}'.format(file_location))

    post = template.gpx_template_start(gpx_file=file_location, start_time=start_time, end_time=end_time)
    post_file_location = injectors.insert_file(start_time, file_component.with_suffix('.md'), frontmatter.dumps(post))
    print('Injected file at: {}'.format(post_file_location))
