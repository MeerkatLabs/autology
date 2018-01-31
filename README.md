# Autology

Autology is a text file based life log.  Using the contents of markdown files (to include frontmatter) it will provide a 
collection of reports for later viewing.  It currently uses git as a backend for syncing between multiple clients.

## Contributing

Please report all software issues to [Bug tracker](https://github.com/MeerkatLabs/autology/issues).  Any issues 
associated with the templates that are provided by default should be reported to the 
[Autology Template Bug Tracker](https://github.com/MeerkatLabs/autology_templates/issues).

## Installation

It is recommended that you use this tool in a virtual environment associated with the directory that you'll be using to 
store all of the content.  

```bash
mkdir log; cd log
python3 -m venv env
source env/bin/activate

pip install autology
```

To create the log directory structure, execute:
 
```bash
autology init
```

This will retrieve the [template files](https://github.com/MeerkatLabs/autology_templates) from GitHub, and create a new
`config.yaml` file with the default values of all of the parameters that can be used.

## Configuration

### Git Storage

In order to use this log with git as the backend you will need to modify the `config.yaml` file and enable git support. 
The first time it is run, it will initialize a git environment (if necessary).  Configuring the git environment with a
remote and refspec will allow the make_note sub-command to push the changes to the backend of your choosing.

### Configuring Editor

By default, the editor used to modify the text files is `xdg-open`.  Depending on the editor that is currently set as the 
default, this may not work correctly.  For example, executing `gvim` will automatically return when the editor is 
opened instead of waiting for the user to save and close the file.  To get around this, you will need to set the value
of the editor to something more sane.  To continue the example of gvim, the setting is:

```yaml
make_note:
  editor: gvim -f {file} +2
``` 

You will need to provide the full command for the editor, including the `{file}` parameter.  The `-f` flag is 
responsible for executing the tool in the foreground.  `+2` moves the editor to the second line of the file (skipping 
the opening frontmatter tag).

## Execution

To generate a new note file, use the following command while the virtual environment is activated.

```bash
autology make_note
```

Once you have some notes, you can then use the `generate` sub-command to translate the log files into a HTML output. 

```bash
autology generate
```

To view the content that has been generated, you can use the `serve` sub-command to create a simple http server for 
viewing.  Note this server does not auto-generate the content on changes, and is incredibly slow.  As such, you should
not use it in production.
