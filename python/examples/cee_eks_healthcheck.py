import boto3
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


# logger = logging.getLogger()

finalMsg = ""

# -----------------------------------------------------
def get_logger(LOG_FILENAME):
    logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
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


# -----------------------------------------------------
def readconfig():
    configfilename = os.path.basename(__file__).replace(".py", ".config")
    configuration = getconfigdictionary(configfilename)
    print("DEBUG - configuration['jira_url'] = " + configuration["jira_url"])

    #os.environ["HTTP_PROXY"] = "http://proxy.example.com:80"
    #os.environ["HTTPS_PROXY"] = "http://proxy.example.com:80"
    #os.environ["http_proxy"] = "http://proxy.example.com:80"
    #os.environ["https_proxy"] = "http://proxy.example.com:80"

    return configuration


# -----------------------------------------------------
def handle_all_issues(configuration):
    print("INFO - Action is ALL so process all 'recent' issues. handle_all_issues started.")
    jira = JIRA(configuration["jira_url"], auth=(configuration["jira_user"], configuration["jira_password"]))

    # -----------------------------------------------------
    # 1. Sync Epics
    # -----------------------------------------------------
    jql = configuration["jql_epics"]
    issues_processed = sync_parent_issues_by_jql(configuration, jira, jql)

    print("DEBUG - DONE! Epic level ... sync_parent_issues_by_jql() returend. Issues processed = " + str(
        issues_processed) + ". jql = " + jql)

    print("INFO - handle_all_issues ended.")


# -----------------------------------------------------
def sync_parent_issues_by_jql(configuration, jira, jql):
    issues_in_proj = jira.search_issues(jql, fields='id,key,status,issuetype', maxResults=1000)
    for issue in issues_in_proj:
        print("DEBUG - " + issue.key, issue.id)

    return len(issues_in_proj)


# -----------------------------------------------------
def main(argv):
    # read config file
    configuration = readconfig()

    # create logger
    # LOG_FILENAME = 'cee_set_parent_status.log'
    # logger = get_logger(LOG_FILENAME)
    print("INFO - Function started.")

    # ---
    action = ''
    try:
        opts, args = getopt.getopt(argv, "ha:u:", ["user=", "action="])
    except getopt.GetoptError:
        msg = "cee_set_parent_status.py -a <action>"
        # logger.error(msg)
        print(msg)
        # sys.exit(2)

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
        # logger.error(msg)
        print(msg)
        sys.exit()
    else:
        print("Action is '" + action + "'.")
        if action == 'ALL':
            handle_all_issues(configuration)
        else:
            handle_this_issue(configuration, action)

    print("INFO - Function finished")


# -----------------------------------------------------
def performHealthCheck(configuration):
    global finalMsg

    usrPass = "U1ZDLU9ORUpJUkFSRVBPUlRFUjpxWDE5ZUwxOHRxWDE5ZUwxOHRxWDE5ZUwxOA=="
    #url = configuration["jira_url"] + "rest/troubleshooting/1.0/check/"
    url = configuration["jira_url"] + "rest/api/latest/serverInfo"
    resp = requests.get(url,
                        headers={"Authorization": "Basic %s" % usrPass})
    print(resp)
    # print(resp.json())

    if not (200 <= resp.status_code < 400):
        raise ApiError(status_code=session.status_code,
                       reason=session.content)
    results = {
        "healthy": [],
        "unhealthy": [],
    }

    for status in resp.json().get('statuses', []):
        entry = {
            "name": status["name"],
            "description": status["description"],
            "is_healthy": status["healthy"],
        }
        if status["healthy"] == False:
            results["unhealthy"].append(entry)
        results["healthy"].append(entry)

    return results["unhealthy"]


# -----------------------------------------------------
def lambda_handler(event, context):
    print('Event received:')
    print(event)

    current_date = (datetime.now().strftime("%m-%d-%Y"))

    # read config file
    configuration = readconfig()
    unhealthy_results = performHealthCheck(configuration)
    print(unhealthy_results)

    final_result = {
        "source": "EKS",
        "overallStatus": "?",
        "statusReason": "?",
        "healthmetrics": [],
    }

    healthmetric = {
        "message": "",
    }

    if len(unhealthy_results) == 0:
        final_result["overallStatus"] = "green"
        final_result["statusReason"] = ""
        healthmetric["message"] = "we all good!"
        final_result["healthmetrics"].append(healthmetric)
    elif len(unhealthy_results) == 1 and unhealthy_results[0]["name"] == "Cluster Locks":
        final_result["overallStatus"] = "yellow"
        final_result[
            "statusReason"] = "All but one checks reported PASS. The failure was for 'Cluster Locks' which is not unusual but indicates overall slowness."
    else:
        final_result["overallStatus"] = "red"
        final_result["statusReason"] = str(len(
            unhealthy_results)) + " checks have failed. Future investigate each of the failing checks listed in 'healthmetrics'."
        for msg in unhealthy_results:
            healthmetric["message"] = msg["description"]
            final_result["healthmetrics"].append(healthmetric)

    # format a string for return
    # resp = '{"source": "Jira","overallStatus":"green/yellow/red","statusReason":"Derived from code - x of y checks passed.","healthmetrics": [{"message": "sample_msg"}]}'
    print (final_result)
    print ('End')

    # 'body': json.dumps(resp)
    return {
        'isBase64Encoded': 'false',
        'statusCode': 200,
        'headers': {
            "Content-Type": "text/html; charset=utf-8"
        },
        'body': """<html><body>"""+json.dumps(final_result)+"""</body></html>"""
    }


# -----------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])
