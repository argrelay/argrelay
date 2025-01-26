from __future__ import annotations

from enum import Enum


class TopDir(Enum):
    """
    Top-level directories for `argrelay` - see also `argrelay_dir`.

    See also FS_29_54_67_86 project `dir_structure`.
    """

    bin_dir = "bin"

    conf_dir = "conf"

    data_dir = "data"

    docs_dir = "docs"

    dst_dir = "dst"

    exe_dir = "exe"

    src_dir = "src"

    test_dir = "test"

    tmp_dir = "tmp"

    var_dir = "var"

    def __str__(self):
        return self.name
