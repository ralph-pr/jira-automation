from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

#Variables
admin = "YOURJIRAUSER"
pwd = "YOURJIRAPWD"
#baseurl = "https://confluence-test.example.com"
baseurl = "https://confluence-test.example.com"

#Main
driver = webdriver.Chrome()

# establish a global variable that will be used to control 1st call activities
firsttime = "Y" 

#-- Start "per iteration" loop (by user in this case) --
def processthisuser(user):
    #driver.get(baseurl + '/admin/users/reactivateuser.action?username=' + user)
    driver.get(baseurl + '/admin/users/deactivateuser.action?username=' + user)

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
        time.sleep(15)

        #Handle the Admin Authorization
        elemp = driver.find_element_by_name("password")
        elemp.send_keys(pwd)
        time.sleep(5)
        #elemp.send_keys(Keys.RETURN)
        driver.find_element_by_name('authenticate').click()
        time.sleep(15)
        #turn off the flag
        firsttime = "N"

    #Click the Confirm button
    driver.find_element_by_name('confirm').click()
    time.sleep(15)
#-- End "per iteration" loop (by user in this case) --

processthisuser("AAM17MD")
processthisuser("AAMIRAB")

driver.close()


