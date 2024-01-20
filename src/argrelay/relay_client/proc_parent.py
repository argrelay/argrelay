import os
import signal
import time
from random import randrange

from argrelay.client_spec.ShellContext import ShellContext
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper_common import eprint

# Use regular Tab indent size:
spinner_length: int = 4

# Noticeable threshold is around 200 ms:
initial_sleep_sec: float = 0.2

# Rotate spinner state every:
spinner_frame_sec: float = 0.1

def signal_handler(signal_number, signal_frame):
    if signal_number == signal.SIGCHLD:
        # The child exited:
        pass


def spin_wait_for_child(
    child_pid: int,
    shell_ctx: ShellContext,
):
    """
    Display spinner while child request is running.
    """

    signal.signal(signal.SIGCHLD, signal_handler)
    # Prevent spinner on instant replies - have an initial sleep first
    # before drawing spinner for the first time
    # (this sleep will exit prematurely if the child exits):
    time.sleep(initial_sleep_sec)
    if not is_child_running(child_pid):
        return

    # We waited enough - start spinner:
    pending_cursor = generate_pending_cursor()
    while is_child_running(child_pid):
        # Print spinner state chars:
        eprint(next(pending_cursor), end = "", flush = True)
        time.sleep(spinner_frame_sec)
        # Step backward:
        eprint("\b" * spinner_length, end = "")

    # Overwrite spinner state chars by expected content from the prev command line
    # (padded with spaces, if beyond the end of the line):
    first_cpos = shell_ctx.cursor_cpos
    last_cpos = shell_ctx.cursor_cpos + spinner_length
    line_portion = shell_ctx.command_line[first_cpos:last_cpos]
    pad_length = spinner_length - len(line_portion)
    eprint(line_portion + " " * pad_length, end = "")
    # Step backward:
    eprint("\b" * spinner_length, end = "", flush = True)


def is_child_running(
    child_pid: int,
):
    (
        child_pid,
        child_status,
    ) = os.waitpid(child_pid, os.WNOHANG)
    if child_pid == 0 and child_status == 0:
        return True
    else:
        return False


def generate_pending_cursor():
    cursor_states = [
        f"{TermColor.spinner_color.value}/|\\|{TermColor.reset_style.value}",
        f"{TermColor.spinner_color.value}|/|\\{TermColor.reset_style.value}",
        f"{TermColor.spinner_color.value}\\|/|{TermColor.reset_style.value}",
        f"{TermColor.spinner_color.value}|\\|/{TermColor.reset_style.value}",
    ]
    # Use random start state:
    random_shift = randrange(len(cursor_states))
    shifted_states = cursor_states[random_shift:] + cursor_states[:random_shift]
    while True:
        for cursor_state in shifted_states:
            yield cursor_state
