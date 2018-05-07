#Python libraries that we need to import for our bot
import random
import os
import json
import pyrebase
from flask import Flask, request
from pymessenger.bot import Bot
from googletrans import Translator
import config
import languages

app = Flask(__name__)

translator = Translator()

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
TESTING_MODE = os.environ['TESTING_MODE']

MEMBERS = {}



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
                    if message_text == None:
                        break
                    sender_id = message['sender']['id']
                    # check if this is a
                    # We've done all the parsing input, so check if they're new
                    if message_text[0] == "/":
                        if message_text == "/leave_room":
                            leave_room(sender_id)
                        elif message_text == "/join_room":
                            print("Please enter your room number")
                        elif message_text.split(" ")[0] == "/join_room":
                            room_id = message_text.split(" ", 1)[1]
                            join_room(sender_id, room_id)
                        elif message_text.split(" ")[0] == "/set_name":
                            new_name = message_text.split(" ", 1)[1]
                            change_name(sender_id, new_name)
                        elif message_text.split(" ")[0] == "/set_lang":
                            new_lang = message_text.split(" ", 1)[1]
                            set_language(sender_id, new_lang)
                    elif int(TESTING_MODE):
                        send_translated_message(sender_id, message_text, "*TEST*")
                    elif not check_new_user(message['sender']['id']):
                        print("Sending message to ", get_room(sender_id))
                        send_room_message(message_text, sender_id, get_room(sender_id))

                else:
                    print("This isn't a text message")
                    bot.send_raw(message)

    return "Message Processed"

def get_room(user_id):
    with open('rooms.json', 'r') as room_data:
        rooms = json.load(room_data)
        room_data.close()
        for key in rooms:
            print(key)
            if user_id in rooms[key]:
                return key

def get_name(sender_id):
    with open('members.json', 'r') as member_data:
        members = json.load(member_data)
        member_data.close()
        return "*" + str(members[sender_id]) + "*: "



def change_name(user_id, new_name):
    with open('members.json', 'r') as member_data:
        members = json.load(member_data)
        members[user_id] = new_name
        with open('members.json', 'w') as member_data:
            json.dump(members, member_data)
        member_data.close()
        print("User ", user_id, " changed their name to ", member_data)

def leave_room(user_id):
    with open('rooms.json', 'r') as room_data:
        rooms = json.load(room_data)
        for users, room in rooms.items():
            for user in users:
                if user == user_id:
                    room.pop(user, None)
                    room_data.close()
                    with open('rooms.json', 'w') as room_data:
                        json.dump(room, room_data)
                    room_data.close()
                    print("User ", user_id, " removed from room ", room)

def join_room(user_id, room_id):
    with open('rooms.json', 'r') as room_data:
        rooms = json.load(room_data)
        if rooms.get(room_id):
            rooms[room_id].append(user_id)
        else:
            rooms[room_id] = [user_id]
        room_data.close()
        with open('rooms.json', 'w') as room_data:
            json.dump(rooms, room_data)
        room_data.close()
        print("User ", user_id, " added to room ", room_id)

def send_room_message(message_text, user_id, room_id):
    with open('rooms.json', 'r') as rooms:
        room = json.load(rooms).get(room_id)
        rooms.close()
        if room == None:
            send_message(user_id, "Please join a room first!")
        else:
            for user in room:
                if user != user_id:
                    send_translated_message(user, message_text, get_name(user_id))

def send_translated_message(user_id, message_text, name):
    with open('language.json', 'r') as language_data:
        language = json.load(language_data).get(user_id)
        language_data.close()
        send_message(user_id, name + translator.translate(message_text, dest=language).text)

def check_new_user(user_id):
    with open('members.json', 'r') as member_data:
        members = json.load(member_data)
        member_data.close()
        if user_id not in members.keys():
            members[user_id] = 1
            with open('members.json', 'w') as member_data:
                json.dump(members, member_data)
            member_data.close()
            return True
        else:
            return False


def check_room(room_name, user_id):
    with open('rooms.json', 'r+') as rooms:
        d = json.load(rooms)
        if user_id not in d.get(room_name):
            return False
        return True

def set_language(user_id, language):
    with open('language.json', 'r') as language_data:
        d = json.load(language_data)
        d[user_id] = language
        language_data.close()
        with open('language.json', 'w') as language_data:
            json.dump(d, language_data)
        language_data.close()
        message = "Your language is now: " + languages.LANGUAGES[d[user_id]]
        send_message(user_id, message)

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

#chooses a random message to send to the user
def reply_message(message):
    if int(MAINTENANCE_MODE):
        return "help"
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