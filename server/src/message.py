import json
import uuid


class Message:
    def __init__(self, text, sender_name, time, seen_by, message_id=None):
        self.text = text
        self.sender_name = sender_name
        self.time = time
        self.seen_by = seen_by
        if message_id is None:
            self.message_id = str(uuid.uuid4())
        else:
            self.message_id = message_id

    def serialize(self):
        return json.dumps({
            "message_id": self.message_id,
            "text": self.text,
            "sender_name": self.sender_name,
            "time": self.time,
            "seen_by": self.seen_by
        }).encode()

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
