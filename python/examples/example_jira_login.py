from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()
driver.get('https://jira-preprod.example.com/secure/Dashboard.jspa')

#elem.send_keys(Keys.RETURN)
#driver.switchTo().alert().accept();
alert = driver.switch_to_alert()
alert.accept()

#assert "Google" in driver.title
elem = driver.find_element_by_name("os_username")
elem.clear()
elem.send_keys("YOUREXAMPLEID")
elemp = driver.find_element_by_name("os_password")
elemp.send_keys("YOURPASSWORD")
time.sleep(5)
#elemp.send_keys(Keys.RETURN)
driver.find_element_by_name('login').click()
time.sleep(30)

#assert "No results found." not in driver.page_source
driver.get('https://jira-preprod.example.com/plugins/servlet/eazybi/accounts/29/source_data#source_applications')
driver.find_element_by_class_name('action_import').click()
time.sleep(10)

driver.close()


#can't find import button = print("<id> - import button not found")
#import button failed to click correctly = print("<id> - button failed to click")
#button click success = print("<id> - success")
