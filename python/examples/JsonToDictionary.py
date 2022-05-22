import json
import os

def getconfigdictionary(configfilename):
    print("start getconfigdictionary")
    def js_r(filename):
        with open(filename) as f_in:
            return(json.load(f_in))

    configurationdictionary = js_r(configfilename)
    return(configurationdictionary)

#print (getconfigdictionary("example_CallFunctionFromAnotherFile.config"))
