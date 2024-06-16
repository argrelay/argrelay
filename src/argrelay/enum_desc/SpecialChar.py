from enum import Enum


class SpecialChar(Enum):
    """
    Character (or groups of them) which have special meaning on the command line.
    """

    TokenDelimiter = "\\s+"
    """
    See FS_27_16_67_19 line syntax.
    """

    ArgBucketDelimiter = "%"
    """
    See FS_97_64_39_94 arg buckets.
    """

    KeyValueDelimiter = ":"
    """
    See FS_20_88_05_60 named args.
    """

    NoPropValue = "~"
    """
    The choice of `~` was dictated by the two facts:
    *   `~` is not supposed to be typed (and it expands into user name in Bash which also hides plain `~`)
    *   `~` sorts last among alphanumeric characters

    See: TODO_39_25_11_76: `data_envelope`-s with missing props.
    """
