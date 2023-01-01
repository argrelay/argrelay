from __future__ import annotations

from argrelay.data_schema.DataObjectSchema import object_data_
from argrelay.data_schema.FunctionObjectDataSchema import accept_object_classes_
from argrelay.data_schema.GenericInterpConfigSchema import function_query_, object_class_queries_
from argrelay.data_schema.ObjectClassQuerySchema import keys_to_types_list_, object_class_
from argrelay.interp_plugin.AbstractInterp import AbstractInterp
from argrelay.interp_plugin.ArgProcessor import ArgProcessor
from argrelay.meta_data.CompType import CompType
from argrelay.meta_data.ReservedObjectClass import ReservedObjectClass
from argrelay.meta_data.SpecialChar import SpecialChar
from argrelay.meta_data.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.runtime_context.InterpContext import InterpContext, assigned_types_to_values_

"""
This module auto-completes command line args when integrated with shell (Bash).

See use case: derived :class:`ServiceInterp`.
"""


class GenericInterp(AbstractInterp):
    all_processors: list[ArgProcessor]

    function_query: dict
    # List to preserve order:
    object_class_queries_list: list[dict]
    # Dict for quick lookup:
    object_class_queries_dict: dict[str, dict]

    # Object of `ReservedObjectClass.ClassFunction` from database which defines all other objects to be found:
    function_object_found: dict
    # When `function_object_found`, it is list of object classes function requires:
    accept_object_classes: list[str]
    # When `function_object_found`, it is an ipos into `accept_object_classes` to select `curr_object_class`:
    accept_object_class_ipos: int
    # It contains pending object to be found (including data from `function_object_found`):
    # TODO: Formalize this in schema - see also `InterpContext.assigned_types_to_values_per_object`:
    # *   `object_class_`
    # *   `object_data_`
    # *   `assigned_types_to_values_`
    # *   TODO: maybe also `keys_to_types` (the query)?
    curr_data_object: dict

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
        # TODO: provide dict in config directly, there is no usage of list variant (no ordering is defined by this list):
        self.object_class_queries_list = config_dict[object_class_queries_]
        self.object_class_queries_dict = {}
        for object_class_query in self.object_class_queries_list:
            self.object_class_queries_dict[object_class_query[object_class_]] = object_class_query

        # None until function object is found:
        self.function_object_found = None
        self.accept_object_classes = None
        self.accept_object_class_ipos = None

        self._init_next_object_to_find()
        self.curr_data_object[object_class_] = self.function_query[object_class_]

        # Init to find function class:
        self._set_object_class_query(self.function_query)

    def _set_object_class_query(self, object_class_query):
        self.curr_data_object[object_class_] = object_class_query[object_class_]
        self._set_curr_keys_to_type(object_class_query[keys_to_types_list_])

    def _set_curr_keys_to_type(self, keys_to_types_list):
        self.curr_keys_to_types_list = keys_to_types_list

        self.curr_keys_to_types_dict = self.list_to_dict(self.curr_keys_to_types_list)

        # generate reverse:
        self.curr_types_to_keys = {v: k for k, v in self.curr_keys_to_types_dict.items()}

        # instantiate processors:
        self.all_processors = []
        for curr_type in self.curr_types_to_keys.keys():
            self.all_processors.append(ArgProcessor(
                self.interp_ctx.static_data,
                self.curr_types_to_keys[curr_type],
                curr_type,
            ))

    @staticmethod
    def list_to_dict(dict_list: list[dict]) -> dict:
        """
        Convert list[dict] (with dict having single { key: value }) into dict of keys to values.
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
        self._assign_explicit_args()
        self._assign_implicit_args()

    def _assign_explicit_args(self) -> None:
        """
        Scans through `unconsumed_tokens` and tries to match its value against values of each type.
        """

        consumed_tokens = []
        for unconsumed_token_ipos in self.interp_ctx.unconsumed_tokens:
            other_token = self.interp_ctx.parsed_ctx.all_tokens[unconsumed_token_ipos]
            # see if token matches any type by value:
            for curr_processor in self.all_processors:
                if curr_processor.try_explicit_arg(self.interp_ctx, other_token):
                    consumed_tokens.append(unconsumed_token_ipos)

        # perform list modifications out of the prev loop:
        for consumed_token in consumed_tokens:
            self.interp_ctx.unconsumed_tokens.remove(consumed_token)
            self.interp_ctx.consumed_tokens.append(consumed_token)

    def _assign_implicit_args(self) -> None:
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

    def try_iterate(self) -> int:
        """
        Try to consume more args if possible.

        *   If function was found, start with its first required object class.
        *   If curr object class found, move to the next until all found.

        :returns:
            = 0: move to next interpreter: curr interpreter is fully satisfied from the args
            > 0: call again curr interpreter: still more things to find in the args
            < 0: stop: interpreter sees no point to continue main loop (`InterpContext.interpret_command`)
        """
        if not self.function_object_found:
            # Function is still not found - try to find now:
            query_res = self._query_objects({
                object_class_: ReservedObjectClass.ClassFunction.name,
            })
            # We want single function object found, not zero, not more than one:
            query_res_iter = iter(query_res)
            first_found = next(query_res_iter, None)
            eprint("first_found: ", first_found)
            if first_found is not None:
                next_found = next(query_res_iter, None)
                if next_found:
                    eprint("next_found: ", next_found)
                    # Too many - stop:
                    return -1
                else:
                    self.function_object_found = first_found
                    self._rotate_object_found(self.function_object_found)

                    # Init next objects to find:
                    self.accept_object_classes = (
                        self.function_object_found[object_data_][accept_object_classes_]
                    )
                    if not self.accept_object_classes:
                        # Function does not need any object:
                        return 0

                    self.accept_object_class_ipos = 0
                    self._set_object_class_query(
                        self.object_class_queries_dict[self.accept_object_classes[self.accept_object_class_ipos]]
                    )
                    # Need more args to consume (for objects to find):
                    return +1
            else:
                # No function = nothing to do:
                return -1
        else:
            query_res = self._query_objects({
                object_class_: self.curr_data_object[object_class_],
            })
            # We need single object:
            query_res_iter = iter(query_res)
            first_found = next(query_res_iter, None)
            data_object: dict = first_found
            eprint("first_found: ", first_found)
            if data_object is not None:
                next_found = next(query_res_iter, None)
                eprint("next_found: ", next_found)
                if next_found:
                    # Too many - stop:
                    return -1
                else:
                    self._rotate_object_found(data_object)
                    self.accept_object_class_ipos += 1
                    if self.accept_object_class_ipos < len(self.accept_object_classes):
                        # Move to the next object class to find:
                        self._set_object_class_query(self.accept_object_classes[self.accept_object_class_ipos])
                        return +1
                    else:
                        # Move to the next interp:
                        return 0
            else:
                # No object = stop:
                return -1

    def _init_next_object_to_find(self):
        self.interp_ctx.curr_assigned_types_to_values = {}
        self.curr_data_object = {
            assigned_types_to_values_: self.interp_ctx.curr_assigned_types_to_values
        }
        # Also, keep it in the list even if it is incomplete:
        self.interp_ctx.assigned_types_to_values_per_object.append(self.curr_data_object)

    def _rotate_object_found(self, object_data):
        # Finalize missing data field:
        self.curr_data_object[object_data_] = object_data
        self._init_next_object_to_find()

    def _query_objects(self, query_dict):
        for arg_type, arg_val in self.interp_ctx.curr_assigned_types_to_values.items():
            query_dict[arg_type] = arg_val.arg_value
        query_dict[object_class_] = ReservedObjectClass.ClassFunction.name
        query_res = self.interp_ctx.mongo_col.find(query_dict)
        return query_res

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
                name + SpecialChar.KeyValueDelimiter.value
                for name in self.curr_types_to_keys.keys() if not name.startswith('_')
            ]

        if self.interp_ctx.parsed_ctx.comp_type == CompType.SubsequentHelp:
            if self.interp_ctx.parsed_ctx.sel_token_l_part == "":
                return self.remaining_from_next_missing_types()
            else:
                return self.remaining_from_all_missing_types()

        if self.interp_ctx.parsed_ctx.sel_token_l_part == "":
            # assert t == CompType.PartialWord, "Is this partial word but selected token left part is empty?"
            if (
                self.interp_ctx.parsed_ctx.comp_type == CompType.PrefixHidden or
                self.interp_ctx.parsed_ctx.comp_type == CompType.PrefixShown or
                self.interp_ctx.parsed_ctx.comp_type == CompType.MenuCompletion
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
            return self.remaining_from_next_missing_types()

    def remaining_from_next_missing_types(self) -> list[str]:
        proposed_tokens: list[str] = []

        # Return filtered value set fom next missing arg:
        for arg_type in self.curr_types_to_keys.keys():
            if not proposed_tokens and arg_type not in self.interp_ctx.curr_assigned_types_to_values:
                proposed_tokens = [
                    x for x in self.interp_ctx.static_data.types_to_values[arg_type]
                    if x.startswith(self.interp_ctx.parsed_ctx.sel_token_l_part)
                ]

        return proposed_tokens

    def remaining_from_all_missing_types(self) -> list[str]:
        proposed_tokens: list[str] = []

        # Add entire value sets for missing args to proposed set:
        for arg_type in self.curr_types_to_keys.keys():
            if arg_type not in self.interp_ctx.curr_assigned_types_to_values:
                proposed_tokens += [
                    x for x in self.interp_ctx.static_data.types_to_values[arg_type]
                    if x.startswith(self.interp_ctx.parsed_ctx.sel_token_l_part)
                ]

        return proposed_tokens

    # noinspection PyMethodMayBeStatic
    def print_complete(self) -> None:
        eprint(TermColor.INFO.value)
        eprint(f"DONE", end = "")
        eprint(TermColor.RESET.value)
