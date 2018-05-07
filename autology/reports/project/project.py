"""Processes the front data in the markdown files to process project stat recordings."""
import datetime
import logging

from autology import topics
from autology.publishing import publish
from autology.reports.models import Report
from autology.utilities.log_file import MetaKeys

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from dict_recursive_update import recursive_update as _r_update
from autology.utilities import log_file

# Constants:
PROJECT_KEY = 'mkl-project'
ORGANIZATION_KEY = 'mkl-organization'
CUSTOMER_KEY = 'mkl-customer'

# This is a dictionary containing all of the defined projects, they key is a project identifier that is defined when
# defining the project. Inside should be a dictionary containing a key of datetime object for an entry, and then the
# entry that is associated with that project.
_defined_projects = {}
_defined_organizations = {}
_defined_customers = {}

logger = logging.getLogger(__name__)


def register_plugin():
    """ Subscribe to the initialize method and add default configuration values to the settings object. """
    topics.Application.INITIALIZE.subscribe(_initialize)


def _initialize():
    """ Register for all of the required events that will be fired off by the main loop """
    topics.Processing.PROCESS_FILE.subscribe(process_file)
    topics.Processing.END.subscribe(_build_report)


def _build_report():
    """Convert all the collated data into renderable templates."""
    orphaned_projects = []

    for project in _defined_projects.values():
        organization = _defined_organizations.get(project.get('organization'))
        if organization:
            organization.setdefault('projects', []).append(project)
        else:
            orphaned_projects.append(project)

        # Sort the logs that are stored on the project
        project['log'] = sorted(project.get('log', []), key=lambda x: x.metadata['time'])

        # Now generate a report for each of the projects.
        url = publish('project', 'project', project=project)
        project['url'] = url

    main_context = {
        'projects': _defined_projects.values(),
        'organizations': _defined_organizations.values(),
        'customers': _defined_customers.values(),
    }

    if orphaned_projects:
        main_context['orphaned_projects'] = orphaned_projects

    url = publish('project', 'index', **main_context)
    topics.Reporting.REGISTER_REPORT.publish(report=Report('Project', 'List of all project files', url))


def process_file(entry):
    """
    Process the file.

    This will subscribe to markdown files, which it will use to record the amount of time that the event is taking
    place.  For YAML files it will will look for root object definitions that it understands.  These will have the
    key:  mkl-project and will contain some kind of project identifier.

    It is not guaranteed that the files that are being processed will be processed in order.
    """

    activities_list = entry.metadata.get(MetaKeys.ACTIVITIES, [])

    if 'project' not in activities_list:
        return

    try:
        if entry.mime_type == 'text/markdown':
            _process_markdown(entry)
        elif entry.mime_type == 'application/x-yaml':
            _process_yaml(entry.python)
    except:
        logger.exception('Error processing file: {}'.format(entry.file))
        raise


def _process_markdown(post):
    """Process the front-matter contents, and store the markdown if necessary."""
    _process_yaml([post.metadata])

    if PROJECT_KEY in post.metadata and post.metadata[PROJECT_KEY] and not isinstance(post.metadata[PROJECT_KEY], dict):

        # Spec says that this can only be a string
        project_definition = _defined_projects.setdefault(post.metadata[PROJECT_KEY],
                                                          {'id': post.metadata[PROJECT_KEY]})
        project_log = project_definition.setdefault('log', [])
        project_log.append(post)

        # Calculate how long the event lasts
        log_date = post.metadata[log_file.MetaKeys.TIME]
        log_end_date = post.metadata[log_file.MetaKeys.END_TIME]
        duration = log_end_date - log_date
        time_on_project = project_definition.get('duration', datetime.timedelta())
        project_definition['duration'] = time_on_project + duration

        # Set the date values in the post to be the python objects instead of just strings
        post.metadata['duration'] = duration


def _process_yaml(documents):
    """Process the document update data structures according to the data values."""

    for document in documents:
        # Figure out if any of the documents contain definitions of project/organization/customers and if so, see if
        # the documents define them (i.e. have dictionaries), or if the document is just about the data.
        if PROJECT_KEY in document:

            project_definition = document[PROJECT_KEY]
            if not isinstance(project_definition, dict):
                return

            _handle_project_definition(project_definition)

        elif ORGANIZATION_KEY in document:

            organization_definition = document[ORGANIZATION_KEY]
            if not isinstance(organization_definition, dict):
                return

            _handle_organization_definition(organization_definition)

        elif CUSTOMER_KEY in document:

            customer_definition = document[CUSTOMER_KEY]
            if not isinstance(customer_definition, dict):
                return

            _handle_customer_definition(customer_definition)


def _handle_organization_definition(definition):
    """Process an organization definition."""
    # Check to see if there are any projects defined, remove them from this definition of the organization, and then
    # add them to the list of defined projects (setting the organization key in the project).
    defined_projects = definition.pop('projects', [])
    if not isinstance(defined_projects, list):
        defined_projects = [defined_projects]

    previous_definition = _defined_organizations.setdefault(definition['id'], {})
    _r_update(previous_definition, definition)

    # Store the defined projects
    for project in defined_projects:

        if not isinstance(project, dict):
            project = {'id': project}

        project['organization'] = definition['id']
        _handle_project_definition(project)


def _handle_project_definition(definition):
    """Process a project definition."""
    defined_customers = definition.pop('customer', [])
    if not isinstance(defined_customers, list):
        defined_customers = [defined_customers]

    previous_definition = _defined_projects.setdefault(definition['id'], {})
    _r_update(previous_definition, definition)

    # Store the defined customers
    for customer in defined_customers:

        if not isinstance(customer, dict):
            customer = {'id': customer}

        _handle_customer_definition(customer)


def _handle_customer_definition(definition):
    """Process customer definition"""
    # A project can define the customer as an identifier or as a dictionary.
    previous_definition = _defined_customers.setdefault(definition['id'], {})
    _r_update(previous_definition, definition)


def get_defined_projects():
    """Return all of the projects that have been defined by the log entries."""
    return _defined_projects
