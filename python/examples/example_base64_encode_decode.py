import base64

unencoded = b'data to be encoded'
encoded = base64.b64encode(unencoded)
print(str(unencoded) + " ... " + str(encoded) + " ... BAD! it has a prefix and suffix wrapping it." )
print(str(unencoded) + " ... " + encoded.decode('utf-8') + " ... GOOD! No prefix/suffix = the way our API calls want it encoded." )
print("")

print("This is a secret = " + str( base64.b64encode(b'This is a secret.')))
print("")

usrPass = "U09NRVVTRVJJRDp0aGVSZWFsUGFzc3dvcmQ="
print("usrPass (" + str(usrPass) + ") decoded = " + str(base64.b64decode(usrPass)))
print("")

jirauser = "SOMEUSERID"
jirapwd = "theRealPassword"
str2bytes = str.encode(jirauser + ":" + jirapwd)
encoded = base64.b64encode(str2bytes)
print("jirauser=" + jirauser + ". jirapwd=" + jirapwd + ". encoded=" + str(encoded))
