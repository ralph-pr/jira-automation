import ldap
import sys

jirausersAPI='http://jira-test.example.com:7999/rest/scriptrunner/latest/custom/GetUserInfo' 
ADOMGroupCreation = 'https://devopstools.example.com/DevOpsServices/api/adom/group/create'
ADOMGroupAddMembers= 'https://devopstools.example.com/DevOpsServices/api/adom/group/membership/insert'
# adminlist=['user1','user2','user3','YOUREXAMPLEID']
def main():
    try:
        userexampleid='userid'
        print(userexampleid)
        AD_LDAP_URL="ldap-vendor.example.com"
        AD_SEARCH_DN="OU=Accounts,DC=adebp,DC=examplewcorp,DC=com"
        AD_SEARCH_FIELDS= ['exampleEmployeeType']

        l = ldap.initialize("ldap://"+AD_LDAP_URL+":389")
        ldap.set_option(ldap.OPT_REFERRALS,0)
        #binddn='CN=SVC-adebp-cicd-devop,OU=SVC,OU=FNA,DC=adebp,DC=examplewcorp,DC=com'+"@"+AD_LDAP_URL
        #l.bind_s(binddn,'ldap-user-pwd-goes-here')
        l.simple_bind_s("CN=SVC-adebp-cicd-devop,OU=SVC,OU=FNA,DC=adebp,DC=examplewcorp,DC=com", "ldap-user-pwd-goes-here")
        
        result=l.search_ext_s(AD_SEARCH_DN,ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % userexampleid,AD_SEARCH_FIELDS)[0][1]
        print(result)
        employeetype=result['exampleEmployeeType'][0]
        print(employeetype)
        if employeetype=='Employee':
            # AddmemberstoADOM('ADEBPSDLC_EXAMPLEEMPLOYEES','ADEBP',userexampleid)
            print(userexampleid+' added to ADEBPSDLC_EXAMPLEEMPLOYEES'+'\n')
        elif employeetype=='Contractor':
            # AddmemberstoADOM('ADEBPSDLC_CONTRACTORS','ADEBP',userexampleid)
            print(userexampleid+' added to ADEBPSDLC_CONTRACTORS'+'\n')
        elif employeetype=='EXAMPLEWNonEmployee':
            # AddmemberstoADOM('ADEBPSDLC_EXAMPLEBUSPARTNERS','ADEBP',userexampleid)
            print(userexampleid+' added to ADEBPSDLC_EXAMPLEBUSPARTNERS'+'\n')
        else:
            print('No data found')
            print(userexampleid+' failed to be added'+'\n')
    except:
        exe=str(sys.exc_info()[1])
        print(exe)
        print('----------------End of result ----------------------------')

main()