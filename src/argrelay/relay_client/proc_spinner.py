import os
import time
import typing
from random import randrange

from argrelay.client_spec.ShellContext import ShellContext
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper_common import eprint
from argrelay.relay_client.proc_split import is_child_exited

# Use regular Tab indent size:
spinner_length: int = 4

# Rotate spinner state every:
spinner_frame_sec: float = 0.1

# Results of multiple stream reads:
child_stdout_chunks: list = []

child_stderr_chunk_max_size: int = 100


def spin_wait_for_child(
    child_pid: int,
    child_stdout: typing.TextIO,
    shell_ctx: ShellContext,
    spinless_sleep_sec: float,
):
    """
    Display spinner while child request is running.
    """

    # Prevent spinner on instant replies - have an initial sleep first
    # before drawing spinner for the first time
    # (this sleep will exit prematurely if the child exits):
    if is_child_running(child_pid):
        # There is a chance that child exits here (after the check above but before the sleep below).
        # Ignore that - it is unlikely and, when it happens, the worst case is a needless sleep.
        time.sleep(spinless_sleep_sec)
    if not is_child_running(child_pid):
        return

    # We waited enough - start spinner:
    pending_cursor = generate_pending_cursor()
    is_child_running_var: bool = is_child_running(child_pid)
    while (
        is_child_running_var
        or
        # Apparently, child block on pipe write (and never exits) if parent does not read it:
        read_next_child_stdout_chunk(child_stdout)
    ):
        # Print spinner state chars:
        eprint(next(pending_cursor), end = "", flush = True)
        if is_child_running_var:
            # Sleep only while child is running:
            time.sleep(spinner_frame_sec)
        # Step backward:
        eprint("\b" * spinner_length, end = "")
        if is_child_running_var:
            # Child exit status can be collected only once:
            is_child_running_var = is_child_running(child_pid)

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
    # NOTE: `os.waitpid` and `is_child_exited` are not atomic - do we need to keep `assert` below?
    if child_pid == 0 and child_status == 0:
        assert not is_child_exited()
        return True
    else:
        assert is_child_exited()
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


def read_next_child_stdout_chunk(
    child_stdout: typing.TextIO,
) -> bool:
    child_stdout_chunk = child_stdout.read(child_stderr_chunk_max_size)
    if child_stdout_chunk:
        child_stdout_chunks.append(child_stdout_chunk)
        return True
    else:
        return False


def print_child_stdout_chunks():
    for child_stdout_chunk in child_stdout_chunks:
        print(child_stdout_chunk, flush = True, end = "")


def spinner_main(
    child_pid,
    child_stdout,
    client_config,
    shell_ctx,
):
    spin_wait_for_child(
        child_pid,
        child_stdout,
        shell_ctx,
        client_config.spinless_sleep_sec,
    )
    while read_next_child_stdout_chunk(child_stdout):
        pass
    print_child_stdout_chunks()
