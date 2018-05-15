import logging
import logging.config
from autology.configuration import add_default_configuration, get_configuration


def load():
    """Initializes the logging default configuration details."""
    add_default_configuration('logging', {
        'version': 1,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'ERROR'
            },
            'recorder': {
                'class': 'autology.reports.logging.LoggingReport',
            }
        },
        'root': {
            'handlers': ['console'],
        },
        'loggers': {
            'autology': {
                'handlers': ['recorder'],
                'level': 'WARNING'
            }
        }
    })


def configure_logging():
    """Configure the logging settings from the configuration file."""
    configuration = get_configuration()

    logging_configuration = configuration.get('logging', {})

    print('Logging_configuration: {}'.format(logging_configuration))

    if logging_configuration:
        logging.config.dictConfig(logging_configuration)
    else:
        logging.basicConfig()

    logger = logging.getLogger(__name__)
    logger.debug('Logging configured.')
