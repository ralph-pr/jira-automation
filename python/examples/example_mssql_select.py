import pyodbc 
print("!!Start script!!")
#driver.find_element_by_css_selector('.button.c_button.s_button').click()

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
server = 'onejirapreprodwestbaseline.cbhxxwrpq3pu.us-west-2.rds.amazonaws.com' 
database = 'onejira_stage' 
username = 'YOURSQLLOGIN' 
password = 'YOURSQLPASSWORD' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

#...3 is the acctID https://jira-preprod.example.com/plugins/servlet/eazybi/accounts/<id>/source_data#source_applications
#Sample select query
#cursor.execute("SELECT @@version;") 
cursor.execute("SELECT TOP 10 pkey From project ORDER BY pkey;") 
row = cursor.fetchone() 
while row: 
    print(row[0]) 
    row = cursor.fetchone()

print("!!End script!!")
