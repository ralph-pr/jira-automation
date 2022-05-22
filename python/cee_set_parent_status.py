import sys, getopt
import requests
import os
from jira import JIRA
from JsonToDictionary import getconfigdictionary
import logging

logger = logging.getLogger()

#-----------------------------------------------------
def get_logger(LOG_FILENAME):
    logger = logging.getLogger()
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    # create console handler and set level to debug
    ch = logging.FileHandler(LOG_FILENAME)
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    return logger

#-----------------------------------------------------
def readconfig():
    configfilename = os.path.basename(__file__).replace(".py",".config")
    configuration = getconfigdictionary(configfilename)
    logger.debug("configuration['jira_url'] = " + configuration["jira_url"])

    return configuration

#-----------------------------------------------------
def handle_all_issues(configuration):
    logger.info("Action is ALL so process all 'recent' issues. handle_all_issues started.")
    jira = JIRA(configuration["jira_url"], auth=(configuration["jira_user"], configuration["jira_password"]))

    #-----------------------------------------------------
    # 1. Sync Epics
    #-----------------------------------------------------
    jql = configuration["jql_epics"]
    issues_processed = sync_parent_issues_by_jql(configuration, jira, jql)

    logger.debug("DONE! Epic level ... sync_parent_issues_by_jql() returend. Issues processed = " + str(issues_processed) + ". jql = " + jql)

    #-----------------------------------------------------
    # 2. Sync Program Epics
    #-----------------------------------------------------
    jql = configuration["jql_program_epics"]
    issues_processed = sync_parent_issues_by_jql(configuration, jira, jql)

    logger.debug("DONE! Program Epic level ... sync_parent_issues_by_jql() returend. Issues processed = " + str(issues_processed) + ". jql = " + jql)

    #-----------------------------------------------------
    # 3. Sync Initiatives
    #-----------------------------------------------------
    jql = configuration["jql_initiatives"]
    issues_processed = sync_parent_issues_by_jql(configuration, jira, jql)

    logger.info("handle_all_issues ended.")

#-----------------------------------------------------
def handle_this_issue(configuration, issuekey):
    global the_issue
    
    jira = JIRA(configuration["jira_url"], auth=(configuration["jira_user"], configuration["jira_password"]))

    logger.debug("Action is single issue - " + issuekey)
    the_issue = jira.issue(issuekey, fields="id,key,status,issuetype,customfield_10006,customfield_45400")
    logger.debug(the_issue.key + "~" + str(the_issue.id) + "~" + the_issue.fields.status.name)
    logger.debug(the_issue.fields.issuetype.name)
    logger.debug(the_issue.raw['fields'][configuration["customfield_epic_link"]])
    logger.debug(the_issue.raw['fields'][configuration["customfield_parent_link"]])

    # IF story level THEN set the epic's status AND the_issue becomes the epic
    story_types = ['Bug', 'New Feature', 'Risk', 'Story', 'Task', 'Tech Debt']
    if the_issue.fields.issuetype.name in story_types and the_issue.fields.customfield_10006 != "None":
        if the_issue.fields.customfield_10006 is None:
            logger.debug("WARNING: Story/Task " + the_issue.key + " does not have an epic/parent. (CSJSYNC03)")
        else:
            the_issue = jira.issue(the_issue.fields.customfield_10006, fields="id,key,status,issuetype,customfield_10006,customfield_45400")
            rv = setstatus(configuration, jira, the_issue.key, the_issue.id, the_issue.fields.status.name, the_issue.fields.issuetype.name)
            logger.debug(rv)

    # IF epic level THEN set the program epic's status AND the_issue becomes the program epic
    if the_issue.fields.issuetype.name == 'Epic' and the_issue.fields.customfield_45400 != "None":
        if the_issue.fields.customfield_45400 is None:
            logger.info("WARNING: Epic " + the_issue.key + " does not have a parent initiative. (CSJSYNC04)")
        else:
            the_issue = jira.issue(the_issue.fields.customfield_45400, fields="id,key,status,issuetype,customfield_10006,customfield_45400")
            rv = setstatus(configuration, jira, the_issue.key, the_issue.id, the_issue.fields.status.name, the_issue.fields.issuetype.name)
            logger.debug(rv)

    # IF program epic level THEN set the initiative's status AND the_issue becomes the program epic
    if the_issue.fields.issuetype.name == 'Program Epic' and the_issue.fields.customfield_45400 != "None":
        if the_issue.fields.customfield_45400 is None:
            logger.info("WARNING: Program Epic " + the_issue.key + " does not have a parent initiative. (CSJSYNC05)")
        else:
            the_issue = jira.issue(the_issue.fields.customfield_45400, fields="id,key,status,issuetype,customfield_10006,customfield_45400")
            rv = setstatus(configuration, jira, the_issue.key, the_issue.id, the_issue.fields.status.name, the_issue.fields.issuetype.name)
            logger.debug(rv)
    
#-----------------------------------------------------
def sync_parent_issues_by_jql(configuration, jira, jql):
    issues_in_proj = jira.search_issues(jql, fields='id,key,status,issuetype', maxResults=1000)
    for issue in issues_in_proj:
        rv = setstatus(configuration, jira, issue.key,issue.id, issue.fields.status.name, issue.fields.issuetype.name)
        logger.debug(rv)

    return len(issues_in_proj)

#-----------------------------------------------------
def setstatus(configuration, jira, issuekey, issueid, old_status, issuetype):
    new_status = old_status
    transitionid = -1
    logger.debug("!!! ... " + issuekey + " ... !!!!")
    jql = "issuekey in childIssuesOf('" + issuekey + "') AND statusCategory != Done"
    matching_children = jira.search_issues(jql, fields='id', maxResults=1)
    total = len(matching_children)
    if total == 0:
        new_status = "Done"
        if issuetype == 'Initiative':
            transitionid = configuration["initiative_transition_id_done"]
        else:
            transitionid = configuration["transition_id_done"]
    else:
        jql = "issuekey in childIssuesOf('" + issuekey + "') AND statusCategory != 'To Do'"
        matching_children = jira.search_issues(jql, fields='id', maxResults=1)
        total = len(matching_children)
        if total == 0:
            new_status = "To Do"
            if issuetype == 'Initiative':
                transitionid = configuration["initiative_transition_id_to_do"]
            else:
                transitionid = configuration["transition_id_to_do"]
        else:
            new_status = "In Progress"
            transitionid = configuration["transition_id_in_progress"]
            if issuetype == 'Initiative':
                transitionid = configuration["initiative_transition_id_in_progress"]
            else:
                transitionid = configuration["transition_id_in_progress"]

    logger.debug(old_status + "~" + new_status)
    if new_status != old_status:
        jira.transition_issue(issueid, transitionid)
        
    #return resp.json()['total']
    return issuekey + " processed. old_status=" + old_status + ". new_status=" + new_status + "."

#-----------------------------------------------------
def main(argv):
    # read config file
    configuration = readconfig()

    # create logger
    LOG_FILENAME = 'cee_set_parent_status.log'
    logger = get_logger(LOG_FILENAME)
    logger.info("Function started.")

    #---
    action = ''
    try:
        opts, args = getopt.getopt(argv,"ha:u:",["user=","action="])
    except getopt.GetoptError:
        msg = "cee_set_parent_status.py -a <action>"
        logger.error(msg)
        print(msg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            msg = "cee_set_parent_status.py -a <action>"
            logger.error(msg)
            print(msg)
            sys.exit()
        elif opt in ("-a", "--action"):
            action = arg

    if action == '':
        msg = "Missing expected -a <action> input from the caller: cee_set_parent_status.py -a <action>"
        logger.error(msg)
        print(msg)
        sys.exit()
    else:
        print("Action is '" + action + "'.")
        if action == 'ALL':
            handle_all_issues(configuration)
        else:
            handle_this_issue(configuration, action)

    logger.info("Function finished")

#-----------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])
