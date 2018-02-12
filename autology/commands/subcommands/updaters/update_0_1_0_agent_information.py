"""
Log file updater that will translate all of the time and end_time values into timezone aware data values.
"""
import frontmatter
from autology.utilities.log_file import MetaKeys
FILE_VERSION_INFORMATION = '0.1.0'


DEFAULT_AGENT_DEFINTION = {
    MetaKeys.Agent.NAME: 'UNDEFINED',
    MetaKeys.Agent.VERSION: '0.0.0',
    MetaKeys.Agent.FILE_VERSION: FILE_VERSION_INFORMATION
}


def add_agent_information(search_path, file_component):
    """
    Will check to see if the file needs to be processed before updating the values.  Will then populate the new agent
    information with what should be used in the future.
    :param search_path:
    :param file_component:
    :return:
    """
    if file_component.suffix != '.md':
        return

    entry = frontmatter.load(file_component)

    write_file = False

    # Check to see if the agent information has been defined in the log file
    if MetaKeys.AGENT_DEFINITION not in entry.metadata:
        entry.metadata[MetaKeys.AGENT_DEFINITION] = dict(DEFAULT_AGENT_DEFINTION)
        write_file = True
    else:
        agent_definition = entry.metadata[MetaKeys.AGENT_DEFINITION]
        try:
            for key in (MetaKeys.Agent.NAME, MetaKeys.Agent.VERSION, MetaKeys.Agent.FILE_VERSION):
                write_file = write_file or _check_set_value(agent_definition, key)

        except (AttributeError, TypeError):
            entry.metadata[MetaKeys.AGENT_DEFINITION] = DEFAULT_AGENT_DEFINTION
            write_file = True

    if write_file:
        with open(file_component, "w") as output_file:
            output_file.write(frontmatter.dumps(entry))


def _check_set_value(destination, key):
    if key not in destination:
        destination[key] = DEFAULT_AGENT_DEFINTION.get(key)
        return True

    return False
