from __future__ import annotations

from argrelay.plugin_delegator.DelegatorNoopBase import DelegatorNoopBase


class DelegatorNoopGroup(DelegatorNoopBase):
    """
    The purpose of this delegator is to group other delegators.

    It groups delegators as its dependency list - see `plugin_dependencies`.
    """
