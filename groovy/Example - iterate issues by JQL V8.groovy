import com.atlassian.jira.component.ComponentAccessor
//import com.atlassian.jira.issue.search.SearchProvider
import com.atlassian.jira.bc.issue.search.SearchService
import com.atlassian.jira.jql.parser.JqlQueryParser
import com.atlassian.jira.web.bean.PagerFilter
import com.atlassian.jira.user.ApplicationUser
import com.atlassian.jira.event.type.EventDispatchOption;
import com.atlassian.jira.issue.UpdateIssueRequest;
import java.sql.Timestamp
import com.atlassian.jira.security.JiraAuthenticationContext
import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.issue.CustomFieldManager
import com.atlassian.jira.issue.fields.CustomField
import com.atlassian.jira.issue.label.LabelManager
import com.atlassian.crowd.embedded.api.User
import com.atlassian.jira.issue.label.Label;
import com.atlassian.jira.issue.label.LabelParser;
import org.apache.log4j.Level
import org.apache.log4j.Logger
import com.atlassian.jira.bc.issue.search.SearchService;
import com.atlassian.mail.Email;
import com.atlassian.mail.server.MailServerManager;
import com.atlassian.mail.server.SMTPMailServer;
import groovy.time.*;
import com.atlassian.jira.user.util.UserUtil;
import java.net.InetAddress;

//888888888888888888888
UserUtil userUtil = ComponentAccessor.userUtil
def authenticationContextUser = userUtil.getUserByName("userid");
ComponentAccessor.getJiraAuthenticationContext().setLoggedInUser(authenticationContextUser);
//999999999999999999999

// *** PICK THE FILTER CAREFULLY – THE LOOP WILL PROCESS EVERY ISSUE SELECTED - !!!test in issue search 1st!!! ****
//String jqlSearch = "updated < DATEADD(-90, d, today()) AND updated < '2017-11-01' AND statusCategory = 3 AND project NOT IN (EIS, ITT) ORDER BY updated ASC"
String jqlSearch = "issuekey in (GCP-372)"
// edit this query to suit

Date date = new Date();

//Logger log = log
log.setLevel(Level.DEBUG)
log.debug "Starting @ " + date.format("MM/dd/yyyy HH:mm");

//Final variable will be set accordingly by the code and will returned in the email on each run.
String status = "failed";
String resolution = "not yet determined. possible incomplete code?";
String minutesExecuted = "TBD";
String finalMsg = "";
//issuesProcessed = the total # of issues processed.
def issuesProcessed = 0;
def issuesDeleted = 0;
def issuesWithError = 0;
def baseurl = com.atlassian.jira.component.ComponentAccessor.getApplicationProperties().getString("jira.baseurl");
def nodeid = InetAddress.getLocalHost().getHostAddress();
log.debug "nodeid=" + nodeid;

//*************************************************************
//*************************************************************
// *** Main process ***
//*************************************************************
//*************************************************************
//def searchProvider = ComponentAccessor.getComponent(SearchProvider);
def issueManager = ComponentAccessor.getIssueManager();
def user = ComponentAccessor.getJiraAuthenticationContext().getLoggedInUser();
def authenticationContext = ComponentAccessor.getJiraAuthenticationContext();
def currentUser = authenticationContext.getLoggedInUser()
def jqlQueryParser = ComponentAccessor.getComponent(JqlQueryParser)
def searchService = ComponentAccessor.getComponent(SearchService)
//def jqlSearch = "project=JSP and assignee=p6s and resolution is empty"
def query = jqlQueryParser.parseQuery(jqlSearch)
//note different order of parameters compared to searchprovider
def results = searchService.search(user,query, PagerFilter.getUnlimitedFilter())

//def results = searchProvider.search(query, user, PagerFilter.getUnlimitedFilter())
finalMsg += "Total issues to be processed: ${results.total}<br />"

//*************************************************************
//Establish the kill switch - time when this job will stop because peak hours are about to start.
log.debug "Starting @ " + date.format("MM/dd/yyyy HH:mm");

//cnt = # of issues processed until we need to check kill switch. We want to check on 1st pass so start at 100.
def cnt = 100;
//results.getIssues().each {documentIssue ->
for (documentIssue in results.getResults()) {
	//Every 100 issues, check to see if we should stop
	cnt = cnt + 1;

	// delete the issue
	issuesProcessed = issuesProcessed + 1;
	try {
	
		def issue = issueManager.getIssueObject(documentIssue.id)

		resolution = "successful completion, all issues processed.";
		//ComponentAccessor.getIssueManager().deleteIssue(currentUser, issue, EventDispatchOption.ISSUE_DELETED, false);
        log.debug(documentIssue.key)
		issuesDeleted = issuesDeleted + 1;
		
		//finalMsg += "<br />Issue deleted <b>" + documentIssue.key + "</b>"
		
	} catch (all) {  // Groovy shortcut: we can omit the Exception class
		//finalMsg += "<br />ERROR on delete for issue.id=<b>" + documentIssue.id + "</b>"
		log.error "Delete failed for issue.id=" + documentIssue.id;
		issuesWithError = issuesWithError + 1;
	}	
}

status = "success";
//finalMsg += "<br />count <b>" + issuesProcessed + "</b>"
log.debug "issuesProcessed=" + issuesProcessed + ". issuesDeleted=" + issuesDeleted + ". issuesWithError=" + issuesWithError;
log.debug "Finished @ " + date.format("MM/dd/yyyy HH:mm") + ". status=" + status + ". resolution=" + resolution;

//return finalMsg
