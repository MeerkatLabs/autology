# Export Log Templates

Dump all of the log generation templates to a directory.  These files can then be used as templates for creating 
log files when the autology command is not available.  An example of this is when generating log files on a phone.  
The content of the exported files can be copied into the new log file.  

## Configuration

This command is configured through command line arguments.

- `-o <dir_name>` or `--output-dir <dir_name>`

  > Specify the output directory of the template files
  >
  > Default: templates/generation
  
## Example Execution

```bash
autology export_log_templates -o templates/logs
```

## TODO

Need to flesh out the point of this command better, which requires updating the android application in order to 
take advantage of the content that is generated by this command.