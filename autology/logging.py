import logging
from autology.configuration import add_default_configuration, get_configuration


def load():
    """Initializes the logging default configuration details."""
    add_default_configuration('logging', {
        'level': 'WARNING'
    })


def configure_logging():
    """Configure the logging settings from the configuration file."""
    configuration = get_configuration()
    logging.basicConfig(**configuration.get('logging', {}))

    logging.debug('Logging configured.')
