# Make Note

This command is a helper for creating new note files in the log.  It will create a new note file for the current date
and time based on the input template that is specified.

## Configuration

### Configuration File Details

This command can be configured using the configuration details stored in `config.yaml`.  The settings are stored under
the `make_note` key value.

```yaml
make_note:

  # The default template value to use when generating the log file.  This value can be overridden by a command line 
  # argument if necessary. 
  default_template: timeline_base
  
  # The editor that will be used to open the file after it has been created on the file system.  Use the string {file} 
  # for placing the path to the file.  
  editor: xdg-open {file}
```

### Command Line Arguments

This command is configured using command line arguments.

- `-t <template_name>` or `--template <template_name>`

  > Specify the template name that will be used to create the new log file.
  >
  > Default: timeline_base
  
- `-T` or `--template-list`

  > List all of the templates that are available to be used to generate a new log file.  Specifying this argument will
  > cause the command to exit after the list has been printed out.
  
- `-d` or `--start-date`

  > Specify the time that the note will be logged for.  This populates the `time` metadata value in the front-matter. 
  > The format of the string must be in `'%Y-%m-%d %H:%M:%S'` format.  Note you will need to put this parameter in 
  > quotes because the value takes a space.  See 
  > [Pythons Strftime](https://docs.python.org/3/library/time.html#time.strftime) documentation for details on this
  > format.
  
- `-D` or `--end-date`

  > Specify the end time that the note will be logged for.  This populates the `end_time` metadata value in the 
  > front-matter. The format of the string must be in `'%Y-%m-%d %H:%M:%S'` format.  Note you will need to put this 
  > parameter in quotes because the value takes a space.  See 
  > [Pythons Strftime](https://docs.python.org/3/library/time.html#time.strftime) documentation for details on this
  > format.
  
- `-K` or `--kwarg-list`

  > List all of the keyword arguments that can be provided to this template.  Specifying this argument will cause the
  > command to exit after the list has been printed out.
  
- `-k` or `--kwarg`

  > Specify the key value definition to the template.  This should be in the format of KEY=VALUE.  Use quotes if 
  > necessary.

## Example Execution

```bash
autology make_note -t project_base
```