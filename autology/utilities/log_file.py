"""Utilities for processing log files."""
import mimetypes
import pathlib
import shutil
import logging

import pytz
from collections import namedtuple
from semantic_version import Version

from autology.configuration import get_configuration, get_configuration_root
from autology import topics


logger = logging.getLogger(__name__)

class MetaKeys:
    # Current version allowed by
    CURRENT_FILE_VERSION = Version.coerce('0.2.0')

    # Common frontmatter keys used by all reports
    TIME = 'time'
    END_TIME = 'end_time'
    LOCATION = 'location'
    ACTIVITIES = 'activities'
    AGENT_DEFINITION = 'autology_agent'

    class Agent:
        # Front matter keys used in determining file version
        NAME = 'name'
        VERSION = 'version'
        FILE_VERSION = 'file_definition'


# File Processor map and definition object.
_file_processors = {}
FileProcessor = namedtuple('FileProcessor', 'mime_type load write')

# Log file definition.  If file is none, it hasn't been written out to file yet.
Entry = namedtuple('Entry', 'date mime_type metadata content file python')


def rebuild_entry(entry, **kwargs):
    """Create a new entry based off an original entry and the kwargs that are defined to override the values."""
    dictionary = entry._asdict()
    dictionary.update(kwargs)

    return Entry(**dictionary)


def register_mime_type(file_extension, mime_type):
    """Register the mime types in the system library. """

    # Check to see if it's defined before setting it
    if file_extension not in mimetypes.guess_all_extensions(mime_type):
        mimetypes.add_type(mime_type, file_extension)


def register_file_processor(mime_type, file_loader, file_writer):
    """Register file processor for specified mime_type."""
    _file_processors[mime_type] = FileProcessor(mime_type, file_loader, file_writer)


def get_file_processor(file=None, mime_type=None):
    """Retrieve the file processor for the provided file."""

    if mime_type is None and file is None:
        raise ValueError('mime_type or file must not be None')
    elif mime_type is None:
        file_component = file.resolve()
        mime_type, encoding = mimetypes.guess_type(file_component.as_uri())

    return _file_processors.get(mime_type, None)


def process_datetimes(dictionary):
    """
    Translate all of the datetime objects that are stored in the front matter and make them timezone aware.
    :param dictionary: the dictionary containing the values to process.  This will need to be called recursively on all
    dictionaries contained within.
    :return:
    """
    for key in dictionary.keys():
        if hasattr(dictionary[key], 'tzinfo') and dictionary[key].tzinfo is None:
            # All of the values read in are parsed into UTC time, yaml does this conversion for us when there is
            # timezone information
            utc_value = pytz.utc.localize(dictionary[key])
            site_timezone = pytz.timezone(get_configuration().site.timezone)
            dictionary[key] = utc_value.astimezone(site_timezone)
        elif hasattr(dictionary[key], 'keys'):
            process_datetimes(dictionary[key])

    return dictionary


def walk_log_files(directories):
    """Generator that will walk through all of the log files and yield each file in datetime order."""
    log_files = []

    _LogEntry = namedtuple('LogEntry', 'date file file_processor')

    # Need to find all of the files that are stored in the input_files directories in order to start building the
    # reports that will be used to generate the static log files.
    for input_path in directories:
        search_path = pathlib.Path(input_path)

        for file_component in search_path.glob('**/*'):

            if not file_component.is_dir():
                file_processor = get_file_processor(file=file_component)

                if file_processor:
                    try:
                        entries = file_processor.load(file_component)
                    except KeyError as e:
                        logger.exception('Error processing file: {}'.format(file_component))
                        continue

                    if entries:
                        # entries is either a log entry data model or a list of them.
                        try:
                            entry_time = entries.date
                        except AttributeError:
                            entry_time = entries[0].date

                        log_files.append(_LogEntry(entry_time, file_component, file_processor))

    log_files = sorted(log_files, key=lambda x: x.date)

    for log_entry in log_files:
        # Load up the content of the file and provide all of the documents that are contained with the metadata, some
        # files provide multiple contents, so need to be able to handle that and yield them appropriately.
        loaded_entries = log_entry.file_processor.load(log_entry.file)

        if hasattr(loaded_entries, 'append'):
            for entry in loaded_entries:
                yield entry
        else:
            yield loaded_entries


def find_file(file_path):
    """Iterate through all of the log defined paths in order to find the file pointed to by a relative path."""
    configuration_settings = get_configuration()

    for log_directory in configuration_settings.processing.inputs:
        test_path = pathlib.Path(log_directory) / file_path

        if test_path.exists():
            return test_path

    return None


def insert_file(date, content_file, content=None, overwrite=False):
    """
    Copy the provided file into the log directory structure for the appropriate date.
    :param date: injection_date
    :param content_file: original file name
    :param content: string containing the content of the file to write, if content is none, copy the file contents out
    of the file.
    :param overwrite: should the file be overwritten if it already exists.
    :return tuple containing log directory and path relative to the log directory
    """

    content_file = pathlib.Path(content_file)

    log_directory = get_configuration_root() / get_configuration().processing.inputs[0]

    log_date_directory = log_directory / "{:04d}".format(date.year) / "{:02d}".format(date.month)
    log_date_directory = log_date_directory / "{:02d}".format(date.day)

    # Just in case the directory doesn't exist yet.
    log_date_directory.mkdir(parents=True, exist_ok=True)

    output_location = log_date_directory / content_file.name

    file_name_pattern = '{stem}{unique}{suffix}'

    # Just in case the file already exists, this should make it unique enough
    if not overwrite:
        creation_index = 0
        while output_location.exists():
            output_location = log_date_directory / file_name_pattern.format(stem=output_location.stem,
                                                                            suffix=output_location.suffix,
                                                                            unique='_{}'.format(creation_index))
            creation_index += 1

    if content:
        output_location.write_text(content)
    else:
        shutil.copy(content_file, output_location)

    # Notify the storage engine that everything is finished, and the file can be sent to the remote
    topics.Storage.FILE_ADDED.publish(file=output_location)

    return log_directory, output_location.relative_to(log_directory)


def generate_file_name(entry, extension=None):
    """
    Create the file path for where the file should be written out if the file_path is not already defined.
    :param entry: the entry to build a file name for.
    :param extension: the extension of the file type to use
    :return:
    """

    if extension is None:
        extension = mimetypes.guess_extension(entry.mime_type)

    file_name_pattern = '{date.hour:02}{date.minute:02}{date.second:02}{extension}'
    file_name = file_name_pattern.format(date=entry.date, extension=extension)

    return file_name
