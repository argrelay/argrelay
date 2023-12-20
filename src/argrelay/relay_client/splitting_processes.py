import os
import sys


def split_process():
    # Create pipe for child to write results to its stdout:
    r_child_stdout, w_child_stdout = os.pipe()
    child_pid: int = os.fork()
    if child_pid == 0:
        os.close(r_child_stdout)
        # Child writes to the pipe (instead of the terminal):
        sys.stdout = os.fdopen(w_child_stdout, "w")
        # Child performs request:
        return True
    else:
        os.close(w_child_stdout)
        # Parent reads from the pipe to the child (later, when child has completed):
        child_stdout = os.fdopen(r_child_stdout)
        # Parent spins:
        from argrelay.relay_client.waiting_parent import spin_while_waiting
        spin_while_waiting(child_pid, child_stdout)
        return False
