import requests
import json
from slack_sdk.webhook import WebhookClient
vcloudUM_URL = "https://USAGE-METER-URL/login"
slack_emoji = ":warning:"
slackURL = 'https://hooks.slack.com/services/TTTTTTT'
url = "https://USAGE-METER-URL:443/api/v1/"
UMUsername = "username"
UMPassword = "password"
loginUrl   = url + "login"
errorState = False

def sendSlack(productType, productUser, productInstance, productStatusText, productStatusCode):
    webhook = WebhookClient(slackURL)
    response = webhook.send(
    blocks=[
        {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "{} You have a new product alert on vCloud Usage Meter {}\n*<{}|vCloud Usage Meter>*".format(slack_emoji, slack_emoji, vcloudUM_URL)
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Product Type:*\n{}".format(productType)
				},
				{
					"type": "mrkdwn",
					"text": "*User:*\n{}".format(productUser)
				},
				{
					"type": "mrkdwn",
					"text": "*Instance:*\n{}".format(productInstance)
				},
				{
					"type": "mrkdwn",
					"text": "*Status Code:*\n{}".format(productStatusCode)
				},
				{
					"type": "mrkdwn",
					"text": "*Status:*\n{}".format(productStatusText)
				}
			]
		}
    ]
)

try:
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "user": f"{UMUsername}",
        "password": f"{UMPassword}"
    }
    response = requests.post(loginUrl, json=payload, headers=headers, verify=False)  
    sessionID = response.json()["sessionid"]
    if response.status_code == 202:
        print("Session ID:", sessionID)
        print("Status Code: ", response.status_code)
    else:
        print("Could not create a session!", response.status_code)

    productUrl = url + "product"
    headers = {
        "Content-Type": "application/json",
        "sessionid": sessionID
    }

    productResponseJson = requests.get(productUrl, headers=headers, verify=False)  
    productResponse = productResponseJson.json()
    formatted_json = json.dumps(productResponseJson.json(), indent=4)
    print(formatted_json)
    products = json.loads(formatted_json)

    for product in products:
        if product["status"]["statusCode"] != "COLLECT_OK":
            productType = product["productType"]
            productUser = product["user"]
            productInstance = product["host"]
            productStatusText = product["status"]["text"]
            productStatusCode = product["status"]["statusCode"]
            sendSlack(productType, productUser, productInstance, productStatusText, productStatusCode)
            errorState = True
    if errorState == False:
        print(0)
    else:
        print(1)
except Exception as e:
    print(e)
