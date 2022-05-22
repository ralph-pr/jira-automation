import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.event.type.EventDispatchOption
import com.atlassian.jira.issue.Issue;
import com.atlassian.jira.issue.IssueInputParameters
import com.atlassian.jira.issue.MutableIssue;
import com.atlassian.jira.user.ApplicationUser;
import com.atlassian.jira.issue.UpdateIssueRequest;
import com.atlassian.jira.bc.issue.IssueService.UpdateValidationResult
import com.atlassian.jira.bc.issue.IssueService.IssueResult
import com.atlassian.jira.bc.issue.IssueService
import com.atlassian.jira.bc.issue.IssueService.TransitionValidationResult
log.info "start"

def issueManager = ComponentAccessor.getIssueManager();
//def user = ComponentAccessor.getJiraAuthenticationContext().getLoggedInUser();
//def issue = issueManager.getIssueObject("EXSRE-262")

MutableIssue issue = issueManager.getIssueObject("EXSRE-262")
//MutableIssue issue = issueManager.getIssueObject("DPEAGILES-558")
ApplicationUser user =  ComponentAccessor.getJiraAuthenticationContext().getLoggedInUser();
IssueService issueService = ComponentAccessor.getIssueService()

log.info issue.getOriginalEstimate()
log.info issue.getTimeSpent()

log.info "...calc..."
def newEstimate = (Long)0	//issue.getTimeSpent() / (Long)60
log.info newEstimate
log.info "...calc..."

IssueInputParameters inputParameters = issueService.newIssueInputParameters()
inputParameters.setOriginalEstimate((Long)newEstimate)
inputParameters.setRemainingEstimate((Long)newEstimate)
//inputParameters.setOriginalAndRemainingEstimate((Long)0, (Long)0)
IssueService.UpdateValidationResult validationResult = issueService.validateUpdate(user,issue.id,inputParameters)
issueService.update(user, validationResult)
log.info issue.key

log.info "done"


