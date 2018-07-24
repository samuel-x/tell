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

# We will receive messages that Facebook sends our bot at this endpoint

# Accept the following requests
@app.route("/", methods=['GET', 'POST', 'DELETE'])
def receive_message():
    '''This is the entry point for our bot. We will receive all GET, POST
    and DELETE requests here.'''
    # If we have a GET request, then it will be facebook's authentication process
    # Reply with the appropriate token
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return profile.verify_fb_token(token_sent, VERIFY_TOKEN)

    # if the request was not a GET,
    # it must be POST and we can
    # proceed with sending a message back to user
    elif request.method == 'POST':
        # get whatever message a user sent the bot
        output = request.get_json()
        event = output['entry']
        messaging = event[0].get('messaging')[0]
        user_id = messaging.get('sender').get('id')

        # If we have a postback, then do the operation
        if messaging.get('postback'):
            postback = messaging.get('postback').get('payload')
            print("We've got a postback: " + postback)
            profile.parse_postback(postback, user_id)

        # Read our message. If it's a command then parse the command,
        # otherwise just send the translated message.
        elif messaging.get('message'):
            message_text = messaging.get('message').get('text')

            # If it's not a text message, just ignore it
            if message_text == None:
                print("This isn't a text message")

            print("Received " + message_text + " from " + user_id)
            if message_text[0] == "/":
                database.parse_command(user_id, message_text)
            elif int(TESTING_MODE):
                send_translated_message(user_id, message_text, "*TEST*")
            elif not database.check_new_user(messaging['sender']['id']):
                print("Sending message to ", database.get_user_room(user_id))
                send_room_message(message_text, user_id)

        # Verify that something has been sent
        elif messaging.get('delivery'):
            print("Message Successfully Received!")
        else:
            # TODO: Handle non-text messages
            print("This isn't a text message")

    return "Message Processed"

def send_room_message(message_text, user_id):
    '''This sends the specified room a text message'''
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
    '''This sends a translated message to the specified user ID in the user's
    specified language'''
    lang = database.get_lang(user_id)
    formatted_name = "*" + name + "*: "
    if lang == None:
        send_message(user_id, formatted_name + translator.translate(message_text).text)
    else:
        send_message(user_id, formatted_name + translator.translate(message_text, dest=lang).text)

def send_message(recipient_id, response):
    '''This sends a message to a user ID'''
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