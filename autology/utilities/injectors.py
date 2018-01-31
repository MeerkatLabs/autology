"""
Module that will allow developers to register their injection methods into inject command.  Each plugin can only
inject a single receiver.  From the content that is provided, the method will have to farm out it's own functionality.
These calls should be made during the plugin registration method.
"""
from datetime import datetime
from autology.configuration import get_configuration, get_configuration_root
from autology import topics

_INJECTORS = {}


def register_injector(_key, _callable):
    """Register the injector based on the key and callable method."""
    global _INJECTORS
    _INJECTORS[_key] = _callable


def get_injector(_key):
    """Retrieved the registered injector."""
    return _INJECTORS.get(_key, None)


def insert_file(date, content_file, content):
    """
    Copy the provided file into the log directory structure for the appropriate date.
    :param date: injection_date
    :param content_file: original file name
    :param content: string containing the content of the file to write
    :return output file location
    """
    log_directory = get_configuration_root() / get_configuration().processing.inputs[0]
    log_date_directory = log_directory / "{:04d}".format(date.year) / "{:02d}".format(date.month) / "{:02d}".format(date.day)

    # Just in case the directory doesn't exist yet.
    log_date_directory.mkdir(parents=True, exist_ok=True)

    output_location = log_date_directory / content_file.name

    # Just in case the file already exists, this should make it unique enough
    if output_location.exists():
        output_location = log_date_directory / '{}-{}{}'.format(content_file.stem,
                                                                datetime.now().strftime('%Y%m%d%H%M%S%f'),
                                                                content_file.suffix)

    output_location.write_text(content)

    # Notify the storage engine that everything is finished, and the file can be sent to the remote
    topics.Storage.FILE_ADDED.publish(file=output_location)
    topics.Storage.FINISHED_MODIFICATIONS.publish(message="Injected note from: {}".format(output_location))
    topics.Storage.PULL_CHANGES.publish()
    topics.Storage.PUSH_CHANGES.publish()

    return output_location.relative_to(log_directory)
