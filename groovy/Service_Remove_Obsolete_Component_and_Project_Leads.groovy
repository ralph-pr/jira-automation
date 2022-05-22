import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.issue.search.SearchProvider
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
import com.atlassian.jira.ComponentManager
import com.atlassian.mail.Email;
import com.atlassian.mail.server.MailServerManager;
import com.atlassian.mail.server.SMTPMailServer;
import groovy.time.*;
import com.atlassian.jira.user.util.UserUtil;
import java.net.InetAddress;
import java.sql.Connection
import groovy.sql.Sql
import org.ofbiz.core.entity.ConnectionFactory
import org.ofbiz.core.entity.DelegatorInterface
import com.onresolve.scriptrunner.runner.rest.common.CustomEndpointDelegate
import com.atlassian.crowd.embedded.impl.ImmutableUser
import com.atlassian.jira.bc.project.component.MutableProjectComponent
import com.atlassian.jira.bc.user.UserService
import com.atlassian.jira.user.DelegatingApplicationUser

//------------------------------------------------------------------------------------------
//************************************************************
// Include the shared_common_functions.groovy file and mix it into the context.
def tools = new GroovyScriptEngine( '.' ).with {
    loadScriptByName( '/apps/opt/jira/jirashared/scripts/shared_common_functions.groovy' )
}
this.metaClass.mixin tools

//************************************************************
// Read the configuration file. It should be specific to this environment.
def config = new XmlSlurper().parse(new File("/apps/opt/jira/jirashared/scripts/shared_common_functions_config.xml"))

//************************************************************
// Setup the devops db variables from the config file 'devops-datasource' section.
String devopsServer = config.'devops-datasource'.server
String devopsDB = config.'devops-datasource'.database
String devopsUser = config.'devops-datasource'.username
String devopsPassword = config.'devops-datasource'.password

//------------------------------------------------------------------------------------------
def delegator = (DelegatorInterface) ComponentAccessor.getComponent(DelegatorInterface)
String helperName = delegator.getGroupHelperName("default");

//888888888888888888888
UserUtil userUtil = ComponentAccessor.userUtil
def authenticationContextUser = userUtil.getUserByName("user3");
ComponentAccessor.getJiraAuthenticationContext().setLoggedInUser(authenticationContextUser);
//999999999999999999999

// *** PICK THE FILTER CAREFULLY – THE LOOP WILL PROCESS EVERY ISSUE SELECTED - !!!test in issue search 1st!!! ****
def sqlStmt = """
	EXEC Reports.list_obsolete_users;
"""

//setup the values needed to call the email function
//String to = "jira.support.team@example.com,ralph.pritchard@org.example.com";
String to = "ralph.pritchard@org.example.com";
String from = "OneJira Obsolete User Removal <OneJira.ObsoleteUserRemoval.Service@jira.baseurl.com>";
String subject = "(~environment~) JIRA Obsolete Owner Removal finished (~status~). ~usersProcessed~ users processed (~usersModified~ modified successfully, ~usersWithError~ error), ran ~minutesExecuted~."
String body = """\
The OneJira Obsolete User Removal Service has completed and reported that ~status~. It processed ~usersProcessed~ issues. 

It started at ~startTime~ and ended at ~endTime~. It ended because ~resolution~. 

This email was sent from the instance with base URL of ~baseurl~ and node's IP address of ~nodeid~. The JQL query used to drive the process was:
~sql~

The source for this service is a groovy script called 'Service_CMA?.groovy' from the 'jirascriptrunnerscripts' repo. Changes should be made there, reviewed and then deployed to the 'scripts' folder on the 'jirashared' folder.

~auditmsg~
""";

Date date = new Date();
String auditmsg = "";

//Logger log = log
def log = Logger.getLogger("com.example.jira.service.componentold")
log.setLevel(Level.DEBUG)
log.info "Starting @ " + date.format("MM/dd/yyyy HH:mm") + " (JCOMP001)";

//Final variable will be set accordingly by the code and will returned in the email on each run.
String status = "failed";
String resolution = "not yet determined. possible incomplete code?";
String minutesExecuted = "TBD";
String finalMsg = "";
//usersProcessed = the total # of issues processed.
def usersProcessed = 0;
def usersModified = 0;
def usersWithError = 0;
def baseurl = com.atlassian.jira.component.ComponentAccessor.getApplicationProperties().getString("jira.baseurl");
def nodeid = InetAddress.getLocalHost().getHostAddress();
log.info "nodeid=" + nodeid + " (JCOMP002)";


//*******************************************************
def getJiraEnvironment() {
	def config = new XmlSlurper().parse(new File("/apps/opt/atlassian/application-data/jira/dbconfig.xml"))
	String jiradb = config.'jdbc-datasource'.url

	def result = "UNKNOWN - see dbconfig.xml"
	if (jiradb.contains("onejira_DB_Prod_west") == true)
	{
		result = "PROD - WEST"
	}
	else if (jiradb.contains("onejira_preprod_east") == true)
	{
		result = "PreProd - East"
	}

	result
}

//*************************************************************
// Send an email
def finalHousekeeping(String to, String from, String subject, String body, Date dtStart, String status, String resolution, String usersProcessed, String usersModified, String usersWithError, String minutesExecuted, String baseurl, String nodeid, String sql, String auditmsg) {
	Date dtEnd = new Date();
	TimeDuration duration = TimeCategory.minus(dtEnd, dtStart);
	log.info "The process ran ${duration}. (JCOMP002)";

	MailServerManager mailServerManager = ComponentAccessor.getMailServerManager();
	SMTPMailServer mailServer = mailServerManager.getDefaultSMTPMailServer();

	// If the mail server configuration is valid, send an email.
	if (mailServer) {
		Email email = new Email(to);
		email.setSubject(formatEmailString(subject, from, subject, body, dtStart, dtEnd, status, resolution, usersProcessed, usersModified, usersWithError, duration.toString(), baseurl, nodeid, sql, auditmsg));
		email.setFrom(from); // Set the FROM address
		//email.setBcc(bcc);
		email.setBody(formatEmailString(body, from, subject, body, dtStart, dtEnd, status, resolution, usersProcessed, usersModified, usersWithError, duration.toString(), baseurl, nodeid, sql, auditmsg));
		mailServer.send(email);
		log.debug("Email sent. (JCOMP003)");
	}
	else {
		//return "No SMTP mail server defined.";
		log.error "No SMTP mail server defined. (JCOMP901)";
	}
}

// Format the email strings
String formatEmailString(String input, String from, String subject, String body, Date dtStart, Date dtEnd, String status, String resolution, String usersProcessed, String usersModified, String usersWithError, String minutesExecuted, String baseurl, String nodeid, String sql, String auditmsg) {
	return input.replace("~startTime~", dtStart.format("MM/dd/yyyy HH:mm")).replace("~endTime~", dtEnd.format("MM/dd/yyyy HH:mm")).replace("~status~", status).replace("~resolution~", resolution).replace("~usersProcessed~", usersProcessed).replace("~usersModified~", usersModified).replace("~usersWithError~", usersWithError).replace("~minutesExecuted~", minutesExecuted).replace("~baseurl~", baseurl).replace("~nodeid~", nodeid).replace("~sql~", sql).replace("~environment~", getJiraEnvironment()).replace("~auditmsg~", auditmsg);
}


//*************************************************************
// *** Main process ***
//*************************************************************
//def searchProvider = ComponentAccessor.getComponent(SearchProvider);
//...this will not be issueManager - probably componentManager?
def issueManager = ComponentAccessor.getIssueManager();
def user = ComponentAccessor.getJiraAuthenticationContext().getLoggedInUser();
def authenticationContext = ComponentAccessor.getJiraAuthenticationContext();
def currentUser = authenticationContext.getLoggedInUser()
def userService = ComponentAccessor.getComponent(UserService.class)
def componentsLeadedBy
def userManager

//***********************************************
Connection conn = ConnectionFactory.getConnection(helperName);
Sql sql = new Sql(conn)
finalMsg += "Total issues to be processed: ?TBD?<br />"

//*************************************************************
log.info "Starting @ " + date.format("MM/dd/yyyy HH:mm") + " (JCOMP000)";
String json_msg = '{"status":"starting"}'
String jiraEnv = getJiraEnvironment("short")
def rc = insert_example_audit_log("Service_Remove_Obsolete_Component_and_Project_Leads.groovy", "start", jiraEnv, "START", json_msg, devopsServer, devopsDB, devopsUser, devopsPassword, log, Class.forName('org.postgresql.Driver').newInstance())

def list = sql.rows(sqlStmt) // sql call will give us a list of user, projectid, componentid needed to call our atomic function
for (item in list) {
	// change the assignee for this component
	usersProcessed = usersProcessed + 1;
	try {
		// get the project components where user leads
		componentsLeadedBy = ComponentAccessor.projectComponentManager.findComponentsByLead(item.user_name)
		userManager = ComponentAccessor.getUserManager();

		// Get the projects where user leads
		def applicationUser = userManager.getUserByName(item.user_name);
		def projectLeadedBy = ComponentAccessor.userUtil.getProjectsLeadBy(applicationUser);

		def projectManager = ComponentAccessor.getProjectManager();
		def projectComponentManager = ComponentAccessor.getProjectComponentManager();
		if (!componentsLeadedBy && !projectLeadedBy) {
			log.info "item.user_name " + item.user_name + " doesn't lead any component or project"
			auditmsg = auditmsg + "\r\n" + "item.user_name " + item.user_name + " doesn't lead any component or project"
		}
		else {
			log.info "Start processing for " + item.user_name
			auditmsg = auditmsg + "\r\n" + "Start processing for " + item.user_name
			//remove userName from project lead roles
			if (projectLeadedBy.size() > 0)
				for (project in projectLeadedBy) {
					log.info "processing project=" + project.name
					auditmsg = auditmsg + "\r\n" + "...processing project=" + project.name
					projectManager.updateProject(project, project.name, project.description, "", project.url, project.assigneeType);

					json_msg = '{"status":"remove_project_lead","user":"' + item.user_name + '","project":"' + project.name + '"}'
					rc = insert_example_audit_log("Service_Remove_Obsolete_Component_and_Project_Leads.groovy", "remove_project_lead", jiraEnv, "IN PROGRESS", json_msg, devopsServer, devopsDB, devopsUser, devopsPassword, log, Class.forName('org.postgresql.Driver').newInstance())
				}

			//remove userName from component lead roles
			if (componentsLeadedBy.size() > 0)
				for (component in componentsLeadedBy) {
					log.info "processing component=" + component.getName()
					auditmsg = auditmsg + "\r\n" + "...processing component=" + component.getName()
					MutableProjectComponent newComponent = MutableProjectComponent.copy(component)
					newComponent.setLead("")
					projectComponentManager.update(newComponent)

					json_msg = '{"status":"remove_project_lead","user":"' + item.user_name + '","component":"' + component.getName() + '"}'
					rc = insert_example_audit_log("Service_Remove_Obsolete_Component_and_Project_Leads.groovy", "remove_component_lead", jiraEnv, "IN PROGRESS", json_msg, devopsServer, devopsDB, devopsUser, devopsPassword, log, Class.forName('org.postgresql.Driver').newInstance())
				}
		}
		//ComponentAccessor.getIssueManager().deleteIssue(currentUser, issue, EventDispatchOption.ISSUE_DELETED, false);
		log.info "Item processesed ... user = " + item.user_name + ". (JCOMP200)";
		usersModified = usersModified + 1;

		//finalMsg += "<br />Issue deleted <b>" + issue.key + "</b>"

	} catch (all) {  // Groovy shortcut: we can omit the Exception class
		//finalMsg += "<br />ERROR on delete for issue.id=<b>" + issue.id + "</b>"
		log.error "Delete failed for component.id=" + item.user_name + ". (JCOMP902)";
		usersWithError = usersWithError + 1;
	}
}

status = "success";
resolution = "successful completion, all issues processed.";
//finalMsg += "<br />count <b>" + usersProcessed + "</b>"
log.info "usersProcessed=" + usersProcessed + ". usersModified=" + usersModified + ". usersWithError=" + usersWithError + " (JCOMP500)";
finalHousekeeping(to, from, subject, body, date, status, resolution, usersProcessed.toString(), usersModified.toString(), usersWithError.toString(), minutesExecuted, baseurl, nodeid, sqlStmt, auditmsg);

//String json_msg = '{"status":"' + status + '","started":"' + started + '","finished":"' + finished + '","numOfDays":"' + numOfDays + '","attempted":"' + countAttempted + '","deactivated":"' + countPass + '","failed":"' + countFail + '","failed_users":' + JsonOutput.toJson(failedUsers) + '}'
json_msg = '{"status":"pass"}'
rc = insert_example_audit_log("Service_Remove_Obsolete_Component_and_Project_Leads.groovy", "final", jiraEnv, "FINAL", json_msg, devopsServer, devopsDB, devopsUser, devopsPassword, log, Class.forName('org.postgresql.Driver').newInstance())

log.info "Finished @ " + date.format("MM/dd/yyyy HH:mm") + ". status=" + status + ". resolution=" + resolution + " (JCOMP501)";

//return finalMsg
 
