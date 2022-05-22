from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

myuser = "YOUREXAMPLEID"
mypwd = "YOURPASSWORD"
baseurl = "https://jira-preprod.example.com"

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
print("start looping")
#iterate a list of itemKey's and call the function per itemKey
itemKey = 3
itemStatus = importthisaccount(str(itemKey))
print(str(itemKey) + " status=" + itemStatus)
itemKey = 400
itemStatus = importthisaccount(str(itemKey))
print(str(itemKey) + " status=" + itemStatus)
itemKey = 60
itemStatus = importthisaccount(str(itemKey))
print(str(itemKey) + " status=" + itemStatus)
print("end looping")

driver.close()


#assert "No results found." not in driver.page_source
#can't find import button = print("<id> - import button not found")
#import button failed to click correctly = print("<id> - button failed to click")
#button click success = print("<id> - success")
