import os
import time
import typing
from random import randrange

from argrelay.client_spec.ShellContext import ShellContext
from argrelay.enum_desc.ProcRole import ProcRole
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper_common import eprint
from argrelay.relay_client.ClientRemote import ClientRemote
from argrelay.relay_client.proc_splitter import has_child_exited

# Use regular Tab indent size:
spinner_length: int = 4

# Rotate spinner state every:
spinner_frame_sec: float = 0.1

# Results of multiple stream reads:
child_data_chunks: list = []

child_data_chunk_max_size: int = 1024


def spin_wait_for_child(
    r_pipe_end: typing.BinaryIO,
    shell_ctx: ShellContext,
    spinless_sleep_sec: float,
):
    """
    Display spinner while child request is running.
    """

    # Ensure we can read from the pipe without blocking if there is no input ready:
    os.set_blocking(r_pipe_end.fileno(), False)

    # TODO: Try busy spin for the `spinless_sleep_sec` instead of sleeping?
    # TODO: Maybe, once spinner started, spin even while pumping?

    # Prevent spinner on instant replies - have an initial sleep first
    # before drawing spinner for the first time
    # (this sleep will exit prematurely if the child exits):
    if not has_child_exited():
        # There is a chance that child exits here (after the check above but before the sleep below).
        # Ignore that - it is unlikely and, when it happens, the worst case is a needless sleep.
        time.sleep(spinless_sleep_sec)
    if has_child_exited():
        # Pump out the rest of data without spinner:
        return

    # We waited enough - start spinner:
    pending_cursor = generate_pending_cursor()
    is_read_successful: bool = read_next_child_data_chunk(r_pipe_end)
    while (
        # Ensure first that no input is ready.
        # Child block on pipe write (and never exits) if parent does not read it:
        is_read_successful
        or
        not has_child_exited()
    ):
        # Print spinner state chars:
        eprint(next(pending_cursor), end = "", flush = True)
        if not is_read_successful:
            # Sleep only while read failed -
            # if child is still running and read is successful,
            # keep pumping data out of the pipe without sleeping:
            time.sleep(spinner_frame_sec)
        # Step backward:
        eprint("\b" * spinner_length, end = "")
        is_read_successful: bool = read_next_child_data_chunk(r_pipe_end)
        if has_child_exited():
            # Pump out the rest of data without spinner:
            break

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


def read_next_child_data_chunk(
    r_pipe_end: typing.BinaryIO,
) -> bool:
    child_data_chunk = r_pipe_end.read(child_data_chunk_max_size)
    if child_data_chunk:
        child_data_chunks.append(child_data_chunk)
        return True
    else:
        return False


def spinner_main(
    call_ctx,
    client_config,
    proc_role: ProcRole,
    is_optimized_completion,
    r_pipe_end,
):
    spin_wait_for_child(
        r_pipe_end,
        call_ctx,
        client_config.spinless_sleep_sec,
    )

    while read_next_child_data_chunk(r_pipe_end):
        pass

    abstract_client = ClientRemote(
        client_config,
        proc_role,
        None,
        is_optimized_completion,
        -1,
    )
    # TODO: Rethink/Rename: spinner does not make any request:
    #       Maybe remove *Client altogether and move its functionality into *ClientCommandFactory?
    #       Then simply execute command here?
    abstract_client.make_request(call_ctx)
