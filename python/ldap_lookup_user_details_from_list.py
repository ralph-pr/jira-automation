#!/usr/bin/python
import os
import json
import datetime
import sys
import pymssql
import requests
import string
import ldap
import pyodbc
import datetime
import smtplib
import string
from datetime import datetime
import smtplib

def GetBacklistedUsers():
    user_name="SVC-DevOpsLoadTest"
    user_passwd="svc-password-goes-here"
    url = "https://confluence.example.com/rest/extender/1.0/group/getUsers/SDLC_BLACKLISTED_USERS"
    headers = {'Content-type': 'application/json'}
    response=requests.get(url,headers=headers,verify=False, auth=(user_name, user_passwd))
    u=json.loads(response.text)
    mydict=u["users"]
    backlist=[]
    for item in mydict:
     for key in item:
         backlist.append(key)
    print(backlist)
    return backlist

date=datetime.now().strftime('%Y%m%d')

print('----------------Truncating the CHILD Table ----------------------------')
#con1 = pymssql.connect(host='mssql.dns', port=1433, user='mssql_user',password='mssql_pwd',database='confluence_prod')
con1 = pymssql.connect(host='confluence-prod-west.knac4x9ekaui.us-west-2.rds.amazonaws.com', port=1433, user='mssql_user',password='mssql_pwd',database='confluence_prod')
cur1 = con1.cursor()
querystring1 = "TRUNCATE TABLE oneconfluence_uswin_child_table"
cur1.execute(querystring1)
con1.commit()
cur1.close()
con1.close()
print('----------------Truncating the CHILD Table done ----------------------------')

#print('----------------Truncating the MASTER Table ----------------------------')
#con16 = pyodbc.connect("DRIVER={ODBC Driver 13 for SQL Server};server=10.77.169.168;database=onestash_production_security_change;uid=db-user;pwd=pwd-goes-here")
#cur16 = con16.cursor()
#querystring16 = "TRUNCATE TABLE oneconfluence_uswin_master_table"
#cur16.execute(querystring16)
#con16.commit()
#cur16.close()
#con16.close()
#print('----------------Truncating the MASTER Table done ----------------------------')


ADOMGroupCreation = 'https://lambda.example.com/DevOpsServices/api/adom/group/create'
ADOMGroupAddMembers = 'https://lambda.example.com/DevOpsServices/api/adom/group/membership/insert'

def child ():
	#con2 = pymssql.connect(host='10.77.169.168', port=1433, user='db-user',password='pwd-goes-here',database='confluence_prod') #production
	con2 = pymssql.connect(host='confluence-prod-west.knac4x9ekaui.us-west-2.rds.amazonaws.com', port=1433, user='mssql_user',password='mssql_pwd',database='confluence_test')
        cur2 = con2.cursor()
	querystring2 = "select a.user_name, a.display_name,b.directory_name from cwd_user a inner join cwd_directory b on a.directory_id=b.id inner join cwd_membership c on a.id=c.child_user_id where b.id in (9502723) and c.parent_id in (select id from cwd_group  where group_name='confluence-users' and display_name not like 'SVC%')"
        #querystring2 = "select a.user_name, a.display_name,b.directory_name from cwd_user a inner join cwd_directory b on a.directory_id=b.id inner join cwd_membership c on a.id=c.child_user_id where b.id in (9502723) and c.parent_id in (select id from cwd_group  where group_name='confluence-users' and display_name not like 'SVC%' and display_name not in ('D''souza, Stanley','O''Neill','O''Neill, Cecilia (Celia)','O''Day, Patrick M (Pat)','O''Brien, Connor','O''Connell, Joseph Adrian (Adrian)','O''Neill, William M  (AZ)','D''Silva, Jeffrey W'))"
        cur2.execute(querystring2)
	print('----------------Inserting Users into the CHILD Table Going on ----------------------------')
        for row in cur2:
            try:
                        userexampleid=(row[0])
                        display_name=(row[1])
                        directory_name=(row[2])
                        #print(userexampleid+","+display_name+","+directory_name)
                        con3 = pymssql.connect(host='confluence-prod-west.knac4x9ekaui.us-west-2.rds.amazonaws.com', port=1433, user='mssql_user',password='mssql_pwd',database='confluence_prod')
                        cur3 = con3.cursor()
                        querystring3 = "insert into oneconfluence_uswin_child_table (user_name,display_name, directory_name) values ('{0}','{1}','{2}')".format(userexampleid,display_name,directory_name)
                        cur3.execute(querystring3)
                        con3.commit()
                        cur3.close()
        		con3.close()
            except:
			print("\nUnable to run the inserts forthe below uer : "+ userexampleid) 
			
	cur2.close()
	con2.close()
	print('----------------Inserting Users into the CHILD Table Done ----------------------------')

def mastr ():
        #con4 = pyodbc.connect("DRIVER={ODBC Driver 13 for SQL Server};server=10.99.99.99;database=devops_db;uid=devops_user;pwd=devops_pwd")
	con4 = pymssql.connect(host='confluence-prod-west.knac4x9ekaui.us-west-2.rds.amazonaws.com', port=1433, user='mssql_user',password='mssql_pwd',database='confluence_prod')
        cur4 = con4.cursor()
        #querystring4 = "SELECT a.user_name, a.display_name, a.directory_name FROM oneconfluence_uswin_child_table a left JOIN oneconfluence_uswin_master_table b ON a.user_name = b.user_name WHERE a.user_name IS NULL OR b.user_name IS NULL"
	querystring4 = "SELECT a.user_name, a.display_name, a.directory_name FROM oneconfluence_uswin_child_table a left JOIN oneconfluence_uswin_master_table b ON a.user_name = b.user_name WHERE ( a.user_name IS NULL OR b.user_name IS NULL ) and a.user_name not in (select user_name from uswin_inactive_users)"
        cur4.execute(querystring4)
        print('----------------Inserting Users into the MASTER Table Going on ----------------------------')
	f1=open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLEXAMPLEEMPLOYEES_Members'+date+'.txt','w')
	f2=open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLCONTRACTORS_Members'+date+'.txt','w')
	f3=open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLEXAMPLEBUSPARTNERS_Members'+date+'.txt','w')
	f4=open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLEXTLBUSPARTNERS_Members'+date+'.txt','w')
	f5=open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_SCMMembersFailed'+date+'.txt','w')
	f6=open('/apps/opt/odc_access_restriction/oneconfluence/uswin/USWIN_Users_REMOVED_FROM_Stash_Users'+date+'.txt','w')
	f7=open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_BLACKLISTED_USERS'+date+'.txt','w')
	sqlcon = pymssql.connect(host='oneconfluenceprodwest.cbhxxwrpq3pu.us-west-2.rds.amazonaws.com', port=1433, user='devopsdbadmin',password='YOURPWD',database='confluence_odc_production')
	print('confluence-new-users members:')
        backlistusers=[]
        backlistusers=GetBacklistedUsers()
        print("BlackListedUsers:"+str(backlistusers))
        for row4 in cur4:
		 try:
                         userexampleid=(row4[0])
			 display_name=(row4[1])
			 directory_name=(row4[2])
			 if userexampleid in backlistusers:
                            f7.write(userexampleid+' member of SDLC_BLACKLISTED_USERS AD group'+'\n')
                         else:
                            print('normal user')
			    US_AD_LDAP_URL="ldap-us.example.com"
			    booleanFlag=True
			    US_AD_SEARCH_DN="DC=uswin,DC=ad,DC=examplewcorp,DC=com"
			    US_AD_SEARCH_FIELDS= ['exampleEmployeeType']
			    ul = ldap.initialize("ldap://"+US_AD_LDAP_URL+":389")
			    ldap.set_option(ldap.OPT_REFERRALS,0)
			    ul.simple_bind_s("SVC-uswin-cicd-devop", "dU0jY0kdU0jY0kdU0jY0dU0jY0kd")
			    result=ul.search_ext_s(US_AD_SEARCH_DN,ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % userexampleid,US_AD_SEARCH_FIELDS)[0][1]
			    employeetype=result['exampleEmployeeType'][0]
			    print(employeetype)			
			    if employeetype=='Employee' and directory_name=='USWIN - Delegated LDAP Authentication':
                                   AddmemberstoADOM('SDLC_COLEXAMPLEEMPLOYEES','USWIN',userexampleid)
                                   f1.write(userexampleid+' added to SDLC_COLEXAMPLEEMPLOYEES'+'\n')
				   cur5 = sqlcon.cursor()
				   cur5.callproc('sp_uswin_master_table_insert',(userexampleid,display_name,directory_name,employeetype,'Yes'))
				   sqlcon.commit()
				   cur5.close()
                            elif employeetype=='Contractor' and directory_name=='USWIN - Delegated LDAP Authentication':
                                   AddmemberstoADOM('SDLC_COLCONTRACTORS','USWIN',userexampleid)
                                   f2.write(userexampleid+' added to SDLC_COLCONTRACTORS'+'\n')
				   cur6 = sqlcon.cursor()
				   cur6.callproc('sp_uswin_master_table_insert',(userexampleid,display_name,directory_name,employeetype,'Yes'))
				   sqlcon.commit()
				   cur6.close()
                            elif employeetype=='EXAMPLEWNonEmployee' and directory_name=='USWIN - Delegated LDAP Authentication':
                                   AddmemberstoADOM('SDLC_COLEXAMPLEBUSPARTNERS','USWIN',userexampleid)
                                   f3.write(userexampleid+' added to SDLC_COLEXAMPLEBUSPARTNERS'+'\n')
				   cur7 = sqlcon.cursor()
				   cur7.callproc('sp_uswin_master_table_insert',(userexampleid,display_name,directory_name,employeetype,'Yes'))
				   sqlcon.commit()
				   cur7.close()
                            elif employeetype=='ExternalBusinessPartner' or  employeetype=='External' or employeetype=='Rehire' and directory_name=='USWIN - Delegated LDAP Authentication':
                                   AddmemberstoADOM('SDLC_COLEXTLBUSPARTNERS','USWIN',userexampleid)
                                   f4.write(userexampleid+' added to SDLC_COLEXTLBUSPARTNERS'+'\n')
				   cur8 = sqlcon.cursor()
				   cur8.callproc('sp_uswin_master_table_insert',(userexampleid,display_name,directory_name,employeetype,'Yes'))
				   sqlcon.commit()
				   cur8.close()

                            else:
                                 print('No data found')
                                 f5.write(userexampleid+' failed to be added'+'\n')

		 except:
			 #print(userexampleid)
			 exe=str(sys.exc_info()[1])
			 f5.write(userexampleid+ ' -- '+exe+'\n')
			 print(exe)
			 #print "Unable to add"	
		
				
	f1.close()
	f2.close()
	f3.close()
	f4.close()
	f5.close()
	f6.close()
        cur4.close()
        con4.close()
	sqlcon.commit()
	sqlcon.close()
        print('----------------Inserting Users into the MASTER Table Done ----------------------------')

def AddmemberstoADOM(grpname,domain,exampleid):
        adomheaders = {'Content-Type': 'application/json;charset=utf-8' }
        test=[]


        if exampleid !='':
                memdata={}
                memdata["MemberDomainName"]=domain
                memdata["MemberSamAccountName"]=exampleid
        test.append(memdata)
        print('Adding Members for the created Adom group for '+grpname)
        if test:
                data = {}
                data['GroupDomainName'] = domain
                data['GroupSamAccountName']=grpname
                data['Membership']=test
                data['AuthenticationKey']='SFxfT8tQ0kii9U9PGAypTJFscTt7JTOr'
                print(json.dumps(data))
                response=requests.post(ADOMGroupAddMembers, headers=adomheaders, data=json.dumps(data))
                if response.status_code == 200:
                        #f.write(exampleid+' added to '+grpname+'\n')
                        print(str(response.json()))
                        print('Done adding memeber for the Adom group '+grpname)
                        BoolFlag=True
                else:
                        #f1.write(exampleid+' failed to be added under '+grpname+'\n')
                        print(str(response.json()))
                        print('Failed adding members for the Adom group '+grpname)
                        BoolFlag=False

child()
mastr()
USWIN_exampleemployee_count = len(open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLEXAMPLEEMPLOYEES_Members'+date+'.txt', 'r').read().splitlines())
USWIN_exampleemployee = open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLEXAMPLEEMPLOYEES_Members'+date+'.txt', 'r')
USWIN_exampleemployee_cotent = USWIN_exampleemployee.read()

USWIN_contractor_count = len(open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLCONTRACTORS_Members'+date+'.txt', 'r').read().splitlines())
USWIN_contractor = open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLCONTRACTORS_Members'+date+'.txt', 'r')
USWIN_contractor_cotent = USWIN_contractor.read()

USWIN_examplebuspartner_count = len(open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLEXAMPLEBUSPARTNERS_Members'+date+'.txt', 'r').read().splitlines())
USWIN_examplebuspartner = open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLEXAMPLEBUSPARTNERS_Members'+date+'.txt', 'r')
USWIN_examplebuspartner_cotent = USWIN_examplebuspartner.read()

USWIN_exterbuspartner_count = len(open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLEXTLBUSPARTNERS_Members'+date+'.txt', 'r').read().splitlines())
USWIN_exterbuspartner = open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_COLEXTLBUSPARTNERS_Members'+date+'.txt', 'r')
USWIN_exterbuspartner_cotent = USWIN_exterbuspartner.read()

USWIN_failedtoadd_count = len(open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_SCMMembersFailed'+date+'.txt', 'r').read().splitlines())
USWIN_failedtoadd = open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_SCMMembersFailed'+date+'.txt', 'r')
USWIN_failedtoadd_cotent = USWIN_failedtoadd.read()

USWIN_remove_stash_users_count = len(open('/apps/opt/odc_access_restriction/oneconfluence/uswin/USWIN_Users_REMOVED_FROM_Stash_Users'+date+'.txt', 'r').read().splitlines())
USWIN_remove_stash_users = open('/apps/opt/odc_access_restriction/oneconfluence/uswin/USWIN_Users_REMOVED_FROM_Stash_Users'+date+'.txt', 'r')
USWIN_remove_stash_users_cotent = USWIN_remove_stash_users.read()

SDLC_BLACKLISTED_USERS_count = len(open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_BLACKLISTED_USERS'+date+'.txt', 'r').read().splitlines())
SDLC_BLACKLISTED_USERS = open('/apps/opt/odc_access_restriction/oneconfluence/uswin/SDLC_BLACKLISTED_USERS'+date+'.txt', 'r')
SDLC_BLACKLISTED_USERS_cotent = SDLC_BLACKLISTED_USERS.read()
def Notifyusers():


        SUBJECT = "Oneconfluence-Report - Users Insertion into ADOM Group : USWIN-Domain"
        FROM = "DevOpsMigrationSupport@org.example.com"
	TOrecipients = ['confluence.support.team@example.com', 'john.smith@example.com']
        text = "Number of Users added to SDLC_COLEXAMPLEEMPLOYEES----------------------------"+str(USWIN_exampleemployee_count)+"\n" + \
             "                                                                                  "+"\n" + \
	     USWIN_exampleemployee_cotent+"\n" +\
            "                                                                                  "+"\n" + \
             "Number of Users added to SDLC_COLCONTRACTORS--------------------------- "+str(USWIN_contractor_count)+"\n" + \
             "                                                                                  "+"\n" + \
	     USWIN_contractor_cotent+"\n" +\
             "                                                                                  "+"\n" + \
             "Number of Users added to SDLC_COLEXAMPLEBUSPARTNERS--------------------------"+str(USWIN_examplebuspartner_count)+"\n" + \
             "                                                                                  "+"\n" + \
	     USWIN_examplebuspartner_cotent+"\n" +\
             "                                                                                  "+"\n" + \
             "Number of Users added to SDLC_COLEXTLBUSPARTNERS--------"+str(USWIN_exterbuspartner_count)+"\n" + \
             "                                                                                  "+"\n" +\
             USWIN_exterbuspartner_cotent+"\n" +\
             "                                                                                  "+"\n" + \
             "Failed to Add User------------------------------------------------"+str(USWIN_failedtoadd_count)+"\n" + \
	     USWIN_failedtoadd_cotent+"\n" +\
             "                                                                                  "+"\n" +\
             "USWIN-confluence Users are removed from confluence-users after added to AD group"+str(USWIN_remove_stash_users_count)+"\n" +\
	     USWIN_remove_stash_users_cotent+"\n" +\
	     "SDLC_BLACKLISTED_USERS should not be added to AD groups---"+str(SDLC_BLACKLISTED_USERS_count)+"\n" + \
              SDLC_BLACKLISTED_USERS_cotent

        BODY = string.join((
        "From: %s" % FROM,
        "To: %s" % TOrecipients,
        "Subject: %s" % SUBJECT ,
        "",
        text
        ), "\r\n")

        try:
                smtpObj = smtplib.SMTP('smtp.example.com', 25)
                smtpObj.sendmail(FROM, TOrecipients, BODY)
                print "Successfully sent email"
                smtpObj.quit()
        except SMTPException:
                print "Eror: Unable to send out email"
if USWIN_exampleemployee_count!=0 or USWIN_contractor_count!=0 or USWIN_examplebuspartner_count!=0 or USWIN_exterbuspartner_count!=0 or USWIN_failedtoadd_count!=0 or USWIN_remove_stash_users_count!=0 or SDLC_BLACKLISTED_USERS_count!=0:
   Notifyusers()

