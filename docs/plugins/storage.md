# Git Storage Plugin

This plugin is responsible for wrapping the git repository that the content files will be stored in.  Currently, this 
is the only storage plugin that is available.

## Configuration

This plugin is configured through the contents of `config.yaml` under the `git` key.

```yaml
git:
  # By default this plugin is disabled.
  enabled: false
  
  # Remote that will be used to push the changes when logs are made or modified
  remote: origin
  
  # Reference that will be used when pushing and pulling changes to the remote repository
  refspec: master
```
