import com.atlassian.jira.component.ComponentAccessor
import com.opensymphony.workflow.InvalidInputException
import com.atlassian.jira.bc.project.component.ProjectComponent
import com.atlassian.jira.issue.Issue
import com.atlassian.jira.user.ApplicationUser
import com.opensymphony.workflow.WorkflowContext

// log.warn("Start - " + issue.key)
log.warn("Start")
List<String> approvedGroups = ['SDLC_KUBE_NONPROD_HOVV_ADMIN','SDLC_KUBE_PROD_HOVV_ADMIN','SDLC_KUBE_NONPROD_GVJV_ADMIN','SDLC_KUBE_PROD_GVJV_ADMIN','SDLC_KUBE_NONPROD_D4KV_ADMIN','SDLC_KUBE_PROD_D4KV_ADMIN','SDLC_KUBE_NONPROD_D0MV_ADMIN','SDLC_KUBE_PROD_D0MV_ADMIN','SDLC_KUBE_NONPROD_HZDV_ADMIN','SDLC_KUBE_PROD_HZDV_ADMIN','SDLC_KUBE_NONPROD_C8KV_ADMIN','SDLC_KUBE_PROD_C8KV_ADMIN','SDLC_KUBE_NONPROD_IENV_ADMIN','SDLC_KUBE_PROD_IENV_ADMIN','SDLC_KUBE_NONPROD_GO0V_ADMIN','SDLC_KUBE_PROD_GO0V_ADMIN','SDLC_KUBE_NONPROD_GJ3V_ADMIN','SDLC_KUBE_PROD_GJ3V_ADMIN','SDLC_KUBE_NONPROD_I0UV_ADMIN','SDLC_KUBE_PROD_I0UV_ADMIN'] as String[]
log.warn("1")

// Manager
def cm = ComponentAccessor.getCommentManager()

def components = issue.getComponents() as List<ProjectComponent>

def component_is_eks = false

log.warn("2")
components.each {comp ->
    log.warn(comp.name)
	log.warn("3")
    if (comp.name.contains('EKS ')) {
		log.warn("4")
        component_is_eks = true 
    }
}
    
if (component_is_eks == true){
	log.warn("5")
	String currentUser = ((WorkflowContext) transientVars.get("context")).getCaller();
	log.warn(currentUser)
	def user_is_authorized = false
	approvedGroups.each {
		log.warn(it)
		if (ComponentAccessor.groupManager.isUserInGroup(currentUser, it) == true) {
			user_is_authorized = true
			break
		}
	}
	if (user_is_authorized == false) {
		log.warn "user is not a member of an acceptable AD group - issue will not be created."
		throw new InvalidInputException("Tickets for EKS can only be opened by organization EKS admins.")
	}
}

log.warn("End")
