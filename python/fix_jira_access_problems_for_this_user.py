# see doc at https://it-lab-site.atlassian.net/wiki/spaces/RAEC/pages/89852796/Manage+users
# see API Activate/deactivete user ... below is example of API removeUsers from the confluence-new-users group.
import os
import json
import sys
import requests
import string
import pyodbc
import psycopg2 
import ldap
import smtplib
from email.headerregistry import Address
from email.message import EmailMessage
from email.utils import make_msgid
from functools import lru_cache

#---------------
# This will be passed in an variable from the caller
call_type = "both" # valid values are: both, jira, confluence. Determines what products are in scope for this call.
#target_user = "kriley"
#target_user = "SVC-jira-reporter" # USWIN service account
target_user = "userid"


#---------------
# These vars need to go to config file
conf_admin_name="SVC-jira-admin"
conf_admin_password="svc-user-password"
confluence_reactivate_url = "https://confluence-test.example.com/rest/extender/1.0/user/activate/"

#---------------
# Establish var for the 4 directories
class EXAMPLEAD(object):
    def __init__(self, domain, url, user, password):
      self.domain = domain
      self.url = url
      self.user = user
      self.password = password
ad_vdsi = EXAMPLEAD("VDSI", "LDAP://ldap-india.example.com:389", "SVC-ldap-user", "svc-user-pwd")
ad_uswin = EXAMPLEAD("USWIN", "LDAP://ldap-us.example.com:389", "SVC-ldap-user", "svc-user-pwd")
ad_emea = EXAMPLEAD("EMEA-DSMAIN", "LDAP://ldap.eurpore.example.com:389", "SVC-ldap-user", "svc-user-pwd")
ad_adebp = EXAMPLEAD("ADEBP", "ldap://ldap-vendor.example.com:389", "SVC-CELVTEST-ADEBP", "svc-user-pwd")

# Establish object to contain employee info
class EXAMPLEUSER(object):
    def __init__(self):
      self.user_name = ""
      self.found = "N"
      self.domain = ""
      self.employeetype = ""
      self.employeestatus = ""
      self.displayname = ""
      self.email = ""
      self.exampleobjectowner = ""
      self.search_domain = ""

#---------------
# SMTP
_EXAMPLE_SMTP_HOST = "examplesmtp.example.com"
_EXAMPLE_SMTP_PORT = 25
# Email
_MAIL_SUBJECT = "Agile Services python automation - fix_jira_access_problems_for_this_user"
_MAIL_FROM = Address("JIRA Support Team", "noreply", "example.com")
_MAIL_TO = ["ralph.pritchard@example.com"]
_MAIL_CC = []
_MAIL_BCC = []  # overwritten

_MAIL_CONTENT = """\
Hello ~user~,
...plain text version here...

Thank you,
JIRA Support Team
"""

_MAIL_BODY = """\
<html>
  <body>
    <p>Hello ~user~</p>
    <p>Automation was run for your user ID for the product(s) ~call_type~</p>
    <p>The automation provided these messages:<br />~finalresponse~</p>
  </body>
</html>
"""


#---------------
# Working variables
finalresponse = []  # contains various msgs related to actions/results to be passed back to the caller

#---------------
# Re-activate this user in Confluence
def reactivate_confluence_user(user_name):
    cheaders = {"Content-type": "application/json"}
    headers = {'Content-type': 'application/json'}
    response=requests.post(confluence_reactivate_url + user_name,data="",headers=headers,verify=False, auth=(conf_admin_name, conf_admin_password))
    #print(response.text)
    return("reactivate_confluence_user called ... result=" + response.text) #"success"

#---------------
# Re-activate this user in JIRA
def reactivate_jira_user(user_name):
    pkey = 'ITT'
    usrPass = "U1ZDLU9ORUpJUkFSRVBPUlRFUjpxWDE5ZUwxOHRxWDE5ZUwxOHRxWDE5ZUwxOA=="
    #url = "https://jira.baseurl.com/rest/zapi/latest/zql/executeSearch?zqlQuery=project=" + pkey
    url = "https://jira-preprod.example.com/rest/scriptrunner/latest/custom/reactivateUserViaGet?user=" + user_name
    
    resp = requests.get(url, 
                    headers={"Authorization": "Basic %s" % usrPass})
    #print("resp.status_code=" + str(resp.status_code))
    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError('POST /tasks/ {}'.format(resp.status_code))
    #print(resp.status_code)
    #print(resp.body)
    result = "reactivate_jira_user called ... result=" + (resp.content).decode("utf-8")
    #return("TO-DO! finish reactivate_jira_user for " + user_name)
    #return resp.json()['totalCount']
    return("SUCCESS - " + result)
    
#---------------
# SQL call to Confluence DB to get current info on this user
def handle_confluence_user_lookup_and_reactivation(user_name):
    pgserver = 'confluencepgsql-preprod.cbhxxwrpq3pu.us-west-2.rds.amazonaws.com' 
    pgdatabase = 'oneconfluence_prod_DB' 
    pgusername = 'devopsdbadmin' 
    pgpassword = 'YOURPWD'
    conn_str = (
        "DRIVER={PostgreSQL Unicode};"
        "DATABASE="+pgdatabase+";"
        "UID="+pgusername+";"
        "PWD="+pgpassword+";"
        "SERVER="+pgserver+";"
        "PORT=5432;"
        )
    cnxn = psycopg2.connect(host=pgserver,database=pgdatabase, user=pgusername, password=pgpassword)
    cursor = cnxn.cursor()
    #cursor.execute("select devops.research_user_access_confluence('userid');")
    cursor.execute("select * from devops.user_access_view where lower_user_name = lower('" + user_name + "');")
    row = cursor.fetchone() 
    result = "This user (" + user_name + ") has never logged into OneConfluence. They do not exist on cwd_user table. See https://? for instructions for initial login."
    if (row):
        result = "This user (" + user_name + ") has these attributes: active=" + str(row[1]) + ",directory_name=" + row[2] \
            + ",email_address=" + row[3] + ",last_login=" + str(row[4]) \
            + ",member_of_sdlc_contractors=" + row[5] + ",member_of_sdlc_exampleemployees=" + row[6] \
            + ",member_of_sdlc_examplebuspartners=" + row[7] + ",member_of_sdlc_extbuspartners=" + row[8] \
            + ",member_of_vdsisdlc_contractors=" + row[9] + ",member_of_vdsisdlc_exampleemployees=" + row[10] \
            + ",member_of_vdsisdlc_examplebuspartners=" + row[11] + ",member_of_vdsisdlc_extbuspartners=" + row[12] \
            + ",member_of_emeasdlc_contractors=" + row[13] + ",member_of_emeasdlc_exampleemployees=" + row[14] \
            + ",member_of_emeasdlc_examplebuspartners=" + row[15] + ",member_of_emeasdlc_extbuspartners=" + row[16] \
            + ",member_of_adebpsdlc_contractors=" + row[17] + ",member_of_adebpsdlc_exampleemployees=" + row[18] \
            + ",member_of_adebpsdlc_examplebuspartners=" + row[19] + ",member_of_adebpsdlc_extbuspartners=" + row[20] #\
        finalresponse.append("SUCCESS - handle_confluence_user_lookup_and_reactivation called ... result=" + result)

        if (str(row[1]) != "T"):
            finalresponse.append(reactivate_confluence_user(target_user))
        else:
            finalresponse.append("INFO - User is currently active in Confluence.")
    else:
        finalresponse.append("FAILURE - " + result)

    return("SUCCESS")
    
#---------------
# SQL call to JIRA DB to get current info on this user . If inactive then activate. 
def handle_jira_user_lookup_and_reactivation(user_name):
    server = 'confluenceprodeast.c5ogzsgipyri.us-east-1.rds.amazonaws.com' 
    database = 'onejira_preprod_east' 
    username = 'devopsdbadmin' 
    #password = 'DevOps1234' 
    password = 'YOURPWD' 
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    cursor.execute('EXEC Reports.research_user_access_jira ?', user_name)
    row = cursor.fetchone()
    result = "This user (" + user_name + ") has never logged into OneJIRA. They do not exist on cwd_user table. See https://? for instructions for initial login."
    if (row):
        result = "This user (" + user_name + ") has these attributes: active=" + str(row.active) + ",directory_name=" + row.directory_name \
            + ",email_address=" + row.email_address + ",last_login=" + str(row.last_login) \
            + ",member_of_sdlc_contractors=" + row.member_of_sdlc_contractors + ",member_of_sdlc_exampleemployees=" + row.member_of_sdlc_exampleemployees \
            + ",member_of_sdlc_examplebuspartners=" + row.member_of_sdlc_examplebuspartners + ",member_of_sdlc_extbuspartners=" + row.member_of_sdlc_extbuspartners \
            + ",member_of_vdsisdlc_contractors=" + row.member_of_vdsisdlc_contractors + ",member_of_vdsisdlc_exampleemployees=" + row.member_of_vdsisdlc_exampleemployees \
            + ",member_of_vdsisdlc_examplebuspartners=" + row.member_of_vdsisdlc_examplebuspartners + ",member_of_vdsisdlc_extbuspartners=" + row.member_of_vdsisdlc_extbuspartners \
            + ",member_of_emeasdlc_contractors=" + row.member_of_emeasdlc_contractors + ",member_of_emeasdlc_exampleemployees=" + row.member_of_emeasdlc_exampleemployees \
            + ",member_of_emeasdlc_examplebuspartners=" + row.member_of_emeasdlc_examplebuspartners + ",member_of_emeasdlc_extbuspartners=" + row.member_of_emeasdlc_extbuspartners \
            + ",member_of_adebpsdlc_contractors=" + row.member_of_adebpsdlc_contractors + ",member_of_adebpsdlc_exampleemployees=" + row.member_of_adebpsdlc_exampleemployees \
            + ",member_of_adebpsdlc_examplebuspartners=" + row.member_of_adebpsdlc_examplebuspartners + ",member_of_adebpsdlc_extbuspartners=" + row.member_of_adebpsdlc_extbuspartners #\
        finalresponse.append("SUCCESS - handle_jira_user_lookup_and_reactivation called ... result=" + result)

        if (row.active == 0):
            finalresponse.append(reactivate_jira_user(target_user))
        else:
            finalresponse.append("INFO - User is currently active in Jira.")
    else:
        finalresponse.append("FAILURE - " + result)

    return("SUCCESS")
    
#---------------
# AD call to get user attributes
def callad_get_user_attributes(user_name, examplead):
    result = ""
    thisUser = EXAMPLEUSER()
    thisUser.user_name = user_name
    thisUser.search_domain = examplead.domain
    thisUser.found = "N"
    display_name="?"
    directory_name="?"
    AD_LDAP_URL=examplead.url        #"ldap://ldap-vendor.example.com:389"
    AD_SEARCH_DN="OU=Accounts,DC=" + examplead.domain + ",DC=examplewcorp,DC=com"
    AD_SEARCH_FIELDS= ['exampleEmployeeType', 'displayName','exampleGeneric01', 'OU', 'exampleVemplStatus', 'mail', 'exampleObjectOwner']
    l = ldap.initialize(AD_LDAP_URL)
    ldap.set_option(ldap.OPT_REFERRALS,0)

    # Each AD is slightly different. May be possible to parameterize and reuse.
    if (examplead.domain == "VDSI"):
        AD_LDAP_URL="ldap-india.example.com"
        AD_SEARCH_DN="OU=Accounts,DC=vdsi,DC=ent,DC=example,DC=com"
        l = ldap.initialize("ldap://"+AD_LDAP_URL+":389")
        ldap.set_option(ldap.OPT_REFERRALS,0)
        l.simple_bind_s("CN=SVC-JIRAAD-USER,OU=SVC,OU=FNA,DC=vdsi,DC=ent,DC=example,DC=com", "mA1_gY9mA1_gY9mA")
        try:
            result = l.search_ext_s("OU=Accounts,DC=vdsi,DC=ent,DC=example,DC=com",ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % user_name,AD_SEARCH_FIELDS)[0][1]
        except IndexError:
            print("....IndexError! Most likely caused by user not foud in this domain (" + examplead.domain + ").")
            return(thisUser)
        except: # catch *all* exceptions
          e = sys.exc_info()[0]
          print( "<p>Error: %s</p>" % e )
          return(thisUser)
    elif (examplead.domain == "USWIN"):
        AD_LDAP_URL="ldap-us.example.com"
        AD_SEARCH_DN="DC=uswin,DC=ad,DC=examplewcorp,DC=com"
        l = ldap.initialize("ldap://"+AD_LDAP_URL+":389")
        ldap.set_option(ldap.OPT_REFERRALS,0)
        l.simple_bind_s("SVC-uswin-cicd-devop", "dU0jY0kdU0jY0kdU0jY0dU0jY0kd")
        try:
            result = l.search_ext_s(AD_SEARCH_DN,ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % user_name,AD_SEARCH_FIELDS)[0][1]
        except IndexError:
            print("....IndexError! Most likely caused by user not foud in this domain (" + examplead.domain + ").")
            return(thisUser)
        except: # catch *all* exceptions
          e = sys.exc_info()[0]
          print( "<p>Error: %s</p>" % e )
          return(thisUser)
    elif (examplead.domain == "EMEA-DSMAIN"):
        AD_LDAP_URL="ldap-europe.example.com"
        #AD_SEARCH_DN="OU=SVC,OU=FNA,DC=EMEA,DC=dsmain,DC=com"
        AD_SEARCH_DN="OU=Accounts,DC=EMEA,DC=dsmain,DC=com"
        l = ldap.initialize("ldap://"+AD_LDAP_URL+":389")
        ldap.set_option(ldap.OPT_REFERRALS,0)
        binddn='CN=SVC-JIRAD-USER,OU=SVC,OU=FNA,DC=EMEA,DC=dsmain,DC=com'
        #print("1")
        l.bind_s(binddn,'pT10@mG5pT10@mG5')
        result = ""
        try:
            result=l.search_ext_s(AD_SEARCH_DN,ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % user_name,AD_SEARCH_FIELDS)[0][1]
        except IndexError:
            print("....IndexError! Most likely caused by user not foud in this domain (" + examplead.domain + ").")
            return(thisUser)
        except: # catch *all* exceptions
          e = sys.exc_info()[0]
          print( "<p>Error: %s</p>" % e )
          return(thisUser)
    elif (examplead.domain == "ADEBP"):
        #AD_LDAP_URL=examplead.url
        AD_LDAP_URL="ldap-vendor.example.com"
        AD_SEARCH_DN="OU=Accounts,DC=adebp,DC=examplewcorp,DC=com"
        l = ldap.initialize("ldap://"+AD_LDAP_URL+":389")
        ldap.set_option(ldap.OPT_REFERRALS,0)
        #l.simple_bind_s("CN=SVC-JIRAAD-USER,OU=SVC,OU=FNA,DC=adebp,DC=examplewcorp,DC=com", "4e22Y2wIZYp22hc6L2Z2L322Nq2")
        l.simple_bind_s("CN=SVC-CELVTEST-ADEBP,OU=SVC,OU=FNA,DC=adebp,DC=examplewcorp,DC=com", "q6chhXeF22PnT229ugQP22czEV")
        result = ""
        try:
            result=l.search_ext_s(AD_SEARCH_DN,ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % user_name,AD_SEARCH_FIELDS)[0][1]
        except IndexError:
            print("....IndexError! Most likely caused by user not foud in this domain (" + examplead.domain + ").")
            return(thisUser)
        except: # catch *all* exceptions
          e = sys.exc_info()[0]
          print( "<p>Error: %s</p>" % e )
          return(thisUser)
    else:
        print("...bad DOAMIN value...")
        return(thisUser)

    # Record the needed attributes from the AD match result
    #print(result)
    thisUser.found = "Y"
    thisUser.displayname = (result['displayName'][0]).decode("utf-8")
    thisUser.email = (result['mail'][0]).decode("utf-8")
    if thisUser.user_name.startswith("SVC"):
        thisUser.employeetype = "Service Account (SVC)"
        thisUser.domain = examplead.domain
        thisUser.exampleobjectowner = (result['exampleObjectOwner'][0]).decode("utf-8")
    else:
        thisUser.employeetype = (result['exampleEmployeeType'][0]).decode("utf-8")
        thisUser.domain = (result['exampleGeneric01'][0]).decode("utf-8")
        thisUser.employeestatus = (result['exampleVemplStatus'][0]).decode("utf-8")

    return(thisUser)
    
#---------------
# AD call to add user to group
def callad_add_user_to_group(grpname,domain,exampleid):
    adomheaders = {'Content-Type': 'application/json;charset=utf-8' }
    test=[] 

    if exampleid !='':
        memdata={}
        memdata["MemberDomainName"] = domain
        memdata["MemberSamAccountName"] = exampleid
    test.append(memdata)
    #print('Adding Members for the created Adom group for '+grpname)
    if test:
        data = {}
        data['GroupDomainName'] = domain
        data['GroupSamAccountName']= grpname
        data['Membership']=test
        data['AuthenticationKey']='SFxfT8tQ0kii9U9PGAypTJFscTt7JTOr' 
        #print(json.dumps(data))
        ADOMGroupAddMembers= 'https://devopstools.example.com/DevOpsServices/api/adom/group/membership/insert'
        response=requests.post(ADOMGroupAddMembers, headers=adomheaders, data=json.dumps(data))
        result = ""
        if response.status_code == 200:
            #f.write(exampleid + ' added to '+ grpname + '\n')
            #print(str(response.json()))
            #print('Done adding memeber for the Adom group '+ grpname)
            result = "SUCCESS - callad_add_user_to_group complete for group " + grpname + ". response.json=" + str(response.json())
            BoolFlag=True
        else:
            #f1.write(exampleid+' failed to be added under '+ grpname + '\n')
            #print(str(response.json()))
            #print('Failed adding members for the Adom group '+ grpname)
            result = "FAILURE - callad_add_user_to_group returned response.status_code=" + str(response.status_code)  + ", response.json=" + str(response.json())
            BoolFlag=False

    return(result)
    
#---------------
# Given a domain and employeetype, return the AD group for this user
def get_domain_group_name(domain, employeetype, product):
    result = ""
    switcher = {
        "VDSI":"VDSISDLC",
        "USWIN":"SDLC",
        "EMEA-DSMAIN":"EMEASDLC",
        "ADEBP":"ADEBPSDLC"
    }
    group_prefix = switcher.get(domain, "")
    group_suffix = ""
    if (product == "jira"):
        switcher = {
            "Employee":"EXAMPLEEMPLOYEES",
            "Contractor":"CONTRACTORS",
            "EXAMPLEWNonEmployee":"EXAMPLEBUSPARTNERS",
            "ExternalBusinessPartner":"EXAMPLEBUSPARTNERS"
        }
        group_suffix = switcher.get(employeetype, "")
    else:
        switcher = {
            "Employee":"COLEXAMPLEEMPLOYEES",
            "Contractor":"COLCONTRACTORS",
            "EXAMPLEWNonEmployee":"COLEXAMPLEBUSPARTNERS",
            "ExternalBusinessPartner":"COLEXTLBUSPARTNERS"
        }
        group_suffix = switcher.get(employeetype, "")

    if (group_prefix > "" and group_suffix > ""):
        result = group_prefix + "_" + group_suffix
    else:
        finalresponse.append("INFO - Cannot match use to a public AD group - probably a service account that must be manually provide only the required access needed.")
    
    #print(result)
    return(result)
    
#---------------
# complete the task including audit/email.
def final_housekeeping(user_email):
    print("send an email")
    # generate email message and populate bcc/interpolated content.
    message = generate_email_message(
            alt_content=_MAIL_BODY,
            bcc=[user_email]
    )
    try:
            with smtplib.SMTP(_EXAMPLE_SMTP_HOST, _EXAMPLE_SMTP_PORT) as smtp:
                    smtp.send_message(message)
                    print("email sent")
    finally:
            # make a local copy of what we are going to send.
            with open('outgoing.msg', 'wb') as f:
                    f.write(bytes(message))
    
    return("SUCCESS")
    
#---------------
# Generate an email message
def generate_email_message(
        subject=_MAIL_SUBJECT,
        sender=_MAIL_FROM,
        receiver=_MAIL_TO,
        cc=_MAIL_CC,
        bcc=_MAIL_BCC,
        content=_MAIL_CONTENT,
        alt_content=_MAIL_BODY):
    #bcc.append("lorraine.wildman@org.example.com")
    #bcc.append("ralph.pritchard@org.example.com")
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = receiver
    #message["Cc"] = bcc
    #message["BCC"] = bcc
    message.set_content(content)
    message.add_alternative(
        alt_content.format(asparagus_cid=make_msgid()[1:-1]).replace("~finalresponse~", generate_finalresponse_as_html(finalresponse)).replace("~user~", "TBDuser").replace("~call_type~", "TBDcall_type"),
        subtype='html')
    return message

#---------------
# Produce an HTML fragment from the finalresponse list
def generate_finalresponse_as_html(listresponse):
    finalhtml = "<ol>"
    for item in listresponse:
        finalhtml = finalhtml + "<li>" + item + "</li>"

    finalhtml = finalhtml + "</ol>"
    return(finalhtml)

#---------------
# description of some_task
def some_task():
    return("TO-DO! finish some_task?")
    
#---------------
# Primary function
def handle_this_request(this_user, this_action):
    print("start")

    #..........
    # Determine what domain the user is in. Check in same order as the products: VDSI, USWIN, EMEA-DSMAIN, ADEBP.
    # Stop as soon as user is found in a domain.
    matchingUsers = []
    adUser = callad_get_user_attributes(this_user, ad_vdsi)
    finalresponse.append("VDSI - callad_get_user_attributes for " + adUser.user_name + " returned: employeetype=" + adUser.employeetype \
        + ",domain=" + adUser.domain + ",employeestatus=" + adUser.employeestatus + ",found=" + adUser.found \
        + ",displayname=" + adUser.displayname + ",email=" + adUser.email + ",exampleobjectowner=" + adUser.exampleobjectowner + "\n\r")
    if (adUser.found == "Y"):
        matchingUsers.append(adUser)

    adUser = callad_get_user_attributes(this_user, ad_uswin)
    finalresponse.append("USWIN - callad_get_user_attributes for " + adUser.user_name + " returned: employeetype=" + adUser.employeetype \
        + ",domain=" + adUser.domain + ",employeestatus=" + adUser.employeestatus + ",found=" + adUser.found \
        + ",displayname=" + adUser.displayname + ",email=" + adUser.email + ",exampleobjectowner=" + adUser.exampleobjectowner + "\n\r")
    if (adUser.found == "Y"):
        matchingUsers.append(adUser)

    adUser = callad_get_user_attributes(this_user, ad_emea)
    finalresponse.append("EMEA-DSMAIN - callad_get_user_attributes for " + adUser.user_name + " returned: employeetype=" + adUser.employeetype \
        + ",domain=" + adUser.domain + ",employeestatus=" + adUser.employeestatus + ",found=" + adUser.found \
        + ",displayname=" + adUser.displayname + ",email=" + adUser.email + ",exampleobjectowner=" + adUser.exampleobjectowner + "\n\r")
    if (adUser.found == "Y"):
        matchingUsers.append(adUser)

    adUser = callad_get_user_attributes(this_user, ad_adebp)
    finalresponse.append("ADEBP - callad_get_user_attributes for " + adUser.user_name + " returned: employeetype=" + adUser.employeetype \
        + ",domain=" + adUser.domain + ",employeestatus=" + adUser.employeestatus + ",found=" + adUser.found \
        + ",displayname=" + adUser.displayname + ",email=" + adUser.email + ",exampleobjectowner=" + adUser.exampleobjectowner + "\n\r")
    if (adUser.found == "Y"):
        matchingUsers.append(adUser)

    # Warning the client if this user is in more than 1 domain.
    if (len(matchingUsers) > 1):
        list_domains = ""
        for thisUser in matchingUsers:
            list_domains = list_domains + ", " + thisUser.search_domain + " (" + thisUser.domain + ")"
        finalresponse.append("WARNING - This user is a member of multiple domains: " + list_domains[2:] + ". Only the 1st domain will be used for Confluence/JIRA authentication.")

    #..........
    # If the user was found in at least 1 AD then we can continue else we must stop (user not found in AD)
    continue_processing = 1
    if (len(matchingUsers) > 0):
        finalresponse.append("SUCCESS - User successfully located in AD domain " + matchingUsers[0].domain + ". Processing can continue.")
    else:
        finalresponse.append("FAILURE - User not located in any AD domain. Processing cannot continue.")
        continue_processing = 0
        
    #..........
    # Given domain and employeetype, determine what group the user should be in. Attempt to add the user to that group
    if (continue_processing == 1):
        if (this_action == "jira" or this_action == "both"):
            group_name = get_domain_group_name(matchingUsers[0].domain, matchingUsers[0].employeetype, "jira")
            #finalresponse.append ("NEXT STEP? callad_add_user_to_group for group=" + group_name + " because domain=" + matchingUsers[0].domain + " and employeetype=" + matchingUsers[0].employeetype + ".")
            if (group_name > ""):
                finalresponse.append(callad_add_user_to_group(group_name, matchingUsers[0].domain, this_user))
        if (this_action == "confluence" or this_action == "both"):
            group_name = get_domain_group_name(matchingUsers[0].domain, matchingUsers[0].employeetype, "confluence")
            #finalresponse.append ("NEXT STEP? callad_add_user_to_group for group=" + group_name + " because domain=" + matchingUsers[0].domain + " and employeetype=" + matchingUsers[0].employeetype + ".")
            if (group_name > ""):
                finalresponse.append(callad_add_user_to_group(group_name, matchingUsers[0].domain, this_user))

    #.........
    # Call SQL to get key Jira info about this user. If the user is not active, then re-act
    if (continue_processing == 1 and (call_type == "jira" or call_type == "both")):
        jira_api_result = handle_jira_user_lookup_and_reactivation(this_user)
    if (continue_processing == 1 and (call_type == "confluence" or call_type == "both")):
        confluence_api_result = handle_confluence_user_lookup_and_reactivation(this_user)

    #.........
    # Wrap it up - write log/aduit entries. email user.
    finalresponse.append(final_housekeeping(matchingUsers[0].email))

    return("SUCCESS")

#---------------
# MAIN
main_result = handle_this_request(target_user, call_type)

#---------------
# TO-DO!!!! finalresponse needs to return to client. Use JSON, add a status_code and put this into a messages node. Include other data that matches sense.
print("\r\n\r\n\r\n...finalresponse list will be sent back to client as json - act like client and iterate the list:")
for msg in finalresponse:
    print("> " + msg)

print("end")
