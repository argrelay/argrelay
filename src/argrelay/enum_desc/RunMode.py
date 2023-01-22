from enum import Enum, auto


class RunMode(Enum):
    """
    Request is meant to run in two modes:
    *   `CompletionMode` - when shell asks `argrelay` for suggestions to complete command line args.
    *   `InvocationMode` - when already executed command uses `argrelay` to determine values for all ags.
    In other words:
    *   `CompletionMode` = (proposing options) collects all possible options.
    *   `InvocationMode` = (exercising options) selects only one option out of all possible.
    Also:
    *   `CompletionMode` excludes tangent token ("touched" by the cursor) as input to provide completion for it.
    *   `InvocationMode` includes tangent token as input arg to execute selected function.
    """
    # TODO: Add docstring if true:
    #       RunMode is client-side property.
    #       It should result in different requests to server.
    #       *   `CompletionMode` (completion request to server) expects response with arg values suggested for current situation.
    #       *   `InvocationMode` (request to server for what to do) expects response with detailed command line to execute on client (or results of this execution if it was done on server side).

    CompletionMode = auto()
    InvocationMode = auto()

    def __str__(self):
        return self.name
