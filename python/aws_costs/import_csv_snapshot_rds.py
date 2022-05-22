import csv
import pyodbc 
print("!!Start script!!")

def handle_this_rds(csvrow):
    #print(csvrow['VPC Id'] + csvrow['Instance Id'] + csvrow['Owner Email'] + csvrow['DPETool'] + csvrow['Component'] + csvrow['Vendor'] + csvrow['Infosys Perspective'] + csvrow['DPEEnv'] + csvrow['Environment'] + csvrow['Environment'] + csvrow['Projected Cost For Month'] + csvrow['Hourly Cost'] + csvrow['Avg CPU (%)'] + csvrow['Max CPU (%)'] + csvrow['State'] + csvrow['Active?'] + csvrow['Instance Name'] + csvrow['Product'] + csvrow['API Name'] + csvrow['Launch Date'] + csvrow['Zone Name'] + csvrow['Min CPU (%)'] + csvrow['Total Cost MTD'] + csvrow['List Price Per Month'] + csvrow['Attached EBS'] + csvrow['aws:cloudformation:stack-name'] + csvrow['Day'])
    server = '10.77.126.234' 
    database = 'awscost' 
    username = 'YOURSQLUSER' 
    password = 'YOURSQLPWD' 
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    cursor.execute("EXEC insert_stage_snapshot_rds ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?;",csvrow['Account Name'],csvrow['Snapshot Id'],csvrow['Instance Id'],csvrow['Size (GB)'],csvrow['Zone Name'],csvrow['Create Date'],csvrow['Tags'],csvrow['Owner'],csvrow['Endpoint'],csvrow['Storage Type'],csvrow['DB Name'],csvrow['Size (GB)2'],csvrow['Snapshots?'],csvrow['Vsad'],csvrow['First Discovered'])
    #print("1")

    row = cursor.fetchone() 
    #print('instance=' + csvrow['Instance Id'] + ', rc=' + row.rc + ', errmsg=' + row.errmsg) 
    print('instance=' + csvrow['Instance Id'] + ', rc=?, errmsg=?')
    print(row)
    cursor.commit()

with open('aws_snapshot_rds.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        handle_this_rds(row)

print("!!End script!!")
