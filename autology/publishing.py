"""
Provides wrapper around common publishing functionality.
"""
import pathlib
import logging

import markdown
import shutil
import yaml
from dict_recursive_update import recursive_update
from jinja2 import Environment, FileSystemLoader, select_autoescape

from autology import topics
from autology.configuration import add_default_configuration, get_configuration

logger = logging.getLogger(__name__)
_environment = None
_output_path = None
_markdown_conversion = None
_template_configuration = {}


def load():
    """
    Subscribe to the initialize method and add default configuration values to the settings object.
    :return:
    """
    topics.Application.INITIALIZE.subscribe(_initialize)
    topics.Processing.END.subscribe(_copy_static_files)

    add_default_configuration('publishing',
                              {
                                  'templates': 'templates',
                                  'output': 'output',
                                  'url_root': '/'
                              })


class TemplateLookupError(LookupError):
    pass


def _initialize():
    """
    Initialize the jinja environment.
    :return:
    """
    global _environment, _output_path, _markdown_conversion, _template_configuration
    configuration_settings = get_configuration()

    # Load up and store the configuration that is defined in the template files
    template_configuration_path = pathlib.Path(configuration_settings.publishing.templates) / 'template.yaml'
    if template_configuration_path.exists():
        with template_configuration_path.open() as tc_file:
            _template_configuration = yaml.load(tc_file)

    # Create markdown conversion object
    _markdown_conversion = markdown.Markdown()

    # Load the same jinja environment for everyone
    _environment = Environment(
        loader=FileSystemLoader(configuration_settings.publishing.templates),
        autoescape=select_autoescape()
    )

    # Load up the custom filters
    _environment.filters['markdown'] = markdown_filter

    # Load up the global functions
    _environment.globals.update({'url': generate_url})

    # Verify that the output directory exists before starting to write out the content
    _output_path = pathlib.Path(configuration_settings.publishing.output)
    _output_path.mkdir(exist_ok=True)


def publish(*args, context=None, **kwargs):
    """
    Notify jinja to publish the template to the output_file location with all of the context provided.
    :param args: the arguments that will be used to find the template in the template configuration
    :param context:
    :param kwargs:
    :return:
    """
    context = _build_context(context=context, **kwargs)
    try:
        template_definition = find_template(*args)
    except TemplateLookupError:
        logger.exception('Could not find template')
        raise

    # Load the template and render to the destination file defined in the template_definition
    root_template = _environment.get_template(str(template_definition['template']))
    output_file = template_definition['destination'].format(**context)
    output_content = root_template.render(context)
    output_file = _output_path / output_file

    # Verify that the path is possible and write out the file
    output_file.parent.mkdir(exist_ok=True, parents=True)
    output_file.write_text(output_content)


def _build_context(context=None, **kwargs):
    """Build up the context values based on the content provided."""

    # Build up the context argument, special kwarg context will be used to provide a starting dictionary
    if not context:
        context = {}
    recursive_update(context, kwargs)

    # Insert all of the site details into the context as well
    site_configuration = get_configuration().site.toDict()
    recursive_update(context.setdefault('site', {}), site_configuration)

    # Insert all of the template variables into the context as well
    template_variables = _template_configuration.get('variables', {})
    recursive_update(context.setdefault('template', {}), template_variables)

    return context


def find_template(*args):
    """Find the template definition object"""
    template_definition = _template_configuration.get('templates', {})
    for template_path in args:
        try:
            template_definition = template_definition[template_path]
        except KeyError:
            logger.debug(f"Cannot find template definition: {args} in template definitions: "
                         f"{_template_configuration.get('templates', {})}")
            raise TemplateLookupError(f'Cannot find template definition: {args}')

    return template_definition


def copy_file(file, *args, context=None, **kwargs):
    """
    Copy a file in place based on the arguments provided and the kwargs that are used to generate the path.
    :param file:
    :param args:
    :param context:
    :param kwargs:
    :return:
    """
    context = _build_context(context=context, **kwargs)
    try:
        template_definition = find_template(*args)
    except TemplateLookupError:
        logger.exception('Could not find template')
        raise

    output_file = template_definition['destination'].format(**context)
    output_file = _output_path / output_file

    output_file.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(str(file), str(output_file))


def generate_url(*args, **kwargs):
    """
    Generate a URL based on the path and the context provided.
    :param args: string containing the template definition path.
    :param kwargs: dictionary containing the context to use when generating the file location.
    :return: string containing URL to be used.
    """
    config = get_configuration()
    root = ""
    if config.publishing.url_root:
        root = config.publishing.url_root

    try:
        template_definition = find_template(*args)
    except TemplateLookupError:
        logger.exception('Could not find template')
        raise

    output_file = template_definition['destination'].format(**kwargs)

    return root + output_file


def markdown_filter(content):
    """Filter that will translate markdown content into HTML for display."""
    return _markdown_conversion.reset().convert(content)


def _copy_static_files():
    """Responsible for copying over the static files after all of the contents have been generated."""
    configuration = get_configuration()
    template_path = pathlib.Path(configuration.publishing.templates)
    output_path = pathlib.Path(configuration.publishing.output)

    static_files_list = _template_configuration.get('static_files', [])

    if static_files_list:
        for glob_definition in static_files_list:
            for file in template_path.glob(glob_definition):
                logger.debug('Copying static file: {}'.format(file))

                # Make sure that the destination directory exists before copying the file into place
                destination_parent = file.parent.relative_to(template_path)
                destination = output_path / destination_parent
                destination.mkdir(parents=True, exist_ok=True)

                shutil.copy(str(file), str(destination))
