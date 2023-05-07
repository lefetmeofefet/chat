import json
import uuid
from bson import ObjectId


class Message:
    def __init__(self, text, sender_name, time, seen_by, _id=None):
        self.text = text
        self.sender_name = sender_name
        self.time = time
        self.seen_by = seen_by
        if _id is None:
            self._id = ObjectId()
        else:
            self._id = _id

    def to_dict(self):
        return {
            "_id": self._id,
            "text": self.text,
            "sender_name": self.sender_name,
            "time": self.time,
            "seen_by": self.seen_by
        }

    @staticmethod
    def from_dict(message_dict):
        return Message(
            text=message_dict["text"],
            sender_name=message_dict["sender_name"],
            time=message_dict["time"],
            seen_by=message_dict["seen_by"],
            _id=message_dict["_id"]
        )
