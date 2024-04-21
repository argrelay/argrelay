from __future__ import annotations

from typing import Union

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.CompScope import CompScope
from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.ReservedArgType import ReservedArgType
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.misc_helper_server import insert_unique_to_sorted_list
from argrelay.plugin_delegator.AbstractDelegator import AbstractDelegator
from argrelay.plugin_interp.AbstractInterp import AbstractInterp
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.InitControl import InitControl
from argrelay.runtime_context.InterpContext import (
    InterpContext,
    function_container_ipos_,
)
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import (
    delegator_plugin_instance_id_,
)
from argrelay.schema_config_interp.InitControlSchema import init_control_desc
from argrelay.schema_config_interp.SearchControlSchema import search_control_desc

func_search_control_ = "func_search_control"
"""
This field is automatically populated by `FuncTreeInterpFactory` inside `interp_tree_node_config_dict`.
"""

func_init_control_ = "func_init_control"
"""
This field is automatically populated by `FuncTreeInterpFactory` inside `interp_tree_node_config_dict`.
"""


class FuncTreeInterp(AbstractInterp):
    """
    Implements FS_26_43_73_72 func tree.

    Finds function `data_envelope` within func tree first,
    then uses its delegator (see `AbstractDelegator`) to find all args-related `data_envelope`-s.

    See FS_55_57_45_04 enum selector.
    """

    def __init__(
        self,
        interp_factory_id,
        interp_tree_node_config_dict: dict,
        interp_ctx: InterpContext,
        func_ids_to_func_rel_paths: dict[str, list[list[str]]],
        paths_to_jump: dict[tuple[str, ...], tuple[str, ...]],
    ):
        super().__init__(
            interp_factory_id,
            interp_tree_node_config_dict,
            interp_ctx,
        )
        self.paths_to_jump: dict[tuple[str, ...], tuple[str, ...]] = paths_to_jump

        # Allocate first container for function `data_envelope`:
        self.base_container_ipos += 1
        self.interp_ctx.envelope_containers.append(EnvelopeContainer(SearchControl()))

        self.select_next_container()
        self._apply_func_init_control()
        self._apply_func_search_control()

        self.func_ids_to_func_rel_paths: dict[str, list[list[str]]] = func_ids_to_func_rel_paths

    def _apply_func_init_control(self):
        self.interp_ctx.curr_container.assigned_types_to_values[
            ReservedArgType.EnvelopeClass.name
        ] = AssignedValue(
            ReservedEnvelopeClass.ClassFunction.name,
            ArgSource.InitValue,
        )
        func_init_control: InitControl = init_control_desc.dict_schema.load(
            self.interp_tree_node_config_dict[func_init_control_],
        )
        for prop_type, prop_value in func_init_control.init_types_to_values.items():
            self.interp_ctx.curr_container.assigned_types_to_values[prop_type] = AssignedValue(
                prop_value,
                ArgSource.InitValue,
            )
            if prop_type in self.interp_ctx.curr_container.remaining_types_to_values:
                del self.interp_ctx.curr_container.remaining_types_to_values[prop_type]

    def _apply_func_search_control(self):
        # Function `search_control` is populated based on
        # tree path (FS_01_89_09_24 interp tree + FS_26_43_73_72 func tree)
        # and plugin config (rather than data found in `data_envelope`):
        self.interp_ctx.curr_container.search_control = search_control_desc.dict_schema.load(
            self.interp_tree_node_config_dict[func_search_control_]
        )

    def consume_pos_args(self) -> bool:
        """
        Scans through `remaining_arg_buckets` and tries to match its value against values of each type.

        Implements:
        *   FS_76_29_13_28 arg consumption priorities.
        *   FS_44_36_84_88 consume args one by one:
            This func consumes all until the first remaining non-singled out arg.
        *   FS_97_64_39_94 `arg_bucket`-s: consumption is limited to single bucket per `envelope_container`.
        """

        consumed_token_ipos_list = []
        any_consumed = False
        # Related to FS_13_51_07_97 singled out implicit values:
        # We can keep consuming args (without creating FS_51_67_38_37 impossible arg combinations)
        # as long as they are singled out - we cannot consume two ambiguous args at once, but
        # we can consume as many singled out as possible (plus one ambiguous).
        # If arg is singled out but still matches remaining arg, it must be assigned as `ArgSource.ExplicitPosArg`
        # rather than be left remaining and (later) be assigned as `ArgSource.ImplicitValue`.
        consumed_ambiguous_value = False
        if self.interp_ctx.curr_container.used_arg_bucket is not None:
            # If `envelope_container` has one `used_arg_bucket`, loop through it only:
            any_consumed = self.consume_pos_args_from_arg_bucket(
                bucket_index = self.interp_ctx.curr_container.used_arg_bucket,
                bucket_list = self.interp_ctx.remaining_arg_buckets[self.interp_ctx.curr_container.used_arg_bucket],
                consumed_ambiguous_value = consumed_ambiguous_value,
                consumed_token_ipos_list = consumed_token_ipos_list,
            )
        else:
            # Otherwise, loop through all buckets until the single `used_arg_bucket` is chosen:
            for bucket_index, bucket_list in enumerate(self.interp_ctx.remaining_arg_buckets):
                any_consumed = self.consume_pos_args_from_arg_bucket(
                    bucket_index = bucket_index,
                    bucket_list = bucket_list,
                    consumed_ambiguous_value = consumed_ambiguous_value,
                    consumed_token_ipos_list = consumed_token_ipos_list,
                )
                if any_consumed:
                    # Consume from single `arg_bucket` only:
                    break

        # perform list modifications out of the prev loop:
        for consumed_token_ipos in consumed_token_ipos_list:
            bucket_index = self.interp_ctx.token_ipos_to_arg_bucket_map[consumed_token_ipos]
            self.interp_ctx.remaining_arg_buckets[bucket_index].remove(consumed_token_ipos)

        return any_consumed

    def consume_pos_args_from_arg_bucket(
        self,
        bucket_index,
        bucket_list,
        consumed_ambiguous_value,
        consumed_token_ipos_list,
    ) -> bool:
        any_consumed = False
        for remaining_token_ipos in bucket_list:

            remaining_token = self.interp_ctx.parsed_ctx.all_tokens[remaining_token_ipos]

            # TODO: FS_76_29_13_28 Why not define the order based on FS_31_70_49_15 `search_control`
            #       (instead of whatever internal order `remaining_types_to_values` has)?
            #       It could already be the case that `remaining_types_to_values` are ordered as `search_control`.
            #       Why not make it explicit?

            # See if token matches any type by value:
            for arg_type, arg_values in self.interp_ctx.curr_container.remaining_types_to_values.items():
                if remaining_token in arg_values:
                    if (
                        len(arg_values) == 1
                        or
                        not consumed_ambiguous_value
                    ):
                        self.interp_ctx.curr_container.assigned_types_to_values[arg_type] = AssignedValue(
                            remaining_token,
                            ArgSource.ExplicitPosArg,
                        )
                        self.interp_ctx.curr_container.used_arg_bucket = bucket_index
                        if len(arg_values) > 1:
                            # This was not singled out arg:
                            # allow only one ambiguous consumption to avoid FS_51_67_38_37 impossible arg combinations.
                            consumed_ambiguous_value = True
                        any_consumed = True
                        consumed_token_ipos_list.append(remaining_token_ipos)

                        self.interp_ctx.consumed_arg_buckets[bucket_index].append(remaining_token_ipos)

                        # TD_76_09_29_31: overlapped
                        # Assign matching remaining arg value to the first type it matches (only once):
                        del self.interp_ctx.curr_container.remaining_types_to_values[arg_type]
                        break
        return any_consumed

    def try_iterate(self) -> InterpStep:
        """
        Try to consume more args if possible.

        *   If function was found, start with search for its first envelope class.
        *   If curr envelope class is found, move to the next (until all are found).

        :returns:
        *   `InterpStep.NextInterp`: move to next interpreter: curr interpreter is fully satisfied from the args
        *   `InterpStep.NextEnvelope`: call again curr interpreter: still more things to find in the args
        *   `InterpStep.StopAll`: interpreter sees no point to continue the loop (`InterpContext.interpret_command`)
        """

        # We want single `data_envelope` to be found, not zero, not more than one:
        if self.interp_ctx.curr_container.found_count > 1:
            # Too many `data_envelope`-s - stop:
            return InterpStep.StopAll
        elif self.interp_ctx.curr_container.found_count == 1:

            if self.interp_ctx.curr_container_ipos == self.base_container_ipos:
                # This is a function envelope:
                search_control_list: list[SearchControl] = self.get_search_control_list()
                # Create `EnvelopeContainer`-s for every `data_envelope` to find:
                self.interp_ctx.alloc_searchable_containers(search_control_list)

            if self.interp_ctx.is_last_container():
                # Function does not need any envelopes:
                return InterpStep.NextInterp
            else:
                self.select_next_container()
                self.delegate_init_control()
                # Need more args to consume for the next envelope to find:
                return InterpStep.NextEnvelope

        else:
            # No `data_envelope` = nothing to do:
            return InterpStep.StopAll

    def get_search_control_list(self) -> list[SearchControl]:
        delegator_plugin = self.get_func_delegator()

        search_control_list: list[SearchControl] = delegator_plugin.run_search_control(
            self.get_found_func_data_envelope()
        )
        return search_control_list

    def delegate_init_control(self):
        delegator_plugin = self.get_func_delegator()
        delegator_plugin.run_init_control(
            self.interp_ctx.envelope_containers,
            self.interp_ctx.curr_container_ipos,
        )

    def has_fill_control(
        self,
    ) -> bool:
        return True

    def delegate_fill_control(
        self,
    ) -> bool:
        delegator_plugin = self.get_func_delegator()
        if delegator_plugin:
            return delegator_plugin.run_fill_control(
                self.interp_ctx,
            )
        else:
            return False

    def get_found_func_data_envelope(self) -> Union[dict, None]:
        func_envelope = self.interp_ctx.envelope_containers[(
            self.base_container_ipos + function_container_ipos_
        )]
        if func_envelope.found_count == 1:
            return func_envelope.data_envelopes[0]
        return None

    def get_func_delegator(self):
        func_data_envelope = self.get_found_func_data_envelope()
        if func_data_envelope:
            delegator_plugin_instance_id = func_data_envelope[instance_data_][delegator_plugin_instance_id_]
            delegator_plugin: AbstractDelegator = self.interp_ctx.action_delegators[delegator_plugin_instance_id]
            return delegator_plugin
        else:
            # func envelope hasn't been found yet:
            return None

    def select_next_container(self):
        self.interp_ctx.curr_container_ipos += 1
        self.interp_ctx.curr_container = self.interp_ctx.envelope_containers[
            self.interp_ctx.curr_container_ipos
        ]

    def next_interp(self) -> "AbstractInterp":
        delegator_plugin = self.get_func_delegator()
        interp_factory_id = delegator_plugin.run_interp_control(self)
        if interp_factory_id:
            self.select_next_interp_tree_abs_path()
            return self.interp_ctx.create_next_interp(interp_factory_id)
        else:
            return None

    def select_next_interp_tree_abs_path(self):
        if self.interp_ctx.interp_tree_abs_path in self.paths_to_jump:
            # FS_91_88_07_23 jump tree: replace current `interp_tree_abs_path` with another one based on config:
            self.interp_ctx.interp_tree_abs_path = self.paths_to_jump[self.interp_ctx.interp_tree_abs_path]

    def propose_arg_completion(self) -> None:
        for comp_value in self.propose_auto_comp_list():
            insert_unique_to_sorted_list(self.interp_ctx.comp_suggestions, comp_value)

    def propose_auto_comp_list(self) -> list[str]:

        # TODO: FS_20_88_05_60: POC: Either remove it or implement properly: just testing named args:
        if (
            self.interp_ctx.parsed_ctx.tan_token_l_part.endswith(":")
            or
            self.interp_ctx.parsed_ctx.tan_token_r_part.startswith(":")
        ):
            return [
                type_name + SpecialChar.KeyValueDelimiter.value
                for type_name in self.interp_ctx.curr_container.search_control.types_to_keys_dict
                if not type_name.startswith("_")
            ]

        # TODO: FS_23_62_89_43: the logic for both if-s (`if-A` and `if-B`) is identical at the moment - what do we want to improve?

        # TODO: FS_23_62_89_43: if-A:
        if self.interp_ctx.parsed_ctx.comp_scope is CompScope.ScopeInitial:
            if self.interp_ctx.parsed_ctx.tan_token_l_part == "":
                return self.remaining_from_next_missing_type()
            else:
                return self.remaining_from_next_missing_type()

        # TODO: FS_23_62_89_43: if-B:
        if self.interp_ctx.parsed_ctx.comp_scope is CompScope.ScopeSubsequent:
            if self.interp_ctx.parsed_ctx.tan_token_l_part == "":
                return self.remaining_from_next_missing_type()
            else:
                # TODO: FS_20_88_05_60: Suggest keys (:) of missing types instead - it is `ScopeSubsequent`, user insist and wants something else:
                return self.remaining_from_next_missing_type()

        return []

    def remaining_from_next_missing_type(self) -> list[str]:
        """
        Clarifications:
        *   remaining = because values for the given type are reduced based on narrowed down `data_envelope` set
        *   missing = because this arg type is not specified yet
        *   next = because arg types are tired in specific order
        """
        proposed_values: list[str] = []

        # Return filtered value set from the next missing arg:
        for arg_type in self.interp_ctx.curr_container.search_control.types_to_keys_dict:
            if (
                # TODO: only one condition should be enough: arg_type is either in one or in another, not in both:
                arg_type not in self.interp_ctx.curr_container.assigned_types_to_values
                and
                arg_type in self.interp_ctx.curr_container.remaining_types_to_values
            ):
                proposed_values = [
                    # FS_71_87_33_52: `help_hint`:
                    self.interp_ctx.help_hint_cache.get_value_with_help_hint(arg_type, x)
                    for x in self.interp_ctx.curr_container.remaining_types_to_values[arg_type]
                    if (
                        # NOTE: This checks for `str` meaning primitive (scalar, not `list` or `dict`),
                        #       but this also filters out `int` or others.
                        #       Primitive types should be converted to `str` when loaded.
                        #       See `ConfigOnlyLoader.convert_envelope_fields_to_string` for example.
                        isinstance(x, str)
                        and
                        # FS_32_05_46_00: using `startswith`:
                        # FS_23_62_89_43: filter using L part of tangent token:
                        x.startswith(self.interp_ctx.parsed_ctx.tan_token_l_part)
                        # TODO: FS_06_99_43_60: Support list[str] - what if one type can have list of values (and we need to match any as in OR)?
                    )
                ]
                if proposed_values:
                    # Collect only until the first proposed value set from missing args:
                    break

        return proposed_values
