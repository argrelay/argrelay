import sys


def handle_main_exception(e1):
    # noinspection PyBroadException
    try:
        # Avoid leaving terminal in unexpected state.
        # For example, due to some terminal control chars printed by client partially,
        # the terminal may be left in mode which does not echo back chars typed by the user.
        if sys.stdout.isatty() or sys.stderr.isatty():
            import os
            os.system("stty sane")
    except BaseException as e2:
        pass
    raise e1
