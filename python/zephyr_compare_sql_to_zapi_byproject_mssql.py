#import psycopg2 
import pyodbc 
import requests
import base64

print("!!Start script!!")
#driver.find_element_by_css_selector('.button.c_button.s_button').click()

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
#server = 'onejiramssqlprodwest.cbhxxwrpq3pu.us-west-2.rds.amazonaws.com' 
#database = 'onejira_DB_Prod_west' 
server = 'jiraarchivalproduction.c5ogzsgipyri.us-east-1.rds.amazonaws.com' 
database = 'oneajira_preprod_east_zephyr32357' 
username = 'YOURSQLLOGIN' 
password = 'YOURSQLPASSWORD'
driver = 'SQL Server Native Client 11.0'

jirauser = "YOURJIRALOGIN"
jirapwd = "YOURJIRAPASSWORD"
#Jira/Zephyr API calls use base64 encoded credentials in the header. Create the string to be used as that header.
encodedCredentials = base64.b64encode(str.encode(jirauser + ":" + jirapwd)).decode('utf-8')
                      
def getexecutioncount(pkey):
    global encodedCredentials
    #print(encodedCredentials)
    url = "https://jira-preprod.example.com/rest/zapi/latest/zql/executeSearch?zqlQuery=project=" + pkey
    resp = requests.get(url, 
                    headers={"Authorization": "Basic %s" % encodedCredentials})

    if resp.status_code != 200:
        # This means something went wrong.
        #raise APIError('GET /tasks/ {}'.format(resp.status_code))
        return -1
    #print(resp.status_code)
    #print(resp.json()['totalCount'])
    try:
        return resp.json()['totalCount']
    except:
        return -2

conn_str = (
    "DRIVER={"+driver+"};"
    "DATABASE="+database+";"
    "UID="+username+";"
    "PWD="+password+";"
    "SERVER="+server+";"
    "PORT=1433;"
    )
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()

#...3 is the acctID https://jira-preprod.example.com/plugins/servlet/eazybi/accounts/<id>/source_data#source_applications
#Sample select query
#cursor.execute("SELECT @@version;") 
cursor.execute("SELECT p.pkey,min(p.pname) AS pname,count(*) as executions FROM [AO_7DEABF_SCHEDULE] s left join jiraissue i on s.[ISSUE_ID] = i.id inner join project p on p.id = i.project group by p.pkey order by 3 desc") 
row = cursor.fetchone() 
while row: 
    print(row[0] + "~" + row[1] + "~" + str(row[2]) + "~" + str(getexecutioncount(row[0])))
    row = cursor.fetchone()

print("!!End script!!")
