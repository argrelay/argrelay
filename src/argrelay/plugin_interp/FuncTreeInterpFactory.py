from __future__ import annotations

from copy import deepcopy
from typing import Union

from argrelay.composite_forest.CompositeForestExtractor import extract_jump_tree, extract_func_tree
from argrelay.composite_forest.CompositeInfoType import CompositeInfoType
from argrelay.composite_forest.DictTreeWalker import DictTreeWalker, normalize_tree, sequence_starts_with
from argrelay.enum_desc.CompScope import CompScope
from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.ReservedEnvelopeClass import ReservedEnvelopeClass
from argrelay.enum_desc.ReservedPropName import ReservedPropName
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.misc_helper_server import insert_unique_to_sorted_list
from argrelay.plugin_delegator.DelegatorAbstract import DelegatorAbstract
from argrelay.plugin_interp.AbstractInterpFactory import AbstractInterpFactory, AbstractInterp
from argrelay.plugin_interp.FuncTreeInterpFactoryConfigSchema import (
    func_tree_interp_config_desc,
)
from argrelay.runtime_context.AbstractArg import ArgCommandValueOffered, ArgCommandValueDictated, ArgCommandIncomplete
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.InitControl import InitControl
from argrelay.runtime_context.InterpContext import InterpContext, function_container_ipos_
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_data.AssignedValue import AssignedValue
from argrelay.runtime_data.EnvelopeCollection import EnvelopeCollection
from argrelay.runtime_data.ServerConfig import ServerConfig
from argrelay.schema_config_interp.DataEnvelopeSchema import instance_data_
from argrelay.schema_config_interp.FunctionEnvelopeInstanceDataSchema import delegator_plugin_instance_id_
from argrelay.schema_config_interp.InitControlSchema import init_types_to_values_, init_control_desc
from argrelay.schema_config_interp.SearchControlSchema import (
    arg_name_to_prop_name_map_,
    populate_search_control,
    search_control_desc,
)

func_search_control_ = "func_search_control"
"""
This field is automatically populated by `FuncTreeInterpFactory` inside `interp_tree_node_config_dict`.
"""

func_init_control_ = "func_init_control"
"""
This field is automatically populated by `FuncTreeInterpFactory` inside `interp_tree_node_config_dict`.
"""

tree_step_prop_name_prefix_ = "tree_step_"
tree_step_arg_name_prefix_ = "step_"


class FuncTreeInterpFactory(AbstractInterpFactory):
    """
    Implements FS_26_43_73_72 func tree.
    Implements FS_91_88_07_23 jump tree.
    """

    def __init__(
        self,
        server_config: ServerConfig,
        plugin_instance_id: str,
        plugin_config_dict: dict,
    ):
        super().__init__(
            server_config,
            plugin_instance_id,
            plugin_config_dict,
        )

        # FS_26_43_73_72 func tree: func id to list of its absolute paths populated by `load_func_envelopes`.
        # These func tree paths are absolute within FS_33_76_82_84 composite forest.
        # Each func id can be attached to more than one leaf (hence, there is a list of paths to that func id).
        self.func_ids_to_func_abs_paths: dict[str, list[list[str]]] = {}

        # FS_91_88_07_23 jump tree
        dict_tree_walker: DictTreeWalker = DictTreeWalker(
            CompositeInfoType.jump_tree,
            extract_jump_tree(
                self.server_config.server_plugin_control.composite_forest,
            ),
        )
        self.paths_to_jump: dict[tuple[str, ...], tuple[str, ...]] = dict_tree_walker.build_paths_to_paths()
        """
        Implements FS_91_88_07_23 jump tree:
        for given `interp_tree_abs_path` (FS_01_89_09_24) selects next `interp_tree_abs_path`.
        """

        self.plugin_search_control: Union[SearchControl, None] = None

    def load_config(
        self,
        plugin_config_dict,
    ) -> dict:
        return func_tree_interp_config_desc.dict_from_input_dict(plugin_config_dict)

    def provide_plugin_search_control(
        self,
    ) -> list[SearchControl]:
        if self.plugin_search_control:
            return [self.plugin_search_control]
        else:
            return []

    def load_interp_tree_abs_paths(
        self,
        this_plugin_instance_interp_tree_abs_paths: list[tuple[str, ...]],
    ):
        self.interp_tree_abs_paths.extend(
            this_plugin_instance_interp_tree_abs_paths,
        )

    def load_func_envelopes(
        self,
        interp_tree_abs_path: tuple[str, ...],
        func_ids_to_func_envelopes: dict[str, dict],
    ) -> tuple[
        # mapped_func_ids:
        list[str],
        # index_props:
        list[str],
        # func_data_envelopes:
        list[dict],
    ]:
        """
        To implement FS_26_43_73_72 func tree, this plugin loads func `data_envelope`-s automatically.

        It loops through func `data_envelope`-s and populates their tree path search props
        according to extracted `func_tree` where each function is plugged into.
        """

        (
            mapped_func_ids,
            index_props,
            func_data_envelopes,
        ) = super().load_func_envelopes(
            interp_tree_abs_path,
            func_ids_to_func_envelopes,
        )
        interp_tree_node_config_dict = self.interp_tree_abs_paths_to_node_configs[interp_tree_abs_path]

        func_selector_tree = normalize_tree(extract_func_tree(
            self.server_config.server_plugin_control.composite_forest,
            self.plugin_instance_id,
        ))

        dict_tree_walker = DictTreeWalker(
            CompositeInfoType.func_tree,
            func_selector_tree,
        )
        self.func_ids_to_func_abs_paths: dict[str, list[list[str]]] = dict_tree_walker.build_str_leaves_paths()

        # `func_envelope` (2-level map) per `func_id` per `func_abs_path`
        func_id_to_func_abs_path_to_func_envelope: dict[str, dict[tuple[str, ...], dict]] = {}
        # Loop through func `data_envelope`-s from all delegators:
        for func_id, func_envelope in func_ids_to_func_envelopes.items():
            if func_id not in self.func_ids_to_func_abs_paths:
                # TODO: TODO_19_67_22_89: remove `ignored_func_ids_list` - load as `FuncState.fs_unplugged`:
                #       This `func_id` is not plugged into given tree.
                #       It will be loaded as `FuncState.fs_unplugged`.
                continue
            func_abs_paths = self.func_ids_to_func_abs_paths[func_id]
            for func_abs_path in func_abs_paths:
                assert (
                    func_id not in func_id_to_func_abs_path_to_func_envelope
                    or
                    tuple(func_abs_path) not in func_id_to_func_abs_path_to_func_envelope[func_id]
                )
                if self._is_best_matching_abs_tree_path(func_abs_path, interp_tree_abs_path):
                    # This `func_id` is mapped into the `func_tree` under this plugin:
                    func_id_to_func_abs_path_to_func_envelope.setdefault(
                        func_id,
                        {},
                    )[tuple(func_abs_path)] = deepcopy(func_envelope)
                    mapped_func_ids.append(func_id)

        (
            extra_index_props,
            extra_func_data_envelopes,
        ) = self.populate_func_envelope_collection(
            func_id_to_func_abs_path_to_func_envelope,
            interp_tree_abs_path,
            interp_tree_node_config_dict,
        )
        index_props.extend(extra_index_props)
        func_data_envelopes.extend(extra_func_data_envelopes)

        return (
            mapped_func_ids,
            index_props,
            func_data_envelopes,
        )

    def populate_func_envelope_collection(
        self,
        func_id_to_func_abs_path_to_func_envelope: dict[str, dict[tuple[str, ...], dict]],
        interp_tree_abs_path: tuple[str, ...],
        interp_tree_node_config_dict,
    ) -> tuple[
        # index_props:
        list[str],
        # func_data_envelopes:
        list[dict],
    ]:
        """
        Returns:
        *   `index_prop`-s used by all loaded funcs
        *   func `data_envelope`-s
        """

        self.populate_func_init_control(
            interp_tree_abs_path,
            interp_tree_node_config_dict,
        )
        self.populate_func_search_control(
            interp_tree_node_config_dict,
        )
        (
            interp_tree_abs_path_func_envelopes,
            prop_names,
        ) = self.populate_func_tree_props(
            func_id_to_func_abs_path_to_func_envelope,
        )
        envelope_collection = EnvelopeCollection(
            collection_name = ReservedEnvelopeClass.class_function.name,
            data_envelopes = interp_tree_abs_path_func_envelopes,
        )
        return (
            prop_names,
            envelope_collection.data_envelopes,
        )

    def _is_best_matching_abs_tree_path(
        self,
        func_abs_path,
        given_interp_tree_abs_path,
    ) -> bool:
        if sequence_starts_with(func_abs_path, given_interp_tree_abs_path):
            best_matching_abs_tree_path = given_interp_tree_abs_path
            max_matched_len = len(best_matching_abs_tree_path)
            for interp_tree_abs_path in self.interp_tree_abs_paths:
                if given_interp_tree_abs_path == interp_tree_abs_path:
                    continue
                if sequence_starts_with(func_abs_path, interp_tree_abs_path):
                    if max_matched_len < len(interp_tree_abs_path):
                        best_matching_abs_tree_path = interp_tree_abs_path
                        max_matched_len = len(best_matching_abs_tree_path)
                        break
                    elif max_matched_len == len(interp_tree_abs_path):
                        # There should not be two plugin paths leading to the same func:
                        raise RuntimeError()
                    else:
                        continue
            return given_interp_tree_abs_path == best_matching_abs_tree_path
        else:
            return False

    # noinspection PyMethodMayBeStatic
    def populate_func_init_control(
        self,
        interp_tree_abs_path: tuple[str, ...],
        interp_tree_node_config_dict: dict,
    ):
        interp_tree_node_config_dict[func_init_control_] = {
            init_types_to_values_: {},
        }

        init_types_to_values = interp_tree_node_config_dict[func_init_control_][init_types_to_values_]
        for sel_ipos, path_step in enumerate(interp_tree_abs_path):
            init_types_to_values[f"{func_envelope_path_step_prop_name(sel_ipos)}"] = path_step

    def populate_func_search_control(
        self,
        interp_tree_node_config_dict,
    ):
        """
        Provide `func_search_control` based on `func_ids_to_func_abs_paths`.
        """

        plugin_search_control_dict: dict = populate_search_control(
            ReservedEnvelopeClass.class_function.name,
            {
                ReservedPropName.envelope_class.name: ReservedEnvelopeClass.class_function.name,
            },
            [
                # TODO: TODO_61_99_68_90: figure out what to do with explicit `envelope_class` `search_prop`:
                {"class": ReservedPropName.envelope_class.name},
            ],
        )

        # `func_search_control` should include keys from the interp tree abs path:
        arg_name_to_prop_name_map = plugin_search_control_dict[arg_name_to_prop_name_map_]

        # Include func tree path:
        max_len = max_path_len(self.func_ids_to_func_abs_paths)
        for sel_ipos in range(max_len):
            arg_name_to_prop_name_map.append({
                f"{tree_step_arg_name(sel_ipos)}": f"{func_envelope_path_step_prop_name(sel_ipos)}"
            })

        # Include other fields:
        arg_name_to_prop_name_map.append({
            "state": ReservedPropName.func_state.name
        })
        arg_name_to_prop_name_map.append({
            "id": ReservedPropName.func_id.name
        })

        interp_tree_node_config_dict[func_search_control_] = plugin_search_control_dict
        self.plugin_search_control = search_control_desc.obj_from_input_dict(plugin_search_control_dict)

    def populate_func_tree_props(
        self,
        func_envelopes_index: dict[str, dict[tuple[str, ...], dict]],
    ) -> tuple[list[dict], list[str]]:
        """
        Populates func tree properties for each func `data_envelope` based on its path in func tree.

        For each func envelope:
        *   Select its place on the func tree (provided by plugin config).
        *   Populate the path as envelope props with `tree_step_prop_name_prefix_`.
        """
        interp_tree_abs_path_func_envelopes: list[dict] = []
        prop_names: set[str] = set()
        for func_id in self.func_ids_to_func_abs_paths:
            func_abs_paths: list[list[str]] = self.func_ids_to_func_abs_paths[func_id]

            for func_abs_path in func_abs_paths:

                if (
                    func_id not in func_envelopes_index
                    or
                    tuple(func_abs_path) not in func_envelopes_index[func_id]
                ):
                    continue

                func_envelope = func_envelopes_index[func_id][tuple(func_abs_path)]

                # Include func tree path:
                for sel_ipos, path_step_id in enumerate(func_abs_path):
                    prop_name = func_envelope_path_step_prop_name(sel_ipos)
                    func_envelope[prop_name] = path_step_id
                    prop_names.add(prop_name)

                interp_tree_abs_path_func_envelopes.append(func_envelope)

        return (
            interp_tree_abs_path_func_envelopes,
            list(prop_names),
        )

    def create_interp(
        self,
        interp_ctx: InterpContext,
    ) -> AbstractInterp:
        return FuncTreeInterp(
            self.plugin_instance_id,
            self.interp_tree_abs_paths_to_node_configs[interp_ctx.interp_tree_abs_path],
            interp_ctx,
            self.func_ids_to_func_abs_paths,
            self.paths_to_jump,
        )


def func_envelope_path_step_prop_name(
    path_step_ipos: int,
) -> str:
    return f"{tree_step_prop_name_prefix_}{path_step_ipos}"


def tree_step_arg_name(
    path_step_ipos: int,
) -> str:
    return f"{tree_step_arg_name_prefix_}{path_step_ipos}"


def max_path_len(
    func_ids_to_func_abs_paths: dict[str, list[list[str]]],
):
    """
    Find maximum path length.
    """
    max_len: int = 0
    for func_rel_paths in func_ids_to_func_abs_paths.values():
        for func_rel_path in func_rel_paths:
            max_len = max(max_len, len(func_rel_path))
    return max_len


class FuncTreeInterp(AbstractInterp):
    """
    Implements FS_26_43_73_72 func tree.

    Finds function `data_envelope` within func tree first,
    then uses its delegator (see `DelegatorAbstract`) to find all args-related `data_envelope`-s.

    See FS_55_57_45_04 enum selector.
    """

    def __init__(
        self,
        interp_factory_id,
        interp_tree_node_config_dict: dict,
        interp_ctx: InterpContext,
        func_ids_to_func_abs_paths: dict[str, list[list[str]]],
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

        self.func_ids_to_func_abs_paths: dict[str, list[list[str]]] = func_ids_to_func_abs_paths

    def _apply_func_init_control(self):
        self.interp_ctx.curr_container.assigned_prop_name_to_prop_value[
            ReservedPropName.envelope_class.name
        ] = AssignedValue(
            ReservedEnvelopeClass.class_function.name,
            ValueSource.init_value,
        )
        func_init_control: InitControl = init_control_desc.dict_schema.load(
            self.interp_tree_node_config_dict[func_init_control_],
        )
        for prop_type, prop_value in func_init_control.init_types_to_values.items():
            self.interp_ctx.curr_container.assigned_prop_name_to_prop_value[prop_type] = AssignedValue(
                prop_value,
                ValueSource.init_value,
            )
            if prop_type in self.interp_ctx.curr_container.remaining_prop_name_to_prop_value:
                del self.interp_ctx.curr_container.remaining_prop_name_to_prop_value[prop_type]

    def _apply_func_search_control(self):
        # Function `search_control` is populated based on
        # tree path (FS_01_89_09_24 interp tree + FS_26_43_73_72 func tree)
        # and plugin config (rather than data found in `data_envelope`):
        self.interp_ctx.curr_container.search_control = search_control_desc.dict_schema.load(
            self.interp_tree_node_config_dict[func_search_control_]
        )

    def _select_next_token_bucket(self) -> None:
        """
        FS_97_64_39_94: Logic for selecting `token_bucket`-s use by `EnvelopeContainer`-s.

        Each subsequent `EnvelopeContainer` uses next unused `token_bucket`
        until there is no more unused `token_bucket` left, in which case
        `EnvelopeContainer` uses `last_token_bucket_used`.
        """

        if self.interp_ctx.curr_container.used_token_bucket is None:

            if self.interp_ctx.last_token_bucket_used is None:
                self.interp_ctx.last_token_bucket_used = 0
            else:
                self.interp_ctx.last_token_bucket_used += 1
                if self.interp_ctx.last_token_bucket_used == len(self.interp_ctx.included_token_buckets):
                    self.interp_ctx.last_token_bucket_used -= 1

            self.interp_ctx.curr_container.used_token_bucket = self.interp_ctx.last_token_bucket_used

    def consume_dictated_args(self) -> bool:

        # All `dictated_arg`-s are consumed from the same `token_bucket`
        # (no need to have nested lists per `token_bucket`):
        consumed_dictated_args: list[ArgCommandValueDictated] = []
        any_consumed = False

        self._select_next_token_bucket()

        any_consumed = self.consume_one_dictated_arg_from_token_bucket(
            bucket_index = self.interp_ctx.curr_container.used_token_bucket,
            dictated_args = self.interp_ctx.remaining_dictated_args_per_bucket[
                self.interp_ctx.curr_container.used_token_bucket
            ],
            consumed_dictated_args = consumed_dictated_args,
        )

        # perform list modifications out of the prev loop:
        for dictated_arg in consumed_dictated_args:
            # If there are any consumed `dictated_arg`-s,
            # the `used_token_bucket` should be set:
            token_bucket_ipos = self.interp_ctx.curr_container.used_token_bucket
            assert token_bucket_ipos is not None
            # TODO: TODO_66_09_41_16: clarify command line processing
            #       Use helper functions which ensure consistency
            #       (like in this case, if one is removed, another is removed)
            self.interp_ctx.remaining_dictated_args_per_bucket[token_bucket_ipos].remove(dictated_arg)
            for token_ipos in dictated_arg.get_arg_tokens():
                self.interp_ctx.consumed_token_buckets[token_bucket_ipos].append(token_ipos)
                self.interp_ctx.remaining_token_buckets[token_bucket_ipos].remove(token_ipos)

        return any_consumed

    def consume_one_dictated_arg_from_token_bucket(
        self,
        bucket_index: int,
        dictated_args: list[ArgCommandValueDictated],
        consumed_dictated_args: list[ArgCommandValueDictated],
    ) -> bool:
        """
        Consumes at most one `dictated_arg` from given `bucket_index`.
        """

        any_consumed = False
        for dictated_arg in dictated_args:

            arg_name = dictated_arg.get_arg_name()
            arg_value = dictated_arg.get_arg_value()

            # TODO: FS_76_29_13_28 Why not define the order based on FS_31_70_49_15 `search_control`
            #       (instead of whatever internal order `remaining_prop_name_to_prop_value` has)?
            #       It could already be the case that `remaining_prop_name_to_prop_value` are ordered as `search_control`.
            #       Why not make it explicit?

            # See if `arg_name` matches any of `prop_name`-s:
            if arg_name in self.interp_ctx.curr_container.search_control.arg_name_to_prop_name_dict:
                prop_name = self.interp_ctx.curr_container.search_control.arg_name_to_prop_name_dict[arg_name]
                if prop_name in self.interp_ctx.curr_container.remaining_prop_name_to_prop_value:
                    self._assign_prop_name_as_explicit(
                        prop_name = prop_name,
                        arg_value = arg_value,
                        value_source = ValueSource.explicit_dictated_arg,
                    )

                    any_consumed = True
                    consumed_dictated_args.append(dictated_arg)

                    self._remove_determined_prop_name_from_remaining(prop_name)

                    # Consume one at most
                    # (caller function decides if this callee can remove one more):
                    break

        return any_consumed

    def consume_offered_args(self) -> bool:
        """
        Scans through `remaining_token_buckets` and tries to match its value against values of each type.

        Implements:
        *   FS_76_29_13_28 `command_arg` consumption priority.
        *   FS_44_36_84_88 consume args one by one:
            This func consumes all until the first remaining non-singled out arg.
        *   FS_97_64_39_94 `token_bucket`-s: consumption is limited to single bucket per `envelope_container`.
        """

        # All `offered_arg`-s are consumed from the same `token_bucket`
        # (no need to have nested lists per `token_bucket`):
        consumed_offered_args: list[ArgCommandValueOffered] = []
        any_consumed = False

        # Related to FS_51_67_38_37 avoid impossible arg combinations:
        # We can keep consuming `arg_value` without re-querying as long as matching `prop_value`-s are singled out.
        # We can also consume `arg_value` for ambiguous `prop_name` (with multiple `prop_value`-s) before re-querying.
        consumed_ambiguous_value = False

        self._select_next_token_bucket()

        any_consumed = self.consume_one_offered_arg_from_token_bucket(
            bucket_index = self.interp_ctx.curr_container.used_token_bucket,
            offered_args = self.interp_ctx.remaining_offered_args_per_bucket[
                self.interp_ctx.curr_container.used_token_bucket
            ],
            consumed_ambiguous_value = consumed_ambiguous_value,
            consumed_offered_args = consumed_offered_args,
        )

        # perform list modifications out of the prev loop:
        for offered_arg in consumed_offered_args:
            # If there are any consumed `offered_arg`-s,
            # the `used_token_bucket` should be set:
            token_bucket_ipos = self.interp_ctx.curr_container.used_token_bucket
            assert token_bucket_ipos is not None
            # TODO: TODO_66_09_41_16: clarify command line processing
            #       Use helper functions which ensure consistency
            #       (like in this case, if one is removed, another is removed)
            self.interp_ctx.remaining_offered_args_per_bucket[token_bucket_ipos].remove(offered_arg)
            self.interp_ctx.consumed_token_buckets[token_bucket_ipos].append(offered_arg.get_arg_token())
            self.interp_ctx.remaining_token_buckets[token_bucket_ipos].remove(offered_arg.get_arg_token())

        return any_consumed

    def consume_one_offered_arg_from_token_bucket(
        self,
        bucket_index: int,
        offered_args: list[ArgCommandValueOffered],
        consumed_ambiguous_value: bool,
        consumed_offered_args: list[ArgCommandValueOffered],
    ) -> bool:
        """
        Consumes at most one `offered_arg` from given `bucket_index`.
        """

        any_consumed = False
        for offered_arg in offered_args:

            arg_value = offered_arg.get_arg_value()

            # TODO: FS_76_29_13_28 Why not define the order based on FS_31_70_49_15 `search_control`
            #       (instead of whatever internal order `remaining_prop_name_to_prop_value` has)?
            #       It could already be the case that `remaining_prop_name_to_prop_value` are ordered as `search_control`.
            #       Why not make it explicit?

            # See if `arg_value` matches any of `prop_value`-s:
            for prop_name, prop_values in self.interp_ctx.curr_container.remaining_prop_name_to_prop_value.items():
                if arg_value in prop_values:
                    if (
                        len(prop_values) == 1
                        or
                        not consumed_ambiguous_value
                    ):
                        self._assign_prop_name_as_explicit(
                            prop_name = prop_name,
                            arg_value = arg_value,
                            value_source = ValueSource.explicit_offered_arg,
                        )

                        if len(prop_values) > 1:
                            # This was not a singled out `prop_value` for the given `prop_name`:
                            # allow only one ambiguous consumption without re-querying
                            # (for the `prop_name` according to the priority set by `search_control`).
                            # If more than one `prop_name` has multiple `prop_value`-s,
                            # some of the combinations of (`prop_name`, `prop_value`) pairs may not match
                            # the data and cannot be assigned, but it is possible to assign the first such `prop_name`
                            # with multiple (ambiguous) `prop_value` before re-querying without violating
                            # FS_51_67_38_37 avoid impossible arg combinations.
                            consumed_ambiguous_value = True

                        any_consumed = True
                        consumed_offered_args.append(offered_arg)

                        self._remove_determined_prop_name_from_remaining(prop_name)

                        # Consume one at most
                        # (caller function decides if this callee can remove one more):
                        break

        return any_consumed

    def _remove_determined_prop_name_from_remaining(
        self,
        prop_name: str,
    ):
        # TD_76_09_29_31: overlapped
        # Assign matching `prop_value` to the first `prop_name` it matches only once =
        # remove that `prop_name` from remaining:
        del self.interp_ctx.curr_container.remaining_prop_name_to_prop_value[prop_name]

    def _assign_prop_name_as_explicit(
        self,
        prop_name: str,
        arg_value: str,
        value_source: ValueSource,
    ):
        # Related to FS_13_51_07_97 singled out implicit values:
        # If `prop_name` is singled out (assigned as `ValueSource.implicit_value`)
        # but `offered_arg` or `dictated_arg` still determines `prop_name`,
        # `prop_name` must be updated as assigned by one of the explicit `ValueSource.*`.
        assert (
            value_source is ValueSource.explicit_dictated_arg
            or
            value_source is ValueSource.explicit_offered_arg
        )
        self.interp_ctx.curr_container.assigned_prop_name_to_prop_value[prop_name] = AssignedValue(
            arg_value,
            value_source,
        )

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

            # Func container or beyond:
            if self.interp_ctx.curr_container_ipos >= self.base_container_ipos:
                # Func param envelopes beyond func envelope: 0 for the first func param:
                func_param_container_offset = self.interp_ctx.curr_container_ipos - self.base_container_ipos
                # TODO: optimize it:
                #       *   we request one `search_control` from a list of them (internally)
                #       *   then, we give this item to allocate `searchable_container` but it may have already been allocated before:
                search_control: SearchControl = self.get_search_control(func_param_container_offset)
                while search_control is not None:
                    # Create `EnvelopeContainer`-s for next `data_envelope`-s to find:
                    self.interp_ctx.alloc_searchable_container(
                        self.base_container_ipos,
                        func_param_container_offset,
                        search_control,
                    )
                    func_param_container_offset += 1
                    search_control: SearchControl = self.get_search_control(func_param_container_offset)

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

    def get_search_control(
        self,
        func_param_container_offset: int,
    ) -> Union[SearchControl, None]:
        delegator_plugin = self.get_func_delegator()

        search_control: SearchControl = delegator_plugin.run_search_control(
            self.interp_ctx,
            self.get_found_func_data_envelope(),
            func_param_container_offset,
        )
        return search_control

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
            # TODO: TODO_73_23_85_93: use helper to select container ipos:
            self.base_container_ipos + function_container_ipos_
        )]
        if func_envelope.found_count == 1:
            return func_envelope.data_envelopes[0]
        return None

    def get_func_delegator(self):
        func_data_envelope = self.get_found_func_data_envelope()
        if func_data_envelope:
            delegator_plugin_instance_id = func_data_envelope[instance_data_][delegator_plugin_instance_id_]
            delegator_plugin: DelegatorAbstract = self.interp_ctx.action_delegators[delegator_plugin_instance_id]
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
        comp_values = self.propose_auto_comp_list()
        for comp_value in comp_values:
            insert_unique_to_sorted_list(self.interp_ctx.comp_suggestions, comp_value)

    def propose_auto_comp_list(self) -> list[str]:

        # TODO: TODO_51_14_50_19: ensure `tangent_token` always exists
        #       This may simplify this condition:
        if self.interp_ctx.parsed_ctx.tan_token_ipos >= 0:

            if self.interp_ctx.parsed_ctx.tan_token_ipos in self.interp_ctx.token_ipos_to_arg_map:
                tangent_arg = self.interp_ctx.token_ipos_to_arg_map[self.interp_ctx.parsed_ctx.tan_token_ipos]
                if isinstance(tangent_arg, ArgCommandIncomplete):
                    incomplete_arg: ArgCommandIncomplete = tangent_arg
                    return self._propose_for_incomplete_arg_with_tangent_token(incomplete_arg)
                elif isinstance(tangent_arg, ArgCommandValueDictated):
                    dictated_arg: ArgCommandValueDictated = tangent_arg
                    return self._propose_for_dictated_arg(dictated_arg)
                elif isinstance(tangent_arg, ArgCommandValueOffered):
                    offered_arg: ArgCommandValueOffered = tangent_arg
                    return self._propose_for_offered_arg(offered_arg)
                else:
                    raise TypeError(f"unhandled argument type: {type(tangent_arg)}")
            else:
                # TODO: TODO_66_09_41_16: clarify command line processing
                #       It makes sense to model every token as `command_arg` including `token_bucket` delimiter
                #       instead of using `excluded_tokens`, no?
                # This must be `token_bucket` delimiter.
                assert self.interp_ctx.parsed_ctx.tan_token_value == SpecialChar.TokenBucketDelimiter.value
                # TODO: TODO_66_09_41_16: clarify command line processing
                #       `token_bucket` delimiter should be suggested everywhere where applicable
                #       especially when `tan_token_l_part` starts with `SpecialChar.TokenBucketDelimiter.value`.

        elif self.interp_ctx.parsed_ctx.prev_token_ipos >= 0:

            if self.interp_ctx.parsed_ctx.prev_token_ipos in self.interp_ctx.token_ipos_to_arg_map:
                prev_arg = self.interp_ctx.token_ipos_to_arg_map[self.interp_ctx.parsed_ctx.prev_token_ipos]
                if isinstance(prev_arg, ArgCommandIncomplete):
                    incomplete_arg: ArgCommandIncomplete = prev_arg
                    return self._propose_for_incomplete_arg_with_prev_token(incomplete_arg)
                else:
                    return self._propose_remaining_prop_values_based_on_comp_scope()

        else:
            return self._propose_remaining_prop_values_based_on_comp_scope()

    def _propose_for_incomplete_arg_with_tangent_token(
        self,
        incomplete_arg: ArgCommandIncomplete,
    ):
        prop_name_token_ipos = incomplete_arg.get_arg_tokens()[0]
        assert self.interp_ctx.parsed_ctx.tan_token_ipos == prop_name_token_ipos
        return self._propose_arg_names_based_on_comp_scope()

    def _propose_for_incomplete_arg_with_prev_token(
        self,
        incomplete_arg: ArgCommandIncomplete,
    ):
        prop_name_token_ipos = incomplete_arg.get_arg_tokens()[0]
        assert self.interp_ctx.parsed_ctx.prev_token_ipos == prop_name_token_ipos
        arg_name = incomplete_arg.get_arg_name()
        if arg_name in self.interp_ctx.curr_container.search_control.arg_name_to_prop_name_dict:
            prop_name = self.interp_ctx.curr_container.search_control.arg_name_to_prop_name_dict[arg_name]
            return self._remaining_prop_values_from_given_prop_name(prop_name)
        else:
            return []

    def _propose_for_dictated_arg(
        self,
        dictated_arg: ArgCommandValueDictated,
    ):
        prop_name_token_ipos = dictated_arg.get_arg_tokens()[0]
        prop_value_token_ipos = dictated_arg.get_arg_tokens()[1]
        if self.interp_ctx.parsed_ctx.tan_token_ipos == prop_name_token_ipos:
            return self._propose_arg_names_based_on_comp_scope()
        elif self.interp_ctx.parsed_ctx.tan_token_ipos == prop_value_token_ipos:
            arg_name = dictated_arg.get_arg_name()
            if arg_name in self.interp_ctx.curr_container.search_control.arg_name_to_prop_name_dict:
                prop_name = self.interp_ctx.curr_container.search_control.arg_name_to_prop_name_dict[arg_name]
                return self._remaining_prop_values_from_given_prop_name(prop_name)
            else:
                return []
        else:
            raise ValueError("unexpected")

    def _propose_for_offered_arg(
        self,
        offered_arg: ArgCommandValueOffered,
    ):
        prop_value_token_ipos = offered_arg.get_arg_token()
        assert (
            self.interp_ctx.parsed_ctx.tan_token_ipos == prop_value_token_ipos
            or
            self.interp_ctx.parsed_ctx.prev_token_ipos == prop_value_token_ipos
        )
        return self._propose_remaining_prop_values_based_on_comp_scope()

    def _propose_arg_names_based_on_comp_scope(self) -> list[str]:
        """
        Complete `arg_name` (as `arg_name` 1-to-1 corresponds to `prop_name`):
        *   If initial completion, complete `arg_name` from remaining `prop_name`-s.
        *   If subsequent completion, complete `arg_name` from all `prop_name`-s of current `search_control`.
        """

        arg_name_prefix = self.interp_ctx.parsed_ctx.tan_token_l_part[1:]
        # TODO: TODO_66_09_41_16: clarify command line processing
        #       Selected `envelope_container` should depend on which
        #       `token_bucket` this `tangent_token` belongs to.
        #       There can be many `envelope_container`-s using that `token_bucket` -
        #       we may need to list suggestions from all (not from one).
        selected_container = self.interp_ctx.curr_container

        if self.interp_ctx.parsed_ctx.comp_scope in [
            CompScope.ScopeInitial,
            CompScope.ScopeUnknown,
        ]:
            prefixed_arg_names = []
            for prop_name in selected_container.remaining_prop_name_to_prop_value:
                arg_name = selected_container.search_control.prop_name_to_arg_name_dict[prop_name]
                if (
                    # TODO: TODO_66_09_41_16: clarify command line processing
                    #       What does this char mean? Put it into one of the `SpecialChar.*`.
                    not arg_name.startswith("_")
                    and
                    arg_name.startswith(arg_name_prefix)
                ):
                    prefixed_arg_names.append(SpecialChar.ArgNamePrefix.value + arg_name)
            return prefixed_arg_names

        if self.interp_ctx.parsed_ctx.comp_scope is CompScope.ScopeSubsequent:
            prefixed_arg_names = []
            for arg_name in selected_container.search_control.prop_name_to_arg_name_dict.values():
                if (
                    # TODO: TODO_66_09_41_16: clarify command line processing
                    #       What does this char mean? Put it into one of the `SpecialChar.*`.
                    not arg_name.startswith("_")
                    and
                    arg_name.startswith(arg_name_prefix)
                ):
                    prefixed_arg_names.append(SpecialChar.ArgNamePrefix.value + arg_name)
            return prefixed_arg_names

        return []

    def _propose_remaining_prop_values_based_on_comp_scope(self) -> list[str]:
        # TODO: FS_23_62_89_43: `tangent_token`
        #       The logic for both if-s (`if-A` and `if-B`) is identical at the moment - what do we want to improve?

        # TODO: FS_23_62_89_43: if-A:
        if self.interp_ctx.parsed_ctx.comp_scope in [
            CompScope.ScopeInitial,
            CompScope.ScopeUnknown,
        ]:
            if self.interp_ctx.parsed_ctx.tan_token_l_part == "":
                return self._remaining_prop_values_from_next_missing_prop_name()
            else:
                return self._remaining_prop_values_from_next_missing_prop_name()

        # TODO: FS_23_62_89_43: if-B:
        if self.interp_ctx.parsed_ctx.comp_scope is CompScope.ScopeSubsequent:
            if self.interp_ctx.parsed_ctx.tan_token_l_part == "":
                return self._remaining_prop_values_from_next_missing_prop_name()
            else:
                # TODO: FS_20_88_05_60: Suggest `arg_name`-s (:) for missing `prop_name`-s instead - it is `ScopeSubsequent`, user insist and wants something else:
                return self._remaining_prop_values_from_next_missing_prop_name()

        return []

    def _remaining_prop_values_from_next_missing_prop_name(self) -> list[str]:
        """
        Clarifications:
        *   remaining = because values for the given type are reduced based on narrowed down `data_envelope` set
        *   missing = because this `prop_name` is not specified yet
        *   next = because `prop_name`-s are tired in specific order
        """
        proposed_values: list[str] = []

        # Return filtered value set from the next missing arg:
        for prop_name in self.interp_ctx.curr_container.search_control.prop_name_to_arg_name_dict:
            if prop_name in self.interp_ctx.curr_container.remaining_prop_name_to_prop_value:
                # TODO: TODO_66_09_41_16: clarify command line processing
                #       only one condition should be enough:
                #       `prop_name` is either in assigned or in remaining, not in both:
                assert prop_name not in self.interp_ctx.curr_container.assigned_prop_name_to_prop_value

                proposed_values = [
                    # FS_71_87_33_52: `help_hint`:
                    self.interp_ctx.help_hint_cache.get_value_with_help_hint(prop_name, x)
                    for x in self.interp_ctx.curr_container.remaining_prop_name_to_prop_value[prop_name]
                    if (
                        # TODO: TODO_66_09_41_16: clarify command line processing
                        #       This does not make sense - only str are expected.
                        #       Clean this up (or, at least, keep assert for a while).
                        # NOTE: This checks for `str` meaning primitive (scalar, not `list` or `dict`),
                        #       but this also filters out `int` or others.
                        #       Primitive types should be converted to `str` when loaded.
                        #       See `ConfigOnlyLoader.convert_envelope_fields_to_string` for example.
                        isinstance(x, str)
                        and
                        # FS_32_05_46_00: using `startswith`:
                        # FS_23_62_89_43: filter using L part of tangent token:
                        x.startswith(self.interp_ctx.parsed_ctx.tan_token_l_part)
                        # TODO: FS_06_99_43_60: Support list[str] - what if one type can have array of values (and we need to match any as in OR)?
                    )
                ]
                if proposed_values:
                    # Collect only until the first proposed value set from missing args:
                    break

        return proposed_values

    def _remaining_prop_values_from_given_prop_name(
        self,
        prop_name: str,
    ) -> list[str]:
        """
        # TODO: TODO_66_09_41_16: clarify command line processing
        #       Maybe we should elaborate logic and give different lists depending on `CompScope`.
        #       *   Current: If initial, use remaining.
        #       *   Extra: If subsequent, list all possible for given `prop_name`.
        """
        proposed_values: list[str] = []

        # Return filtered value set from the next missing arg:
        if prop_name in self.interp_ctx.curr_container.remaining_prop_name_to_prop_value:
            # TODO: TODO_66_09_41_16: clarify command line processing
            #       only one condition should be enough:
            #       `prop_name` is either in assigned or in remaining, not in both:
            assert prop_name not in self.interp_ctx.curr_container.assigned_prop_name_to_prop_value

            proposed_values = [
                # FS_71_87_33_52: `help_hint`:
                self.interp_ctx.help_hint_cache.get_value_with_help_hint(prop_name, x)
                for x in self.interp_ctx.curr_container.remaining_prop_name_to_prop_value[prop_name]
                if (
                    # TODO: TODO_66_09_41_16: clarify command line processing
                    #       This does not make sense - only str are expected.
                    #       Clean this up (or, at least, keep assert for a while).
                    # NOTE: This checks for `str` meaning primitive (scalar, not `list` or `dict`),
                    #       but this also filters out `int` or others.
                    #       Primitive types should be converted to `str` when loaded.
                    #       See `ConfigOnlyLoader.convert_envelope_fields_to_string` for example.
                    isinstance(x, str)
                    and
                    # FS_32_05_46_00: using `startswith`:
                    # FS_23_62_89_43: filter using L part of tangent token:
                    x.startswith(self.interp_ctx.parsed_ctx.tan_token_l_part)
                    # TODO: FS_06_99_43_60: Support list[str] - what if one type can have array of values (and we need to match any as in OR)?
                )
            ]

        return proposed_values
