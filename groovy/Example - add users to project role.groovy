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
import org.apache.log4j.Level
import org.apache.log4j.Logger
import com.atlassian.jira.util.SimpleErrorCollection
import com.atlassian.jira.project.ProjectManager;
import com.atlassian.jira.security.roles.ProjectRole;
import com.atlassian.jira.security.roles.ProjectRoleActors;
import com.atlassian.jira.security.roles.ProjectRoleManager;
import com.atlassian.jira.bc.projectroles.ProjectRoleService;

Logger log = log
log.setLevel(Level.DEBUG)

log.debug "Start"

String finalMsg = "";

// Define a function to do the work
def removeAndAdd(String projectKey, String userName, String roleName){
	//String actorType = "atlassian-user-role-actor"; 
	String actorType = "atlassian-group-role-actor"; 
	def simpleErrorCollection = new SimpleErrorCollection(); 
	ComponentAccessor.getProjectManager().getProjectByCurrentKeyIgnoreCase(projectKey); 
	Project project = ComponentAccessor.getProjectManager().getProjectByCurrentKeyIgnoreCase(projectKey); 

	//add the new groups
	ProjectRoleManager projectRoleManager = ComponentAccessor.getComponentOfType(ProjectRoleManager.class); 
	ProjectRole projectRole = projectRoleManager.getProjectRole(roleName); 
	ProjectRoleService projectRoleService = ComponentAccessor.getComponentOfType(ProjectRoleService.class); 
	ArrayList<String> listAdd = new ArrayList<String>([userName]); 
	projectRoleService.addActorsToProjectRole(listAdd, projectRole, project, actorType, simpleErrorCollection);
}

finalMsg += removeAndAdd("ONEAPI", "jrsmith2", "Developers");


log.debug "End"
