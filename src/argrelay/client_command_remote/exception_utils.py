class ServerResponseError(Exception):
    """
    Exception for failed server responses.

    It is related to `ClientExitCode.ServerError`.

    Specifically, it is NOT connection error.
    """

    pass


def print_full_stack_trace(given_exception):
    """
    Print full stack trace equivalent to not catching exception.

    Somehow Python does not have standard function
    (only stack trace to current line and stack trace for exception from current caller)
    which requires implementations like these:
    https://stackoverflow.com/a/16589622/441652
    """
    import traceback, sys
    exception_obj = sys.exc_info()[0]
    # Remove curr func frame:
    caller_stack = traceback.extract_stack()[:-1]
    if exception_obj is not None:
        # Remove curr func frame:
        del caller_stack[-1]
    head_message = "Traceback (most recent call last):\n"
    caller_stack_str = head_message + "".join(traceback.format_list(caller_stack))
    if exception_obj is not None:
        exception_stack_str = traceback.format_exc().lstrip(head_message)
        full_stack_str = caller_stack_str + exception_stack_str
    else:
        exc_line = f"{type(given_exception).__name__}: {str(given_exception)}"
        full_stack_str = caller_stack_str + exc_line
    print(full_stack_str, file = sys.stderr)
