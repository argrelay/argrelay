from __future__ import annotations

from copy import deepcopy
from dataclasses import field, dataclass
from typing import Union

from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.enum_desc.TermColor import TermColor
from argrelay.enum_desc.ValueSource import ValueSource
from argrelay.misc_helper_common import eprint
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_server.HelpHintCache import HelpHintCache
from argrelay.relay_server.QueryEngine import QueryEngine, populate_query_dict
from argrelay.relay_server.QueryResult import QueryResult
from argrelay.runtime_context.AbstractArg import (
    ArgCommandValueOffered, ArgCommandValueDictated, ArgCommand,
    ArgCommandIncomplete, ArgCommandValue,
)
from argrelay.runtime_context.DataArg import (
    ArgCommandDataValueDictated, ArgCommandDataValueOffered,
    ArgCommandDataIncomplete,
)
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_context.token_bucket_utils import token_buckets_to_token_ipos_list

function_container_ipos_ = 0


@dataclass
class InterpContext:
    """
    Mutable state for the process of command line interpretation.
    """

    parsed_ctx: ParsedContext = field()

    # TODO: Move all dynamic and non-serializable objects into `InterpRuntime` (or something like that).
    interp_factories: dict[str, "AbstractInterpFactory"] = field()
    """
    Reference to `ServerConfig.action_delegators`.
    """

    action_delegators: dict[str, "DelegatorAbstract"] = field()
    """
    Reference to `ServerConfig.action_delegators`.
    """

    query_engine: QueryEngine = field()

    help_hint_cache: HelpHintCache = field()

    excluded_tokens: list[int] = field(init = False, default_factory = lambda: [])
    """
    Tokens excluded by ways other than consumption into `consumed_token_buckets`.
    """

    last_token_bucket_used: Union[int, None] = None
    """
    FS_97_64_39_94: ipos of the `token_bucket` which was used by one of the `EnvelopeContainer`-s
    """

    included_token_buckets: list[list[int]] = field(init = False, default_factory = lambda: [])
    """
    FS_97_64_39_94: `token_bucket`-s
    
    If `included_token_buckets` are combined,
    the result will contain both `remaining_token_buckets` and `consumed_token_buckets`.
    Field `included_token_buckets` is a maximum set for `token_bucket`-s -
    it is similar to the maximum set `ParsedContext.all_tokens`,
    but it cannot contain all tokens - it must exclude at least `SpecialChar.TokenBucketDelimiter` to start with.
    """

    remaining_token_buckets: list[list[int]] = field(init = False)
    """
    Same as `included_token_buckets` but for remaining tokens only.
    """

    consumed_token_buckets: list[list[int]] = field(init = False, default_factory = lambda: [])
    """
    Same as `included_token_buckets` but for consumed tokens only.
    """

    token_ipos_to_token_bucket_map: dict[int, int] = field(init = False, default_factory = lambda: {})
    """
    Index reversed to `included_token_buckets` -
    for each `token_ipos` it gives the index of the `token_bucket` it is in.
    It does not map `token_ipos`-es from `excluded_tokens`.
    """

    remaining_dictated_args_per_bucket: list[list[ArgCommandValueDictated]] = field(
        init = False,
        default_factory = lambda: [],
    )
    """
    Remaining `dictated_arg`-s for each bucket.
    """

    remaining_offered_args_per_bucket: list[list[ArgCommandValueOffered]] = field(
        init = False,
        default_factory = lambda: [],
    )
    """
    Remaining `offered_arg`-s for each bucket.
    """

    remaining_incomplete_args_per_bucket: list[list[ArgCommandIncomplete]] = field(
        init = False,
        default_factory = lambda: [],
    )
    """
    Remaining FS_08_58_30_24 `incomplete_arg`-s for each bucket.
    """

    tangent_arg: Union[ArgCommand, None] = field(init = False, default = None)
    """
    Similar to `tangent_token` but affects entire `command_arg` this `tangent_token` is part of.
    """

    token_ipos_to_arg_map: dict[int, ArgCommand] = field(init = False, default_factory = lambda: {})
    """
    Maps `token_ipos` into one of the args in
    either `remaining_offered_args_per_bucket` or `remaining_offered_args_per_bucket` (or `None`).
    """

    envelope_containers: list[EnvelopeContainer] = field(init = False, default_factory = lambda: [])
    """
    Each `envelope_container` wraps `data_envelope`-s matching query and some associated data.
    """

    curr_container: EnvelopeContainer = field(init = False, default = None)
    """
    One of the `envelope_containers` currently being searched.
    """

    curr_container_ipos: int = field(init = False, default = -1)
    """
    It is an `ipos` into `envelope_containers` to select `curr_container` (what is currently being searched for).

    Check `EnvelopeContainer.found_count` to see whether this container is singled out or not.

    All `envelope_containers` after `curr_container_ipos` will not be pointing to any `data_envelope`-s
    (search procedure has not reached them yet).
    """

    prev_interp: "AbstractInterp" = field(init = False, default = None)

    curr_interp: "AbstractInterp" = field(init = False, default = None)
    """
    Current interpreter during command line interpretation.
    """

    comp_suggestions: list[str] = field(init = False, default_factory = lambda: [])
    """
    Sorted list of completion suggestions.
    """

    interp_tree_abs_path: tuple[str, ...] = field(init = False, default = tuple([]))
    """
    Provides curr path within FS_01_89_09_24 interp tree.
    Takes part in implementation of FS_01_89_09_24 interp tree.
    """

    def __post_init__(self):
        self._init_token_buckets()
        self._build_arg_collections()

    def _init_token_buckets(self):
        self.included_token_buckets.append([])
        curr_bucket_index = len(self.included_token_buckets) - 1
        curr_token_bucket = self.included_token_buckets[curr_bucket_index]
        for token_ipos in range(0, len(self.parsed_ctx.all_tokens)):

            # Split and populate FS_97_64_39_94 `token_bucket`-s:
            if self.parsed_ctx.all_tokens[token_ipos] == SpecialChar.TokenBucketDelimiter.value:
                self.included_token_buckets.append([])
                curr_bucket_index = len(self.included_token_buckets) - 1
                curr_token_bucket = self.included_token_buckets[curr_bucket_index]
                # Exclude `SpecialChar.TokenBucketDelimiter` unconditionally:
                self.excluded_tokens.append(token_ipos)
            else:
                curr_token_bucket.append(token_ipos)
                self.token_ipos_to_token_bucket_map[token_ipos] = curr_bucket_index

        # Init remaining and consumed:
        self.remaining_token_buckets = deepcopy(self.included_token_buckets)
        for i in range(len(self.included_token_buckets)):
            self.consumed_token_buckets.append([])

    def _build_arg_collections(
        self,
    ):
        """
        Interpret `command_token`-s as `command_arg`-s within `token_bucket`-s
        """

        all_tokens = self.parsed_ctx.all_tokens

        for token_bucket in self.remaining_token_buckets:

            offered_args: list[ArgCommandValueOffered] = []
            dictated_args: list[ArgCommandValueDictated] = []
            incomplete_args: list[ArgCommandIncomplete] = []
            self.remaining_offered_args_per_bucket.append(offered_args)
            self.remaining_dictated_args_per_bucket.append(dictated_args)
            self.remaining_incomplete_args_per_bucket.append(incomplete_args)

            arg_name_ipos: Union[int, None] = None
            arg_name_value: Union[str, None] = None
            for token_ipos in token_bucket:

                token_value = all_tokens[token_ipos]

                if arg_name_value is None:
                    if token_value.startswith(SpecialChar.ArgNamePrefix.value):
                        # Skip `SpecialChar.ArgNamePrefix`:
                        arg_name_value = token_value[1:]
                        arg_name_ipos = token_ipos
                        continue
                    else:
                        command_arg = ArgCommandDataValueOffered(
                            token_ipos_list = [token_ipos],
                            arg_value = token_value,
                        )
                        offered_args.append(command_arg)
                        self.token_ipos_to_arg_map[token_ipos] = command_arg
                else:
                    command_arg = ArgCommandDataValueDictated(
                        token_ipos_list = [arg_name_ipos, token_ipos],
                        arg_name = arg_name_value,
                        arg_value = token_value,
                    )
                    dictated_args.append(command_arg)
                    self.token_ipos_to_arg_map[arg_name_ipos] = command_arg
                    self.token_ipos_to_arg_map[token_ipos] = command_arg
                    arg_name_ipos = None
                    arg_name_value = None

            # If `dictated_arg` is incomplete (has `arg_name`, but missing `arg_value`),
            # it is registered as `incomplete_arg`.
            if arg_name_value is not None:
                command_arg = ArgCommandDataIncomplete(
                    token_ipos_list = [arg_name_ipos],
                    arg_name = arg_name_value,
                )
                incomplete_args.append(command_arg)
                self.token_ipos_to_arg_map[arg_name_ipos] = command_arg
                arg_name_ipos = None
                arg_name_value = None

            # TODO: TODO_51_14_50_19: ensure `tangent_token` always exists
            #       This may simplify this condition:
            # Post-process `tangent_arg`:
            if (
                self.parsed_ctx.server_action is ServerAction.ProposeArgValues
                and
                self.parsed_ctx.tan_token_ipos >= 0
                and
                self.parsed_ctx.tan_token_ipos in self.token_ipos_to_arg_map
            ):
                tangent_arg = self.token_ipos_to_arg_map[self.parsed_ctx.tan_token_ipos]
                token_bucket_ipos = self.token_ipos_to_token_bucket_map[self.parsed_ctx.tan_token_ipos]
                # FS_23_62_89_43 `tangent_token` completion:
                # `ServerAction.ProposeArgValues` excludes tangent token from consumption because
                # this action is not supposed to consume that tangent token (and complete it instead):
                if isinstance(tangent_arg, ArgCommandIncomplete):
                    # `incomplete_arg` is not consumed - no need to remove:
                    pass
                elif isinstance(tangent_arg, ArgCommandValueDictated):
                    dictated_arg: ArgCommandValueDictated = tangent_arg
                    # TODO: TODO_66_09_41_16: clarify command line processing
                    #       Use helper functions which ensure consistency
                    #       (like in this case, if one is removed, another is removed)
                    self.remaining_dictated_args_per_bucket[token_bucket_ipos].remove(dictated_arg)
                    for token_ipos in dictated_arg.get_arg_tokens():
                        self.remaining_token_buckets[token_bucket_ipos].remove(token_ipos)
                        self.included_token_buckets[token_bucket_ipos].remove(token_ipos)
                        self.excluded_tokens.append(token_ipos)
                elif isinstance(tangent_arg, ArgCommandValueOffered):
                    offered_arg: ArgCommandValueOffered = tangent_arg
                    # TODO: TODO_66_09_41_16: clarify command line processing
                    #       Use helper functions which ensure consistency
                    #       (like in this case, if one is removed, another is removed)
                    self.remaining_offered_args_per_bucket[token_bucket_ipos].remove(offered_arg)
                    self.remaining_token_buckets[token_bucket_ipos].remove(offered_arg.get_arg_token())
                    self.included_token_buckets[token_bucket_ipos].remove(offered_arg.get_arg_token())
                    self.excluded_tokens.append(offered_arg.get_arg_token())
                else:
                    raise TypeError(f"unhandled argument type: {type(tangent_arg)}")
            else:
                # FS_23_62_89_43 `tangent_token` completion:
                # Set all tokens for consumption (including tangent token) in case of
                # `ServerAction.DescribeLineArgs` and `ServerAction.RelayLineArgs`.
                pass

    def remaining_token_ipos_list(
        self,
    ) -> list[int]:
        return token_buckets_to_token_ipos_list(self.remaining_token_buckets)

    def consumed_token_ipos_list(
        self,
    ) -> list[int]:
        return token_buckets_to_token_ipos_list(self.consumed_token_buckets)

    def alloc_searchable_container(
        self,
        base_container_ipos: int,
        func_param_container_offset: int,
        search_control: SearchControl,
    ):
        if (base_container_ipos + func_param_container_offset + 1) >= len(self.envelope_containers):
            envelope_container = EnvelopeContainer(search_control)
            self.envelope_containers.append(envelope_container)

    def is_last_container(self) -> bool:
        return self.curr_container_ipos + 1 == len(self.envelope_containers)

    def is_func_found(self) -> bool:
        return (
            self.curr_container_ipos >= function_container_ipos_
            and
            self.envelope_containers[function_container_ipos_].found_count == 1
        )

    def query_prop_values(self):
        if not self.curr_container:
            return

        ElapsedTime.measure(f"begin_query_envelopes: {self.curr_container.search_control.collection_name}")
        query_dict = populate_query_dict(self.curr_container)
        query_result: QueryResult = self.query_engine.query_prop_values(
            query_dict,
            self.curr_container.search_control,
            self.curr_container.assigned_prop_name_to_prop_value,
        )
        self.curr_container.remaining_prop_name_to_prop_value = query_result.remaining_prop_name_to_prop_value
        self.curr_container.data_envelopes = query_result.data_envelopes
        self.curr_container.found_count = query_result.found_count
        ElapsedTime.measure(f"end_query_envelopes: {query_dict} {self.curr_container.found_count}")

    def consume_args(
        self,
        interp_n: int
    ):
        while True:

            # FS_44_36_84_88 consume args one by one:
            while True:
                # Query envelope values only - they will be used for consumption of command line args:
                ElapsedTime.measure(f"[i={interp_n}]: before_entry_query: {self.curr_interp}")
                self.query_prop_values()
                # Reset to False as we just executed new query:
                arg_was_consumed = False

                # Because each `prop_value` set (per `prop_type`) is treated independently,
                # assignment of `prop_value`-s from args may set combinations
                # which yields no search result in subsequent query.
                # Logically, it is better to consume args one by one and running query after each consumption,
                # but this is not done due to query overhead.
                # Note that Tab-completion and selection (via manual step by human) in separate requests to server and
                # separate `interpret_command` calls is close to that logically better approach.
                if not arg_was_consumed:
                    ElapsedTime.measure(f"[i={interp_n}]: before_consume_dictated_args: {self.curr_interp}")
                    arg_was_consumed = self.curr_interp.consume_dictated_args()
                if not arg_was_consumed:
                    ElapsedTime.measure(f"[i={interp_n}]: before_consume_offered_args: {self.curr_interp}")
                    arg_was_consumed = self.curr_interp.consume_offered_args()

                if arg_was_consumed:
                    if self.curr_interp.consumes_args_at_once():
                        # No known interp consuming at once depends on query - do not query, simply exit loop:
                        break
                    else:
                        # Run next cycle to see if one more can be consumed:
                        pass
                else:
                    break

            query_changed = False

            if self.curr_container:
                # Set implicit values (so that applying defaults knows what they are):
                self.curr_container.populate_implicit_arg_values()

            if self.curr_interp.has_fill_control():
                # FS_72_53_55_13: options before defaults
                # Describing args will need to show options except default - query values before applying defaults:
                ElapsedTime.measure(f"[i={interp_n}]: before_query_without_defaults: {self.curr_interp}")
                # This step may be optimized away and is only needed to detect non-default options for
                # `ServerAction.DescribeLineArgs` but we perform it for all requests to
                # ensure they have common view in case of possible data issues
                # (e.g. TODO_39_25_11_76: `data_envelope`-s with missing props).
                self.query_prop_values()
                # Reset to False as we just executed new query:
                query_changed = False

                self._save_potentially_hidden_by_defaults()

                # Apply defaults (they may apply more than single value at a time):
                query_changed = (
                    self.curr_interp.delegate_fill_control()
                    or
                    query_changed
                )
                self._leave_only_hidden_by_defaults()

            # Query envelopes after all implicit and default values assigned:
            # TODO: We could probably select whether to query only envelopes or
            #       query their values depending on `ServerAction`.
            #       But init of next envelope depends on prev envelope found.
            if query_changed:
                if self.curr_interp.consumes_args_at_once():
                    # No known interp consuming at once depends on query - do not query, simply exit loop:
                    break
                else:
                    pass
            else:
                break

    # TODO: Move all dynamic and non-serializable objects into `InterpRuntime` (or something like that) together with this loop:
    def interpret_command(
        self,
        first_interp_factory_id: str,
    ) -> None:
        """
        Implements FS_55_57_45_04 enum selector version of FS_15_79_76_85 line processor.

        Start with initial interpreter and continue until curr interpreter returns no more next interpreter.

        TODO: TODO_18_51_46_14: refactor FS_42_76_93_51 zero_arg_interp into FS_15_79_76_85 line processor.
        """

        interp_n: int = 0

        # FS_01_89_09_24 interp tree:
        # start of tracking interp tree abs path while processing command
        # (to pass it to the next interp factory to create next interp):
        self.interp_tree_abs_path = tuple([])

        self.curr_interp = self.create_next_interp(first_interp_factory_id)
        while True:
            interp_n += 1

            self.consume_args(interp_n)

            ElapsedTime.measure(f"[i={interp_n}]: before_try_iterate: {self.curr_interp}")
            interp_step: InterpStep = self.curr_interp.try_iterate()
            ElapsedTime.measure(f"[i={interp_n}]: after_try_iterate: {self.curr_interp}: {interp_step}")
            if interp_step is InterpStep.NextEnvelope:
                continue
            elif interp_step is InterpStep.StopAll:
                ElapsedTime.measure(
                    f"[i={interp_n}]: before_contribute_to_completion: {self.curr_interp}"
                )
                self._contribute_to_completion()
                ElapsedTime.measure(
                    f"[i={interp_n}]: after_contribute_to_completion: {self.curr_interp}"
                )
                return
            elif interp_step is InterpStep.NextInterp:
                ElapsedTime.measure(
                    f"[i={interp_n}]: before_contribute_to_completion: {self.curr_interp}"
                )
                self._contribute_to_completion()
                ElapsedTime.measure(
                    f"[i={interp_n}]: after_contribute_to_completion: {self.curr_interp}"
                )
                self.prev_interp = self.curr_interp
                next_interp = self.curr_interp.next_interp()
                if next_interp:
                    self.curr_interp = next_interp
                else:
                    return
            else:
                raise RuntimeError(interp_step)

    def _save_potentially_hidden_by_defaults(self):
        """
        Save all `remaining_prop_name_to_prop_value` before applying defaults.

        These `filled_prop_values_hidden_by_defaults` are subsequently
        filtered out in `_leave_only_hidden_by_defaults`.
        """
        if not self.curr_container:
            return
        for remaining_prop_name in self.curr_container.remaining_prop_name_to_prop_value.keys():
            self.curr_container.filled_prop_values_hidden_by_defaults[
                remaining_prop_name
            ] = deepcopy(self.curr_container.remaining_prop_name_to_prop_value[remaining_prop_name])

    def _leave_only_hidden_by_defaults(self):
        """
        Weed out those `assigned_prop_name_to_prop_value` from `filled_prop_values_hidden_by_defaults`
        which were set by applying defaults.

        Use `filled_prop_values_hidden_by_defaults` saved before applying defaults
        (in `_save_potentially_hidden_by_defaults` for all `remaining_prop_name_to_prop_value`)
        and remove those which were not hidden by defaults
        to yield only those hidden by defaults.
        """
        if not self.curr_container:
            return
        types_not_hidden_by_defaults = []
        for prop_name_potentially_hidden_by_defaults in self.curr_container.filled_prop_values_hidden_by_defaults.keys():
            if prop_name_potentially_hidden_by_defaults in self.curr_container.assigned_prop_name_to_prop_value:
                if (
                    self.curr_container.assigned_prop_name_to_prop_value[
                        prop_name_potentially_hidden_by_defaults
                    ].value_source
                    is not
                    ValueSource.default_value
                ):
                    types_not_hidden_by_defaults.append(prop_name_potentially_hidden_by_defaults)
            else:
                types_not_hidden_by_defaults.append(prop_name_potentially_hidden_by_defaults)
        # Delete items outside the previous loop:
        for prop_name in types_not_hidden_by_defaults:
            del self.curr_container.filled_prop_values_hidden_by_defaults[prop_name]

    def _contribute_to_completion(self):
        # Each one in the chain of interpreters hava a chance to suggest completion values (contribute):
        self.curr_interp.propose_arg_completion()

    def propose_arg_values(self) -> list[str]:
        """
        FS_71_87_33_52: remove `help_hint` (after first space) if there is only one option
        """
        if len(self.comp_suggestions) == 1:
            first_space_ipos = self.comp_suggestions[0].find(' ')
            if first_space_ipos >= 0:
                self.comp_suggestions[0] = self.comp_suggestions[0][:first_space_ipos]
        return self.comp_suggestions

    def create_next_interp(
        self,
        next_interp_factory_id: str,
    ) -> "AbstractInterp":
        interp_factory: "AbstractInterpFactory" = self.interp_factories[next_interp_factory_id]
        return interp_factory.create_interp(
            self,
        )

    def print_debug(self, end_str: str = "\n") -> None:
        if not self.parsed_ctx.is_debug_enabled:
            return
        self.parsed_ctx.print_debug("")
        eprint(TermColor.debug_output.value, end = "")
        eprint(f"comp_suggestions: {self.comp_suggestions}", end = " ")
        eprint(TermColor.reset_style.value, end = end_str)
