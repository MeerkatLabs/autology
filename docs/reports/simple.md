# Simple Report Generator

This is a report generator that can be used to collate the logs for an activity together.  It collects all of the 
logs together and generates an index and daily log page.

## Configuration

This plugin is configured by adding the following information to the `config.yaml` file.

```yaml
simple:

  # List of all of the activities that will be defined for the configuration details. 
  activities:
  
     # Identifier that will be used as the configuration detail.
     - id: activity_name
     
       # Human readable version of the name
       name: Activity Name
     
       # Long description of the report
       description: Long Description that can be used to describe the rest of the report.
````


## Log Inputs

This uses the same input formats and definitions as the [Timeline Reports](timeline.md).

## Generated Reports

This generates the same reports as the [Timeline Reports](timeline.md).