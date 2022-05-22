/*
Case:
Given a user name and group name, remove the user from that group
*/

import com.atlassian.jira.bc.security.login.LoginService
import com.atlassian.jira.component.ComponentAccessor
import com.atlassian.jira.user.util.UserManager
import com.atlassian.jira.user.util.UserUtil

def result = ""

String groupname = "jira-administrators";
String username = "abrolde";

UserUtil userUtil = ComponentAccessor.userUtil;
userUtil.removeUserFromGroup(userUtil.getGroup(groupname) ,userUtil.getUser(username))
result = result + "Removed " + username + " from " + groupname

result
