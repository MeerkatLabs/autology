"""Sub-command that will dump the current configuration, to include all of the default values."""
import pathlib
from pkg_resources import iter_entry_points
from autology.configuration import get_configuration_root, dump_configuration
from autology.utilities import plugins
from autology.publishing import load as load_publishing_plugin
from autology.storage import load as load_storage_plugin


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    parser = subparser.add_parser('dump_config', help='Create a new note object.')
    parser.set_defaults(func=_main)
    parser.set_defaults(configure=_configure)

    parser.add_argument('--output', '-o', default='config.yaml', help='File that will store the output.')


def _configure():
    """
    Load up the report plugins and allow them to insert their configuration details into the default configuration
    object.
    """
    for entry_point in iter_entry_points(group=plugins.REPORTS_ENTRY_POINT):
        entry_point.load()()

    for entry_point in iter_entry_points(group=plugins.FILE_PROCESSOR_ENTRY_POINT):
        entry_point.load()()

    load_publishing_plugin()
    load_storage_plugin()


def _main(args):
    """
    Dump the current configuration file
    :param args:
    :return:
    """
    output_path = pathlib.Path(args.output)

    if not output_path.is_absolute():
        output_path = get_configuration_root() / output_path

    # Now need to find the templates definition of that zip file and locate it in the file system so that it can be
    dump_configuration(output_path)
