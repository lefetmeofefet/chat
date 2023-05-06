import _thread
import json
import socket

from .message import Message

HOST = "localhost"  # The server's hostname or IP address
PORT = 6668  # The port used by the server


class Api:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        # TODO: Error handling

    def listen_to_messages(self, on_message_cb):
        _thread.start_new_thread(self._listen_to_messages_thread, (on_message_cb,))

    def _listen_to_messages_thread(self, on_message_cb):
        while True:
            data = self.socket.recv(1024)
            parsed_message = Message.deserialize(data)
            # TODO: Error handling
            on_message_cb(parsed_message)

    def send_message(self, text):
        self.socket.sendall(json.dumps({
            "text": text
        }).encode())
