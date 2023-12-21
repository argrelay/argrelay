import os
import time
from random import randrange

from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import eprint

spinner_length: int = 4

def spin_while_waiting(
    child_pid: int,
    child_stdout,
):
    """
    Display spinner while child request is running.
    """
    pending_cursor = generate_pending_cursor()
    while is_running(child_pid):
        eprint(next(pending_cursor), end = "", flush = True)
        time.sleep(0.1)
        eprint("\b" * spinner_length, end = "", flush = True)

    # Clear spinner state chars:
    eprint(" " * spinner_length + "\b" * spinner_length, end = "", flush = True)

    # Print everything what child has written:
    print(child_stdout.read())


def is_running(pid: int):
    (
        pid,
        status,
    ) = os.waitpid(pid, os.WNOHANG)
    if pid == 0 and status == 0:
        return True
    else:
        return False


def generate_pending_cursor():
    cursor_states = [
        f"{TermColor.spinner_color.value}|   {TermColor.reset_style.value}",
        f"{TermColor.spinner_color.value} |  {TermColor.reset_style.value}",
        f"{TermColor.spinner_color.value}  | {TermColor.reset_style.value}",
        f"{TermColor.spinner_color.value}   |{TermColor.reset_style.value}",
    ]
    # Use random start state:
    random_shift = randrange(len(cursor_states))
    shifted_states = cursor_states[random_shift:] + cursor_states[:random_shift]
    while True:
        for cursor_state in shifted_states:
            yield cursor_state
