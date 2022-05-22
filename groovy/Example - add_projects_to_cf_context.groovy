import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.config.properties.APKeys
import com.atlassian.jira.issue.IssueFieldConstants
import com.atlassian.jira.project.Project
import com.atlassian.jira.issue.context.manager.JiraContextTreeManager
import com.atlassian.jira.issue.customfields.CustomFieldUtils
import com.atlassian.jira.issue.fields.CustomField
import com.atlassian.jira.issue.fields.config.FieldConfigScheme
import com.atlassian.jira.issue.fields.config.manager.FieldConfigSchemeManager
import com.atlassian.jira.issue.fields.config.manager.IssueTypeSchemeManager
import com.atlassian.jira.issue.fields.layout.field.FieldConfigurationScheme
import com.atlassian.jira.issue.customfields.CustomFieldUtils
import com.atlassian.jira.issue.fields.FieldManager
import com.atlassian.jira.user.ApplicationUser
import org.apache.log4j.Level
import org.apache.log4j.Logger
import com.atlassian.jira.project.Project;
import com.atlassian.jira.project.DefaultProjectManager;

Logger log = log
log.setLevel(Level.DEBUG)
log.debug "Start"

String finalMsg = "";

// GOAL: Given a std context name, find all fields with that context and add this project to that context if it is not already there.
def addProjectsToOrgContext(String cfName, Long fcsId, String listOfProjects){
    if (listOfProjects == "") {
        log.debug("listOfProjects for ${cfName} is empty. Bypassing this field."); 
        return;
    }
    
   
    def projectManager = ComponentAccessor.getProjectManager()
    def customFieldManager = ComponentAccessor.getCustomFieldManager()
    FieldManager fieldManager = ComponentAccessor.getFieldManager();
    def fieldConfigSchemeManager = ComponentAccessor.getComponent(FieldConfigSchemeManager.class)
    JiraContextTreeManager jiraContextTreeManager = new JiraContextTreeManager(projectManager, ComponentAccessor.getConstantsManager())
	
	def	fcs = fieldConfigSchemeManager.getFieldConfigScheme(fcsId);

	ArrayList<Long> projectList = new ArrayList<Long>()
	def projectKeys = listOfProjects.split(',');
	projectKeys.each {pkey ->
		projectList << projectManager.getProjectObjByKey(pkey).id;
	}
	
	List contexts = CustomFieldUtils.buildJiraIssueContexts(false,
														null,
														projectList as Long[],
														jiraContextTreeManager);
	log.debug(contexts)            
	log.debug ("Modifying cfConfigScheme: ${fcs.getName()}")
	fieldConfigSchemeManager.updateFieldConfigScheme(fcs, contexts, customFieldManager.getCustomFieldObjectByName(cfName))

	fieldManager.refresh(); 
	}
    
// given customfield.id, fieldconfigscheme.id and the list of project keys, add the projects to the context
addProjectsToOrgContext("Actual Fix Time", 16606L, "DELELP")
