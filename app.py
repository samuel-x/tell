#Python libraries that we need to import for our bot
import random
import os
import json
from flask import Flask, request
from pymessenger.bot import Bot
from googletrans import Translator

app = Flask(__name__)

translator = Translator()

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]
MAINTENANCE_MODE = os.environ["MAINTENANCE_MODE"]
SHOW_MESSAGES = os.environ["SHOW_MESSAGES"]

MEMBERS = {}

with open('joined.json') as member_data:
    MEMBERS = json.load(member_data)

bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint 

@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    message_text = message.get('message').get('text')
                    sender_id = message['sender']['id']
                    if not check_exists(message['sender']['id']):
                        print("Splitting: ", message_text)
                        (language, room) = message_text.split(",")
                        set_language(language, sender_id)
                        check_room(room, sender_id)
                    #Facebook Messenger ID for user so we know where to send response back to
                    else:
                        send_room_message(message_text, sender_id, "123")


    return "Message Processed"

def send_room_message(message_text, user_id, room_id):
    with open('rooms.json', 'r+') as rooms:
        room = json.load(rooms)[room_id]
        for user in room:
            if user != user_id:
                send_translated_message(user, message_text)

def send_translated_message(user_id, message_text):
    with open('language.json', 'r+') as languages:
        language = json.load(languages)[user_id]
        send_message(user_id, translator.translate(message_text, dest=language).text)

def check_exists(user_id):
    print("Checking ", user_id, " vs ", MEMBERS.keys())
    if user_id not in MEMBERS.keys():
        MEMBERS[user_id] = 1
        return False
    else:
        return True

def check_room(room_name, user_id):
    with open('rooms.json', 'r+') as rooms:
        d = json.load(rooms)
        if user_id not in d.get(room_name):
            d.get(room_name).append(user_id)
            json.dump(d, rooms)
        send_message(user_id, ("Successfully joined room ", room_name, "!"))

def set_language(language, user_id):
    with open('language.json', 'r+') as languages:
        d = json.load(languages)
        if user_id in d.keys():
            d[user_id] = language
            json.dump(d, languages)
        send_message(user_id, ("Your language is now: ", language))

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

#chooses a random message to send to the user
def reply_message(message):
    if int(MAINTENANCE_MODE):
        return MAINTENANCE_MESSAGE
    else:
        # return selected item to the user
        return message

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()