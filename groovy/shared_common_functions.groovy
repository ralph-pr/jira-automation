// shared_common_functions.groovy - Common functions to be reused for Jira and Confluence script purposes.
//	See shared_common_functions_tester.groovy for examples of how to use and call these functions.

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
//import com.atlassian.mail.server.MailServerManager
//import com.atlassian.mail.server.SMTPMailServer
import groovy.time.*
import com.atlassian.jira.user.util.UserUtil
import java.net.InetAddress
import groovy.xml.*

class examplecommon {
	//*******************************************************
	//helloWorld - sample function
	def helloWorld() {
		return("Hello World!")
	}

	//*******************************************************
	//getJiraEnvironment - identifies the JIRA environment by reading the DB name from dbconfig.xml
	def getJiraEnvironment(String output_type) {
		def config = new XmlSlurper().parse(new File("/apps/opt/atlassian/application-data/jira/dbconfig.xml"))
		String jiradb = config.'jdbc-datasource'.url
		
		def result
		if (output_type == "long") {
			result = "UNKNOWN - see dbconfig.xml ... " + jiradb
		}
		else {
			result = "UNKNOWN - see dbconfig.xml"
		}
		if (jiradb.contains("onejira_DB_Prod_west") == true)
		{
			result = "PROD - WEST"
		}
		else if (jiradb.contains("onejira_preprod_east") == true) {
			result = "PREPROD"
		}
		else if (jiradb.contains("onejira_test") == true) {
			result = "TEST"
		}
		else if (jiradb.contains("archive") == true) {
			result = "ARCHIVE"
		}
		else if (jiradb.contains("reports") == true) {
			result = "REPORTS"
		}
		
		result
	}
		
	//************************************************************
	//insert_example_audit_log - makes a PostgreSQL call to a function. That function will enforce our rule on all eazyBI data sources.
	//...sample call = def rc = insert_example_audit_log(category, subcategory, environment, msg_type, json_msg, server, database, sqluser, sqlpassword, log, Class.forName('org.postgresql.Driver').newInstance())
	//...NOTE: This method requires the caller to pass in a copy of the DB driver class because metaClass.mixin had a problem 
	//...      finding the DB class file even though the caller has no problem (context/lib search problem).
	def insert_example_audit_log(def category, def subcategory, def environment, def msg_type, def json_msg, def server, def database, def sqluser, def sqlpassword, def log, def driver) {
		try {
			def sqlStmt = "SELECT insert_example_audit_log('" + category + "', '" + subcategory + "', '" + environment + "', '" + msg_type + "', '" + json_msg + "');"
			def url = 'jdbc:postgresql://' + server + '/' + database
			//def driver = Class.forName('org.postgresql.Driver').newInstance() as Driver 
			//def driver = classloader.forName('org.postgresql.Driver').newInstance() as Driver 

			def props = new Properties()
			props.setProperty("user", sqluser) 
			props.setProperty("password", sqlpassword)

			def conn = driver.connect(url, props) 
			def sql = new Sql(conn)

			log.info "before eachRow loop"	
			sql.eachRow(sqlStmt) { sqlrow ->
				log.info "The SQL statement was successfully processed (GVNEZ200) ... " //+ sqlrow.exampletimestamp
				//Long linktype = sqlrow.linktype
				//createThisIssueLink(sqlrow.sourcekey, sqlrow.destinationkey, linktype, sqlrow.sequence, issueManager, issueLinkManager, user, log)
			}
			log.info "after eachRow loop"	

			// Finish processing - close SQL and log results.
			sql.close()
		} catch (Exception ex) {  // Groovy shortcut: we can omit the Exception class
			//finalMsg += "<br />ERROR on delete for issue.id=<b>" + documentIssue.id + "</b>"
			log.error "ERROR! " + ex.getMessage() + " (GVNEZ900)"
			return "failure"
		}
		
		return "success"
	}
}

