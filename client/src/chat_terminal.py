import sys

from rich.console import Console
from rich.text import Text
from .message import Message


class ChatTerminal:
    def __init__(self):
        self.messages_count = 0
        self.console = Console()
        self.console.clear()
        self.console.set_window_title("Granuchat")
        self.console.print("Welcome to Granuchat!", style="red", justify="center")
        self.console.print("")

    @staticmethod
    def _move_cursor_up(lines=1):
        sys.stdout.write(f"\u001b[{lines}A")

    @staticmethod
    def _move_cursor_down(lines=1):
        sys.stdout.write(f"\u001b[{lines}B")

    @staticmethod
    def _move_cursor_left(lines=1):
        sys.stdout.write(f"\u001b[{lines}D")

    @staticmethod
    def _clear_line():
        sys.stdout.write("\u001b[2K")

    @staticmethod
    def _save_cursor_position():
        sys.stdout.write("\u001b[s")

    @staticmethod
    def _restore_cursor_position():
        sys.stdout.write("\u001b[u")

    @staticmethod
    def _clear_lines_above(n):
        for _ in range(n):
            ChatTerminal._move_cursor_up()
            ChatTerminal._clear_line()

    def add_message(self, message: Message, my_name):
        self._move_cursor_up()
        self._clear_line()

        are_you_the_sender = my_name == message.sender_name
        self.messages_count += 1
        message.message_index = self.messages_count
        direction = "left" if are_you_the_sender else "right"
        color = "green" if are_you_the_sender else "blue"
        sender = "you" if are_you_the_sender else message.sender_name

        self.console.print("")
        self.console.rule(title=Text(sender, style=color), style="grey11", align=direction)
        self.console.print(message.text, justify=direction)
        self.print_seen_by(message, my_name)
        self.console.print("")

    def print_seen_by(self, message, my_name):
        are_you_the_sender = my_name == message.sender_name
        direction = "left" if are_you_the_sender else "right"
        if message.seen_by is None:
            seen_string = "nobody"
        else:
            seen_by = [seen_by for seen_by in message.seen_by if seen_by != my_name]
            seen_string = "nobody" if len(seen_by) == 0 else ", ".join(seen_by)
        self.console.print(f"seen by {seen_string}", style="grey42", justify=direction, highlight=False)

    def update_message_seen_by(self, message: Message, my_name):
        """
        Finds the message's location in the terminal and updates the "seen by" line
        :param message:
        :param my_name:
        :return:
        """
        rows_to_seen_by = 4 * (self.messages_count - message.message_index)
        self._save_cursor_position()
        self._move_cursor_up(rows_to_seen_by + 2)
        self.print_seen_by(message, my_name)
        self._restore_cursor_position()
        self._move_cursor_up()
        self.console.print("")

    def ask_for_server_address(self):
        host = self.console.input("Please enter server IP address (default is 'localhost'): ") or "localhost"
        port = self.console.input("Please enter server port (default is 6668): ") or 6668
        self.console.print(f"Connecting to {host}:{port}")
        return host, port

    def ask_for_name(self):
        self._clear_lines_above(3)
        self.console.print(f"Connected! You can log in now.")
        name = self.console.input("Please enter your nickname: ")
        while name == "":
            name = self.console.input("Name cannot be empty. Enter your nickname: ")
        return name

    def ask_for_password(self, is_new_user):
        password = self.console.input(
            f"Creating new user. Enter password: " if is_new_user else "Loggin in to existing user. Enter password: ")
        return password

    def wrong_password_prompt(self):
        self._clear_lines_above(1)
        password = self.console.input(f"Wrong password. Try again: ")
        return password

    def ask_for_room(self):
        self._clear_lines_above(3)
        room = self.console.input("Please enter chat room name (default is 'lobby'): ") or "lobby"
        self.console.print(f"Entering room {room}")
        return room

    def notify_entered_room(self, room):
        self._clear_lines_above(2)  # From previous room dialog
        self.console.print(f"You're in room {room}! You can start chatting.")
        self.console.print(f"")

    def error_and_exit(self, error):
        self.console.print(f"")
        self.console.print(f"Error: {error}", style="red")
        sys.exit(0)

    def input_loop(self, on_input_cb):
        while True:
            text = self.console.input()
            if text == "":
                text = " "  # This is so messages will not be empty, deleting the message row and fucking up the lines
            self._move_cursor_up(1)
            self._clear_line()
            on_input_cb(text)
