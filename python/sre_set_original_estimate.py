# GOAL: Ensure the originalEstimate value is correctly set for new issues that were created from the Portfolio (aka Roadmaps) plugin.
# The current design of the plugin causes the originalEstimate value to not get set. Instead the plugin sets the remainingEstimate value.
# This script will find new issues where the originalEstimate is null and set it to the remainingEstimate value provided there is no work yet logged.

import json
from datetime import datetime
import logging
import calendar
import random
import time
import sys, getopt
import requests
import os
from jira import JIRA
from JsonToDictionary import getconfigdictionary

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
    print("DEBUG - configuration['jira_url'] = " + configuration["jira_url"])

    #os.environ["HTTP_PROXY"] = "http://proxy.example.com:80"
    #os.environ["HTTPS_PROXY"] = "http://proxy.example.com:80"
    #os.environ["http_proxy"] = "http://proxy.example.com:80"
    #os.environ["https_proxy"] = "http://proxy.example.com:80"

    return configuration

#-----------------------------------------------------
def handle_all_issues(configuration):
    print("INFO - Action is ALL so process all 'recent' issues. handle_all_issues started.")
    jira = JIRA(configuration["jira_url"], auth=(configuration["jira_user"], configuration["jira_password"]))

    #-----------------------------------------------------
    # 1. Sync Epics
    #-----------------------------------------------------
    jql = configuration["jql_epics"]
    issues_processed = iterate_issues_by_jql(configuration, jira, jql)

    print("DEBUG - DONE! Epic level ... iterate_issues_by_jql() returend. Issues processed = " + str(issues_processed) + ". jql = " + jql)

    print("INFO - handle_all_issues ended.")
    
#-----------------------------------------------------
def iterate_issues_by_jql(configuration, jira, jql):
    issues_in_proj = jira.search_issues(jql, fields='id,key,status,issuetype,timetracking', maxResults=1000)
    for issue in issues_in_proj:
        print("DEBUG - " + issue.key,issue.id)
        rv = updateissue(configuration, jira, issue)
        logger.debug(rv)

    return len(issues_in_proj)


# -----------------------------------------------------
def updateissue(configuration, jira, issue):
    print("!!! ... " + issue.key + " ... " + issue.fields.timetracking.remainingEstimate + "!!!!")

    #issue.update(update={"timetracking": [{"edit": {"originalEstimate": "0h", "remainingEstimate": "0h"}}]})
    issue.update(update={"timetracking": [{"edit": {"originalEstimate": issue.fields.timetracking.remainingEstimate}}]})
    #issue.update(comment='Added a new comment')
    #issue.update(assignee={'name': 'SVC-jira-reporter'})  # reassigning in update requires issue edit permission
    print("update complete")

    # return resp.json()['total']
    return issue.key + "."

#-----------------------------------------------------
def main(argv):
    # read config file
    configuration = readconfig()

    # create logger
    #LOG_FILENAME = 'cee_set_parent_status.log'
    #logger = get_logger(LOG_FILENAME)
    print("INFO - Function started.")

    #---
    action = ''
    try:
        opts, args = getopt.getopt(argv,"ha:u:",["user=","action="])
    except getopt.GetoptError:
        msg = "cee_set_parent_status.py -a <action>"
        #logger.error(msg)
        print(msg)
        #sys.exit(2)
        
    action = "ALL"
##    for opt, arg in opts:
##        if opt == '-h':
##            msg = "cee_set_parent_status.py -a <action>"
##            #logger.error(msg)
##            print(msg)
##            sys.exit()
##        elif opt in ("-a", "--action"):
##            action = arg

    if action == '':
        msg = "Missing expected -a <action> input from the caller: cee_set_parent_status.py -a <action>"
        #logger.error(msg)
        print(msg)
        sys.exit()
    else:
        print("Action is '" + action + "'.")
        if action == 'ALL':
            handle_all_issues(configuration)
        else:
            handle_this_issue(configuration, action)

    print("INFO - Function finished")

#-----------------------------------------------------
def lambda_handler(event, context):
    print('Event received:')
    print(event)

    current_date = (datetime.now().strftime("%m-%d-%Y"))

    firstname = "First" # event["queryStringParameters"]['firstname']
    lastname = "Last" # event["queryStringParameters"]['lastname']
    # format a string for return
    resp = "Hello from Lambda to " + firstname + " " + lastname + "! The current date and time is " + current_date + "."
    print (resp)

    # read config file
    configuration = readconfig()
    handle_all_issues(configuration)
    
    print ('End')

    return {
        'statusCode': 200,
        'body': json.dumps(resp)
    }

#-----------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])
