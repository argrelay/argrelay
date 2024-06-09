from __future__ import annotations

from enum import Enum


class TopDir(Enum):
    """
    Top-level directories for `argrelay` - see also `argrelay_dir`.

    See also FS_29_54_67_86 project `dir_structure`.
    """

    BinDir = "bin"

    ConfDir = "conf"

    DataDir = "data"

    DocsDir = "docs"

    DstDir = "dst"

    ExeDir = "exe"

    SrcDir = "src"

    TestDir = "test"

    def __str__(self):
        return self.name
