# Project Report

This plugin will provide a collection of all of the projects that have been registered with the 
application.  This is done through front matter details in each of the markdown files or via YAML
definition files that are also included in the log directories.

Each post can then be tagged with a report identifier that will be used to collate logs with the
projects that they are about, as well as track the amount of time that is spent on each of the 
projects.

## Data Structures

### Organization

An organization is a means of grouping multiple projects together.  For example, you can store all of the open source
projects that you are doing development on in an `open_source` organization, and then all of your company projects 
together under an organization representing your company or company structure.

### Project

A project is a collection of logs and posts that are associated with a time frame or goal.  A project can provide 
information about hours allowed, time frame for when the project is active, and team information.

### Customer

A customer provides additional details about an individual project.  For example it provides details about the point of
contact for a specific project.  

## Configuration

N/A

## Log Inputs

This plugin will process data log files that it receives.  It splits the incoming files into two types based on the 
filename extension that is provided.  

### Markdown Front Matter Content

The processor will split the markdown files into the front matter meta data and the content.  It hands the content of 
the front matter to the YAML Data parser to determine if there are new projects, customers, or organizations defined. 
Please see the next section below for documentation on that functionality.

In addition to looking for new definitions, it is also responsible for determining the time tracking values for projects
that are defined elsewhere.  In this case it will look to see if the `mkl-project` key exists and will then use that 
value to associate worked time with that project.  It will also tag the rest of the post with that project so that it 
can be displayed in the logs associated with that project file.

It uses the `time` and `end_time` values for determining the length of time that a project was worked on.  See 
documentation on the [Timeline Report](timeline.md) for more details on the formats of these values. 

```yaml
time: 15:00:00
end_time: 15:30:00
mkl-project: project_id
```

### YAML Data Structures

The report processor uses in-stream YAML files for adding new data into the database.  This can be used to inject new
project, organization, or customer definitions into the data stream.  

#### Organization Data Model

```yaml
mkl-organization:
  
  # unique identifier across all organizations, this is used to link projects to the organizations that are responsible
  # for them.  OPTIONAL
  id: some_org_id
  
  # Human readable name of the organization. OPTIONAL
  name: Some Organization
  
  # List of Points of Contact for the organization. OPTIONAL
  poc:
  
  - name: Some Person
    email: some.person@example.com
   
  # List of all projects that are associated with this organization.  This data structure is populated by the report
  # generator, so adding projects to this list may cause duplicates to be registered, if they are defined in other
  # locations as well.  See Project Data Model for details on the contents of this definition. 
  projects:
    id: s_pi
    name: SPI
    # .. Other details
   
    
```

#### Project Data Model

```yaml
mkl-project: 

  # unique identifier across all projects.  This is used to register time worked for each project. REQUIRED
  id: some_project_id
  
  # human readable name for the project. REQUIRED
  name: Some Project
  
  # Identifier used to reference an organization that is responsible for this project. OPTIONAL
  organization: some_org_id
  
  # Identifier used to reference customer information for this project. OPTIONAL Can also be a 
  # customer definition, see Customer Data Model.
  customer: some_customer_id 
  
  # NOTE:
  # The following fields are maintained by the reporting framework and should not be used for storing user-defined data
  
  # Duration that the project has been worked on.
  duration: <date time delta object>
  
  # List of all of the logs that are associated with working on the project.  The keys in this dictionary are a 
  # python datetime object, with the value being a frontmatter post object.
  log: []
  
  # NOTE:
  # The following fields are planned for future use, but not yet implemented or used by the report.  They are here
  # strictly for planning purposes.
  
  # Date that the project was started.  OPTIONAL
  start_date: 2017-01-01
  
  # Date that the project is scheduled or was completed. OPTIONAL
  end_date: 2017-12-31
  
  # Amount number of hours that is allowed for work on this project. OPTIONAL
  hours_allowed: 40:00:00
  
  # Repository information for the project
  repositories:
  
    - name: repo name
      uri: repo uri
      
  issue_tracker: <tracker uri>
  continuous_integration: <ci uri>
```

#### Customer Data Model

```yaml
mkl-customer:

  # unique identifier across all customers. REQUIRED
  id: some_customer_id
  
  # human readable name of the customer.  REQUIRED
  name: Some Customer
  
  # Points of contact for the customer. OPTIONAL
  poc:
    - name: Some Customer Contact
      email: some.customer@exmaple.com
```

## Generated Reports

### Main Report

Lists all of the organizations and the associated projects.

#### Template Path Definition

- project
    - index

#### Publishing Context Objects

- `projects` 

  > List containing all of the projects that have been defined inside the report.
  
- `organizations`

  > List of all the organizations that have been defined inside the report.
  
- `customers`

  > List of all the customers that have been defined inside the report.
  
- `orphaned_projects`

  > List of all the projects that have not been assigned to an organization.  This value will 
  > only be populated if there are any projects that match this criteria.

### Individual Project Report

Lists all of the logs associated with the report as well as the current state of the project. This
is done by collecting all of the values stored in the front matter.  It can also list the customers
of each project and the POC information.

#### Template Path Definition

- project
    - project

#### Publishing Context Objects

- `project`

  > Project object for which the individual report is about
  
