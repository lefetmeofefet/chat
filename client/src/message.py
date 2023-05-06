import json


class Message:
    def __init__(self, text, sender_name, time, seen_by, message_id):
        self.text = text
        self.sender_name = sender_name
        self.time = time
        self.seen_by = seen_by
        self.message_id = message_id

    @staticmethod
    def deserialize(message):
        message_dict = json.loads(message)
        return Message(
            text=message_dict["text"],
            sender_name=message_dict["sender_name"],
            time=message_dict["time"],
            seen_by=message_dict["seen_by"],
            message_id=message_dict["message_id"]
        )
