from setuptools import find_packages, setup
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='autology',
    version='0.4.0',
    packages=find_packages(),
    url='https://github.com/MeerkatLabs/autology/',
    license='MIT',
    author='Robert Robinson',
    author_email='rerobins@meerkatlabs.org',
    description='File-based life log',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6, <4',
    classifiers=[
        'Environment :: Console',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Processing'
    ],
    install_requires=[
        'dict-recursive-update>=1.0.0,<2',
        'Jinja2>=2.9.6,<3',
        'Markdown>=2.6.9,<3',
        'munch>=2.2.0,<3',
        'Pypubsub>=4.0.0,<5',
        'python-frontmatter>=0.4.2,<0.5',
        'PyYAML>=3.12,<4',
        'requests>=2.18.4',
        'GitPython>=2.1.7<3',
        'pytz>=2017.3<2018',
        'tzlocal>=1.5.1<2',
        'semantic-version>=2.6.0<3',
        'gpxpy>=1.1.2<2',
    ],

    extras_require={
        'dev': ['pylint>=1.7.4'],
        'test': [],
    },

    entry_points={
        'console_scripts': ['autology=autology.commands.main:main'],

        # These are the reports that should be loaded
        'autology_reports': ['index_report=autology.reports.index:register_plugin',
                             'timeline_report=autology.reports.timeline:register_plugin',
                             'project_report=autology.reports.project:register_plugin',
                             'simple=autology.reports.simple:register_plugin',
                             'exercise=autology.reports.exercise.exercise:register_plugin',
                             ],

        # Commands that are defined as execution points.  These are methods that take an arg parser as it's only
        # argument.
        'autology_commands': ['generate=autology.commands.subcommands.generate:register_command',
                              'serve=autology.commands.subcommands.serve:register_command',
                              'init=autology.commands.subcommands.initialize:register_command',
                              'make_note=autology.commands.subcommands.make_note:register_command',
                              'export_log_template=autology.commands.subcommands.export_log_templates:register_command',
                              'dump_config=autology.commands.subcommands.dump_config:register_command',
                              'update=autology.commands.subcommands.update:register_command',
                              ],

        # These are instantiations of Template named tuples
        'autology_templates': ['timeline_base=autology.reports.timeline.template:timeline_base',
                               'project_base=autology.reports.project.template.project_base:project_base',
                               'project_yaml=autology.reports.project.template.project_yaml:project_yaml',
                               'gpx_data=autology.reports.exercise.template:gpx_data'
                               ],

        # File processors that are loaded in
        'autology_file_processors': ['markdown=autology.utilities.processors.markdown:register',
                                     'yaml=autology.utilities.processors.yaml:register']
    },

    project_urls={
        'Bug Reports': 'https://github.com/MeerkatLabs/autology/issues',
        'Source': 'https://github.com/MeerkatLabs/autology',
    },
)
