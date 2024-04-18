from __future__ import annotations

from copy import deepcopy
from dataclasses import field, dataclass
from typing import Union

from argrelay.enum_desc.ArgSource import ArgSource
from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.ServerAction import ServerAction
from argrelay.enum_desc.SpecialChar import SpecialChar
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper_common import eprint
from argrelay.misc_helper_common.ElapsedTime import ElapsedTime
from argrelay.relay_server.HelpHintCache import HelpHintCache
from argrelay.relay_server.QueryEngine import QueryEngine, populate_query_dict
from argrelay.relay_server.QueryResult import QueryResult
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.runtime_context.SearchControl import SearchControl
from argrelay.runtime_context.arg_buckets_utils import arg_buckets_to_token_ipos_list

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

    action_delegators: dict[str, "AbstractDelegator"] = field()
    """
    Reference to `ServerConfig.action_delegators`.
    """

    query_engine: QueryEngine = field()

    help_hint_cache: HelpHintCache = field()

    excluded_tokens: list[int] = field(init = False, default_factory = lambda: [])
    """
    Tokens excluded by ways other than consumption into `consumed_arg_buckets`.
    """

    included_arg_buckets: list[list[int]] = field(init = False, default_factory = lambda: [])
    """
    FS_97_64_39_94: arg buckets
    
    If `included_arg_buckets` are combined,
    the result will contain both `remaining_arg_buckets` and `consumed_arg_buckets`.
    Field `included_arg_buckets` is maximum set for arg buckets -
    it is similar to maximum set `ParsedContext.all_tokens`,
    but it cannot contain all tokens - it must exclude at least `SpecialChar.ArgBucketDelimiter` to start with.
    """

    remaining_arg_buckets: list[list[int]] = field(init = False)
    """
    Same as `included_arg_buckets` but for remaining tokens only.
    """

    consumed_arg_buckets: list[list[int]] = field(init = False, default_factory = lambda: [])
    """
    Same as `included_arg_buckets` but for consumed tokens only.
    """

    token_ipos_to_arg_bucket_map: dict[int, int] = field(init = False, default_factory = lambda: {})
    """
    Index reversed to `included_arg_buckets` -
    for each `token_ipos` it gives the index of the `arg_bucket` it is in.
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
        self._init_arg_buckets()

    def _init_arg_buckets(self):
        self.included_arg_buckets.append([])
        curr_bucket_index = len(self.included_arg_buckets) - 1
        curr_arg_bucket = self.included_arg_buckets[curr_bucket_index]
        for token_ipos in range(0, len(self.parsed_ctx.all_tokens)):

            # Split and populate FS_97_64_39_94 arg buckets:
            if self.parsed_ctx.all_tokens[token_ipos] == SpecialChar.ArgBucketDelimiter.value:
                self.included_arg_buckets.append([])
                curr_bucket_index = len(self.included_arg_buckets) - 1
                curr_arg_bucket = self.included_arg_buckets[curr_bucket_index]
                # Exclude `SpecialChar.ArgBucketDelimiter` unconditionally:
                self.excluded_tokens.append(token_ipos)
            else:

                if self.parsed_ctx.server_action is ServerAction.ProposeArgValues:
                    # FS_23_62_89_43 tangent arg value completion:
                    # `ServerAction.ProposeArgValues` excludes tangent token because it is supposed to be completed:
                    if token_ipos == self.parsed_ctx.tan_token_ipos:
                        self.excluded_tokens.append(token_ipos)
                    else:
                        curr_arg_bucket.append(token_ipos)
                        self.token_ipos_to_arg_bucket_map[token_ipos] = curr_bucket_index
                else:
                    # FS_23_62_89_43 tangent arg value completion:
                    # Process all tokens (including tangent token) in case of `ServerAction.DescribeLineArgs`.
                    # Obviously, same applies for `ServerAction.RelayLineArgs` (as there is no chance to propose more).
                    curr_arg_bucket.append(token_ipos)
                    self.token_ipos_to_arg_bucket_map[token_ipos] = curr_bucket_index

        # Init remaining and consumed:
        self.remaining_arg_buckets = deepcopy(self.included_arg_buckets)
        for i in range(len(self.included_arg_buckets)):
            self.consumed_arg_buckets.append([])

    def next_remaining_token_ipos(
        self,
    ) -> Union[int, None]:
        for arg_bucket in self.remaining_arg_buckets:
            for token_ipos in arg_bucket:
                return token_ipos
        return None

    def remaining_token_ipos_list(
        self,
    ) -> list[int]:
        return arg_buckets_to_token_ipos_list(self.remaining_arg_buckets)

    def consumed_token_ipos_list(
        self,
    ) -> list[int]:
        return arg_buckets_to_token_ipos_list(self.consumed_arg_buckets)

    def alloc_searchable_containers(
        self,
        search_control_list: list[SearchControl],
    ):
        for search_control in search_control_list:
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
        if not (
            self.curr_container
            and
            self.curr_container.search_control.envelope_class
        ):
            # If `ReservedArgType.EnvelopeClass` is not specified, nothing to search:
            return

        ElapsedTime.measure(f"begin_query_envelopes: {self.curr_container.search_control.envelope_class}")
        query_dict = populate_query_dict(self.curr_container)
        query_result: QueryResult = self.query_engine.query_prop_values(
            query_dict,
            self.curr_container.search_control,
            self.curr_container.assigned_types_to_values,
        )
        self.curr_container.remaining_types_to_values = query_result.remaining_types_to_values
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
                    ElapsedTime.measure(f"[i={interp_n}]: before_consume_key_args: {self.curr_interp}")
                    arg_was_consumed = self.curr_interp.consume_key_args()
                if not arg_was_consumed:
                    ElapsedTime.measure(f"[i={interp_n}]: before_consume_pos_args: {self.curr_interp}")
                    arg_was_consumed = self.curr_interp.consume_pos_args()

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
                if self.parsed_ctx.server_action is ServerAction.DescribeLineArgs:
                    # TODO: FS_72_53_55_13: options before defaults
                    # Describing args will need to show options except default - query values before defaults:
                    ElapsedTime.measure(f"[i={interp_n}]: before_query_without_defaults: {self.curr_interp}")
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
        if not self.curr_container:
            return
        for remaining_type in self.curr_container.remaining_types_to_values.keys():
            self.curr_container.filled_types_to_values_hidden_by_defaults[
                remaining_type
            ] = deepcopy(self.curr_container.remaining_types_to_values[remaining_type])

    def _leave_only_hidden_by_defaults(self):
        if not self.curr_container:
            return
        types_not_hidden_by_defaults = []
        for type_potentially_hidden_by_defaults in self.curr_container.filled_types_to_values_hidden_by_defaults.keys():
            if type_potentially_hidden_by_defaults in self.curr_container.assigned_types_to_values:
                if (
                    self.curr_container.assigned_types_to_values[
                        type_potentially_hidden_by_defaults
                    ].arg_source
                    is not
                    ArgSource.DefaultValue
                ):
                    types_not_hidden_by_defaults.append(type_potentially_hidden_by_defaults)
            else:
                types_not_hidden_by_defaults.append(type_potentially_hidden_by_defaults)
        for arg_type in types_not_hidden_by_defaults:
            del self.curr_container.filled_types_to_values_hidden_by_defaults[arg_type]

    def _contribute_to_completion(self):
        if self.parsed_ctx.server_action is ServerAction.ProposeArgValues:
            # Each in the chains of interpreters hava a chance to suggest completion values (contribute):
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
