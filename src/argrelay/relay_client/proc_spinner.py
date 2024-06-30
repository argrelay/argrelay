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

child_stdout_chunk_max_size: int = 1000


def spin_wait_for_child(
    child_pid: int,
    r_child_stdout: typing.BinaryIO,
    shell_ctx: ShellContext,
    spinless_sleep_sec: float,
):
    """
    Display spinner while child request is running.
    """

    # Ensure we can read from the pipe without blocking if there is no input ready:
    os.set_blocking(r_child_stdout.fileno(), False)

    # Prevent spinner on instant replies - have an initial sleep first
    # before drawing spinner for the first time
    # (this sleep will exit prematurely if the child exits):
    if not is_child_exited():
        # There is a chance that child exits here (after the check above but before the sleep below).
        # Ignore that - it is unlikely and, when it happens, the worst case is a needless sleep.
        time.sleep(spinless_sleep_sec)
    if is_child_exited():
        return

    # We waited enough - start spinner:
    pending_cursor = generate_pending_cursor()
    is_child_running_var: bool = not is_child_exited()
    while (
        # Ensure first that no input is ready.
        # Child block on pipe write (and never exits) if parent does not read it:
        read_next_child_stdout_chunk(r_child_stdout)
        or
        is_child_running_var
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
            is_child_running_var = not is_child_exited()

    # Overwrite spinner state chars by expected content from the prev command line
    # (padded with spaces, if beyond the end of the line):
    first_cpos = shell_ctx.cursor_cpos
    last_cpos = shell_ctx.cursor_cpos + spinner_length
    line_portion = shell_ctx.command_line[first_cpos:last_cpos]
    pad_length = spinner_length - len(line_portion)
    eprint(line_portion + " " * pad_length, end = "")
    # Step backward:
    eprint("\b" * spinner_length, end = "", flush = True)


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


# TODO: This function (in the condition for while-loop)
#       may block child from writing more until next iteration of spinner
def read_next_child_stdout_chunk(
    r_child_stdout: typing.BinaryIO,
) -> bool:
    child_stdout_chunk = r_child_stdout.read(child_stdout_chunk_max_size)
    if child_stdout_chunk:
        child_stdout_chunks.append(child_stdout_chunk)
        return True
    else:
        return False


# TODO: spinner does not print stdout of worker anymore:
# def print_child_stdout_chunks():
#     for child_stdout_chunk in child_stdout_chunks:
#         print(child_stdout_chunk, flush = True, end = "")


def spinner_main(
    child_pid,
    r_child_stdout,
    client_config,
    shell_ctx,
):
    spin_wait_for_child(
        child_pid,
        r_child_stdout,
        shell_ctx,
        client_config.spinless_sleep_sec,
    )
    while read_next_child_stdout_chunk(r_child_stdout):
        pass
    # TODO: spinner does not print stdout of worker anymore:
    # print_child_stdout_chunks()
