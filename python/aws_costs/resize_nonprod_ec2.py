import pyodbc 
print("!!Start script!!")
#driver.find_element_by_css_selector('.button.c_button.s_button').click()

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
server = '10.77.126.234,1433' 
database = 'awscost' 
username = 'awscostuser' 
password = 'VeS@3MJN4zx!' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

#Call SQL to get the dataset
cursor.execute("EXEC uspReportRightSizingRecommendations;") 
row = cursor.fetchone() 
while row: 
    print(row.Owner) 
    print(row.htmlTableEc2ResizeRecommendations) 
    row = cursor.fetchone()

print("!!End script!!")
