import _thread
import json
import socket

from .message import Message


class Api:
    def __init__(self, host, port):
        self.session_id = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        # TODO: Error handling

    def send_request(self, request_dict):
        if self.session_id is not None:
            request_dict["session_id"] = self.session_id
        # the null byte is for delimiting multiple messages in the same 'socket.recv' call
        serialized_request = json.dumps(request_dict, default=str).encode() + b'\0'
        self.socket.sendall(serialized_request)

    def wait_for_message_flux(self):
        requests = self.socket.recv(1048576)  # Max tcp receive size
        requests = requests[:-1]  # Remove the null byte at the end
        return [json.loads(request) for request in requests.split(b"\0")]

    def listen_to_messages(self, on_message_cb, on_message_seen_cb, on_messages_history_cb):
        _thread.start_new_thread(self._listen_to_messages_thread,
                                 (on_message_cb, on_message_seen_cb, on_messages_history_cb))

    def _listen_to_messages_thread(self, on_message_cb, on_message_seen_cb, on_messages_history_cb):
        while True:
            for request in self.wait_for_message_flux():
                # TODO: Error handling
                if request["type"] == "message":
                    on_message_cb(Message.from_dict(request["message"]))
                elif request["type"] == "seen_message":
                    on_message_seen_cb(
                        request["message_id"],
                        request["seen_by"]
                    )
                elif request["type"] == "messages_history":
                    on_messages_history_cb(
                        [Message.from_dict(message_dict) for message_dict in request["messages"]]
                    )

    def check_if_user_exists(self, name):
        self.send_request({
            "type": "does_user_exist",
            "name": name
        })
        response = self.wait_for_message_flux()[0]
        return response["user_exists"]

    def register(self, name, password_hash):
        self.send_request({
            "type": "register",
            "name": name,
            "password_hash": password_hash
        })
        response = self.wait_for_message_flux()[0]
        self.session_id = response["session_id"]

    def login(self, name, password_hash):
        self.send_request({
            "type": "login",
            "name": name,
            "password_hash": password_hash
        })
        response = self.wait_for_message_flux()[0]
        self.session_id = response["session_id"]

    def send_message(self, text):
        self.send_request({
            "type": "message",
            "text": text
        })

    def enter_room(self, room):
        self.send_request({
            "type": "enter_room",
            "room": room
        })

    def update_seen_message(self, message):
        self.send_request({
            "type": "seen_message",
            "message_id": message._id
        })
