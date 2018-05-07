import argparse

from pkg_resources import iter_entry_points

from autology import topics, logging as autology_logging
from autology.configuration import load_configuration_file as _load_configuration_file
from autology.utilities.plugins import COMMANDS_ENTRY_POINT


def _build_arguments():
    """Load sub-commands defined in setup.py and allow them to build their arguments."""
    parser = argparse.ArgumentParser(description='Execute autology root command')
    parser.add_argument('--config', '-c', action='store', default='config.yaml',)

    # Process all of the sub-commands that have been registered
    subparsers = parser.add_subparsers(help='sub-command help')
    for ep in iter_entry_points(group=COMMANDS_ENTRY_POINT):
        ep.load()(subparsers)

    return parser


def main():
    """Load up all of the plugins and determine which of the sub-commands to execute."""
    parser = _build_arguments()
    args = parser.parse_args()

    # Load up default logging configuration
    autology_logging.load()

    # Allow the command to load up any configuration details that need to be loaded in before the configuration
    # file is loaded in and overrides any defaults.
    if hasattr(args, 'configure'):
        args.configure()

    # Override the default values in configuration with the values from settings file.
    _load_configuration_file(args.config)

    # Configure the logging for all of the components
    autology_logging.configure_logging()

    # Initialize all of the plugins in the architecture now that the settings have been loaded
    topics.Application.INITIALIZE.publish()

    # Execute the sub-command requested. (as per the argparse documentation)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

    topics.Application.FINALIZE.publish()


if __name__ == '__main__':
    main()
