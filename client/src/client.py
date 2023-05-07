import hashlib
from .api import Api
from .chat_terminal import ChatTerminal
from .message import Message


class Client:
    def __init__(self):
        try:
            self.messages = {}
            self.chat_terminal = ChatTerminal()
            (host, port) = self.chat_terminal.ask_for_server_address()
            try:
                self.server_api = Api(host, port, self.error_from_server)
            except ConnectionRefusedError:
                self.chat_terminal.error_and_exit("Server is down or server address is wrong")
            name = self.login_sequence()
            self.name = name
            self.room = self.chat_terminal.ask_for_room()
            self.server_api.enter_room(self.room)
            self.chat_terminal.notify_entered_room(self.room)
        except Exception as e:
            self.chat_terminal.error_and_exit(str(e))

        self.server_api.listen_to_messages(self.message_received, self.message_seen_by, self.messages_downloaded)
        self.chat_terminal.input_loop(self.send_message)

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login_sequence(self):
        name = self.chat_terminal.ask_for_name()
        user_exists = self.server_api.check_if_user_exists(name)
        if user_exists:
            password = self.chat_terminal.ask_for_password(is_new_user=False)
            while True:
                login_successful = self.server_api.login(name, password_hash=self.hash_password(password))
                if login_successful:
                    break
                password = self.chat_terminal.wrong_password_prompt()
        else:
            password = self.chat_terminal.ask_for_password(is_new_user=True)
            self.server_api.register(name, password_hash=self.hash_password(password))
        return name

    def message_received(self, message: Message):
        self.messages[message._id] = message
        self.chat_terminal.add_message(
            message,
            my_name=self.name,
        )
        if self.name not in message.seen_by:  # Do not send "seen" if you've already seen it
            self.server_api.update_seen_message(message)

    def messages_downloaded(self, messages: [Message]):
        for message in messages:
            self.message_received(message)

    def message_seen_by(self, message_id, name):
        message = self.messages[message_id]
        message.seen_by.append(name)
        self.chat_terminal.update_message_seen_by(
            self.messages[message_id],
            my_name=self.name
        )

    def send_message(self, text):
        self.server_api.send_message(text)

    def error_from_server(self, error):
        self.chat_terminal.error_and_exit(error)


if __name__ == '__main__':
    Client()
