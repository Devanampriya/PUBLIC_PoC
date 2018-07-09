from pprint import pprint
import requests
import json
import sys
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from flask import Flask
from flask import request
from keyword_mapping import keywords_map
from requests_toolbelt.multipart.encoder import MultipartEncoder
import re


bearer = "" # BOT'S ACCESS TOKEN
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": "Bearer " + bearer
}



def send_spark_get(url, payload=None,js=True):
    if payload == None:
        request = requests.get(url, headers=headers)
    else:
        request = requests.get(url, headers=headers, params=payload)
    if js == True:
        request= request.json()
    return request


def send_spark_post(url, data):
    request = requests.post(url, json.dumps(data), headers=headers).json()
    return request

###########################################
# Bot Menu Section Below
###########################################

admin_email = [ "xxx@cisco.com",
                "xxxx@cisco.com",
                "xxx@cisco.com"
                ]

def keywordmenu(result):
    i = 0
    category = ""
    for entry in keywords_map:
        if(entry["slides"]!=[""]):
            if(i==0):
                category = "<br/>*Category : PSOG*<br/>"
                result = result + "<br/>" + category
                result = result +"`"+', '.join(entry["keywords"])+"`"+"<br/>"
            elif(i==6):
                category = "<br/>*Category : Partner Tools*<br/>"
                result = result + category
                result = result +"`"+', '.join(entry["keywords"])+"`"+"<br/>"
            elif(i==15):
                category = "<br/>*Category : Cisco Services*<br/>"
                result = result + category
                result = result +"`"+', '.join(entry["keywords"])+"`"+"<br/>"
            elif(i==24):
                category = "<br/>*Category : Incentives and Programs*<br/>"
                result = result + category
                result = result +"`"+', '.join(entry["keywords"])+"`"+"<br/>"
            elif(i==32):
                category = "<br/>*Category : Technology*<br/>"
                result = result + category
                result = result +"`"+', '.join(entry["keywords"])+"`"+"<br/>"
            elif(i==40):
                category = "<br/>*Category : Others*<br/>"
                result = result + category
                result = result +"`"+', '.join(entry["keywords"])+"`"+"<br/>"
            else:
                result = result +"`"+', '.join(entry["keywords"])+"`"+"<br/>"
            i = i+1
    return result

def help_me(user_email):
    if(user_email in admin_email):
        result = "Sure! I can help. Below are the commands that I understand:<br/>" \
            "**Latest version of the PSOG document is available here :** [SalesConnect](https://salesconnect.cisco.com/#/briefcase-details/P04197793) <br/>"\
            "`help` - I will display what I can do.<br/>" \
            "`broadcast` - I will broadcast the message to all users of the psog bot <br/>" \
            "`get_usage_details` - I will share the details of all current users of the psog bot <br/>" \
            "*Please type any of the keywords(below the category) to get more details from the PSOG document*"
    else:
        result = "Sure! I can help. Below are the commands that I understand:<br/>" \
            "**Latest version of the PSOG document is available here :** [SalesConnect](https://salesconnect.cisco.com/#/briefcase-details/P04197793) <br/>"\
            "`help` - I will display what I can do.<br/>" \
            "*Please type any of the keywords(below the category) to get more details from the PSOG document*"
    
    result = keywordmenu(result)
    return(result)


###########################################
# Bot User Function Section Below
###########################################

def greetings():
    return "Hi my name is %s.<br/>" \
           "Type `help me` to see what I can do.<br/>" % bot_name

def broadcast(message):
    result = send_spark_get(
                'https://api.ciscospark.com/v1/rooms')
    for entry in result["items"]:
        print("**",entry["id"])
        send_spark_post("https://api.ciscospark.com/v1/messages",
                {
                    "roomId": entry["id"],
                    "markdown": message
                }
                )
    return("broadcast send..")

def sendfile(roomid,filenames,desc):
    i = 0
    for entry in filenames:
        if(i==0):
            send_spark_post("https://api.ciscospark.com/v1/messages",
                        {
                            "roomId": roomid,
                            "markdown": desc
                        }
                        )
        m = MultipartEncoder({'roomId': roomid,
                        'text': "",
                        'files': (entry, open('PDF-slides/'+entry, 'rb'),
                        'application/pdf')})
        r = requests.post('https://api.ciscospark.com/v1/messages', data=m,
                        headers={'Authorization': 'Bearer '+ bearer,
                        'Content-Type': m.content_type})
        i = i+1
        print ("**",r.text)

def catch_keyword(roomid,message):
    result = False
    for entry in keywords_map:
        for word in entry["keywords"]:
            if(re.search(word, message,re.IGNORECASE)):
                print("keyword match found!!",entry)
                sendfile(roomid,entry["slides"],entry["description"])
                result = True
                break
    return result

def getusers():
    ignorelist = ["spark-cisco-it-admin-bot@cisco.com","apj_po@sparkbot.io"]
    output = ""
    count = 0
    result = send_spark_get('https://api.ciscospark.com/v1/rooms')
    for entry in result["items"]:
        members = send_spark_get('https://api.ciscospark.com/v1/memberships?roomId='+entry["id"])
        output = output + "<br/>" + "Name of room : "+entry["title"] + "<br/>"
        output = output + "Type of access : "+entry["type"] + "<br/>"
        output = output + "List of members in the room : <br/>"
        for item in members["items"]:
            output = output + "Name : " + item["personDisplayName"] + "<br/>"
            output = output + "Email_ID : " + item["personEmail"] + "<br/>"
            if(item["personEmail"] in ignorelist):
                continue
            ignorelist.append(item["personEmail"])
            count = count + 1
    output = output + "<br/>" + "Total count of unique members reached : " + str(count) + "<br/>"
    return output


###########################################
# Bot User Function Section Above
###########################################

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def spark_webhook():
    if request.method == 'POST':
        webhook = request.get_json(silent=True)
        print(webhook)
        if webhook['data']['personEmail']!= bot_email:
            pprint(webhook)
        if webhook['resource'] == "memberships" and webhook['data']['personEmail'] == bot_email:
            send_spark_post("https://api.ciscospark.com/v1/messages",
                            {
                                "roomId": webhook['data']['roomId'],
                                "markdown": (greetings() +
                                             "**Note This is a group room and you have to call "
                                             "me specifically with `@%s` for me to respond**" % bot_name)
                            }
                            )
        msg = None
        message = ""
        if webhook['data']['personEmail'] != bot_email:
            user_email = webhook['data']['personEmail']
            result = send_spark_get(
                'https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
            in_message = result.get('text', '')
            in_message = in_message.replace(bot_name + " ", '')


###########################################
# Bot Menu to User Function Connector Section Below
###########################################  

### admin commands start
            if(user_email in admin_email):
                if in_message.startswith('help'):
                    msg = help_me(user_email)
                elif(in_message.startswith('broadcast')):
                    msg = broadcast(in_message.split(' ', 1)[1])
                elif(in_message.startswith('get_usage_details')):
                    msg = getusers()
                elif (in_message == "") :
                    print("NULL")
                else:
                    if(catch_keyword(webhook['data']['roomId'],in_message) is False):
                        print("**"+in_message+"**")
                        msg = "Sorry, but I did not understand your request("+in_message+"). Type `help me` to see what I can do" 
### admin commands end
            else:
                if in_message.startswith('help'):
                    msg = help_me(user_email)
                elif (in_message == "") :
                    print("NULL")
                else:
                    if(catch_keyword(webhook['data']['roomId'],in_message) is False):
                        print("**"+in_message+"**")
                        msg = "Sorry, but I did not understand your request("+in_message+"). Type `help` to see what I can do" 
            if len(message) > 0:
                msg = "{0}".format(message)
            if msg != None:
                send_spark_post("https://api.ciscospark.com/v1/messages",
                                {"roomId": webhook['data']['roomId'], "markdown": msg})
        return "true"
    elif request.method == 'GET':
        message = "<center><img src=\"http://bit.ly/SparkBot-512x512\" alt=\"Spark Bot\" style=\"width:256; height:256;\"</center>" \
                  "<center><h2><b>Congratulations! Your <i style=\"color:#ff8000;\">%s</i> bot is up and running.</b></h2></center>" \
                  "<center><b><i>Please don't forget to create Webhooks to start receiving events from Cisco Spark!</i></b></center>" % bot_name
        return message

def main():
    global bot_email, bot_name
    if len(bearer) != 0:
        test_auth = send_spark_get("https://api.ciscospark.com/v1/people/me", js=False)
        if test_auth.status_code == 401:
            print("Looks like provided access token is not correct. \n"
                  "Please review it and make sure it belongs to your bot account.\n"
                  "Do not worry if you have lost the access token. "
                  "You can always go to https://developer.ciscospark.com/apps.html "
                  "URL and generate a new access token.")
            #sys.exit()
        if test_auth.status_code == 200:
            test_auth = test_auth.json()
            #bot_name = test_auth.get("displayName","")
            bot_name = "PSOG"
            bot_email = test_auth.get("emails","")[0]
    else:
        print("'bearer' variable is empty! \n"
              "Please populate it with bot's access token and run the script again.\n"
              "Do not worry if you have lost the access token. "
              "You can always go to https://developer.ciscospark.com/apps.html "
              "URL and generate a new access token.")
        #sys.exit()
    if "@sparkbot.io" not in bot_email:
        print("You have provided access token which does not belong to your bot.\n"
              "Please review it and make sure it belongs to your bot account.\n"
              "Do not worry if you have lost the access token. "
              "You can always go to https://developer.ciscospark.com/apps.html "
              "URL and generate a new access token.")
        #sys.exit()
    else:
        IP="0.0.0.0"
        PORT=os.getenv("PORT")
        app.run(host=IP, port=int(PORT))
if __name__ == "__main__":
    main()
