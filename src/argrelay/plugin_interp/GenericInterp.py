from __future__ import annotations

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.plugin_interp.ArgProcessor import ArgProcessor
from argrelay.runtime_context.InterpContext import (
    InterpContext,
    assigned_types_to_values_,
    remaining_types_to_values_,
    is_found_,
)
from argrelay.runtime_data.ArgValue import ArgValue
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_, context_control_
from argrelay.schema_config_interp.EnvelopeClassQuerySchema import keys_to_types_list_, envelope_class_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    envelope_class_queries_,
)
from argrelay.schema_config_interp.GenericInterpConfigSchema import function_query_

"""
This module auto-completes command line args when integrated with shell (Bash).

See use case: derived :class:`DemoInterp`.
"""


# TODO: Rename from `GenericInterp` to something like `FuncArgsInterp`.
class GenericInterp(AbstractInterp):
    all_processors: list[ArgProcessor]

    function_query: dict

    # Envelope of `ReservedEnvelopeClass.ClassFunction` from database which defines all other envelopes to be found:
    function_envelope: dict
    # When `function_envelope` found, it is an ordered list of specs how to query other `data_envelope`:
    envelope_class_queries: list[dict]
    # When `function_envelope` found, it is an ipos into `envelope_class_queries` to select curr `envelope_class_query`:
    envelope_class_queries_ipos: int

    # It contains pending envelopes to be found (including data from `function_envelope`):
    # TODO: Formalize this in schema - see also `InterpContext.assigned_types_to_values_per_envelope`:
    # *   `envelope_class_`
    # *   `envelope_payload_`
    # *   `assigned_types_to_values_`
    # *   `remaining_types_to_values_`
    # *   TODO: maybe also `keys_to_types` (the query)?
    # It is the last among `InterpContext.assigned_types_to_values_per_envelope`.
    curr_data_envelope: dict

    # Envelopes found in the last query:
    res_count: int
    # First object found in the last query
    first_found: dict

    # Direct list to preserve order:
    curr_keys_to_types_list: list[dict[str, str]]
    # Direct dict for quick lookup:
    curr_keys_to_types_dict: dict[str, str]
    # Reverse lookup:
    curr_types_to_keys: dict[str, str]

    def __init__(self, interp_ctx: InterpContext, config_dict: dict):
        super().__init__(interp_ctx, config_dict)
        self.interp_ctx = interp_ctx

        self.function_query = config_dict[function_query_]

        # TODO: unify `function_envelope` and `curr_data_envelope` - there should not many special treatment/logic for `function_envelope` as it is found just like any other envelope
        # None until function envelope is found:
        self.function_envelope = None
        self.envelope_class_queries = None
        # TODO: Ugly because search of `function_envelope` and `curr_data_envelope`: -2 as we are moving to -1 in `_init_next_envelope_to_find` which corresponds to `function_envelope`.
        self.envelope_class_queries_ipos = -2

        self._init_next_envelope_to_find()

        # Init to find function class:
        self._set_envelope_class_query_and_query(self.function_query)

    def _set_envelope_class_query_and_query(self, envelope_class_query):
        self.curr_data_envelope[envelope_class_] = envelope_class_query[envelope_class_]
        self._set_curr_keys_to_type(envelope_class_query[keys_to_types_list_])
        self.query_envelopes()

    def _set_curr_keys_to_type(self, keys_to_types_list):
        self.curr_data_envelope[keys_to_types_list_] = keys_to_types_list
        self.curr_keys_to_types_list = keys_to_types_list

        self.curr_keys_to_types_dict = self.convert_list_of_ordered_singular_dicts_to_unordered_dict(self.curr_keys_to_types_list)

        # generate reverse:
        self.curr_types_to_keys = {v: k for k, v in self.curr_keys_to_types_dict.items()}

        # init remaining:
        for arg_type in self.curr_types_to_keys.keys():
            self.interp_ctx.curr_remaining_types_to_values[arg_type] = []

        # TODO: Do we even need `ArgProcessor`-s if they all do the same thing, always (at the moment)?
        # instantiate processors:
        self.all_processors = []
        for curr_type in self.curr_types_to_keys.keys():
            self.all_processors.append(ArgProcessor(
                self.interp_ctx.static_data,
                self.curr_types_to_keys[curr_type],
                curr_type,
            ))

    @staticmethod
    def convert_list_of_ordered_singular_dicts_to_unordered_dict(dict_list: list[dict]) -> dict:
        """
        Convert ordered list[dict] (with dict having single { key: value }) into unordered dict { keys: values }.
        """
        converted_dict = {}
        for key_to_value_dict in dict_list:
            curr_key = next(iter(key_to_value_dict))
            curr_value = key_to_value_dict[curr_key]
            converted_dict[curr_key] = curr_value

        return converted_dict

    def consume_key_args(self) -> None:
        pass

    def consume_pos_args(self) -> None:
        self._assign_explicit_pos_args()
        self._assign_implicit_pos_args()

    def _assign_explicit_pos_args(self) -> None:
        """
        Scans through `unconsumed_tokens` and tries to match its value against values of each type.
        """

        consumed_token_ipos_list = []
        for unconsumed_token_ipos in self.interp_ctx.unconsumed_tokens:
            unconsumed_token = self.interp_ctx.parsed_ctx.all_tokens[unconsumed_token_ipos]
            # see if token matches any type by value:
            for curr_processor in self.all_processors:
                if curr_processor.try_explicit_arg(self.interp_ctx, unconsumed_token):
                    consumed_token_ipos_list.append(unconsumed_token_ipos)
                    self.interp_ctx.consumed_tokens.append(unconsumed_token_ipos)
                    self.query_envelopes()
                    # TD-2023-01-07--1:
                    # Assign current ArgVal by the first ArgProcessor only:
                    break

        # perform list modifications out of the prev loop:
        for consumed_token_ipos in consumed_token_ipos_list:
            self.interp_ctx.unconsumed_tokens.remove(consumed_token_ipos)

    def _assign_implicit_pos_args(self) -> None:
        """
        Invokes all :class:`ArgProcessor` and
        assigns args known implicitly for each arg type.
        """

        while True:
            any_assignment = False
            for curr_processor in self.all_processors:
                # TODO: at the moment, there is no implementation used which implicitly assigns something (one was CodeMaturityProcessor)
                if curr_processor.try_implicit_arg(self.interp_ctx):
                    any_assignment = True
            if not any_assignment:
                break

    def try_iterate(self) -> InterpStep:
        """
        Try to consume more args if possible.

        *   If function was found, start with its first required envelope class.
        *   If curr envelope class is found, move to the next until all are found.

        :returns:
        *   `InterpStep.NextInterp`: move to next interpreter: curr interpreter is fully satisfied from the args
        *   `InterpStep.NextEnvelope`: call again curr interpreter: still more things to find in the args
        *   `InterpStep.StopAll`: interpreter sees no point to continue the loop (`InterpContext.interpret_command`)
        """
        if not self.function_envelope:
            # We want single function envelope to be found, not zero, not more than one:
            eprint("first_found: ", self.first_found)
            if self.first_found is not None:
                if self.res_count > 1:
                    # Too many `data_envelope`-s - stop:
                    return InterpStep.StopAll
                else:
                    self.function_envelope = self.first_found
                    self._register_found_envelope(self.function_envelope)

                    # Init next objects to find:
                    self.envelope_class_queries = self.function_envelope[instance_data_][envelope_class_queries_]
                    if not self.envelope_class_queries:
                        # Function does not need any envelopes:
                        return InterpStep.NextInterp
                    else:
                        self._set_envelope_class_query_and_query(
                            self.envelope_class_queries[self.envelope_class_queries_ipos]
                        )
                        # Need more args to consume for the next envelope to find:
                        return InterpStep.NextEnvelope
            else:
                # No `data_envelope` = nothing to do:
                return InterpStep.StopAll
        else:
            # We need single envelope:
            eprint("first_found: ", self.first_found)
            if self.first_found is not None:
                if self.res_count > 1:
                    # Too many `data_envelope`-s - stop:
                    return InterpStep.StopAll
                else:
                    if self.envelope_class_queries_ipos + 1 == len(self.envelope_class_queries):
                        # TODO: We are finalizing but not rotating to the next one.
                        #       What if next interp start to write into this envelope again?
                        self._finalize_curr_envelope(self.first_found)
                        return InterpStep.NextInterp
                    else:
                        self._register_found_envelope(self.first_found)
                        # Move to the next object class to find:
                        self._set_envelope_class_query_and_query(
                            self.envelope_class_queries[self.envelope_class_queries_ipos]
                        )
                        return InterpStep.NextEnvelope

            else:
                # No `data_envelope` = nothing to do:
                return InterpStep.StopAll

    def _init_next_envelope_to_find(self):
        self.envelope_class_queries_ipos += 1
        self.interp_ctx.curr_assigned_types_to_values = {}
        self.interp_ctx.curr_remaining_types_to_values = {}

        self.curr_data_envelope = {
            is_found_: False,
            assigned_types_to_values_: self.interp_ctx.curr_assigned_types_to_values,
            remaining_types_to_values_: self.interp_ctx.curr_remaining_types_to_values,
        }
        # Also, keep the envelope in the list right away (even if it may not be found):
        self.interp_ctx.assigned_types_to_values_per_envelope.append(self.curr_data_envelope)

        self._propagate_context()

    def _propagate_context(self):
        """
        FD-2023-01-17--1:
        Copy arg value from prev `data_envelope` for arg types specified in `context_control` into next `arg_context`.
        """
        if self.interp_ctx.last_found_envelope_ipos >= 0:
            prev_envelope = self.interp_ctx.assigned_types_to_values_per_envelope[
                self.interp_ctx.last_found_envelope_ipos
            ]
            if context_control_ in prev_envelope:
                arg_type_list_to_push = prev_envelope[context_control_]
                for arg_type_to_push in arg_type_list_to_push:
                    if arg_type_to_push in prev_envelope:
                        if arg_type_to_push in self.interp_ctx.curr_assigned_types_to_values:
                            arg_value = self.interp_ctx.curr_assigned_types_to_values[arg_type_to_push]
                            if arg_value.arg_source.value <= ArgSource.ImplicitValue.value:
                                # Override value with source of higher priority:
                                arg_value.arg_source = ArgSource.ImplicitValue
                                arg_value.arg_value = prev_envelope[arg_type_to_push]
                        else:
                            self.interp_ctx.curr_assigned_types_to_values[arg_type_to_push] = ArgValue(
                                prev_envelope[arg_type_to_push],
                                ArgSource.ImplicitValue,
                            )

    def _register_found_envelope(self, envelope_found):
        self._finalize_curr_envelope(envelope_found)
        self._populate_implicit_arg_values()
        self._init_next_envelope_to_find()

    def _finalize_curr_envelope(self, envelope_found):
        self.interp_ctx.last_found_envelope_ipos += 1
        self.curr_data_envelope[is_found_] = True
        # Finalize missing data field:
        self.curr_data_envelope.update(envelope_found)

    # See: FD-2023-01-17--3:
    def _populate_implicit_arg_values(self):
        """
        When `data_envelope` is singled out, all remaining `arg_type`-s become `ArgSource.ImplicitValue`.
        """
        # TODO: This will not populate `ArgSource.ImplicitValue`-s in cases when a function is found.
        if self.envelope_class_queries:
            curr_envelope_class_query = self.envelope_class_queries[self.envelope_class_queries_ipos]
            keys_to_types_dict = self.convert_list_of_ordered_singular_dicts_to_unordered_dict(
                curr_envelope_class_query[keys_to_types_list_]
            )
            for arg_type in keys_to_types_dict.values():
                if arg_type in self.curr_data_envelope:
                    if arg_type not in self.interp_ctx.curr_assigned_types_to_values:
                        assert arg_type in self.interp_ctx.curr_remaining_types_to_values
                        # Update only `curr_assigned_types_to_values`,
                        # because `curr_remaining_types_to_values` will be updated automatically.
                        self.interp_ctx.curr_assigned_types_to_values[arg_type] = ArgValue(
                            self.curr_data_envelope[arg_type],
                            ArgSource.ImplicitValue,
                        )

    def query_envelopes(self):
        query_dict = {
            envelope_class_: self.curr_data_envelope[envelope_class_],
        }
        for arg_type, arg_val in self.interp_ctx.curr_assigned_types_to_values.items():
            query_dict[arg_type] = arg_val.arg_value
        # TODO: How to query values contained in arrays? For example, `GitRepoRelPath` is array. How to query envelopes which contain given value in elements of the array?
        query_res = self.interp_ctx.mongo_col.find(query_dict)
        self._update_curr_remaining_types_to_values(query_res)

    def _update_curr_remaining_types_to_values(self, query_res):
        # reset:
        self.interp_ctx.curr_remaining_types_to_values.clear()

        self.res_count: int = 0
        self.first_found = None
        # find all remaining arg vals per arg type:
        for envelope_found in iter(query_res):
            self.res_count += 1
            if not self.first_found:
                self.first_found = envelope_found
            # `arg_type` must be known:
            for arg_type in self.curr_types_to_keys.keys():
                # `arg_type` must be in one of the `data_envelope`-s found:
                if arg_type in envelope_found:
                    # `arg_type` must not be assigned/consumed:
                    if arg_type not in self.interp_ctx.curr_assigned_types_to_values.keys():
                        arg_val = envelope_found[arg_type]
                        if arg_type not in self.interp_ctx.curr_remaining_types_to_values:
                            val_list = []
                            self.interp_ctx.curr_remaining_types_to_values[arg_type] = val_list
                        else:
                            val_list = self.interp_ctx.curr_remaining_types_to_values[arg_type]
                        # ensure unique `arg_value`-s:
                        if arg_val not in val_list:
                            val_list.append(arg_val)

    def propose_arg_completion(self) -> None:
        self.interp_ctx.comp_suggestions = self.propose_auto_comp_list()

    def propose_auto_comp_list(self) -> list[str]:

        # TODO: POC: Either remove it or implement properly: just testing named args:
        if (
            self.interp_ctx.parsed_ctx.sel_token_l_part.endswith(":")
            or
            self.interp_ctx.parsed_ctx.sel_token_r_part.startswith(":")
        ):
            return [
                type_name + SpecialChar.KeyValueDelimiter.value
                for type_name in self.curr_types_to_keys.keys() if not type_name.startswith("_")
            ]

        if self.interp_ctx.parsed_ctx.comp_type == CompType.SubsequentHelp:
            if self.interp_ctx.parsed_ctx.sel_token_l_part == "":
                return self.remaining_from_next_missing_types()
            else:
                # TODO: Suggest keys (:) of missing types instead - it is `SubsequentHelp`, user insist and wants something else:
                return self.remaining_from_next_missing_types()

        if self.interp_ctx.parsed_ctx.sel_token_l_part == "":
            # assert t == CompType.PartialWord, "Is this partial word but selected token left part is empty?"
            if (
                self.interp_ctx.parsed_ctx.comp_type == CompType.PrefixHidden or
                self.interp_ctx.parsed_ctx.comp_type == CompType.PrefixShown or
                self.interp_ctx.parsed_ctx.comp_type == CompType.MenuCompletion
            ):
                # Cannot complete => show first missing:
                # TODO: differentiate when have proposed and no proposed:
                first_missing_type_values = self.remaining_from_next_missing_types()
                if first_missing_type_values:
                    return first_missing_type_values
                else:
                    self.print_complete()
                    return []
        else:
            if self.interp_ctx.parsed_ctx.comp_type == CompType.PrefixHidden:
                return self.remaining_from_next_missing_types()
            if self.interp_ctx.parsed_ctx.comp_type == CompType.MenuCompletion:
                # Note that this space will be cached by shell and used without completion script invocation
                # until cycling through these options by repetitive menu completion is not over.
                # TODO: Test cycling through options limited by current prefix (versus cycling through every item at current arg space):
                return self.remaining_from_next_missing_types()
            if self.interp_ctx.parsed_ctx.comp_type == CompType.PrefixShown:
                # Can complete => show matching:
                # TODO: We have an option here: filter `startswith` or `in`:
                #       But bash auto-completion with colors highlights according to `startswith` only:
                return self.remaining_from_next_missing_types()
            else:
                return self.remaining_from_next_missing_types()

    def remaining_from_next_missing_types(self) -> list[str]:
        proposed_tokens: list[str] = []

        # Return filtered value set fom next missing arg:
        for arg_type in self.curr_types_to_keys.keys():
            if (
                not proposed_tokens
                and
                # TODO: I think only one condition is enough: arg_type is either in one or in another, not in both:
                arg_type not in self.interp_ctx.curr_assigned_types_to_values
                and
                arg_type in self.interp_ctx.curr_remaining_types_to_values
            ):
                proposed_tokens = [
                    x for x in self.interp_ctx.curr_remaining_types_to_values[arg_type]
                    if (
                        isinstance(x, str)
                        and
                        x.startswith(self.interp_ctx.parsed_ctx.sel_token_l_part)
                        # TODO: Support list[str] - what if one type can have list of values (and we need to match any as in OR)?
                    )
                ]

        return proposed_tokens

    # noinspection PyMethodMayBeStatic
    def print_complete(self) -> None:
        eprint(TermColor.INFO.value)
        eprint(f"DONE", end = "")
        eprint(TermColor.RESET.value)
