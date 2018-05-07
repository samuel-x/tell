#Python libraries that we need to import for our bot
import os
from flask import Flask, request
from pymessenger.bot import Bot
from googletrans import Translator
import database

app = Flask(__name__)

translator = Translator()

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
TESTING_MODE = os.environ['TESTING_MODE']

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
                    print("Received " + message_text + " from " + sender_id)
                    # check if this is a
                    # We've done all the parsing input, so check if they're new
                    if message_text[0] == "/":
                        database.parse_command(sender_id, message_text)
                    elif int(TESTING_MODE):
                        send_translated_message(sender_id, message_text, "*TEST*")
                    elif not database.check_new_user(message['sender']['id']):
                        print("Sending message to ", database.get_user_room(sender_id))
                        send_room_message(message_text, sender_id)

                else:
                    print("This isn't a text message")
                    bot.send_raw(message)

    return "Message Processed"

def send_room_message(message_text, user_id):
    room_id = database.get_user_room(user_id)
    if room_id == None:
        send_message(user_id, "Please join a room first! Do it with '/join_room <room_number>'")
    else:
        room = database.get_room(room_id)
        if room == None:
            send_translated_message(user_id, message_text, database.get_name(user_id))
        else:
            for user in room:
                if user != user_id:
                    send_translated_message(user, message_text, database.get_name(user_id))

def send_translated_message(user_id, message_text, name):
    lang = database.get_lang(user_id)
    formatted_name = "*" + name + "*: "
    if lang == None:
        send_message(user_id, name + translator.translate(message_text).text)
    else:
        send_message(user_id, name + translator.translate(message_text, dest=lang).text)

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"



if __name__ == "__main__":
    app.run()