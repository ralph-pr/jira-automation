import java.net.URLEncoder;
def fileContents = new File('/apps/opt/atlassian/application-data/jira/dbconfig.xml').text;
return(URLEncoder.encode(fileContents, "UTF-8"));