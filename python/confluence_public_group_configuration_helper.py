from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
import pyodbc
from collections import namedtuple
from JsonToDictionary import getconfigdictionary
import os
from collections import OrderedDict
from selenium.common.exceptions import NoSuchElementException

print(datetime.datetime.now().strftime("%a, %d %B %Y %H:%M:%S") +" - starting...")

#----------------------------------------------------------------------
# Read the configuration file. Avoid hard-coding values in this script.
# By default, the configuration is in the .config file of the same name as this .py file
configfilename = os.path.basename(__file__).replace(".py",".config")    #preprod_ralph.config
configuration = getconfigdictionary(configfilename)
print(configuration)
print("")

#---------------------------------------
# Configure the UI/API connection
admin = configuration["uiuser"]
pwd = configuration["uipassword"]
baseurl = configuration["baseurl"]

#---------------------------------------
# Configure the database connection
dbserver = configuration["sqlserver"]
database = configuration["sqldatabase"]
username = configuration["sqluser"]
password = configuration["sqlpassword"]
# The SQL SELECT statement provides the list of SPACEKEY values. This drives the list of spaces to be modified.
sqlselect = configuration["sqlselect"]

#---------------------------------------
# These are the permissions that can be given to a group. They are represented by checkboxes on a row for each "group" in the UI. The checkboxes can be located using permssion+group name.
listPermissions = configuration["listPermissions"]
# These are the groups that must be removed from the projects.
listOldGroups = configuration["listOldGroups"]
# These are the new "public" ODC groups that must be added to the projects
listNewGroups = configuration["listNewGroups"]

#---------------------------------------
# Translate the strings into list objects
print("!!! Add Selenium and iterate oldGroups x Permissions!!!")
permissions = listPermissions.split(",")
oldGroups = listOldGroups.split(",")
newGroups = listNewGroups.split(",")
#spacekeys = listSpaces.split(",")

#Start up the Chrome webdriver
driver = webdriver.Chrome()

# establish a global variable that will be used to control 1st call activities
firsttime = "Y" 

#-- Start "per iteration" loop (by user in this case) --
def processthisspace(spacekey):
    print("")
    print("")
    print("----------- PROCESSING SPACE = " + spacekey + " @ " + datetime.datetime.now().strftime("%a, %d %B %Y %H:%M:%S") + " -------------------------")
    print("")
    print("---Start Step 1: Produce the unique list of public permissions. Turn off existing permissions on the old groups. ---")
    #driver.get(baseurl + '/admin/users/reactivateuser.action?username=' + user)
    driver.get(baseurl + '/spaces/editspacepermissions.action?key=' + spacekey + '&edit=Edit+Permissions')

    # the 1st time thru, we need to login and elevate. We use a global variable for this flag.
    global firsttime
    if (firsttime == "Y"):
        #Handle the User Login
        elem = driver.find_element_by_name("os_username")
        elem.clear()
        elem.send_keys(admin)
        elemp = driver.find_element_by_name("os_password")
        elemp.send_keys(pwd)
        time.sleep(5)
        #elemp.send_keys(Keys.RETURN)
        driver.find_element_by_name('login').click()
        time.sleep(5)

        #Handle the Admin Authorization
        elemp = driver.find_element_by_name("password")
        elemp.send_keys(pwd)
        time.sleep(5)
        #elemp.send_keys(Keys.RETURN)
        driver.find_element_by_name('authenticate').click()
        time.sleep(5)
        #turn off the flag
        firsttime = "N"

    # Step 1: Establish the list of public permissions by going to the EditPermissions page for this <space> then iterating oldGroups x Permissions = publicPermissions
    publicPermissions = []
    for oldGroup in oldGroups[:]:
        if oldGroup != "anonymous":
            oldGroup = "group_" + oldGroup.strip()

        for permission in permissions[:]:
            try:
                elem = driver.find_element_by_name("confluence_checkbox_" + permission.strip() + "_" + oldGroup)
                if elem.get_attribute("checked") is None:
                    checked = "false"
                else:
                    checked = elem.get_attribute("checked")
                #print("...checkbox " + elem.get_attribute("name") + " = " + checked)
                if checked == "true":
                    publicPermissions.append(permission.strip())
                    # click on the element to turn OFF this permission on the old group.
                    elem.click()
            except:
                pass  #print("exception! ... probably confluence-users <tr> not found")
      
    print("---End Step 1: Produce the unique list of public permissions. Turn off existing permissions on the old groups. ---")
    for key in list(OrderedDict.fromkeys(publicPermissions))[:]:
        print("PUBLIC PERMISSION AUDIT: Space = " + spacekey + ", Permission = " + key + " should show up on the ODC AD groups after this script completes.")

    # Step 2: For each new group, decide if the group (<tr>) is already on the page. If not then add it.
    print("---Start Step 2: For each new group, decide if the group (<tr>) is already on the page. If not then add it. ---")
    for newGroup in newGroups[:]:
        try:
            elem = driver.find_element_by_name("confluence_checkbox_viewspace_group_" + newGroup.strip())
        except NoSuchElementException:
            print("Adding the missing group - " + newGroup.strip())
            driver.find_element_by_name("groupsToAdd").send_keys(newGroup.strip())
            driver.find_element_by_name("groupsToAddButton").click()

        #Iterate the public permissions and ensure they are turned on
        for permission in publicPermissions:
            elem = driver.find_element_by_name("confluence_checkbox_" + permission.strip() + "_group_" + newGroup.strip())
            if elem.get_attribute("checked") is None:
                elem.click()

    print("---End Step 2: For each new group, decide if the group (<tr>) is already on the page. If not then add it. ---")

    # Step 3: Click the Save button to complete the changes to this space.
    print("---Start Step 3: Click the Save button to complete the changes to this space. ---")
    driver.find_element_by_name("save").click()
    print("---End Step 3: Click the Save button to complete the changes to this space. ---")

    # Step 4: Report end of space status/metrics.
    #print("Report end of space status/metrics.")
#-- End "per iteration" loop (by user in this case) --

#-----------------------------------------
# MAIN: Establish a SQL connection, get the list of spaces, iterate them and call the function to set the groups for each space.
conn_str = (
    "DRIVER={SQL Server Native Client 11.0};"
    "DATABASE="+database+";"
    "UID="+username+";"
    "PWD="+password+";"
    "SERVER="+dbserver+";"
    "PORT=5432;"
    )
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()

cursor.execute(sqlselect) 
rdef = namedtuple('dataset', ' '.join([x[0] for x in cursor.description])) 
for r in map(rdef._make, cursor.fetchall()): 
    processthisspace(r.SPACEKEY)

driver.close()

print(datetime.datetime.now().strftime("%a, %d %B %Y %H:%M:%S") +" - finished.")

