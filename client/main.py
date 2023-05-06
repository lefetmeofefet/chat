import sys
import _thread
import time

from rich.console import Console
from rich.text import Text


def move_cursor_up(lines=1):
    sys.stdout.write(f"\u001b[{lines}A")


def move_cursor_down(lines=1):
    sys.stdout.write(f"\u001b[{lines}B")


def move_cursor_left(lines=1):
    sys.stdout.write(f"\u001b[{lines}D")


def clear_line():
    sys.stdout.write("\u001b[2K")


console = Console()
console.clear()
console.set_window_title("Granuchat")
console.print("Welcome to Granuchat!", style="red", justify="center")
console.print("")


def incoming_messages_loopy_loop():
    while True:
        time.sleep(2)
        move_cursor_up()
        clear_line()

        console.rule(style="#222222")
        console.print("i am sender", style="blue", justify="right")
        console.print("i am message content, read me", justify="right")
        console.print("seen by 3/12", style="#666666", justify="right", highlight=False)
        console.print("")


_thread.start_new_thread(incoming_messages_loopy_loop, ())

while True:
    message = console.input()
    move_cursor_up(1)
    clear_line()
    console.print("sending...")
    time.sleep(0.3)

    move_cursor_up()
    clear_line()
    console.rule(style="#222222")
    console.print("you", style="green", justify="left")
    console.print(message, justify="left")
    console.print("seen by 3/12", style="#666666", justify="left", highlight=False)
    console.print("")
