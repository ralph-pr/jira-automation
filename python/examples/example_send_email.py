import smtplib
 
server = smtplib.SMTP('smtp.example.com', 25)
#server.starttls()
#server.login("", "YOUR PASSWORD")
 
msg = "Test message from python."
server.sendmail("python@jira-preprod.example.com", "ralph.pritchard@org.example.com", msg)
server.quit()
