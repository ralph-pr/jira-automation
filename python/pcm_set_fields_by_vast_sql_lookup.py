# GOAL: Update VAST-related reporting fields in the PCM project to ensure the values stay in sync with the golden VSAT/VSAD source data.
# This script will evaluate recently changed PCM tickets, lookup the current `VAST Appl ID` value and ensure the Portfolio, VP/Exec Dir and Appl ID fields are correct.
# This is needed to correctly identify the users, their teams and organizations. This module runs every 10 minutes as a cron job on a CELV PreProd/Archive EC2.

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
import pymssql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#-----------------------------------------------------
def get_logger(LOG_FILENAME):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    #logger.setLevel(logging.INFO)
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

LOG_FILENAME = os.path.basename(__file__).replace(".py", ".log")
logger = get_logger(LOG_FILENAME)
logger.info("!!Start script!!")

errors = [];

# -----------------------------------------------------
def readconfig():
    configfilename = os.path.basename(__file__).replace(".py", ".config")
    configuration = getconfigdictionary(configfilename)
    logger.info("DEBUG - configuration['jira_url'] = " + configuration["jira_url"])

    return configuration

#-----------------------------------------------------
def send_email():
    email_to = "pcm_set_fields_by_vast_sql_lookup@python.example.com"
    email_from = "ralph.pritchard@org.example.com"
    email_subject = "Completion report for pcm_set_fields_by_vast_sql_lookup.py python script"

    email_template = """\
    <html>
      <head></head>
      <body>
        <p>The python script pcm_set_fields_by_vast_sql_lookup has completed.
        <br />
        ~errors~
        </p>
      </body>
    </html>
    """

    # -----------------------------------------------------
    err_msg = "There were no errors."
    if len(errors) > 0:
        err_msg = "The following errors were reported:<ol>"
        for msg in errors:
            err_msg = err_msg + "<li>" + msg + "</li>"
        err_msg = err_msg + "</ol>"

    custom_email = email_template.replace("~errors~", err_msg)

    # -----------------------------------------------------
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = email_subject
    msg['From'] = email_to
    msg['To'] = email_from

    # Record the MIME types of both parts - text/plain and text/html.
    part2 = MIMEText(custom_email, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('smtp.example.com', 25)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(email_to, email_from, msg.as_string())
    s.quit()

#-----------------------------------------------------
def fields(cursor):
    results = {}
    column = 0
    for d in cursor.description:
        results[d[0]] = column
        column = column + 1
    return results

#-----------------------------------------------------
def handle_this_issue(configuration, issue, cursor):
    global errors

    #logger.info("DEBUG - " + issue.key, issue.id, issue.fields.customfield_10500, issue.fields.customfield_40800)
    vast_key = issue.fields.customfield_47800[0]

    sql_select_vast = "SELECT TOP 1 ApplicationID, ApplID, ApplicationAcronym, ApplicationName, CustodianFullName, BusinessUnit, Tier5ManagerFullName, BusinessUnitExecutiveName FROM VAST_AppMaster WHERE ApplID = '~VAST~'"
    cursor.execute(sql_select_vast.replace('~VAST~', vast_key))
    row = cursor.fetchone()
    field_map = fields(cursor)
    #logger.info(str(row[field_map['ApplicationID']]) + ' ...2 ' + row[field_map['ApplicationAcronym']] + ' ... ' + row[field_map['ApplicationName']] + ' ... ' + row[field_map['BusinessUnitExecutiveName']])
    issue.update(fields={"customfield_42002":vast_key})

    # handle Portfolio field
    newval = str(row[field_map['BusinessUnit']])
    logger.info("~" + newval + "~")
    try:
        issue.update(fields={"customfield_16304":{"value":newval}})
        print("!!!@@@ updated - Portfolio @@@!!!")
    except:
        logger.error("Unexpected error:", sys.exc_info()[0])
        logger.error("Cannot find matching value for Portfolio: " + issue.key + ", " + row[field_map['BusinessUnit']])
        errors.append("Cannot find matching value for Portfolio: " + issue.key + ", " + row[field_map['BusinessUnit']])

    # try to set the value to VP first. if fail then try mgr else error
    newval = str(row[field_map['BusinessUnitExecutiveName']]) #"Dan Gerola"
    logger.info("~" + newval + "~")
    try:
        newval = row[field_map['BusinessUnitExecutiveName']]
        issue.update(fields={"customfield_40800":{"value":newval}})
        logger.info("!!!@@@ updated - VP @@@!!!")
    except:
        try:
            newval = row[field_map['Tier5ManagerFullName']]
            issue.update(fields={"customfield_40800": {"value": newval}})
            logger.info("!!!@@@ updated - mgr @@@!!!")
        except:
            logger.error("Unexpected error:", sys.exc_info()[0])
            logger.error("Cannot find matching value for VP / Exec Dir: " + issue.key + ", " + row[field_map['BusinessUnitExecutiveName']]+ ", " + row[field_map['Tier5ManagerFullName']])
            errors.append("Cannot find matching value for VP / Exec Dir: " + issue.key + ", " + row[field_map['BusinessUnitExecutiveName']]+ ", " + row[field_map['Tier5ManagerFullName']])

# -----------------------------------------------------
def handle_all_issues(configuration):
    logger.info("INFO - Action is ALL so process all 'recent' issues. handle_all_issues started.")
    # -----------------------------------------------------
    jira = JIRA(configuration["jira_url"], auth=(configuration["jira_user"], configuration["jira_password"]))

    # -----------------------------------------------------
    server = configuration["vast_sql_server"]
    database = configuration["vast_sql_db"]
    username = configuration["vast_sql_user"]
    password = configuration["vast_sql_password"]
    odbc_driver = configuration["vast_sql_driver"]  # on EC2 Linux = ODBC Driver 11 for SQL Server
    #cnxn = pyodbc.connect('DRIVER={' + odbc_driver + '};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cnxn = pymssql.connect(server, username, password, database)
    cursor = cnxn.cursor()

    # -----------------------------------------------------
    # Iterate issues returned from JQL
    # -----------------------------------------------------
    jql = configuration["jql_epics"]
    #key fields (Prod / PreProd IDs) ... eventually move to config file!!!
    #47800 VAST Appl ID	- nfeed
    #16304 Portfolio - select
    #42002 Appl ID - textbox
    #40800 VP/Exec Dir - select
    issues_in_proj = jira.search_issues(jql, fields='id,key,status,issuetype,customfield_47800,customfield_10500,customfield_40800,customfield_16304', maxResults=1000)
    for issue in issues_in_proj:
        handle_this_issue(configuration, issue, cursor)

    # -----------------------------------------------------
    issues_processed = len(issues_in_proj)
    cursor.close()
    del cursor
    cnxn.close()
    del cnxn

    #logger.info("DEBUG - DONE! Epic level ... sync_parent_issues_by_jql() returned. Issues processed = " + str(issues_processed) + ". jql = " + jql)

   #logger.info("INFO - handle_all_issues ended.")

#-----------------------------------------------------
if __name__ == "__main__":
    #main(sys.argv[1:])
    configuration = readconfig()
    logger.info(configuration["jira_user"])
    handle_all_issues(configuration)
    logger.info("...$$$ start errors $$$...")
    for err in errors:
        print(err)
    logger.info("...$$$ end errors $$$...")
    send_email()

logger.info("!!End script!!")
