import pyrebase
import app
import languages
import os
import ast

API_KEY = os.environ['API_KEY']
AUTH_DOMAIN = os.environ['AUTH_DOMAIN']
DATABASE_URL = os.environ['DATABASE_URL']
PROJECT_ID = os.environ['PROJECT_ID']
STORAGE_BUCKET = os.environ['STORAGE_BUCKET']
MESSAGING_SENDER_ID = os.environ['MESSAGING_SENDER_ID']
SERVICE_ACCOUNT = ast.literal_eval(os.environ['SERVICE_ACCOUNT'])

config = {
    "apiKey": API_KEY,
    "authDomain": AUTH_DOMAIN,
    "databaseURL": DATABASE_URL,
    "projectId": PROJECT_ID,
    "storageBucket": STORAGE_BUCKET,
    "messagingSenderId": MESSAGING_SENDER_ID,
    "serviceAccount": SERVICE_ACCOUNT
};

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()

db = firebase.database()


def parse_command(sender_id, message_text):
    '''This parses commands to do things'''
    # TODO: Make a dictionary with commands and just pass the function into it
    if message_text == "/leave_room":
        leave_room(sender_id)
    elif message_text == "/join_room":
        app.send_message(sender_id,
                         "Please enter your room number. Usage: /join_room <room_number>")
    elif message_text == "/set_name":
        app.send_message(sender_id,
                         "Please enter your new name. Usage: /set_name <new_name>")
    elif message_text == "/get_commands":
        get_commands(sender_id)
    elif message_text == "/show_langs":
        send_language_list(sender_id)
    elif message_text.split(" ")[0] == "/join_room":
        room_id = message_text.split(" ", 1)[1]
        join_room(sender_id, room_id)
    elif message_text.split(" ")[0] == "/set_name":
        new_name = message_text.split(" ", 1)[1]
        change_name(sender_id, new_name)
    elif message_text.split(" ")[0] == "/set_lang":
        new_lang = message_text.split(" ", 1)[1]
        set_language(sender_id, new_lang)


def send_language_list(user_id):
    '''Sends a user a list of languages and their codes'''
    language_list = "```\nLanguage: Code\n"
    for lang, code in languages.LANGCODES.items():
        language_list += (lang + ": " + code + "\n")
    language_list += "```"
    app.send_message(user_id, language_list)


def join_room(user_id, room_id):
    '''This allows our user to join a room'''

    # Try and get our user
    try:
        current_room = \
            db.child("users").child(user_id).get().val().get("room_id")
        if current_room is not None:
            app.send_message(user_id, "You're already currently in room "
                             + room_id
                             + ". Please leave the room first with /leave_room.")
    except AttributeError:
        # They aren't in a room
        pass

    # Get our room
    room = db.child("rooms").child(room_id).get().val()

    # If our room does not exist, create a new one
    if room == None:
        db.child("rooms").child(room_id).update({"users": [user_id]})
        db.child("users").child(user_id).update({"room_id": room_id})
        message = "Started a new room with id " \
                  + room_id \
                  + "\nNote: If the room is empty you will only get echoed responses.\n"
        app.send_message(user_id, message)
        return False
    else:
        # Otherwise, set our room_id and join the room
        room.get("users").append(user_id)
        db.child("rooms").child(room_id).update(room)
        db.child("users").child(user_id).update({"room_id": room_id})
        app.send_message(user_id, "Successfully joined room " + room_id)
        print("Successfully added " + user_id + " to " + room_id)
        return True


def change_name(user_id, new_name):
    ''' Allows a user to change their name '''
    db.child("users").child(user_id).update({"name": new_name})


def leave_room(user_id):
    ''' Lets a user leave a room '''
    # Get our room id
    room_id = get_user_room(user_id)
    if room_id is None:
        # If it doesn't exist, then ask them to join a room first
        app.send_message(user_id, "Please join a room first!")
        return False
    else:
        # Remove from room and reset room id
        room = db.child("rooms").child(room_id).get().val()
        room.get("users").remove(user_id)
        db.child("rooms").child(room_id).update(room)
        db.child("users").child(user_id).update({"room_id": None})
        app.send_message(user_id, "Successfully left room " + room_id)
        return True


def set_language(user_id, language):
    ''' Allows a user to change their name '''
    if language not in languages.LANGUAGES.keys():
        app.send_message(user_id,
                         "Please enter a valid language. Language codes can be found by typing /show_langs")
    else:
        db.child("users").child(user_id).update({"lang": language})
        app.send_message(user_id,
                         "Successfully set language to " + languages.LANGUAGES.get(
                             language))


def get_user_room(user_id):
    ''' Returns the Room ID of the user'''
    try:
        return db.child("users").child(user_id).get().val().get("room_id")
    except AttributeError:
        return None


def get_room(room_id):
    ''' Returns a room from an ID '''
    return db.child("rooms").child(room_id).get().val()


def get_name(user_id):
    ''' Returns the name of the user '''
    return db.child("users").child(user_id).get().val().get("name")


def get_lang(user_id):
    ''' Returns the name of the user '''
    try:
        lang = db.child("users").child(user_id).get().val().get("lang")
        return lang
    except AttributeError:
        return 'en'


def get_db_size():
    '''This retrieves the size of the database'''
    try:
        size = len(db.child("users").get().val().keys())
    except AttributeError:
        size = 0
    return str(size)


def check_new_user(user_id):
    '''This checks firebase if the user is a new user. If they are new, then
        send the appropriate greeting and add them to the database.'''
    print("Checking if " + user_id + " is a new user")
    try:
        if user_id in list(db.child("users").get().val().keys()):
            return False
        else:
            # We do have a new user!
            print("We have a new user!")
            db.child("users").child(user_id).update({"name": "New User"})
            db.child("users").child(user_id).update({"lang": "en"})
            welcome_message = """Welcome to Tell! Your language has been set to English. 
            Type '/get_commands' to get a list of commands!"""
            app.send_message(user_id, welcome_message)
            return True
    except AttributeError:
        # We do have a new user!
        print("We have a new user!")
        db.child("users").child(user_id).update({"name": "New User"})
        db.child("users").child(user_id).update({"lang": "en"})
        welcome_message = """Welcome to Tell! Your language has been set to English. 
                    Type '/get_commands' to get a list of commands!"""
        app.send_message(user_id, welcome_message)
        return True


def get_commands(user_id):
    commands = """
    ```
/join_room <room number>: Join a room
/leave_Room: Leave a room
/set_name <name>: Set your name
/set_lang <language>: Set your language. For a full list of languages type '/show_langs'
    ```"""
    app.send_message(user_id, commands)


def check_room(user_id, room_id):
    '''Checks if a user is in a room'''

    room = db.child("rooms").child(room_id).get().val()
    if room == None:
        # our room doesn't exist
        return False
    elif user_id in room:
        # Our user is in the room!
        return True
    else:
        # Our user isn't in the room :(
        return False
