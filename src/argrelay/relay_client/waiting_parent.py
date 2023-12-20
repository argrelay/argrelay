import os
import time
from random import randrange

from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import eprint


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
        eprint("\b", end = "", flush = True)

    # Clean up last spinner state char:
    eprint(" \b", end = "", flush = True)

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
    # TODO: Use one and clean up the rest:
    cursor_states = [
        # f"{TermColor.spinner_state_0.value}┛{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}┗{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}┏{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}┓{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}▁{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▂{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▃{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▄{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▅{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▆{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▇{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}█{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▇{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▆{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▅{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▄{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▃{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▂{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▁{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}0{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}1{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}2{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}3{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}4{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}5{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}6{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}7{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}8{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}9{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}▖{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▘{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▝{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}▗{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}<{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}={TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}>{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}={TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}{{{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}}}{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}[{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}]{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",

        # f"{TermColor.spinner_state_0.value}\\{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}/{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value}|{TermColor.reset_style.value}",
        # f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",

        f"{TermColor.spinner_state_0.value}<{TermColor.reset_style.value}",
        f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
        f"{TermColor.spinner_state_0.value}={TermColor.reset_style.value}",
        f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
        f"{TermColor.spinner_state_0.value}>{TermColor.reset_style.value}",
        f"{TermColor.spinner_state_0.value} {TermColor.reset_style.value}",
    ]
    # Use random start state:
    random_shift = randrange(len(cursor_states))
    shifted_states = cursor_states[random_shift:] + cursor_states[:random_shift]
    while True:
        for cursor_state in shifted_states:
            yield cursor_state
