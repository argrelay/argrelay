from argrelay.plugin_delegator.DelegatorAbstract import DelegatorAbstract


class DelegatorSingleFuncAbstract(DelegatorAbstract):
    """
    This is a base delegator which implements single func.

    TODO: TODO_06_54_83_58: extend via func instead of delegator:
    Unlike this (single func) class, its base `DelegatorAbstract` is potentially responsible for
    multiple funcs which is a bad pattern leading to complex logic (to handle each func differently)
    without separation of concerns.
    """
