import pyodbc 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
from JsonToDictionary import getconfigdictionary

LOG_FILENAME = 'send_email_ec2_rightsizing.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
print("!!Start script!!")
logging.debug("!!Start script!!")

# Define connection values
# Assume the .config file has the same name as the .py file that we are running.
configfilename = os.path.basename(__file__).replace(".py",".config")
configuration = getconfigdictionary(configfilename)
server = configuration["server"]
database = configuration["database"]
username = configuration["username"]
password = configuration["password"]
cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# Define email variables
def sendEmail(emailTemplate, owner, sectionec2):
    emailFrom = "celv.awscost.governance@example.com (CELV AWS Cost Governance)"
    emailTo = "ralph.pritchard@org.example.com"
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "(" + owner + ") CELV EC2 Rightsizing recommendations/actions - You have EC2s flagged for resizing. Please review / act"
    msg['From'] = emailFrom
    msg['To'] = emailTo
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText('', 'plain')
    part2 = MIMEText(emailTemplate.replace('~sectionec2~', sectionec2), 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('smtp.example.com', 25)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(emailFrom, emailTo, msg.as_string())
    s.quit()

#Define the atomic function that will be called per list item
def uspGetOperationalVariable(category, key, dbconn):
    rv = "NOTFOUND"
    cursor = dbconn.cursor()
    sql = """\
    DECLARE @strValue nvarchar(max);
    EXEC [dbo].[uspGetOperationalVariable] @strCategory = ?, @strName = ?, @strValue = @strValue OUTPUT;
    SELECT @strValue AS the_output;
    """
    params = (category, key, )
    cursor.execute(sql, params)
    row = cursor.fetchone() 
    while row: 
        rv = row[0]
        row = cursor.fetchone()
    return(rv)

#Gather inputs
emailTemplate = uspGetOperationalVariable("EmailTemplate", "Ec2Rightsizing", cnxn)
print(emailTemplate)

#Start of the loop
cursor.execute("EXEC uspReportRightSizingRecommendations;") 
row = cursor.fetchone() 
while row: 
    print(row.Owner) 
    print(row.htmlTableEc2ResizeRecommendations)
    sendEmail(emailTemplate, row.Owner, row.htmlTableEc2ResizeRecommendations)
    row = cursor.fetchone()

print("!!End script!!")
logging.debug("!!End script!!")
