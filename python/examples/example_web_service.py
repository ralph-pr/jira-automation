#import urllib.request, urllib.parse, urllib.error
import requests
import json

# -----------------------------------------------------
#def main(argv):
def performHealthCheck():
    #url = "https://camp-api-np.example.com/insightsdataapi/GO0V/119"

    final_result = {
        "source": "EKS",
        "overallStatus": "?",
        "statusReason": "?",
        "healthmetrics": [],
    }

    healthmetric = {
        "message": "",
    }

    # TO-DO!!! do each NRQL query and derive status
    final_result["overallStatus"] = "Yellow"
    final_result["statusReason"] = "There are no checks yet"
    
    return(final_result)

# -----------------------------------------------------
if __name__ == "__main__":
    #final_result = main(sys.argv[1:])
    final_result = performHealthCheck()

    print(final_result)
    print("DONE!")
