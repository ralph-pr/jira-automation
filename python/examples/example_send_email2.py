import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

server = smtplib.SMTP('smtp.example.com', 25)
#server.starttls()
#server.login("", "YOUR PASSWORD")
body = "Test message from python."
#server.sendmail("", "", msg)
#server.quit()

msg = MIMEMultipart()
msg['From'] = 'python@jira-preprod.example.com'
msg['To'] = 'ralph.pritchard@org.example.com'
msg['Subject'] = 'Example email from python'
msg['Body'] = body
server.sendmail('python@jira-preprod.example.com','ralph.pritchard@org.example.com',msg.as_string())
