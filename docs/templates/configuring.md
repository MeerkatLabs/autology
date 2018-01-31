# Configuring Templates

## Configuration File

The settings associated with a template implementation are stored in the `template.yaml` file.  This file should be at
the root of the template definition.  It contains a list of parameters that will define how the template is installed 
into the root log directory as well as how the templates should be treated by the publishing engine.

### Configuration Details

- `name`

  > This provides a human readable name for the template
  
- `static_files`

  > This provides a list of file globs (glob patterns specify sets of file names with wildcard characters) that are used to copy static (non-template) files into the final output 
  > directory.  The most common use of this is for any javascript or css files that must be provided as part of the 
  > output.
  
