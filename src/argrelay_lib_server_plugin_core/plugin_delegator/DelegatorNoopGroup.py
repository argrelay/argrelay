from __future__ import annotations

from argrelay_lib_server_plugin_core.plugin_delegator.DelegatorNoopBase import DelegatorNoopBase


class DelegatorNoopGroup(DelegatorNoopBase):
    """
    The purpose of this delegator is to group other delegators.

    It groups delegators as its dependency list - see `plugin_dependencies`.
    """
