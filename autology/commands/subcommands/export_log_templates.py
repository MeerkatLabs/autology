"""Sub-command that will export all of the log generation templates to a directory."""
import frontmatter
from pkg_resources import iter_entry_points

from autology.configuration import get_configuration_root
from autology.utilities.plugins import TEMPLATES_ENTRY_POINT


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    parser = subparser.add_parser('export_log_templates', help='Export the defined log templates to a directory')
    parser.set_defaults(func=_main)

    parser.add_argument('--output-dir', '-o', help='Location to output all of the templates to',
                        default='templates/generation')


def _main(args):
    """Dumps all of the templates to the output directory provided by args."""
    loaded_templates = {ep.name: ep.load() for ep in iter_entry_points(group=TEMPLATES_ENTRY_POINT)}

    output_directory = get_configuration_root() / args.output_dir

    for name, template in loaded_templates.items():
        output_file = output_directory / "{}.md".format(name)

        post = template.start()

        output_file.write_text(frontmatter.dumps(post))
