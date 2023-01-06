from enum import Enum


class TermColor(Enum):
    """
    Color codes for terminal text
    """

    DARK_RED = '\033[31m'
    DARK_GREEN = '\033[32m'
    DARK_YELLOW = '\033[33m'
    DARK_GRAY = '\033[90m'

    BRIGHT_BLUE = '\033[94m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GRAY = '\033[37m'

    DEBUG = DARK_GRAY
    INFO = BRIGHT_GREEN

    WARNING = '\033[93m'
    FAIL = '\033[91m'

    RESET = '\033[0m'
