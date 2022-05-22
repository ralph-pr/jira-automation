from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

#Variables
user = "ENDUSEREXAMPLEID"
admin = "YOURJIRAUSER"
pwd = "YOURJIRAPWD"
#baseurl = "https://confluence-test.example.com"
baseurl = "https://confluence-test.example.com"

#Main
driver = webdriver.Chrome()
driver.get(baseurl + '/admin/users/reactivateuser.action?username=' + user)

#elem.send_keys(Keys.RETURN)
#driver.switchTo().alert().accept();
#alert = driver.switch_to_alert()
#alert.accept()

#Handle the User Login
elem = driver.find_element_by_name("os_username")
elem.clear()
elem.send_keys(admin)
elemp = driver.find_element_by_name("os_password")
elemp.send_keys(pwd)
time.sleep(5)
#elemp.send_keys(Keys.RETURN)
driver.find_element_by_name('login').click()
time.sleep(15)

#Handle the Admin Authorization
elemp = driver.find_element_by_name("password")
elemp.send_keys(pwd)
time.sleep(5)
#elemp.send_keys(Keys.RETURN)
driver.find_element_by_name('authenticate').click()
time.sleep(15)

#Click the Confirm button
driver.find_element_by_name('confirm').click()
time.sleep(15)

#assert "No results found." not in driver.page_source
#driver.get(baseurl + '/plugins/servlet/eazybi/accounts/29/source_data#source_applications')
#driver.find_element_by_class_name('action_import').click()
#time.sleep(10)

driver.close()


