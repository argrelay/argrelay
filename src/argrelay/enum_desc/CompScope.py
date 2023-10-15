from __future__ import annotations

from enum import IntEnum

from argrelay.enum_desc.CompType import CompType


class CompScope(IntEnum):
    """
    Provides scope of completion.

    Roughly this means:
    *   size of the proposed list of values
    *   allowed sources of values for completion
    """

    ScopeUnknown = 0

    ScopeInitial = 1

    ScopeSubsequent = 2

    @classmethod
    def from_comp_type(
        cls,
        comp_type: CompType,
    ) -> CompScope:
        """
        Original idea is to decouple client and server.

        Completion type based on action in Bash (see `CompType`) seen by client includes artificial cases
        like `CompType.DescribeArgs` and `CompType.InvokeAction` which are already orthogonally modeled via
        `ServerAction` and should not be seen in `CompScope`.

        Completion type based on initial and subsequent request fall into only two categories (so far)
        and do not need to be distinguished further on the server side:
        *   initial request: `CompType.PrefixShown` == `CompType.PrefixHidden` == `CompType.MenuCompletion`
        *   subsequent request: `CompType.SubsequentHelp`
        """
        if comp_type in [
            CompType.PrefixShown,
            CompType.PrefixHidden,
            CompType.MenuCompletion,
        ]:
            return CompScope.ScopeInitial

        if comp_type is CompType.SubsequentHelp:
            return CompScope.ScopeSubsequent

        return CompScope.ScopeUnknown
