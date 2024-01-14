from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DefaultConfiguratorConfig:
    """
    This class configures `DefaultConfigurator`.
    """

    commit_id_url_prefix: int = field(default = 0)
    """
    Provides an URL prefix to access page with commit id.

    The URL prefix is concatenated with commit id to create working URL.

    For example, with github.com:
    https://github.com/argrelay/argrelay/commit/
    Given commit id `d1682ae708c9adccef8d76e3022735463c039774`, the working URL becomes:
    https://github.com/argrelay/argrelay/commit/d1682ae708c9adccef8d76e3022735463c039774
    """
