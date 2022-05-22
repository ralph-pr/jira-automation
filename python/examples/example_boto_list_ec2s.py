import boto3
import os

print('Loading function')

os.environ["HTTP_PROXY"] = "http://proxy.example.com:80/"
os.environ["HTTPS_PROXY"] = "http://proxy.example.com:80/"
os.environ["http_proxy"] = "http://proxy.example.com:80/"
os.environ["https_proxy"] = "http://proxy.example.com:80/"
os.environ["no_proxy"] = "localhost.localdomain,169.254.169.254,example.com,np.example.com,vpc.example.com"

client = boto3.client('ec2', 'us-east-1')

custom_filter = [{
    'Name':'tag:Owner', 
    'Values': ['ralph.pritchard@org.example.com']}]

response = client.describe_instances(Filters=custom_filter)
print(response);
for r in response['Reservations']:
  for i in r['Instances']:
    print i['InstanceId'], i['Hypervisor']
    for b in i['BlockDeviceMappings']:
      print b['Ebs']['DeleteOnTermination']

print("DONE!")
