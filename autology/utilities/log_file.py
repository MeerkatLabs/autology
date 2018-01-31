"""Utilities for processing log files."""
import mimetypes
import datetime
import tzlocal
import pathlib
import pytz
from autology.configuration import get_configuration

from collections import namedtuple

_file_processors = {}


_FileProcessor = namedtuple('FileProcessor', 'mime_type load')
_LogEntry = namedtuple('LogEntry', 'date file file_processor')


def register_mime_type(file_extension, mime_type):
    """Register the mime types in the system library. """

    # Check to see if it's defined before setting it
    if file_extension not in mimetypes.guess_all_extensions(mime_type):
        mimetypes.add_type(mime_type, file_extension)


def lookup_mime_type(file_component):
    """Lookup the mime type based on the pathlib path provided."""
    file_component = file_component.resolve()
    file_type, encoding = mimetypes.guess_type(file_component.as_uri())
    return file_type


def register_file_processor(mime_type, file_loader):
    """Register file processor for specified mime_type."""
    _file_processors[mime_type] = _FileProcessor(mime_type, file_loader)


def get_file_processor(file):
    """Retrieve the file processor for the provided file."""
    mime_type = lookup_mime_type(file)
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

    # Need to find all of the files that are stored in the input_files directories in order to start building the
    # reports that will be used to generate the static log files.
    for input_path in directories:
        search_path = pathlib.Path(input_path)

        for file_component in search_path.glob('**/*'):

            if not file_component.is_dir():
                file_processor = get_file_processor(file_component)

                if file_processor:
                    try:
                        entries = file_processor.load(file_component)
                    except KeyError:
                        print('Error processing file: {}'.format(file_component))
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
