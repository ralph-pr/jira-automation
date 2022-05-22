import psycopg2 
print("!!Start script!!")
#driver.find_element_by_css_selector('.button.c_button.s_button').click()

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
server = 'onejirapostgrespreprodeast94.c5ogzsgipyri.us-east-1.rds.amazonaws.com' 
database = 'onejira_archive_201811' 
username = 'devopsreader' 
password = 'lka@0d9n&aM&f!'
conn_str = (
    "DRIVER={PostgreSQL Unicode};"
    "DATABASE="+database+";"
    "UID="+username+";"
    "PWD="+password+";"
    "SERVER="+server+";"
    "PORT=5432;"
    )
cnxn = psycopg2.connect(host=server,database=database, user=username, password=password)
cursor = cnxn.cursor()

#...3 is the acctID https://jira-preprod.example.com/plugins/servlet/eazybi/accounts/<id>/source_data#source_applications
#Sample select query
#cursor.execute("SELECT @@version;") 
cursor.execute("select DISTINCT pname from project where pkey = 'TOOLS'") 
row = cursor.fetchone() 
while row: 
    print(row[0]) 
    row = cursor.fetchone()

print("!!End script!!")
