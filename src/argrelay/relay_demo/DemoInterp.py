from __future__ import annotations

from argrelay.plugin_interp.FuncArgsInterp import FuncArgsInterp

"""
`DemoInterp` is a configured use case of :class:`FuncArgsInterp` for auto-completion of service attributes.

The command line tokens are translated to typed args.
A user keeps adding the typed arg values until all requited types unambiguously specify what to do:
    `[some_command] rw upstream goto amer`
The order is (usually) not important.

If there is an ambiguity, auto-completion suggests possible options -
in this case, the missing option is `CodeMaturity` ("prod", "qa", "dev", ...):
    `[some_command] rw upstream goto amer prod`

Each arg value belongs to its own type (see :class:`ServiceArgType`), for example:
*   "rw": `AccessType`
*   "upstream": `FlowStage`
*   "goto": `ActionType`
*   "amer": `GeoRegion`
*   "prod": `CodeMaturity`
These types are:
*   discrete (limited set of values) and
*   non-orthogonal (possible values of one type may affect/depend on already given values for another type).

TODO: fix description (below): not just value, first by its key, then by its item position (ipos), then by its value.
The arg type is determined by its value.
If value sets from different arg types overlap, the order of the args becomes important,
but it does not have to be remembered because auto-completion suggest them according to that order.
"""


class DemoInterp(FuncArgsInterp):
    pass
