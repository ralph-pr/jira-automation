import requests
from datetime import datetime
import json
import os
from JsonToDictionary import getconfigdictionary

#-----------------------------------------------------
def readconfig():
    configfilename = os.path.basename(__file__).replace(".py",".config")
    configuration = getconfigdictionary(configfilename)
    print("DEBUG - configuration['jira_url'] = " + configuration["jira_url"])

    #os.environ["HTTP_PROXY"] = "http://proxy.example.com:80"
    #os.environ["HTTPS_PROXY"] = "http://proxy.example.com:80"
    #os.environ["http_proxy"] = "http://proxy.example.com:80"
    #os.environ["https_proxy"] = "http://proxy.example.com:80"

    return configuration

# -----------------------------------------------------
def performHealthCheck(configuration):
    usrPass = "U1ZDLU9ORUpJUkFSRVBPUlRFUjpxWDE5ZUwxOHRxWDE5ZUwxOHRxWDE5ZUwxOA=="
    #url = "https://onejira-test.example.com/rest/troubleshooting/1.0/check/"
    url = "https://onejira-test.example.com/rest/api/latest/serverInfo"
    resp = requests.get(url,
                    headers={"Authorization": "Basic %s" % usrPass})
    print(resp)
    #print(resp.json())

    if not (200 <= resp.status_code < 400):
        raise ApiError(status_code=session.status_code,
                       reason=session.content)
    results = {
        "healthy": [],
        "unhealthy": [],
    }

    for status in resp.json().get('statuses', []):
        entry = {
            "name": status["name"],
            "description": status["description"],
            "is_healthy": status["healthy"],
        }
        if status["healthy"] == False:
            results["unhealthy"].append(entry)
        results["healthy"].append(entry)

    return results["unhealthy"]

# -----------------------------------------------------
def performHealthCheck2(configuration):
    usrPass = "U1ZDLU9ORUpJUkFSRVBPUlRFUjpxWDE5ZUwxOHRxWDE5ZUwxOHRxWDE5ZUwxOA=="
    url = "https://onejira-test.example.com/rest/api/latest/serverInfo"
    resp = requests.get(url,
                    headers={"Authorization": "Basic %s" % usrPass})
    print(resp)
    #print(resp.json())

    if not (200 <= resp.status_code < 400):
        raise ApiError(status_code=session.status_code,
                       reason=session.content)
    results = {
        "healthy": [],
        "unhealthy": [],
    }

    for status in resp.json().get('statuses', []):
        entry = {
            "name": status["name"],
            "description": status["description"],
            "is_healthy": status["healthy"],
        }
        if status["healthy"] == False:
            results["unhealthy"].append(entry)
        results["healthy"].append(entry)

    return results["unhealthy"]

# -----------------------------------------------------
def lambda_handler():
    print('Event received:')
    #print(event)

    current_date = (datetime.now().strftime("%m-%d-%Y"))

    # read config file
    configuration = readconfig()
    unhealthy_results = performHealthCheck2(configuration)
    print(unhealthy_results)

    final_result = {
        "source": "Jira",
        "overallStatus": "?",
        "statusReason": "?",
        "healthmetrics": [],
    }

    healthmetric = {
        "message": "",
    }

    if len(unhealthy_results) == 0:
        final_result["overallStatus"] = "green"
        final_result["statusReason"] = ""
        healthmetric["message"] = "we all good!"
        final_result["healthmetrics"].append(healthmetric)
    elif len(unhealthy_results) == 1 and unhealthy_results[0]["name"] == "Cluster Locks":
        final_result["overallStatus"] = "yellow"
        final_result["statusReason"] = "All but one checks reported PASS. The failure was for 'Cluster Locks' which is not unusual but indicates overall slowness."
    else:
        final_result["overallStatus"] = "red"
        final_result["statusReason"] = str(len(unhealthy_results)) + " checks have failed. Future investigate each of the failing checks listed in 'healthmetrics'."
        for msg in unhealthy_results:
            healthmetric["message"] = msg["description"]
            final_result["healthmetrics"].append(healthmetric)

    # format a string for return
    #resp = '{"source": "Jira","overallStatus":"green/yellow/red","statusReason":"Derived from code - x of y checks passed.","healthmetrics": [{"message": "sample_msg"}]}'
    print (final_result)
    print ('End')

    # 'body': json.dumps(resp)
    return {
        'statusCode': 200,
        'body': json.dumps(final_result)
    }

rv = lambda_handler()

print("DONE! ... lambda_handler() returend " + str(rv))
