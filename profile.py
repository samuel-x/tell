from flask import request
import requests
import database
import app

def verify_fb_token(token_sent, verify_token):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    if token_sent == verify_token:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def parse_postback(postback, user_id):
    if postback == "JOIN_PAYLOAD":
        app.send_message(user_id, "Work in Progress...")
    elif postback == "LEAVE_PAYLOAD":
        database.leave_room(user_id)
    elif postback == "NAME_PAYLOAD":
        app.send_message(user_id, "Work in Progress...")
    elif postback == "ROOM_INFO_PAYLOAD":
        room = database.get_user_room(user_id)
        if room is None:
            app.send_message(user_id, "You're not currently in a room. Please join one.")
        else:
            app.send_message(user_id, "You're currently in room: " + room)
    elif postback == "COMMAND_INFO_PAYLOAD":
        database.get_commands(user_id)

def setup_profile(verify_token):
    url = "https://graph.facebook.com/v2.6/me/messenger_profile?access_token={0}".format(verify_token)
    profile = {
        "greeting": [
            {
               "locale": "default",
               "text": "Hello!"
            },
            {
               "locale": "en_US",
               "text": "Hello! This is a test"
            }
         ],
        "get_started": {
            "payload": "GET_STARTED_PAYLOAD"
        },
        "whitelisted_domains": [
            "https://facebook.com/"
        ],
        "persistent_menu":
        [
            {
                "locale":"default",
                "composer_input_disabled": False,
                "call_to_actions":[
                {
                    "title":"Room Options",
                    "type":"nested",
                    "call_to_actions":
                    [
                        {
                            "title":"Join a Room",
                            "type":"postback",
                            "payload":"JOIN_PAYLOAD"
                        },
                        {
                            "title":"Leave Room",
                            "type":"postback",
                            "payload":"LEAVE_PAYLOAD"
                        },
                        {
                            "title":"Room Information",
                            "type":"postback",
                            "payload":"ROOM_INFO_PAYLOAD"
                        }

                    ]
                },
                {
                    "title": "Set Name",
                    "type": "postback",
                    "payload": "NAME_PAYLOAD"
                },
                {
                    "type":"web_url",
                    "title":"Set Language",
                    "url":"http://www.messenger.com/",
                    "webview_height_ratio":"full"
                }
              ]
            }

        ]
    }

    req = requests.post(url, json=profile)
    return req.json()