from JsonToDictionary import getconfigdictionary
import os

# This example shows how to read a config file into a dictionary.​
# This allows storing of configuration in JSON format and removes​
# hard-coded values from this script.​

# Assume the .config file has the same name as the .py file that we are running.
configfilename = os.path.basename(__file__).replace(".py",".config")
configuration = getconfigdictionary(configfilename)
print(configuration)
print("")
print("Node title = " + configuration["title"])
for item in configuration["GlossSeeAlso"]:
    print("Node GlossSeeAlso[item] = " + item)
print("Node Abbrev = " + configuration["Abbrev"])
