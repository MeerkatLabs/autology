"""
Log file updater that will translate all of the time and end_time values into timezone aware data values.
"""
import frontmatter
import tzlocal
import logging

from semantic_version import Version

from autology.utilities.log_file import MetaKeys

import datetime
import pytz

logger = logging.getLogger(__name__)
DEFAULT_EVENT_LENGTH = 60  # minutes
FILE_VERSION_INFORMATION = Version.coerce('0.2.0')


def change_date_time_values(search_path, file_component):
    """
    Will check to see if the file needs to be processed before updating the values.  Will then populate the new agent
    information with what should be used in the future.
    :param search_path:
    :param file_component:
    :return:
    """
    if file_component.suffix != '.md':
        return

    entry = frontmatter.load(file_component)

    # Can assume that the entry has the agent definition data because it passed through the previous values
    agent_definition = entry[MetaKeys.AGENT_DEFINITION]
    version = Version.coerce(agent_definition[MetaKeys.Agent.FILE_VERSION])

    if version >= FILE_VERSION_INFORMATION:
        return

    year, month, day = file_component.parent.relative_to(search_path).parts

    logger.info('Processing: {} {}/{}/{}'.format(file_component, year, month, day))

    date = datetime.date(int(year), int(month), int(day))

    local_timezone = tzlocal.get_localzone()

    start_date = _get_start_time(date, entry.metadata, file_component, tzinfo=local_timezone)
    end_time = _get_end_time(start_date, entry.metadata, tzinfo=local_timezone)

    entry.metadata[MetaKeys.TIME] = start_date
    entry.metadata[MetaKeys.END_TIME] = end_time
    entry.metadata[MetaKeys.AGENT_DEFINITION][MetaKeys.Agent.FILE_VERSION] = "{}".format(FILE_VERSION_INFORMATION)

    with open(file_component, "w") as output_file:
        output_file.write(frontmatter.dumps(entry))


def _get_start_time(date, front_matter, file_path=None, tzinfo=pytz.utc):
    """
    Convert the details in front matter into a start time for the file.  If there isn't a value stored in the front
    matter data values, then if defined the file_path will be used.

    Will search for start_time key in the front matter dictionary, if that value is a string, then it will be parsed as:
    HH:MM.
    If it's an integer or a if it's a duration, then it will be parsed as [HH:]MM:SS duration value which is what YAML
    uses by default.  Please know that this is because of YAML parsing rules.

    if the front_matter doesn't contain a start_time and file_path is None, then the start_time will be returned as
    midnight.

    :param date: date to be used for the time.
    :param front_matter: the front matter dictionary associated with the file
    :param file_path: the file path of the log file.
    :param tzinfo: the timezone value to localize the date into after processing
    :return datetime object containing the date time start of the file.
    """
    if 'time' in front_matter:
        front_matter_value = front_matter['time']
        return_value = _parse_time_value(date, front_matter_value)
    else:
        logger.warning('File: {} doesn\'t have a time value: '.format(file_path))
        return_value = datetime.datetime.combine(date, datetime.time.min)

    return tzinfo.localize(return_value)


def _get_end_time(start_time, front_matter, tzinfo=pytz.utc):
    """
    Parse the end time value out of front matter.  Cannot use a file to determine this value, but the rest of the
    documentation in get_start_time is relevant to this method.
    :param start_time:
    :param front_matter:
    :param tzinfo: the timezone value to localize the date into after processing
    :return:
    """
    if 'end_time' in front_matter and front_matter['end_time']:
        front_matter_value = front_matter['end_time']
        return_value = _parse_time_value(start_time.date(), front_matter_value)
    else:
        return_value = start_time + datetime.timedelta(minutes=DEFAULT_EVENT_LENGTH)

    if return_value.tzinfo:
        return return_value

    return tzinfo.localize(return_value)


def _parse_time_value(date, time_value):

    if isinstance(time_value, int):
        # Convert it as a duration from midnight of the date.
        return datetime.datetime.combine(date, datetime.time.min) + datetime.timedelta(seconds=time_value)
    elif isinstance(time_value, datetime.datetime):
        return time_value
    else:
        splits = time_value.split(':')
        rv_hours = splits[0]
        rv_minutes = splits[1]
        rv_seconds = 0
        if len(splits) == 3:
            rv_seconds = splits[2]

        return datetime.datetime.combine(date, datetime.time(int(rv_hours), int(rv_minutes), int(rv_seconds)))
