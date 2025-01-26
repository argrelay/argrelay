import os
import signal

_child_status: int = 0
_child_exit_code: int = 0
_child_pid: int = 0
_child_exited: bool = False


def _signal_handler(signal_number, ignored_signal_frame):
    if signal_number == signal.SIGCHLD:
        global _child_status
        global _child_exit_code
        global _child_pid
        global _child_exited

        _child_exited = True
        (
            _child_pid,
            _child_status,
        ) = os.waitpid(_child_pid, os.WNOHANG)

        # Decode exit_code:
        # https://github.com/python/cpython/issues/84275#issuecomment-1093867008
        if os.WIFSIGNALED(_child_status):
            _child_exit_code = -os.WTERMSIG(_child_status)
        elif os.WIFEXITED(_child_status):
            _child_exit_code = os.WEXITSTATUS(_child_status)
        elif os.WIFSTOPPED(_child_status):
            _child_exit_code = -os.WSTOPSIG(_child_status)
        else:
            raise RuntimeError(f"unrecognized child_status: {_child_status}")


def has_child_exited() -> bool:
    global _child_exited
    return _child_exited


def is_child_successful() -> bool:
    return get_child_exit_code() == 0


def get_child_exit_code() -> int:
    global _child_exit_code
    assert has_child_exited()
    return _child_exit_code


def split_process() -> (
    bool,
    int,
    "typing.BinaryIO",
    "typing.BinaryIO",
):
    """
    Part of FS_14_59_14_06 pending requests implementation.

    The func splits parent and child processes setting up a communication pipe between the two.

    Returns tuple:
    *   bool: whether it is a parent (True) or a child (False)
    *   int: child PID for parent, None for child
    *   io: open pipe between parent and child:
        *   read-only pipe for parent
        *   write-only pipe for child

    The pipe contains data from child which, in turn, was received by child from server.

    This way, while waiting for the child to complete, the parent can do anything else (like drawing spinner).

    Both child and parent still keep their stdout and stderr connected to the terminal (this output may interleave).
    But it is expected that child prints nothing to stdout and only uses stderr in case of failure.

    NOTE: Technically, using the extra pipe between parent and child is not required
          for `ServerAction.ProposeArgValues` = Tab because Bash already captures
          stdout in that case until client completes.
          But implementation is uniform here for simplicity.
    """

    # Create pipe for the between parent and (future) child:
    r_pipe_fd, w_pipe_fd = os.pipe()

    # This seems unnecessary (probably necessary for `os.exec`), but anyway:
    # https://stackoverflow.com/q/30277081/441652
    os.set_inheritable(r_pipe_fd, True)
    os.set_inheritable(w_pipe_fd, True)

    signal.signal(signal.SIGCHLD, _signal_handler)
    child_pid: int = os.fork()

    if child_pid > 0:
        # Parent: does not write:
        os.close(w_pipe_fd)
        # Parent: reads from the pipe connected to the child:
        r_pipe_end = os.fdopen(r_pipe_fd, "rb")

        global _child_pid
        _child_pid = child_pid

        return (
            True,
            child_pid,
            r_pipe_end,
            None,
        )
    elif child_pid == 0:
        # Child: does not read:
        os.close(r_pipe_fd)
        # Child: writes into the pipe connected to the parent:
        w_pipe_end = os.fdopen(w_pipe_fd, "wb")

        return (
            False,
            0,
            None,
            w_pipe_end,
        )
    else:
        raise RuntimeError("could not fork child process")
