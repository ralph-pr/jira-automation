import org.apache.log4j.Level
import org.apache.log4j.Logger
import java.sql.Connection
import groovy.sql.Sql
import java.sql.Driver
import org.ofbiz.core.entity.ConnectionFactory
import org.ofbiz.core.entity.DelegatorInterface
import com.onresolve.scriptrunner.runner.rest.common.CustomEndpointDelegate
import groovy.json.JsonBuilder
import groovy.transform.BaseScript
import javax.ws.rs.core.MultivaluedMap
import javax.ws.rs.core.Response
import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.user.util.UserManager
import com.atlassian.jira.user.util.UserUtil
import com.atlassian.jira.user.ApplicationUser

import com.atlassian.mail.Email
import com.atlassian.mail.server.MailServerManager
import com.atlassian.mail.server.SMTPMailServer
import groovy.time.*
import com.atlassian.jira.user.util.UserUtil
import java.net.InetAddress
import groovy.xml.*

//************************************************************
// Initial housekeeping - setup logging
Date date = new Date()
def log = Logger.getLogger("com.example.jira.service.governance")
log.setLevel(Level.DEBUG)
String started = date.format("MM/dd/yyyy HH:mm")
log.info "Starting @ " + started + " (GVNEZ000)"

//************************************************************
// Include the shared_common_functions.groovy file and mix it into the context.
def tools = new GroovyScriptEngine( '.' ).with {
    loadScriptByName( '/apps/opt/jira/jirashared/scripts/shared_common_functions.groovy' )
}
this.metaClass.mixin tools

//************************************************************
// Read the configuration file. It should be specific to this environment.
def config = new XmlSlurper().parse(new File("/apps/opt/jira/jirashared/scripts/shared_common_functions_config.xml"))
//// Debug only - echo back some config values.
//log.debug config.name
//log.debug config.'eazybi-datasource'.server
//log.debug config.'eazybi-datasource'.database
//log.debug config.'eazybi-datasource'.'driver-class'
//log.debug config.'eazybi-datasource'.username
//log.debug config.'eazybi-datasource'.password

//************************************************************
// Setup the eazybi db variables from the config file 'eazybi-datasource' section.
String eazybiServer = config.'eazybi-datasource'.server
String eazybiDB = config.'eazybi-datasource'.database
String eazybiUser = config.'eazybi-datasource'.username
String eazybiPassword = config.'eazybi-datasource'.password
def sqlStmt = """SELECT update_eazybi_source_applications_import_frequency();"""

//************************************************************
// Setup the devops db variables from the config file 'devops-datasource' section.
String devopsServer = config.'devops-datasource'.server
String devopsDB = config.'devops-datasource'.database
String devopsUser = config.'devops-datasource'.username
String devopsPassword = config.'devops-datasource'.password

//************************************************************
// Setup the values needed to call the email function
String to = "agile.services@org.example.com"
//String to = "ralph.pritchard@org.example.com"
String from = "OneJira Governance Automation <OneJira.Governance.Automation@jira.baseurl.com>"
String subject = "(~environment~) Governance Automation for eazyBI import frequency is complete. Status = ~status~."
String body = """\
The Groovy service for eazyBI import frequency governance has finished with a status of ~status~.

It started at ~startTime~ and ended at ~endTime~.

This email was sent from the instance with base URL of ~baseurl~ and node's IP address of ~nodeid~.

The source for this service is a groovy script called 'Service_GovernEazybiImportFrequency.groovy' from the 'jirascriptrunnerscripts' repo. Changes should be made there, reviewed and then deployed to the 'scripts' folder on the 'jirashared' folder.

The SQL statement that controls this process was: 
~sql~
"""

//*************************************************************
// Send an email
def finalHousekeeping(String to, String from, String subject, String body, Date dtStart, String sql, String baseurl, String nodeid, String environment, String status) {
	Date dtEnd = new Date();
	TimeDuration duration = TimeCategory.minus(dtEnd, dtStart)
    log.info "The process ran ${duration}. (GVNEZ006)"
    
	MailServerManager mailServerManager = ComponentAccessor.getMailServerManager()
	SMTPMailServer mailServer = mailServerManager.getDefaultSMTPMailServer()
	// If the mail server configuration is valid, send an email.
	if (mailServer) {
		def passed = false
		def keeptrying = true
		def trycount = 0
		def maxtries = 5
		for (trycount = 0; trycount < maxtries; trycount++) {
			try {
				Email email = new Email(to)
				email.setSubject(formatEmailString(subject, from, subject, body, dtStart, dtEnd, duration.toString(), sql, baseurl, nodeid, status, environment))
				email.setFrom(from) // Set the FROM address
				//email.setBcc(bcc)
				email.setBody(formatEmailString(body, from, subject, body, dtStart, dtEnd, duration.toString(), sql, baseurl, nodeid, status, environment))
				mailServer.send(email)
				log.info("Email sent. (GVNEZ007)")
				break
			} catch (all) {  // Groovy shortcut: we can omit the Exception class
				log.error "ERROR - email failed to send. trycount=" + trycount + " (GVNEZ902)" 
			}
        }
	}
	else {
		//return "No SMTP mail server defined."
		log.error "No SMTP mail server defined. (GVNEZ901)"
	}
}

//************************************************************
// Format the email strings
String formatEmailString(String input, String from, String subject, String body, Date dtStart, Date dtEnd, String minutesExecuted, String sql, String baseurl, String nodeid, String status, String environment) {
	return input.replace("~startTime~", dtStart.format("MM/dd/yyyy HH:mm")).replace("~endTime~", dtEnd.format("MM/dd/yyyy HH:mm")).replace("~minutesExecuted~", minutesExecuted).replace("~baseurl~", baseurl).replace("~nodeid~", nodeid).replace("~sql~", sql).replace("~status~", status).replace("~environment~", environment)
}

//************************************************************
//CallSql - makes a PostgreSQL call to a function. That function will enforce our rule on all eazyBI data sources.
def callSql(def sqlStmt, def server, def database, def sqluser, def sqlpassword) {
	try {
		def url = 'jdbc:postgresql://' + server + '/' + database
		def driver = Class.forName('org.postgresql.Driver').newInstance() as Driver 

		def props = new Properties()
		props.setProperty("user", sqluser) 
		props.setProperty("password", sqlpassword)

		def conn = driver.connect(url, props) 
		def sql = new Sql(conn)

		sql.eachRow(sqlStmt) { sqlrow ->
			log.info "The SQL statement was successfully processed (GVNEZ200)"
			//Long linktype = sqlrow.linktype
			//createThisIssueLink(sqlrow.sourcekey, sqlrow.destinationkey, linktype, sqlrow.sequence, issueManager, issueLinkManager, user, log)
		}

		// Finish processing - close SQL and log results.
		sql.close()
	} catch (Exception ex) {  // Groovy shortcut: we can omit the Exception class
		//finalMsg += "<br />ERROR on delete for issue.id=<b>" + documentIssue.id + "</b>"
		log.error "ERROR! " + ex.getMessage() + " (GVNEZ900)"
        return "failure"
	}
    
    return "success"
}

//************************************************************
//*** MAIN PROCESS
//************************************************************
def baseurl = com.atlassian.jira.component.ComponentAccessor.getApplicationProperties().getString("jira.baseurl")
def nodeid = InetAddress.getLocalHost().getHostAddress()
log.info "nodeid=" + nodeid + " (GVNEZ05)"

def status = callSql(sqlStmt, eazybiServer, eazybiDB, eazybiUser, eazybiPassword)

// Final housekeeping - send an email and log the run.
String finished = date.format("MM/dd/yyyy HH:mm")
String jiraEnv = getJiraEnvironment("short")
log.info "Finished @ " + date.format("MM/dd/yyyy HH:mm") + ". status=" + status + ". (GVNEZ500)"
String json_msg = '{"status":"' + status + '","started":"' + started + '","finished":"' + finished + '"}'
def rc = insert_example_audit_log("Service_GovernEazybiImportFrequency.groovy", "final", jiraEnv, "FINAL", json_msg, devopsServer, devopsDB, devopsUser, devopsPassword, log, Class.forName('org.postgresql.Driver').newInstance())
finalHousekeeping(to, from, subject, body, date, sqlStmt, baseurl, nodeid, jiraEnv, status)
