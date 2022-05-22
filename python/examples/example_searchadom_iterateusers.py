import os
import json
import datetime
import sys
import pymssql
import requests
import string

MSQLServer,MSSQLPort,MSSQLUser,MSSQLPassword,MSSQLDatabaseName="jira-test.lnekj4knch1aw.us-east-1.rds.amazonaws.com",1433,"YOURSQLUSER","YOURSQLPASSWORD","jira_test_db"
user='user1'
pw='3edcCDE#'
jirausersAPI='http://jira-test.example.com:7999/rest/scriptrunner/latest/custom/GetUserInfo' 
ADOMGroupCreation = 'https://devopstools.example.com/DevOpsServices/api/adom/group/create'
ADOMGroupAddMembers= 'https://devopstools.example.com/DevOpsServices/api/adom/group/membership/insert'
adminlist=['user1','user2','user3','YOUREXAMPLEID']
def main():
	from requests.auth import HTTPBasicAuth
	headers = {'Content-Type': 'application/json' }
	response=requests.get(jirausersAPI, auth=HTTPBasicAuth(user, pw),headers=headers)
	if response.status_code == 200 or response.status_code == 201:
		strjson=json.loads(response.text)
		f=open('ADOMjiraADEBPMembers.txt','w')
		f1=open('ADOMjiraADEBPMembersFailed.txt','w')
		for apiresp in strjson:
			import ldap
			try:
				
				print(apiresp)			
				userexampleid=apiresp['name']
				print userexampleid
				AD_LDAP_URL="ldap-vendor.example.com"
				AD_SEARCH_DN="OU=Accounts,DC=adebp,DC=examplewcorp,DC=com"
				AD_SEARCH_FIELDS= ['exampleEmployeeType']

				l = ldap.initialize("ldap://"+AD_LDAP_URL+":389")
				ldap.set_option(ldap.OPT_REFERRALS,0)
				l.simple_bind_s("CN=SVC-adebp-cicd-devop,OU=SVC,OU=FNA,DC=adebp,DC=examplewcorp,DC=com", "ldap-user-pwd-goes-here")
				
				result=l.search_ext_s(AD_SEARCH_DN,ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % userexampleid,AD_SEARCH_FIELDS)[0][1]
				print result
				employeetype=result['exampleEmployeeType'][0]
				print(employeetype)
				if employeetype=='Employee':
					AddmemberstoADOM('ADEBPSDLC_EMPLOYEES','ADEBP',userexampleid)
					f.write(userexampleid+' added to ADEBPSDLC_EMPLOYEES'+'\n')
				elif employeetype=='Contractor':
					AddmemberstoADOM('ADEBPSDLC_CONTRACTORS','ADEBP',userexampleid)
					f.write(userexampleid+' added to ADEBPSDLC_CONTRACTORS'+'\n')
				elif employeetype=='EXAMPLEWNonEmployee':
					AddmemberstoADOM('ADEBPSDLC_BUSPARTNERS','ADEBP',userexampleid)
					f.write(userexampleid+' added to ADEBPSDLC_BUSPARTNERS'+'\n')
				else:
					print('No data found')
					f1.write(userexampleid+' failed to be added'+'\n')
			except:
				exe=str(sys.exc_info()[1])
				print(exe)
		f.close()
		f1.close()
		print('----------------End of result ----------------------------')

		
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
	#f.close()
	#f1.close()
#CreateAdomGroup()
main()
