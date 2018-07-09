import requests
import json

url =  "https://api.ciscospark.com/v1/webhooks"
payload = {
"name": "PSOG-Bot Webhook Firehose", 
"targetUrl": "https://psog-bot.herokuapp.com/", 
"resource": "all", 
"event": "all"
}
headers = {
"Content-type": "application/json; charset=utf-8",
"Authorization": "Bearer " # ADD the Token of the Bot
}

r = requests.post(url, data=json.dumps(payload), headers=headers)
print(r.content)