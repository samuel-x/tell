from pymessenger import Element


MENU = """{
  "setting_type" : "call_to_actions",
  "thread_state" : "existing_thread",
  "call_to_actions":[
    {
      "type":"postback",
      "title":"Set Language",
      "payload":"/set_lang"
    },
    {
      "type":"postback",
      "title":"Leave Room",
      "payload":"/leave_room"
    },
    {
      "type":"postback",
      "title":"Join a Different Room",
      "payload":"/join_room"
    },
    {
      "type":"postback",
      "title":"Set Your Name",
      "payload":"/set_name"
    }
  ]
}"""

BUTTONS = Element(buttons="""[
    {
      "type":"postback",
      "title":"Set Language",
      "payload":"/set_lang"
    },
    {
      "type":"postback",
      "title":"Leave Room",
      "payload":"/leave_room"
    },
    {
      "type":"postback",
      "title":"Join a Different Room",
      "payload":"/join_room"
    },
    {
      "type":"postback",
      "title":"Set Your Name",
      "payload":"/set_name"
    }
  ]""")