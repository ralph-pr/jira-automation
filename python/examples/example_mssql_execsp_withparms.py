import pyodbc 
print("!!Start script!!")
#driver.find_element_by_css_selector('.button.c_button.s_button').click()

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
server = 'YOURSERVER' 
database = 'awscost' 
username = 'YOURSQLLOGIN' 
password = 'YOURSQLPASSWORD' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

#...3 is the acctID https://jira-preprod.example.com/plugins/servlet/eazybi/accounts/<id>/source_data#source_applications
#Sample select query
#cursor.execute("SELECT @@version;")
val1 = "ec2"
# The SQL statement has 2 placeholders: val1 and the literal "dbo". We can do similar for EXEC sp @p1, @p2, @p3.
cursor.execute('SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ? AND TABLE_SCHEMA = ?', val1, "dbo") 
row = cursor.fetchone() 
while row: 
    print(row[0]) 
    row = cursor.fetchone()

print("!!End script!!")
