"""
Defines the markdown file processor.  Registers the mimetype that will be used to fetch the time values from the
markdown file, as well as a means of translating the data into a data definition.

This will be registered in the generator as part of the report initialization plugin.
"""
import frontmatter

from autology.utilities import log_file

MIME_TYPE = 'text/markdown'


def load_file(path):
    """
    Translate the file pointed to by path into a front matter post.  It will also go through all of the timestamps that
    are stored in the front matter and make them timezone aware.
    :param path:
    :return:
    """
    with path.open() as loaded_file:
        entry = frontmatter.load(loaded_file)

    log_file.process_datetimes(entry.metadata)

    return log_file.Entry(entry.metadata[log_file.MetaKeys.TIME], MIME_TYPE, entry.metadata, entry.content, path,
                          entry.content)


def write_file(entry):
    """Writes the entry out to the path provided, or the file path pointed to by the entry object."""

    # If both of these are false, then need to generate a new file name for this.  Don't update the entry because
    # content hasn't been defined for it yet.
    if entry.file is None:
        file_path = log_file.generate_file_name(entry)
        overwrite = False
    else:
        file_path = entry.file
        overwrite = True

    # Write out the file to the entry's file
    post = frontmatter.Post(entry.content, **entry.metadata)

    # If the entry already has a file, then we are going to overwrite the content
    log_directory, file_path = log_file.insert_file(entry.date, file_path, frontmatter.dumps(post), overwrite)

    # Update the entry with the new file path
    entry = log_file.rebuild_entry(entry, file=log_directory / file_path)

    return entry


def register():
    """Register the markdown file processor."""
    log_file.register_mime_type('.md', MIME_TYPE)
    log_file.register_mime_type('.markdown', MIME_TYPE)
    log_file.register_file_processor(MIME_TYPE, load_file, write_file)
