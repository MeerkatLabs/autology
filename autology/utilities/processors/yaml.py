"""
Defines the yaml file processor.  YAML files must have a document at the beginning that provides metadata about the
file that is being injected.  For example it must contain the metadata showing activities, times and the information
about the version information.
"""
import frontmatter
import yaml

from autology.utilities.processors.markdown import write_file
from autology.utilities import log_file

MIME_TYPE = 'application/x-yaml'


def load_file(path):
    """
    Translate the file pointed to by path into a dictionary.
    :param path:
    :return:
    """
    with path.open() as loaded_file:
        post = frontmatter.load(loaded_file)

    post.metadata = log_file.process_datetimes(post.metadata)

    return log_file.Entry(post[log_file.MetaKeys.TIME], MIME_TYPE, post.metadata, post.content, path,
                          [content for content in yaml.load_all(post.content) if content])


def register():
    """Register the YAML mimetype and the YAML file processor."""
    log_file.register_mime_type('.yaml', MIME_TYPE)
    log_file.register_file_processor(MIME_TYPE, load_file, write_file)
