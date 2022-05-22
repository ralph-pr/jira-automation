# jira-automation
Automation related to Jira using python and Groovy.

## Groovy
Groovy scripts include examples of various customizations in Jira that can be accomplished using the [ScriptRunner](https://scriptrunner.adaptavist.com/latest/index.html) app as well as certain admin troubleshooting scripts that can be run directly from the ScriptRunner Console within the Jira admin section. ScriptRunner is a vast and powerfule with many features. Each feature is detailed [here](https://docs.adaptavist.com/sr4js/6.51.0/features) and each feature contains examples and snippets within the documentation.

## Python
Python files provide examples of Atlassian admin tasks that are automated externally and interact with Jira/Confluence via their native APIs as well as many other platform and infrastructure APIs such as AWS, NewRelic, Splunk, CloudHealth, Gitlab and Jenkins. These scripts are used to *automate the toil* of the admin team. These include Lambda functions triggered by events such as a new user login to nightly processes to manual incident mitigation tasks.
