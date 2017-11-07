from setuptools import find_packages, setup

setup(
    name='autology',
    version='0.1.0.dev',
    packages=find_packages(),
    url='',
    license='MIT',
    author='Robert Robinson',
    author_email='rerobins@meerkatlabs.org',
    description='File-based life log',
    python_requires='>=3.6, <4',
    classifiers=[
        'Environment :: Console',
        'Development Status :: 1 - Planning',
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
    ],

    extras_require={
        'dev': ['pylint>=1.7.4'],
        'test': [],
    },

    entry_points={
        'console_scripts': ['autology=autology.commands.main:main'],
        'autology_plugins': ['index_report=autology.reports.index:register_plugin',
                             'timeline_report=autology.reports.timeline:register_plugin',
                             'project_report=autology.reports.project:register_plugin',
                             'publishing=autology.publishing:register_plugin'],
        'autology_commands': ['generate=autology.commands.subcommands.generate:register_command']
    }
)
