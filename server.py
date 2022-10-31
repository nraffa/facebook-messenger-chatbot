from distutils.log import debug
from flask import Flask, request
#from flask_ngrok import run_with_ngrok #ngrok
import requests
from mafalda_v1 import GetBotResponse,GetIntentOfMessage,HandoverProtocol,persistent_menu,RobotTakeOver,GetMostSimilarWord
import os
import json

app = Flask(__name__)
#run_with_ngrok(app) #ngrok

port = int(os.environ.get("PORT", 5000))

req_counter = 0

FB_API_URL = 'https://graph.facebook.com/v13.0/me/messages' 
VERIFY_TOKEN = os.environ['VERIFY_TOKEN'] 
PAGE_ACCESS_TOKEN = os.environ['PAGE_ACCESS_TOKEN'] 

def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def respond(sender, message):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    amount_of_messages = GetIntentOfMessage(message)[1]
    intent = GetIntentOfMessage(message)[0]
    i = 0

    if amount_of_messages == 1:
        payload = GetBotResponse(message,sender)
        send_message(payload)
    else:
        try:
            for i in range(amount_of_messages):
                print("\n----------MULTIPLE MESSAGE OUTPUT----------\n")
                payload = GetBotResponse(message,sender)[i]
                send_message(payload)

            if intent == 'human_tag':
                HandoverProtocol(sender)      
        except:
            payload = GetBotResponse(message,sender)
            send_message(payload)

def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))

def is_postback_message(message):
    """Check if the message is a postback message"""
    return (message.get('postback') and
            message['postback'].get('payload'))

#function to send payload to facebook with the reply to the user's message (text)
def send_message(payload):
    """Send a response to Facebook"""

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()


@app.route("/webhook", methods=['GET', 'POST'])
def listen():
    """This is the main function flask uses to 
    listen at the `/webhook` endpoint"""

    
    if request.method == 'GET':        
        return verify_webhook(request)

    #try:
    if request.method == 'POST':
        payload = request.json
        
        if 'messaging' in payload['entry'][0]:    
            event = payload['entry'][0]['messaging']
        elif 'standby' in payload['entry'][0]:
            event = payload['entry'][0]['standby']      
            pass      
        i = 0
        for x in event:    
            i += 1
            print('\n---------- LOOP nº{} ----------\n'.format(i))
            sender = x['sender']['id']
            if is_user_message(x):
                text = x['message']['text']
            elif is_postback_message(x):
                text = x['postback']['payload']
            else:
                break            
            try:
                most_similar_word = GetMostSimilarWord(text,persistent_menu)
            except:
                most_similar_word = 'none'
            
            if most_similar_word == 'mafalda':
                RobotTakeOver(sender)
                respond(sender, text)
            else:
                respond(sender, text)

        return "ok"

@app.route("/webhook_inbox", methods=['GET', 'POST'])
def listen_2():
    """This is the main function flask uses to 
    listen at the `/webhook` endpoint"""

    
    if request.method == 'GET':        
        return verify_webhook(request)
    
    if request.method == 'POST':
        payload = request.json
        print('\n----------WEBHOOK INBOX MESSAGE OUTPUT----------\n')
        print('\n\n',payload,'\n\n')
        return "ok"
    #try:
    # if request.method == 'POST':
    #     payload = request.json
    #     try:    
    #         event = payload['entry'][0]['messaging']
    #     except:
    #         event = payload['entry'][0]['standby']
    #         pass
    #     for x in event:
    #         if is_user_message(x):
    #             text = x['message']['text']
    #             sender_id = x['sender']['id']
    #             respond(sender_id, text)        

    #     return "ok"



    #handle 500 error
    # except requests.exceptions.RequestException as e:
    #    return "Error: {}".format(e)
    


if __name__ == "__main__":
    #app.run()
    #app.run(port=port, debug=True) #descomentar para produccion
    app.run(host='0.0.0.0', port=port, debug=True) #descomentar para produccion
    

#pending: 1) error handling, 2) excess of message income handling fail (queue system)