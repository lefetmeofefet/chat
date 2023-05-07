import pymongo
from bson import ObjectId
import os
from .message import Message

MONGO_CONNECTION_STRING = os.environ[
    'MONGO_CONNECTION_STRING'] if 'MONGO_CONNECTION_STRING' in os.environ else "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(MONGO_CONNECTION_STRING)


class Database:
    def __init__(self):
        chat_db = mongo_client.chat
        self.messages = chat_db.messages
        self.users = chat_db.users

    def get_messages(self, room):
        messages = []
        for message in self.messages.find({"room": room}).sort("time"):
            messages.append(Message.from_dict(message))
        return messages

    def save_message(self, message: Message, room):
        message_dict = message.to_dict()
        message_dict["room"] = room
        self.messages.insert_one(message_dict)

    def update_seen_by(self, message_id, name):
        self.messages.update_one({'_id': ObjectId(message_id)}, {'$push': {'seen_by': name}})

    def does_user_exist(self, name):
        user = self.users.find_one({"name": name})
        return user is not None

    def create_user(self, name, password_hash, session_id, session_expiration):
        self.users.insert_one({
            "name": name,
            "password_hash": password_hash,
            "session_id": session_id,
            "session_expiration": session_expiration
        })

    def get_user(self, name):
        return self.users.find_one({"name": name})

    def set_user_session(self, name, session_id, session_expiration):
        self.users.update_one({
            "name": name
        }, {
            "$set": {
                "session_id": session_id,
                "session_expiration": session_expiration
            }
        })


db = Database()
