"""
Report that will collect all of the logging messages passed to the handler and generate a report based on the
results.
"""

import logging
from autology import topics
from autology.publishing import publish
from autology.reports.models import Report

_initialized = False


def register_plugin():
    """ Subscribe to the initialize method and add default configuration values to the settings object. """
    topics.Application.INITIALIZE.subscribe(_initialize)


def _initialize():
    """Subscribe to the end of file processing so can publish the report."""
    global _initialized
    topics.Processing.BEGIN.subscribe(_publish_report)
    _initialized = True


class LoggingReport(logging.Handler):

    _log_records = []

    def __init__(self, level=logging.NOTSET):
        super(LoggingReport, self).__init__(level)

    def emit(self, record):
        self._log_records.append(record)

    def close(self):
        if _initialized:
            publish('logging', 'index', log_records=self._log_records)
        super(LoggingReport, self).close()


def _publish_report():
    """
    Publish the report containing all of the log records that were collected by the handler.
    :return:
    """
    topics.Reporting.REGISTER_REPORT.publish(report=Report('Logging', 'Collected Error Messages', ['logging', 'index'],
                                                           {}))
