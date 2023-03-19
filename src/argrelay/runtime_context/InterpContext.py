from __future__ import annotations

from dataclasses import field, dataclass

from argrelay.enum_desc.CompType import CompType
from argrelay.enum_desc.InterpStep import InterpStep
from argrelay.enum_desc.RunMode import RunMode
from argrelay.enum_desc.TermColor import TermColor
from argrelay.misc_helper import eprint
from argrelay.misc_helper.ElapsedTime import ElapsedTime
from argrelay.relay_server.HelpHintCache import HelpHintCache
from argrelay.relay_server.QueryEngine import QueryEngine, populate_query_dict
from argrelay.relay_server.QueryResult import QueryResult
from argrelay.runtime_context.EnvelopeContainer import EnvelopeContainer
from argrelay.runtime_context.ParsedContext import ParsedContext
from argrelay.runtime_context.SearchControl import SearchControl

function_envelope_ipos_ = 0


@dataclass
class InterpContext:
    """
    Mutable state for the process of command line interpretation.
    """

    parsed_ctx: ParsedContext

    # TODO: Move all dynamic and non-serializable objects into `InterpRuntime` (or something like that).
    interp_factories: dict[str, "AbstractInterpFactory"]
    """
    Reference to `ServerConfig.action_delegators`.
    """

    action_delegators: dict[str, "AbstractDelegator"]
    """
    Reference to `ServerConfig.action_delegators`.
    """

    query_engine: QueryEngine

    help_hint_cache: HelpHintCache

    unconsumed_tokens: list[int] = field(init = False)
    """
    Remaining tokens (their ipos) which are still unconsumed (in ascending order).
    """

    consumed_tokens: list[int] = field(init = False, default_factory = lambda: [])
    """
    Already consumed tokens (their ipos) in the order of their consumption.
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

    def __post_init__(self):
        self.unconsumed_tokens = self._init_unconsumed_tokens()

    def _init_unconsumed_tokens(self):
        return [
            token_ipos for token_ipos in range(0, len(self.parsed_ctx.all_tokens))
            if (
                (
                    self.parsed_ctx.run_mode == RunMode.CompletionMode
                    and
                    # Completion mode excludes tangent token because it is supposed to be completed:
                    token_ipos != self.parsed_ctx.tan_token_ipos
                )
                or
                (
                    self.parsed_ctx.run_mode == RunMode.InvocationMode
                )
            )
        ]

    def alloc_searchable_containers(
        self,
        search_control_list: list[SearchControl],
    ):
        for search_control in search_control_list:
            envelope_container = EnvelopeContainer(search_control)
            self.envelope_containers.append(envelope_container)

    def is_last_container(self) -> bool:
        return self.curr_container_ipos + 1 == len(self.envelope_containers)

    def is_funct_found(self) -> bool:
        return (
            self.curr_container_ipos >= function_envelope_ipos_
            and
            self.envelope_containers[function_envelope_ipos_].found_count == 1
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

        # TODO: FS_06_99_43_60: How to query values contained in arrays? For example, `GitRepoRelPath` is array. How to query envelopes which contain given value in elements of the array?
        query_result: QueryResult = self.query_engine.query_prop_values(
            query_dict,
            self.curr_container.search_control,
            self.curr_container.assigned_types_to_values,
        )
        self.curr_container.remaining_types_to_values = query_result.remaining_types_to_values
        self.curr_container.data_envelope = query_result.data_envelope
        self.curr_container.found_count = query_result.found_count
        ElapsedTime.measure(f"end_query_envelopes: {query_dict} {self.curr_container.found_count}")

    # TODO: Move all dynamic and non-serializable objects into `InterpRuntime` (or something like that) together with this loop:
    def interpret_command(self, first_interp_factory_id: str) -> None:
        """
        Main interpretation loop.

        Start with initial interpreter and continue until curr interpreter returns no more next interpreter.
        """

        interp_n: int = 0
        self.curr_interp = self.create_next_interp(first_interp_factory_id)
        while True:
            interp_n += 1

            # Query envelope values only - they will be used for consumption of command line args:
            ElapsedTime.measure(f"[i={interp_n}]: before_init_query: {type(self.curr_interp).__name__}")
            self.query_prop_values()

            ElapsedTime.measure(f"[i={interp_n}]: before_consume_args: {type(self.curr_interp).__name__}")
            self.curr_interp.consume_key_args()
            self.curr_interp.consume_pos_args()

            ElapsedTime.measure(f"[i={interp_n}]: before_reduce_query: {type(self.curr_interp).__name__}")
            self.query_prop_values()
            if self.curr_container:
                self.curr_container.populate_implicit_arg_values()

            if self.parsed_ctx.comp_type == CompType.DescribeArgs:
                # Describing args will need to show options except default - query values before defaults:
                # TODO:
                pass

            # Apply defaults:
            self.curr_interp.run_fill_control()

            # Query envelopes after all defaults applied:
            # TODO: We could probably select whether to query only envelopes or their values depending on RunMode.
            #       But init of next envelope depends on prev envelope found.
            ElapsedTime.measure(f"[i={interp_n}]: before_final_query: {type(self.curr_interp).__name__}")
            self.query_prop_values()

            ElapsedTime.measure(f"[i={interp_n}]: before_try_iterate: {type(self.curr_interp).__name__}")
            interp_step: InterpStep = self.curr_interp.try_iterate()
            ElapsedTime.measure(f"[i={interp_n}]: after_try_iterate: {type(self.curr_interp).__name__}: {interp_step}")
            if interp_step == InterpStep.NextEnvelope:
                continue
            elif interp_step == InterpStep.StopAll:
                ElapsedTime.measure(
                    f"[i={interp_n}]: before_contribute_to_completion: {type(self.curr_interp).__name__}"
                )
                self._contribute_to_completion()
                ElapsedTime.measure(
                    f"[i={interp_n}]: after_contribute_to_completion: {type(self.curr_interp).__name__}"
                )
                return
            elif interp_step == InterpStep.NextInterp:
                ElapsedTime.measure(
                    f"[i={interp_n}]: before_contribute_to_completion: {type(self.curr_interp).__name__}"
                )
                self._contribute_to_completion()
                ElapsedTime.measure(
                    f"[i={interp_n}]: after_contribute_to_completion: {type(self.curr_interp).__name__}"
                )
                self.prev_interp = self.curr_interp
                next_interp = self.curr_interp.next_interp()
                if next_interp:
                    self.curr_interp = next_interp
                else:
                    return
            else:
                raise RuntimeError(interp_step)

    def _contribute_to_completion(self):
        if self.parsed_ctx.run_mode == RunMode.CompletionMode:
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
        interp_factory_id: str,
    ) -> "AbstractInterp":
        interp_factory: "AbstractInterpFactory" = self.interp_factories[interp_factory_id]
        return interp_factory.create_interp(
            self,
        )

    def print_debug(self, end_str: str = "\n") -> None:
        if not self.parsed_ctx.is_debug_enabled:
            return
        self.parsed_ctx.print_debug("")
        eprint(TermColor.DEBUG.value, end = "")
        eprint(f"comp_suggestions: {self.comp_suggestions}", end = " ")
        eprint(TermColor.RESET.value, end = end_str)
