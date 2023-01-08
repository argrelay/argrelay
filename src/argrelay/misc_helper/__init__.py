"""
"""
import sys


# noinspection SpellCheckingInspection
def eprint(*args, **kwargs):
    print(*args, file = sys.stderr, **kwargs)


# TODO: Are you sure it is required? Looks hacky.
def to_dict(instance):
    return {
        k: v for k, v in
        vars(instance).items()
        if not str(k).startswith('_')
    }


def ensure_value_is_enum(enum_value, enum_cls):
    """
    It seems that if a schema field is defined as `fields.Enum`, it must be enum item instance, not `str`.
    """
    if isinstance(enum_value, str):
        return enum_cls[enum_value]
    else:
        return enum_value
