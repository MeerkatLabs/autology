"""
Provide an injector for the project report.  This will add some front matter to the beginning of the YAML document in
order to provide metadata information.
"""
from autology.utilities import injectors, log_file
from autology.reports.timeline.processors import yaml_processor
from autology.reports.project import template
import pathlib
import frontmatter


def register_injector():
    injectors.register_injector('mkl-project', handle_injection)


def handle_injection(file=None, start_time=None, end_time=None):
    """Inject the provided file into the date requested."""

    if file is None:
        print('Cannot handle null file')
        return

    injection_file = pathlib.Path(file)

    file_processor = log_file.get_file_processor(injection_file)

    if file_processor.mime_type == yaml_processor.MIME_TYPE:
        _inject_yaml_file(injection_file, start_time)


def _inject_yaml_file(file_component, date):
    """Add project template metadata to the file_component and then copy it into place into the directory structure."""

    post = template.template_start(start_time=date)
    post.content = file_component.read_text()

    file_location = injectors.insert_file(date, file_component, frontmatter.dumps(post))

    print('Injected file at: {}'.format(file_location))
