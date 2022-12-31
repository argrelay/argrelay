"""
"""

import sys


# noinspection SpellCheckingInspection
def eprint(*args, **kwargs):
    print(*args, file = sys.stderr, **kwargs)


def to_dict(instance):
    return {
        k: v for k, v in
        vars(instance).items()
        if not str(k).startswith('_')
    }
