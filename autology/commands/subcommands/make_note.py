"""Sub-command that will create a new note file for the log."""
import subprocess
import textwrap

from pkg_resources import iter_entry_points

from autology import topics
from autology.configuration import add_default_configuration, get_configuration
from autology.storage import load as load_storage_plugin
from autology.utilities.log_file import get_file_processor
from autology.utilities.plugins import TEMPLATES_ENTRY_POINT, FILE_PROCESSOR_ENTRY_POINT


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    parser = subparser.add_parser('make_note', help='Create a new note object.')
    parser.set_defaults(func=_main)
    parser.set_defaults(configure=_configure)

    parser.add_argument('--template-list', '-T', help='List all of the templates that are available',
                        action='store_true')
    parser.add_argument('--template', '-t', help='Specify the template file that will be used',
                        default=None)

    parser.add_argument('--kwarg-list', '-K', help='List the arguments associated with the selected template',
                        action='store_true')

    parser.add_argument('--kwarg', '-k', help='Specify key/value pairs to be provided to the template during '
                                              'definition.  These are defined as KEY=value.  Keys cannot contain '
                                              'spaces, but values may.  In such a case, quote the entire key/value'
                                              'string.',
                        action='append', metavar='KEY=VALUE')

    add_default_configuration('make_note',
                              {
                                  'default_template': 'timeline_base',
                                  'editor': 'xdg-open {file}',
                              })


def _configure():
    """Load up the configuration details for the storage component."""
    for entry_point in iter_entry_points(group=FILE_PROCESSOR_ENTRY_POINT):
        entry_point.load()()

    load_storage_plugin()


def _main(args):
    """ Create a new note file in the correct location. """
    loaded_templates = {ep.name: ep.load() for ep in iter_entry_points(group=TEMPLATES_ENTRY_POINT)}

    if args.template_list:
        print('Available templates:')

        _print_documentation_help({key: value.description for key, value in loaded_templates.items()})

        return

    # Load up the template in order to print detailed information about arguments, or to create a new note.
    template_name = args.template if args.template is not None else get_configuration().make_note.default_template
    template = loaded_templates[template_name]

    if args.kwarg_list:
        print('Template Name: {}'.format(template_name))
        print('Description:   {}'.format(template.description))
        print('Arguments: ')

        _print_documentation_help(template.arguments)
    else:
        kwargs = {}
        # Need to split all of the kwargs into a dictionary.
        if args.kwarg:
            kwargs = dict(kv.split('=') for kv in args.kwarg)

        # Create the new entry
        post = template.start(**kwargs)

        # Save the post and update the object to get the filename where the file is stored.
        file_processor = get_file_processor(mime_type=post.mime_type)
        if file_processor is None:
            raise KeyError('Cannot find processor for mime_type: {}'.format(post.mime_type))

        post = file_processor.write(post)

        # Builds the list of command arguments and executes the editor.
        commands = [a.format(file=post.file) for a in get_configuration().make_note.editor.split()]
        subprocess.run(commands)

        # Now need to reload the contents of the file, and convert all of the time values
        post = file_processor.load(post.file)

        # Finish up the template code and write the file back out to the file system
        template.end(post)
        file_processor.write(post)

        # Notify the storage engine that everything is finished, and the file can be sent to the remote
        topics.Storage.FILE_ADDED.publish(file=post.file)
        topics.Storage.FINISHED_MODIFICATIONS.publish(message="New Note from autology make_note")
        topics.Storage.PULL_CHANGES.publish()
        topics.Storage.PUSH_CHANGES.publish()


def _print_documentation_help(dictionary, initial_index='  '):
    """
    Creates a nice list of keys and definitions that can be used to describe the keys.
    :param dictionary: keys and descriptions of the keys
    :param initial_index: initial index that will be used for the keys
    :return:
    """

    formatter = textwrap.TextWrapper(initial_indent=initial_index)

    # add three to the max value in order to have '  ' after each key.
    template_length = max([len(key) for key in dictionary.keys()], default=0) + 3

    formatter.subsequent_indent = ' ' * template_length + formatter.initial_indent

    for key, value in dictionary.items():
        spacing = ' ' * (template_length - len(key))
        print(formatter.fill('{key}{spacing}{description}'.format(key=key, spacing=spacing, description=value)))
        print()
