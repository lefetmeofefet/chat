import sys

from rich.console import Console
from rich.text import Text
from .message import Message


class ChatTerminal:
    def __init__(self):
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

    def add_message(self, message: Message, are_you_the_sender):
        self._move_cursor_up()
        self._clear_line()

        direction = "left" if are_you_the_sender else "right"
        color = "green" if are_you_the_sender else "blue"
        sender = "you" if are_you_the_sender else message.sender_name
        if not are_you_the_sender:
            self.console.print("")
        self.console.rule(title=Text(sender, style=color), style="grey11", align=direction)
        self.console.print(message.text, justify=direction)
        # self.console.print("seen by 3/12", style="grey42", justify=direction, highlight=False)
        self.console.print("")

    def update_message_seen_by(self, message):
        # TODO: do dis
        pass

    def input_loop(self, on_input_cb):
        while True:
            text = self.console.input()
            self._move_cursor_up(1)
            self._clear_line()
            self.console.print("sending...")
            on_input_cb(text)
