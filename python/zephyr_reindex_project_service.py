from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

#Variables
user = "NAZAJO3"
admin = "YOUREXAMPLEID"
pwd = "YOURPASSWORD"
baseurl = "https://jira-archive.example.com"

#List of projects ... should be from a file or some other generated source
projects = ['CIP', 'FBIV_BITS']

#Main
print("!!Start script!!")
driver = webdriver.Chrome()
driver.get(baseurl + '/secure/admin/ViewApplicationProperties.jspa')

#elem.send_keys(Keys.RETURN)
#driver.switchTo().alert().accept();
alert = driver.switch_to_alert()
alert.accept()

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
elemp = driver.find_element_by_name("webSudoPassword")
elemp.send_keys(pwd)
time.sleep(5)
elemp.send_keys(Keys.RETURN)
#driver.find_element_by_id('login-form-submit').click()
time.sleep(5)

#Navigate to the Zephyr re-index page
print("before Zephyr page load")
driver.get(baseurl + '/secure/admin/ZephyrGeneralConfiguration!default.jspa')
print("after Zephyr page load")
time.sleep(5)
#...then click tab with id=aui-uid-2 to get the Re-index dialog
driver.find_element_by_id('aui-uid-2').click()
print("after Re-index tab click")
time.sleep(5)
elemp = driver.find_element_by_id("zephyr-reindex-project-field")
for project in projects:
        elemp.send_keys(project)
        time.sleep(2)
        elemp.send_keys(Keys.ENTER)
        time.sleep(5)

print("after pick project")
driver.find_element_by_id('zephyr-index-all').click()
print("after re-index click")
time.sleep(1000)

#assert "No results found." not in driver.page_source
#driver.get(baseurl + '/plugins/servlet/eazybi/accounts/29/source_data#source_applications')
#driver.find_element_by_class_name('action_import').click()
#time.sleep(10)

driver.close()
print("!!End script!!")


