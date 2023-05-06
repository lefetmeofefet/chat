from .api import Api
from .chat_terminal import ChatTerminal
from .message import Message


class Client:
    def __init__(self):
        self.messages = []
        self.chat_terminal = ChatTerminal()
        self.server_api = Api()
        self.server_api.listen_to_messages(self.message_received)
        self.chat_terminal.input_loop(self.send_message)

    def message_received(self, message: Message):
        self.messages.append(message)
        self.chat_terminal.add_message(
            message,
            are_you_the_sender=message.sender_name == str(self.server_api.socket.getsockname())
        )

    def send_message(self, text):
        self.server_api.send_message(text)

    def update_seen_by(self, seen_user, message_id):
        pass


if __name__ == '__main__':
    Client()
