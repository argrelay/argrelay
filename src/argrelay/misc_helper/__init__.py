"""
"""
import os
import sys

# This global variable is (supposed to be) overridden by `run_argrelay_client` and `run_argrelay_server` or
# whatever/whoever starts `argrelay` code to set to `@/` (`argrelay_dir`) according to FS_29_54_67_86 dir_structure:
_argrelay_dir = None


def set_argrelay_dir(argrelay_dir):
    global _argrelay_dir
    _argrelay_dir = argrelay_dir


def get_argrelay_dir():
    return _argrelay_dir


# noinspection SpellCheckingInspection
def eprint(*args, **kwargs):
    print(*args, file = sys.stderr, **kwargs)


def ensure_value_is_enum(enum_value, enum_cls):
    """
    It seems that if a schema field is defined as `fields.Enum`, it must be enum item instance, not `str`.
    """
    if isinstance(enum_value, str):
        return enum_cls[enum_value]
    else:
        return enum_value


def get_config_path(conf_rel_path: str) -> str:
    if "ARGRELAY_CONF_BASE_DIR" in os.environ:
        base_conf_dir = os.environ.get("ARGRELAY_CONF_BASE_DIR")
    else:
        user_dir = os.path.expanduser("~/.argrelay.conf.d/")
        if os.path.exists(user_dir):
            base_conf_dir = user_dir
        elif _argrelay_dir:
            base_conf_dir = f"{_argrelay_dir}/conf/"
        else:
            raise RuntimeError("argrelay_dir is not defined")
    return f"{base_conf_dir}/{conf_rel_path}"
