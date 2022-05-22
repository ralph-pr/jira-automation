import com.atlassian.jira.component.ComponentAccessor;
import com.atlassian.jira.project.DefaultProjectManager;
import com.atlassian.jira.project.Project;

def projectManager = ComponentAccessor.getProjectManager();
def project = projectManager.getProjectByCurrentKey("TOOLS");

return project.name;