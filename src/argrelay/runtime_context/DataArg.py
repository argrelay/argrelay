"""
This module lists concreate implementations of `AbstractArg`-s.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from argrelay.runtime_context.AbstractArg import (
    ArgCommandValueOffered, ArgCommand, ArgCommandValueDictated,
    ArgCommandIncomplete,
)


@dataclass
class ArgCommandData(ArgCommand):
    """
    Implements `command_arg` - see FS_27_16_67_19 line syntax
    """

    token_ipos_list: list[int] = field()
    """
    List of all token ipos-es (indexes) belonging to that arg.
    
    These ipos-es reference entries within `ParsedContext.all_tokens`.
    """

    def get_arg_tokens(
        self,
    ) -> list[int]:
        return self.token_ipos_list


@dataclass
class ArgCommandDataValue(ArgCommandData):
    """
    Extends `ArgCommandData` with `arg_value`.
    """

    arg_value: str = field()

    def get_arg_value(
        self
    ) -> str:
        return self.arg_value


@dataclass
class ArgCommandDataValueOffered(ArgCommandDataValue, ArgCommandValueOffered):
    """
    Implements FS_96_46_42_30 `offered_arg`.
    """


@dataclass
class ArgCommandDataValueDictated(ArgCommandDataValue, ArgCommandValueDictated):
    """
    Implements FS_20_88_05_60 `dictated_arg``.
    """

    arg_name: str = field()

    def get_arg_name(
        self
    ) -> str:
        return self.arg_name



@dataclass
class ArgCommandDataIncomplete(ArgCommandData, ArgCommandIncomplete):
    """
    Implements FS_08_58_30_24 `incomplete_arg`.
    """

    arg_name: str = field()

    def get_arg_name(
        self
    ) -> str:
        return self.arg_name
