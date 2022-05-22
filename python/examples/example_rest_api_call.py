import requests

url = "https://jira.baseurl.com/rest/scriptrunner/latest/custom/listZephyrTestCyclesByCycleNameSearch?p=IT-Test&c=Regression&s=2018-12-01&e=2019-01-01"

resp = requests.get(url)
if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))
for todo_item in resp.json():
    print('{} {}'.format(todo_item['cycleid'], todo_item['issuekey']))

print resp.json()['']

print("DONE!")
