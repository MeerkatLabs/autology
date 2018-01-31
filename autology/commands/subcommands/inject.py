"""
Injection command for providing non-markdown files into the data stream.  Will provide the content of the file to
the plugin defined in the command line arguments.  This command will then decide how to inject the data into the
data stream.
"""
from autology.utilities import injectors
from datetime import datetime
import tzlocal

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    parser = subparser.add_parser('inject', help='Inject data into the data stream.')
    parser.set_defaults(func=_main)

    parser.add_argument('-i', '--injector', help='Specify which injector should be used to process the input')
    parser.add_argument('-f', '--file', help='Specify the content that should be injected.  If none, the injector is '
                                             'expected to have a default action which doesn\'t require a file')
    parser.add_argument('-d', '--date', help='Specify the date that the file should be injected into')
    parser.add_argument('-D', '--end-date', help='Specify the date that the file should end')


def _main(args):
    """Find an injector for the plugin and provide the file content to it for processing."""

    injector = injectors.get_injector(args.injector)
    if injector is None:
        print('Could not find injector defined by: {}'.format(args.injector))
        return

    start_time = None
    end_time = None

    if args.date is not None:
        start_time = tzlocal.get_localzone().localize(datetime.strptime(args.date, DATE_FORMAT))

    if args.end_date is not None:
        end_time = tzlocal.get_localzone().localize(datetime.strptime(args.end_date, DATE_FORMAT))

    injector(args.file, start_time, end_time)
