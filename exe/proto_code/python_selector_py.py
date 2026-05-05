from __future__ import annotations

import shutil


def select_python_file_abs_path(required_version: tuple[int, int, int]) -> str | None:
    """
    Implements `SelectorFunc.select_python_file_abs_path` from `protoprimer.primer_kernel`.
    """

    return shutil.which("python")
