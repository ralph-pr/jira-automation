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
String username = "jrsmith2";

UserUtil userUtil = ComponentAccessor.userUtil;
userUtil.addUserToGroup(userUtil.getGroup(groupname) ,userUtil.getUser(username))
result = result + "Added " + username + " to " + groupname

result
