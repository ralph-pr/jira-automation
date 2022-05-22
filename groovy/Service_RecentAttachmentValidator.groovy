import org.apache.log4j.Level
import org.apache.log4j.Logger
import java.sql.Connection
import groovy.sql.Sql
import org.ofbiz.core.entity.ConnectionFactory
import org.ofbiz.core.entity.DelegatorInterface
import com.onresolve.scriptrunner.runner.rest.common.CustomEndpointDelegate
import groovy.json.JsonBuilder
import groovy.transform.BaseScript
import javax.ws.rs.core.MultivaluedMap
import javax.ws.rs.core.Response
import com.atlassian.jira.component.ComponentAccessor;
import com.atlassian.jira.user.util.UserManager
import com.atlassian.jira.user.util.UserUtil
import com.atlassian.jira.user.ApplicationUser;

import com.atlassian.mail.Email;
import com.atlassian.mail.server.MailServerManager;
import com.atlassian.mail.server.SMTPMailServer;
import groovy.time.*;
import com.atlassian.jira.user.util.UserUtil;
import java.net.InetAddress;
import groovy.xml.*

//************************************************************
// Initial housekeeping - setup logging
Date date = new Date()
def log = Logger.getLogger("com.example.jira.service.fileattachments")
log.setLevel(Level.DEBUG)
String started = date.format("MM/dd/yyyy HH:mm")
log.info "Starting @ " + started + " (FSREC01)"

String fileToCheck = "/apps/opt/jira/jirashared/export/missingfile_current.log";
File file = new File(fileToCheck)
def filetext = '--- Staring process / report ---' + "\n";

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

//************************************************************
//setup the values needed to call the email function
//String to = "ralph.pritchard@org.example.com";
String to = "agile.services@org.example.com,some.user@example.com";
String from = "OneJira Recent Attachment Validator <OneJira.RecentAttachmentValidator@jira.baseurl.com>";
String subject = "(~environment~) File Attachment Status = ~status~. ~errorCount~ attachments are missing from EFS, ~processed~ attachments processed, ran ~minutesExecuted~."
String body = """\
The File Attachment DB-to-EFS check for recent attachments has completed and reported ~errorCount~ errors.  ~processed~ attachments were audited.  The script log is shown below:
~errors~

It started at ~startTime~ and ended at ~endTime~.

This email was sent from the instance with base URL of ~baseurl~ and node's IP address of ~nodeid~.

The source for this service is a groovy script called 'Service_RecentAttachmentValidator.groovy' from the 'jirascriptrunnerscripts' repo. Changes should be made there, reviewed and then deployed to the 'scripts' folder on the 'jirashared' folder.

The SQL statement that controls this process was: 
~sql~
""";

def baseurl = com.atlassian.jira.component.ComponentAccessor.getApplicationProperties().getString("jira.baseurl");
def nodeid = InetAddress.getLocalHost().getHostAddress();
log.info "nodeid=" + nodeid + " (FSREC05)";

//*************************************************************
// Send an email
def finalHousekeeping(String to, String from, String subject, String body, Date dtStart, String errorCount, String minutesExecuted, String sql, String baseurl, String nodeid, String errors, String processed, String environment) {
	Date dtEnd = new Date();
	TimeDuration duration = TimeCategory.minus(dtEnd, dtStart);
    log.info "The process ran ${duration}. (FSREC06)";
    
    String status = "Passed"
    if (errorCount.toInteger() > 0) {
        status = "FAILED - ALERT!!!"
    }
	
	MailServerManager mailServerManager = ComponentAccessor.getMailServerManager();
	SMTPMailServer mailServer = mailServerManager.getDefaultSMTPMailServer();
	// If the mail server configuration is valid, send an email.
	if (mailServer) {
		def passed = false
		def keeptrying = true
		def trycount = 0
		def maxtries = 5
		for (trycount = 0; trycount < maxtries; trycount++) {
			try {
				Email email = new Email(to); 
				email.setSubject(formatEmailString(subject, from, subject, body, dtStart, dtEnd, errorCount, duration.toString(), sql, baseurl, nodeid, errors, status, processed, environment));
				email.setFrom(from); // Set the FROM address
				//email.setBcc(bcc);
				email.setBody(formatEmailString(body, from, subject, body, dtStart, dtEnd, errorCount, duration.toString(), sql, baseurl, nodeid, errors, status, processed, environment));
				mailServer.send(email);
				log.info("Email sent. (FSREC07)");
				break
			} catch (all) {  // Groovy shortcut: we can omit the Exception class
				//finalMsg += "<br />ERROR on delete for issue.id=<b>" + documentIssue.id + "</b>"
				log.error "ERROR - email failed to send. trycount=" + trycount + " (FSREC92)" 
			}
        }
	}
	else {
		//return "No SMTP mail server defined.";
		log.error "No SMTP mail server defined. (FSREC90)";
	}
}

//************************************************************
// Format the email strings
String formatEmailString(String input, String from, String subject, String body, Date dtStart, Date dtEnd, String errorCount, String minutesExecuted, String sql, String baseurl, String nodeid, String errors, String status, String processed, String environment) {
	//return input.replace("~startTime~", dtStart.format("MM/dd/yyyy HH:mm")).replace("~endTime~", dtEnd.format("MM/dd/yyyy HH:mm")).replace("~killTime~", dtKill.format("MM/dd/yyyy HH:mm")).replace("~status~", status).replace("~resolution~", resolution).replace("~issuesProcessed~", issuesProcessed).replace("~issuesDeleted~", issuesDeleted).replace("~issuesWithError~", issuesWithError).replace("~minutesExecuted~", minutesExecuted).replace("~baseurl~", baseurl).replace("~nodeid~", nodeid).replace("~jql~", jql);
	return input.replace("~startTime~", dtStart.format("MM/dd/yyyy HH:mm")).replace("~endTime~", dtEnd.format("MM/dd/yyyy HH:mm")).replace("~errorCount~", errorCount).replace("~minutesExecuted~", minutesExecuted).replace("~baseurl~", baseurl).replace("~nodeid~", nodeid).replace("~sql~", sql).replace("~errors~", errors).replace("~status~", status).replace("~processed~", processed).replace("~environment~", environment)
}

//*************************************************************
def checkThisFile(String fileToCheck, String filename, def created, String displayname, String pkey, def issuenum) {
    def msg = ""
	File file = new File(fileToCheck)
	if (! (file.exists() && file.isFile())) {
        File filealt = new File(fileToCheck.replace("thumbs/_thumb_", "").replace(".png", ""))
        if (! (filealt.exists() && filealt.isFile())) {
            msg = "~File NOT FOUND - " + fileToCheck.replace("~", "-") + "~" + filename.replace("~", "-") + "~" + fileToCheck.replace("thumbs/_thumb_", "").replace(".png", "").replace("~", "-") + "~" + created + "~" + displayname + "~" + pkey + "-" + issuenum + "~ (FSREC55)\n"
            log.error msg;
        }
    }
    
    return msg
}

//*************************************************************
// Build the file path and name
String buildThisFileName(int id, def pkey, def issuenum, String mimetype) {
	String base = "/apps/opt/jira/jirashared/data/attachments/";
    	
    temp =  (issuenum - 1).div(10000).toInteger() + 1
    String sissuenum = temp
    
    def fileoffset = sissuenum + "0000"
	def finalname = "";
	if (mimetype == "image/png") {
		finalname = base + pkey + "/" + fileoffset + "/" + pkey + "-" + issuenum + "/thumbs/_thumb_"  + id + ".png";
	}
	else {
		finalname = base + pkey + "/" + fileoffset + "/" + pkey + "-" + issuenum + "/" + id;
	}
	
	return finalname;
}

//********************************************
def sqlStmt = """
select p.pkey, p.ORIGINALKEY, i.issuenum
,f.*
,u.display_name
from fileattachment f
inner join jiraissue i
on i.id = f.issueid
inner join project p
on p.id = i.project
inner join cwd_user u
on u.user_name = f.author
where f.CREATED > DATEADD(hour, -8, getdate())
--where (f.CREATED > '2019-02-20 18:00' AND f.CREATED < '2019-02-20 19:00')
order by f.CREATED
"""

def delegator = (DelegatorInterface) ComponentAccessor.getComponent(DelegatorInterface)
String helperName = delegator.getGroupHelperName("default");

Connection conn = ConnectionFactory.getConnection(helperName);
Sql sql = new Sql(conn)

String result = "Start<br />";
int errcount = 0;
int processed = 0;
sql.eachRow(sqlStmt) { sqlrow ->
    processed = processed + 1;
	//result = result + sqlrow.MIMETYPE + ' ... ' + sqlrow.ID + "<br />";
    //log.debug buildThisFileName(sqlrow.ID, sqlrow.pkey, sqlrow.issuenum) + " (FSREC02)"
    int id = sqlrow.ID;
    //log.debug buildThisFileName(id, sqlrow.pkey, sqlrow.issuenum) + " (FSREC02)"
    String errmsg = checkThisFile(buildThisFileName(id, sqlrow.ORIGINALKEY, sqlrow.issuenum, sqlrow.MIMETYPE), sqlrow.FILENAME, sqlrow.CREATED, sqlrow.display_name, sqlrow.pkey, sqlrow.issuenum)
    if (errmsg.length() > 0) {
        filetext = filetext + errmsg;
		errcount = errcount + 1;
    }
}

//return Response.ok(new JsonBuilder(list).toString()).build();
sql.close()

filetext = filetext + "\n" + '--- Finish process / report ---' + "\n";
file.text = filetext;

//********************************************************************************************
//log.debug "issuesProcessed=" + issuesProcessed + ". issuesDeleted=" + issuesDeleted + ". issuesWithError=" + issuesWithError;
String finished = date.format("MM/dd/yyyy HH:mm")
String jiraEnv = getJiraEnvironment("short")
log.info "Finished @ " + finished + ". errcount=" + errcount + " (FSREC04)";
String json_msg = '{"errcount":"' + errcount + '","started":"' + started + '","finished":"' + finished + '"}'
def rc = insert_example_audit_log("Service_RecentAttachmentValidator.groovy", "final", jiraEnv, "FINAL", json_msg, devopsServer, devopsDB, devopsUser, devopsPassword, log, Class.forName('org.postgresql.Driver').newInstance())

if (errcount > 0) {
	finalHousekeeping(to, from, subject, body, date, errcount.toString(), "-1", sqlStmt, baseurl, nodeid, filetext, processed.toString(), jiraEnv);
}
