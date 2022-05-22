//This script shows how to rename a file if it exists.
//Use case: We have some scripts/functions that use the existance of a particular file for state management.
//	This script will let you rename a file to another name. It can be useful to remove a node from LB by renaming
//	the keepalive file or to trigger a kill switch in a long running script.
import org.apache.log4j.Level
import org.apache.log4j.Logger

Logger log = log
log.setLevel(Level.DEBUG)
log.debug "start";

def renameThisFile(fileToCheck, newFileName) {
	File file = new File(fileToCheck)
	//assert newFile.exists()
	//assert 'simple content' == newFile.text

	if (file.exists() && file.isFile()) {
		log.debug "found - " + fileToCheck;
		file.renameTo newFileName;
	} else {
		log.debug "NOT FOUND - " + fileToCheck;
	}
}

renameThisFile("/apps/opt/atlassian/jira/atlassian-jira/static/Keepalive.htm", "/apps/opt/atlassian/jira/atlassian-jira/static/Keepalive.htm.out");
renameThisFile("/apps/opt/atlassian/jira/atlassian-jira/static/Keepalive_GSLB.htm", "/apps/opt/atlassian/jira/atlassian-jira/static/Keepalive_GSLB.htm.out");

log.debug "end";
