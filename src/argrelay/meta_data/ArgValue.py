from argrelay.meta_data.ArgSource import ArgSource


# TODO: Forget about coords everywhere, use args for input, maybe coord for the term of core library.
class ArgValue:
    arg_value: str
    arg_source: ArgSource
    is_required: bool

    def __init__(self, arg_value: str, arg_source: ArgSource):
        self.arg_value = arg_value
        self.arg_source = arg_source
        # TODO: This should be moved elsewhere (whether it is required or not depends on other args):
        self.is_required = None

    def __eq__(self, other):
        if isinstance(other, ArgValue):
            return (
                self.arg_value == other.arg_value and
                self.arg_source == other.arg_source and
                self.is_required == self.is_required
            )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.arg_value!r}, {self.arg_source!r}, {self.is_required!r})"
