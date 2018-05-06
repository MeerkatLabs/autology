"""Sub command that will generate the content of the static site."""
import pathlib

from autology.configuration import get_configuration, get_configuration_root, dump_configuration
from autology.commands.subcommands import updaters
from autology.utilities import templates as template_utilities


def register_command(subparser):
    """Register the subcommand with any additional arguments."""
    update_parser = subparser.add_parser('update', help='Run the log files through an updater.  Used to update '
                                                        'between versions of autology')
    update_parser.set_defaults(func=_main)

    # Arguments
    update_parser.add_argument('-f', '--files', help='Update the files that are currently defined in the log '
                                                     'directories', action='store_true')
    update_parser.add_argument('-t', '--templates', help='Install a new output template', action='store_true')
    update_parser.add_argument('-T', '--template-definition', help='Define a template definition to install',
                               default=template_utilities.DEFAULT_TEMPLATES_URL)


def _main(args):
    """Process the arguments provided and update the files as necessary."""
    if args.files:
        _update_files()

    if args.templates:
        _update_template(args.template_definition)


def _update_files():
    """Find each of the files in the log file and hand them to the file updaters for processing."""
    configuration_settings = get_configuration()

    # Need to find all of the files that are stored in the input_files directories in order to start building the
    # reports that will be used to generate the static log files.
    for input_path in configuration_settings.processing.inputs:
        search_path = pathlib.Path(input_path)

        # Currently going to make the assumption that everyone is using the path naming convention that I'm dictating
        # which is YYYY/MM/DD/file.ext
        for file_component in search_path.glob('*/*/*/*'):
            # Store all of the files into a dictionary containing the keys and a list of the files that are associated
            # with that day
            updaters.update_files(search_path, file_component)


def _update_template(template_path):
    """Update the output generation templates based on the file/uri provided."""
    template_definition = template_path

    # template output directory is output/templates, so need to create that location before pulling out the templates
    template_location = template_utilities.get_template_directory()

    # Install the template and get the path to the template directory for updating the configuration file.
    templates_path = template_utilities.install_template(template_location, template_definition)

    if templates_path:
        # Now need to find the templates definition of that zip file and locate it in the file system so that it can be
        settings = get_configuration()

        # Override the configuration details with the new template path.  This should probably be handled by the
        # publishing plugin, but for now this will work
        settings.publishing.templates = str(templates_path.relative_to(get_configuration_root()))
        configuration_file_path = get_configuration_root() / 'config.yaml'

        dump_configuration(configuration_file_path, settings)
