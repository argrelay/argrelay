import os
import sys
import typing
from typing import Union


def split_process() -> (
    bool,
    int,
    Union[None, typing.TextIO],
):
    """
    Part of FS_14_59_14_06 pending requests implementation.

    Returns tuple:
    *   bool: whether it is a parent (True) or a child (False)
    *   int: child PID for parent, None for child
    *   int: open file for the parent-side end of the read-only pipe with stdout of the child process, 0 for child

    The func splits parent and child processes setting up a communication pipe between the two.

    The pipe works in the single direction from child to parent:
    *   child connects its stdout to the pipe (instead of a terminal)
    *   parent uses the pipe to read results from the child, but does it only after child completes

    This way, while waiting for the child to complete, the parent can print anything to the terminal
    without interleaving with the child stdout.

    Both child and parent still keep their stderr connected to the terminal (this output may interleave).

    NOTE: Technically, using the extra pipe between parent and child is not required
          for `ServerAction.ProposeArgValues` = Tab because Bash already captures
          stdout in that case until client completes.
          But implementation is uniform here for simplicity.
    """
    # Create pipe for the child to write results as its stdout:
    r_child_stdout_fd, w_child_stdout_fd = os.pipe()
    child_pid: int = os.fork()

    if child_pid > 0:
        os.close(w_child_stdout_fd)
        # Parent reads from the pipe to the child (later, when child has completed):
        child_stdout = os.fdopen(r_child_stdout_fd)
        return (
            True,
            child_pid,
            child_stdout,
        )
    elif child_pid == 0:
        os.close(r_child_stdout_fd)
        # Child writes to the pipe (instead of the terminal) -
        # close original stdout file descriptor and use pipe:
        # https://stackoverflow.com/a/31503924/441652
        os.dup2(w_child_stdout_fd, sys.stdout.fileno())
        os.close(w_child_stdout_fd)
        return (
            False,
            0,
            None,
        )
    else:
        raise RuntimeError("could not fork child process")
