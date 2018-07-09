#Python libraries that we need to import for our bot
import os
from flask import Flask, request
from pymessenger.bot import Bot
from googletrans import Translator
import database
import profile

app = Flask(__name__)

translator = Translator()

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
TESTING_MODE = os.environ['TESTING_MODE']

bot = Bot(ACCESS_TOKEN)

# Setup our Facebook Messenger Profile
print(profile.setup_profile(ACCESS_TOKEN))
#We will receive messages that Facebook sends our bot at this endpoint 

@app.route("/", methods=['GET', 'POST', 'DELETE'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return profile.verify_fb_token(token_sent, VERIFY_TOKEN)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    elif request.method == 'POST':
        # get whatever message a user sent the bot
        output = request.get_json()
        event = output['entry']
        messaging = event[0].get('messaging')[0]
        if messaging.get('message'):
            message_text = messaging.get('message').get('text')
            if message_text == None:
                print("This isn't a text message")
            sender_id = messaging['sender']['id']
            print("Received " + message_text + " from " + sender_id)
            # check if this is a
            # We've done all the parsing input, so check if they're new
            if message_text[0] == "/":
                database.parse_command(sender_id, message_text)
            elif int(TESTING_MODE):
                send_translated_message(sender_id, message_text, "*TEST*")
            elif not database.check_new_user(messaging['sender']['id']):
                print("Sending message to ", database.get_user_room(sender_id))
                send_room_message(message_text, sender_id)
        else:
            print("This isn't a text message")

    return "Message Processed"

def send_room_message(message_text, user_id):
    room_id = database.get_user_room(user_id)
    if room_id == None:
        send_message(user_id, "Please join a room first! Do it with '/join_room <room_number>'")
    else:
        room = database.get_room(room_id)
        if room.get("users") == [user_id] and len(room) == 1:
            send_translated_message(user_id, message_text, database.get_name(user_id))
        else:
            for user in room.get("users"):
                if user != user_id:
                    send_translated_message(user, message_text, database.get_name(user_id))

def send_translated_message(user_id, message_text, name):
    lang = database.get_lang(user_id)
    formatted_name = "*" + name + "*: "
    if lang == None:
        send_message(user_id, formatted_name + translator.translate(message_text).text)
    else:
        send_message(user_id, formatted_name + translator.translate(message_text, dest=lang).text)

def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    payload = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': response
        }
    }
    print(bot.send_raw(payload));
    return "success"



if __name__ == "__main__":
    app.run()