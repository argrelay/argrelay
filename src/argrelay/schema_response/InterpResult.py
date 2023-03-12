from __future__ import annotations

from dataclasses import dataclass

from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer


# TODO: Combine InterpResult and InvocationInput - only one need to exits
@dataclass
class InterpResult:
    """
    See :class:`InterpResultSchema`
    """

    all_tokens: list[str]
    """
    Copy from `ParsedContext.all_tokens` - command line args.
    """

    consumed_tokens: list[int]
    """
    Copy from `InterpContext.consumed_tokens` -
    indexes into `all_tokens` pointing to tokens consumed during interpretation.
    """

    envelope_containers: list[EnvelopeContainer]

    def describe_data(self):
        eprint()

        for i in range(len(self.all_tokens)):
            if i in self.consumed_tokens:
                eprint(f"{TermColor.BRIGHT_BLUE.value}{self.all_tokens[i]}{TermColor.RESET.value}", end = " ")
            else:
                eprint(f"{TermColor.DARK_MAGENTA.value}{self.all_tokens[i]}{TermColor.RESET.value}", end = " ")

        EnvelopeContainer.describe_data(self.envelope_containers)
