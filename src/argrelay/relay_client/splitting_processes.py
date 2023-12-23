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
    Part of FS_14_59_14_06 pending requests implementation:

    The func splits parent and child processes setting up a communication pipe between the two.
    The pipe works in the single direction from child to parent:
    *   child uses the pipe to write its stdout
    *   parent uses the pipe to read results from the child when it completes

    Returns tuple:
    *   bool: whether it is a child (True) or a parent (False)
    *   int: child PID for parent, None for child
    *   int: open file for the parent-side end of the read-only pipe with stdout of the child process, 0 for child
    """
    # Create pipe for the child to write results as its stdout:
    r_child_stdout_fd, w_child_stdout_fd = os.pipe()
    child_pid: int = os.fork()
    if child_pid == 0:
        os.close(r_child_stdout_fd)
        # Child writes to the pipe (instead of the terminal):
        sys.stdout = os.fdopen(w_child_stdout_fd, "w")
        return (
            True,
            0,
            None,
        )
    elif child_pid > 0:
        os.close(w_child_stdout_fd)
        # Parent reads from the pipe to the child (later, when child has completed):
        child_stdout = os.fdopen(r_child_stdout_fd)
        return (
            False,
            child_pid,
            child_stdout,
        )
    else:
        raise RuntimeError("could not fork child process")
