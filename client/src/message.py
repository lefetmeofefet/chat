import json


class Message:
    def __init__(self, text, sender_name, time, seen_by, _id):
        self.text = text
        self.sender_name = sender_name
        self.time = time
        self.seen_by = seen_by
        self._id = _id
        self.message_index = None

    @staticmethod
    def from_dict(message_dict):
        return Message(
            text=message_dict["text"],
            sender_name=message_dict["sender_name"],
            time=message_dict["time"],
            seen_by=message_dict["seen_by"],
            _id=message_dict["_id"]
        )
