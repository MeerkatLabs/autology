import datetime
import logging

from autology.utilities.processors import markdown as md_loader
from autology.utilities import log_file


logger = logging.getLogger(__name__)


def pre_processor(entry):
    """Duration pre-processor that is responsible for calculating the duration of the entries."""

    if entry.mime_type is not md_loader.MIME_TYPE:
        return

    # Calculate how long the event lasts
    log_date = entry.metadata[log_file.MetaKeys.TIME]
    log_end_date = entry.metadata[log_file.MetaKeys.END_TIME]

    # Check to see if the end date is defined before doing the math, otherwise just use a duration of an hour
    if log_end_date:
        duration = log_end_date - log_date
    else:
        logger.warning('File: {} doesn\'t have an end time'.format(entry.file))
        duration = datetime.timedelta(hours=1)

    # Set the date values in the post to be the python objects instead of just strings
    entry.metadata['duration'] = duration
