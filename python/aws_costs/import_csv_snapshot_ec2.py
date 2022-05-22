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
    cursor.execute("EXEC insert_stage_snapshot_ec2 ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?;",csvrow['Account Name'],csvrow['Snapshot Name'],csvrow['Snapshot Id'],csvrow['Volume Name'],csvrow['Size (GB)'],csvrow['Region Name'],csvrow['Create Date'],csvrow['Description'],csvrow['Active?'],csvrow['Vsad'],csvrow['# Snapshots'],csvrow['Status'],csvrow['Owner'],csvrow['State'],csvrow['Last Discovered'],csvrow['PIOPS'],csvrow['Type'],csvrow['VSAD2'],csvrow['First Discovered'])
    #print("1")

    row = cursor.fetchone() 
    #print('instance=' + csvrow['Instance Id'] + ', rc=' + row.rc + ', errmsg=' + row.errmsg) 
    print('instance=' + csvrow['Snapshot Id'] + ', rc=?, errmsg=?')
    print(row)
    cursor.commit()

with open('aws_snapshot_ec2.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        handle_this_rds(row)

print("!!End script!!")
