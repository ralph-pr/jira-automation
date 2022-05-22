import requests

def getexecutioncount(pkey):
    usrPass = "U09NRVVTRVJJRDp0aGVSZWFsUGFzc3dvcmQ="
    url = "https://jira.baseurl.com/rest/troubleshooting/1.0/check/"
    resp = requests.get(url, 
                    headers={"Authorization": "Basic %s" % usrPass})

    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError('GET /tasks/ {}'.format(resp.status_code))
    #print(resp.status_code)
    #print(resp.json()['totalCount'])
    #return resp.json()['totalCount']
    return resp.json()

rv = getexecutioncount("notUsed")

print("DONE! ... getexecutioncount() returend " + str(rv))
