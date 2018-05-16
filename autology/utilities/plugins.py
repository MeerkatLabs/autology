"""Core plugins and helpers associated with the entry points."""

TEMPLATES_ENTRY_POINT = 'autology_templates'
COMMANDS_ENTRY_POINT = 'autology_commands'
REPORTS_ENTRY_POINT = 'autology_reports'
FILE_PROCESSOR_ENTRY_POINT = 'autology_file_processors'


def load_input_templates():
    """Load all of the input template definitions and ignore all of the results that are None."""
    from pkg_resources import iter_entry_points
    loaded_templates = {}

    for ep in iter_entry_points(group=TEMPLATES_ENTRY_POINT):
        template = ep.load()

        if template:
            loaded_templates[ep.name] = template

    return loaded_templates
