from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DefaultConfiguratorConfig:
    """
    This class configures `DefaultConfigurator`.
    """

    project_title: str = field(default = "")
    """
    Names an instance of `argrelay`.
    """

    project_page_url: str = field(default = "")
    """
    Project a URL to project page.
    """

    git_files_by_commit_id_url_prefix: str = field(default = "")
    """
    Provides a URL prefix to access files by commit id.

    See also `AbstractConfigurator.provide_project_git_files_by_commit_id_url_prefix`.
    """

    commit_id_url_prefix: str = field(default = "")
    """
    Provides a URL prefix to access page with commit id.

    See also `AbstractConfigurator.provide_project_commit_id_url_prefix`.
    """
