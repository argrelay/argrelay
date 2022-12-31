from __future__ import annotations

from argrelay.interp_plugin.AbstractInterp import AbstractInterp
from argrelay.interp_plugin.ArgProcessor import ArgProcessor
from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.SpecialChar import SpecialChar
from argrelay.meta_data.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.runtime_context.CommandContext import CommandContext

"""
This module auto-completes command line args when integrated with shell (Bash).

See use case: derived :class:`ServiceInterp`.
"""


class GenericInterp(AbstractInterp):
    all_processors: list[ArgProcessor]
    keys_to_types: dict[str, str]

    def __init__(self, command_ctx: CommandContext, config_dict: dict, all_processors: list[ArgProcessor]):
        super().__init__(command_ctx, config_dict)
        self.command_ctx = command_ctx
        self.keys_to_types = config_dict["keys_to_types"]
        # reverse:
        self.types_to_keys = {v: k for k, v in self.keys_to_types.items()}

        self.all_processors = all_processors

    def consume_key_args(self) -> None:
        pass

    def consume_pos_args(self) -> None:
        self._assign_explicit_args()
        self._assign_implicit_args()

    def _assign_explicit_args(self) -> None:
        """
        TODO: Fix description:
        Scans through :property:`CompContext.other_tokens` and
        assigns args specified explicitly for each arg type.
        """

        consumed_tokens = []
        for unconsumed_token_ipos in self.command_ctx.unconsumed_tokens:
            other_token = self.command_ctx.parsed_ctx.all_tokens[unconsumed_token_ipos]
            for curr_processor in self.all_processors:
                if curr_processor.try_explicit_arg(self.command_ctx, other_token):
                    consumed_tokens.append(unconsumed_token_ipos)

        for consumed_token in consumed_tokens:
            self.command_ctx.unconsumed_tokens.remove(consumed_token)
            self.command_ctx.consumed_tokens.append(consumed_token)

    def _assign_implicit_args(self) -> None:
        """
        Invokes all :class:`ArgProcessor` and
        assigns args known implicitly for each arg type.
        """

        while True:
            any_assignment = False
            for curr_processor in self.all_processors:
                if curr_processor.try_implicit_arg(self.command_ctx):
                    any_assignment = True
            if not any_assignment:
                break

    def propose_arg_completion(self) -> None:
        self.command_ctx.comp_suggestions = self.propose_auto_comp_list()

    def propose_auto_comp_list(self) -> list[str]:

        # TODO: POC: Either remove it or implement properly: just testing named args:
        if (
            self.command_ctx.parsed_ctx.sel_token_l_part.endswith(":")
            or
            self.command_ctx.parsed_ctx.sel_token_r_part.startswith(":")
        ):
            return [
                name + SpecialChar.KeyValueDelimiter.value
                for name in self.types_to_keys.keys() if not name.startswith('_')
            ]

        if self.command_ctx.parsed_ctx.comp_type == CompType.SubsequentHelp:
            if self.command_ctx.parsed_ctx.sel_token_l_part == "":
                return self.remaining_from_next_missing_types()
            else:
                return self.remaining_from_all_missing_types()

        if self.command_ctx.parsed_ctx.sel_token_l_part == "":
            # assert t == CompType.PartialWord, "Is this partial word but selected token left part is empty?"
            if (
                self.command_ctx.parsed_ctx.comp_type == CompType.PrefixHidden or
                self.command_ctx.parsed_ctx.comp_type == CompType.PrefixShown or
                self.command_ctx.parsed_ctx.comp_type == CompType.MenuCompletion
            ):
                # Cannot complete => show first missing:
                # TODO: differentiate when have proposed and no proposed:
                first_missing_type = self.remaining_from_next_missing_types()
                if first_missing_type:
                    return first_missing_type
                else:
                    self.print_complete()
                    return []
        else:
            if self.command_ctx.parsed_ctx.comp_type == CompType.PrefixHidden:
                return self.remaining_from_next_missing_types()
            if self.command_ctx.parsed_ctx.comp_type == CompType.MenuCompletion:
                # Note that this space will be cached by shell and used without completion script invocation
                # until cycling through these options by repetitive menu completion is not over.
                # TODO: Test cycling through options limited by current prefix (versus cycling through every item at current arg space):
                return self.remaining_from_next_missing_types()
            if self.command_ctx.parsed_ctx.comp_type == CompType.PrefixShown:
                # Can complete => show matching:
                # TODO: We have an option here: filter `startswith` or `in`:
                #       But bash auto-completion with colors highlights according to `startswith` only:
                return self.remaining_from_next_missing_types()
            return self.remaining_from_next_missing_types()

    def remaining_from_next_missing_types(self) -> list[str]:
        proposed_tokens: list[str] = []

        # Return filtered value set fom next missing arg:
        for arg_type in self.types_to_keys.keys():
            if not proposed_tokens and arg_type not in self.command_ctx.assigned_types_to_values:
                proposed_tokens = [
                    x for x in self.command_ctx.static_data.types_to_values[arg_type]
                    if x.startswith(self.command_ctx.parsed_ctx.sel_token_l_part)
                ]

        return proposed_tokens

    def remaining_from_all_missing_types(self) -> list[str]:
        proposed_tokens: list[str] = []

        # Add entire value sets for missing args to proposed set:
        for arg_type in self.types_to_keys.keys():
            if arg_type not in self.command_ctx.assigned_types_to_values:
                proposed_tokens += [
                    x for x in self.command_ctx.static_data.types_to_values[arg_type]
                    if x.startswith(self.command_ctx.parsed_ctx.sel_token_l_part)
                ]

        return proposed_tokens

    # noinspection PyMethodMayBeStatic
    def print_complete(self) -> None:
        eprint(TermColor.INFO.value)
        eprint(f"DONE", end = "")
        eprint(TermColor.RESET.value)
