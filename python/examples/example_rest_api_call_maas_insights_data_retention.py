#import urllib.request, urllib.parse, urllib.error
import requests
import json

url = "https://camp-api-np.example.com/insightsdataapi/GO0V/119"

resp = requests.get(url)
if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))

print(resp.json())
print('')
print(resp.json()['metadata']['vsad'])
print(resp.json()['metadata']['nrql'])
print('')

for root_item in resp.json():
    print(root_item)
    print('---')
    for child_item in root_item['results']:
        print (child_item.get('members'))
    #print('{} {}'.format(todo_item['cycleid'], todo_item['issuekey']))

print("DONE!")
