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
    cursor.execute("EXEC insert_stage_rds ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?;",csvrow['VPC_ID'],csvrow['Instance Id'],csvrow['DPETool'],csvrow['Component'],csvrow['Vendor'],csvrow['Infosys Perspective'],csvrow['DPEEnv'],csvrow['Environment'],csvrow['Environment'],csvrow['Owner'],csvrow['Projected Cost For Current Month'],csvrow['Price Per Hour'],csvrow['Multi-AZ'],csvrow['Avg CPU Utilization'],csvrow['Max CPU Utilization'],csvrow['Avg Database Connections'],csvrow['Max Database Connections'],csvrow['Flavor'],csvrow['Engine'],csvrow['Version'],csvrow['Size (GB)'],csvrow['Avg Read IOPS'],csvrow['Avg Write IOPS'],csvrow['First Discovered'],csvrow['Created On'],csvrow['Zone Name'],csvrow['DB Name'],csvrow['Active?'],csvrow['Day'],csvrow['On-Demand Price Per Month'],csvrow['List Price Per Month'],csvrow['Current Hourly Cost'],csvrow['Last Discovered'],csvrow['Latest Backup'],csvrow['Billing Account'],csvrow['BYOL'],csvrow['Endpoint'],csvrow['Application'],csvrow['NOSTOP'],csvrow['NOTERMINATE'],csvrow['NORESIZE'])
    #print("1")

    row = cursor.fetchone() 
    #print('instance=' + csvrow['Instance Id'] + ', rc=' + row.rc + ', errmsg=' + row.errmsg) 
    print('instance=' + csvrow['Instance Id'] + ', rc=?, errmsg=?')
    print(row)
    cursor.commit()

with open('aws_rds_instance_metrics.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        handle_this_rds(row)

print("!!End script!!")
