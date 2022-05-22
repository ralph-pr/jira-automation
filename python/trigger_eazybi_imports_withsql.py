from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pyodbc 

myuser = "YOUREXAMPLEID"
mypwd = "YOURPASSWORD"
#baseurl = "https://jira-preprod.example.com"
#baseurl = "https://144.70.115.154:8090"
baseurl = "https://jira.baseurl.com"

print("!!Start script!!")
#driver.find_element_by_css_selector('.button.c_button.s_button').click()

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
#server = 'onejiramssqleazybipreprodwest.cbhxxwrpq3pu.us-west-2.rds.amazonaws.com' 
#driver = 'SQL Server Native Client 11.0'
#database = 'eazybi_stage' 
driver = "PostgreSQL Unicode"
#server = 'onejirapostgrespreprodwest.cbhxxwrpq3pu.us-west-2.rds.amazonaws.com' 
#server = 'onejira-preprod-west-stagexml-postgre.cbhxxwrpq3pu.us-west-2.rds.amazonaws.com'
server = 'onejirapostgreeazybiprodwest.cbhxxwrpq3pu.us-west-2.rds.amazonaws.com'
database = 'eazybi_prod_west' 
username = 'YOURSQLLOGIN' 
password = 'YOURSQLPASSWORD'
conn_str = (
    "DRIVER={"+driver+"};"
    "DATABASE="+database+";"
    "UID="+username+";"
    "PWD="+password+";"
    "SERVER="+server+";"
    "PORT=5432;"
    )
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()

driver = webdriver.Chrome()
driver.get(baseurl + '/secure/Dashboard.jspa')

#elem.send_keys(Keys.RETURN)
#driver.switchTo().alert().accept();
alert = driver.switch_to_alert()
alert.accept()

#assert "Google" in driver.title
elem = driver.find_element_by_name("os_username")
elem.clear()
elem.send_keys(myuser)
elemp = driver.find_element_by_name("os_password")
elemp.send_keys(mypwd)
time.sleep(5)
#elemp.send_keys(Keys.RETURN)
driver.find_element_by_name('login').click()
time.sleep(30)

#Define the atomic function that will be called per list item
def importthisaccount(id):
    finalstatus = ""
    try:
        print("importing account ID=" + str(id))
        driver.get(baseurl + '/plugins/servlet/eazybi/accounts/' + str(id) + '/source_data#source_applications')
        #driver.find_element_by_class_name('action_import').click()
        importbtns = driver.find_elements_by_class_name('action_import')
        for x in range(0,len(importbtns)):
            if importbtns[x].is_displayed():
                importbtns[x].click()
                print("...click")
            else:
                print("...no click")

        time.sleep(1)
        finalstatus = "success"
    except:
        finalstatus = "failed"
    return(finalstatus)

#Start of the loop
cursor.execute("select DISTINCT a.id from source_applications ap inner join source_application_cubes ac on ac.source_application_id = ap.id inner join source_cubes c on c.id = ac.source_cube_id inner join accounts a on a.id = c.account_id where ap.application_type = 'jira_local' and c.last_import_at is null and ap.error_message = 'Was waiting on import too long time' and a.name != 'Proquest_Metrics' order by a.id") 
#cursor.execute("select DISTINCT a.id from source_applications ap inner join source_application_cubes ac on ac.source_application_id = ap.id inner join source_cubes c on c.id = ac.source_cube_id inner join accounts a on a.id = c.account_id where ap.application_type = 'jira_local' and c.last_import_at is null and a.name != 'Proquest_Metrics' order by a.id") 
row = cursor.fetchone() 
while row: 
    #iterate a list of itemKey's and call the function per itemKey
    itemKey = row[0]
    itemStatus = importthisaccount(str(itemKey))
    print(str(itemKey) + " status=" + itemStatus)
    row = cursor.fetchone()

driver.close()
print("!!End script!!")

